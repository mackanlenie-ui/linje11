package se.minaarbetspass;
import android.app.*;
import android.content.*;
import android.os.Build;
import org.json.*;
import java.util.Calendar;

public class Reminders extends BroadcastReceiver {
    static android.content.SharedPreferences prefs(Context c){return c.getSharedPreferences(c.getPackageName()+"_preferences",0);}
    static long start(JSONObject x)throws Exception{
        Calendar cal=Calendar.getInstance();cal.setTimeInMillis(x.getLong("date"));
        String[] t=x.getString("start").split(":");cal.set(Calendar.HOUR_OF_DAY,Integer.parseInt(t[0]));cal.set(Calendar.MINUTE,Integer.parseInt(t[1]));cal.set(Calendar.SECOND,0);cal.set(Calendar.MILLISECOND,0);return cal.getTimeInMillis();
    }
    static PendingIntent intent(Context c,String key,String text,long start){
        Intent i=new Intent(c,Reminders.class).setAction("se.minaarbetspass.REMIND").putExtra("key",key).putExtra("text",text).putExtra("start",start);
        return PendingIntent.getBroadcast(c,700,i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }
    public static void schedule(Context c){
        AlarmManager alarms=(AlarmManager)c.getSystemService(Context.ALARM_SERVICE);alarms.cancel(intent(c,"","",0));
        int minutes=prefs(c).getInt("reminder",0);if(minutes==0)return;
        if(Build.VERSION.SDK_INT>=33&&c.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)!=android.content.pm.PackageManager.PERMISSION_GRANTED)return;
        long now=System.currentTimeMillis(),best=Long.MAX_VALUE,begin=0;String key="",text="";
        try{JSONArray all=new JSONArray(prefs(c).getString("shifts","[]"));
            for(int n=0;n<all.length();n++){JSONObject x=all.getJSONObject(n);if(x.optBoolean("done",false)||x.optInt("owner",0)==1)continue;
                long t=start(x),due=t-minutes*60000L;String k=t+"|"+x.optString("end");
                if(t<=now||prefs(c).getStringSet("sentReminders",java.util.Collections.emptySet()).contains(k))continue;
                long fire=Math.max(due,now+1000);
                if(fire<best){best=fire;begin=t;key=k;text=x.optString("start")+"–"+x.optString("end")+" · "+x.optString("service")+" "+x.optString("line");}
            }
            if(best!=Long.MAX_VALUE)alarms.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP,best,intent(c,key,text,begin));
        }catch(Exception ignored){}
    }
    @Override public void onReceive(Context c,Intent i){
        if("se.minaarbetspass.REMIND".equals(i.getAction())&&prefs(c).getInt("reminder",0)>0){
            String key=i.getStringExtra("key");
            if(key!=null&&!prefs(c).getStringSet("sentReminders",java.util.Collections.emptySet()).contains(key)&&i.getLongExtra("start",0)>System.currentTimeMillis()){
                boolean valid=false;
                try{JSONArray all=new JSONArray(prefs(c).getString("shifts","[]"));for(int n=0;n<all.length();n++){JSONObject x=all.getJSONObject(n);if(x.optInt("owner",0)!=1&&!x.optBoolean("done",false)&&key.equals(start(x)+"|"+x.optString("end")))valid=true;}}catch(Exception ignored){}
                if(valid){
                    java.util.HashSet<String> sent=new java.util.HashSet<>(prefs(c).getStringSet("sentReminders",java.util.Collections.emptySet()));sent.add(key);prefs(c).edit().putStringSet("sentReminders",sent).apply();
                    NotificationManager nm=(NotificationManager)c.getSystemService(Context.NOTIFICATION_SERVICE);
                    if(Build.VERSION.SDK_INT>=26)nm.createNotificationChannel(new NotificationChannel("shifts","Arbetspass",NotificationManager.IMPORTANCE_DEFAULT));
                    Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(c,"shifts"):new Notification.Builder(c);
                    b.setSmallIcon(android.R.drawable.ic_dialog_info).setContentTitle("Ditt arbetspass börjar snart").setContentText(i.getStringExtra("text")).setAutoCancel(true)
                    .setContentIntent(PendingIntent.getActivity(c,701,new Intent(c,MainActivity.class),PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
                    try{nm.notify(700,b.build());}catch(SecurityException ignored){}
                }
            }
        }schedule(c);
    }
}
