package se.minaarbetspass;

import android.app.*;
import android.appwidget.*;
import android.content.*;
import android.widget.RemoteViews;
import org.json.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class WorkWidgetProvider extends AppWidgetProvider {
    @Override public void onUpdate(Context context,AppWidgetManager manager,int[] ids){
        for(int id:ids)manager.updateAppWidget(id,views(context));
    }

    @Override public void onReceive(Context context,Intent intent){
        super.onReceive(context,intent);
        if(Intent.ACTION_TIME_CHANGED.equals(intent.getAction())||Intent.ACTION_TIMEZONE_CHANGED.equals(intent.getAction())||Intent.ACTION_DATE_CHANGED.equals(intent.getAction()))updateAll(context);
    }

    static void updateAll(Context context){
        AppWidgetManager manager=AppWidgetManager.getInstance(context);
        int[] ids=manager.getAppWidgetIds(new ComponentName(context,WorkWidgetProvider.class));
        for(int id:ids)manager.updateAppWidget(id,views(context));
    }

    static RemoteViews views(Context context){
        RemoteViews v=new RemoteViews(context.getPackageName(),R.layout.work_widget);
        ArrayList<WidgetScheduleSummary.Entry> all=entries(context);
        long now=System.currentTimeMillis();
        WidgetScheduleSummary.Entry mine=WidgetScheduleSummary.next(all,0,now),hers=WidgetScheduleSummary.next(all,1,now);
        v.setTextViewText(R.id.widget_mine,"Jag: "+(mine==null?"inga kommande pass":mine.label));
        v.setTextViewText(R.id.widget_lenie,"Lenie: "+(hers==null?"inga kommande pass":hers.label));
        v.setTextViewText(R.id.widget_free,"Tillsammans: "+nextFreeDay(context));
        Intent open=new Intent(context,MainActivityCurrent.class);
        PendingIntent pending=PendingIntent.getActivity(context,0,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.widget_root,pending);
        return v;
    }

    static ArrayList<WidgetScheduleSummary.Entry> entries(Context context){
        ArrayList<WidgetScheduleSummary.Entry> out=new ArrayList<>();
        try{
            JSONArray a=new JSONArray(AppPrefs.get(context).getString("shifts","[]"));
            SimpleDateFormat date=new SimpleDateFormat("EEE d MMM",new Locale("sv","SE"));
            for(int i=0;i<a.length();i++){
                JSONObject o=a.getJSONObject(i);long day=o.optLong("date",0);String start=o.optString("start","08:00"),end=o.optString("end","16:00");int owner=o.optInt("owner",0)==1?1:0;
                long s=at(day,start),e=at(day,end);if(toMin(end)<toMin(start))e=at(addDay(day),end);
                String label=cap(date.format(new Date(day)))+" · "+start+"–"+end;
                out.add(new WidgetScheduleSummary.Entry(owner,s,e,label));
            }
        }catch(Exception ignored){}
        return out;
    }

    static String nextFreeDay(Context context){
        try{
            JSONArray a=new JSONArray(AppPrefs.get(context).getString("shifts","[]"));
            long today=dayStart(System.currentTimeMillis());
            SimpleDateFormat f=new SimpleDateFormat("EEE d MMM",new Locale("sv","SE"));
            for(int i=0;i<14;i++){
                long d=addDays(today,i);boolean mine=false,hers=false;
                for(int j=0;j<a.length();j++){JSONObject o=a.getJSONObject(j);if(dayStart(o.optLong("date",0))!=d)continue;if(o.optInt("owner",0)==1)hers=true;else mine=true;}
                if(!mine&&!hers)return "lediga "+cap(f.format(new Date(d)));
            }
        }catch(Exception ignored){}
        return "ingen gemensam ledig dag hittad";
    }

    static int toMin(String t){try{String[]p=t.split(":");return Integer.parseInt(p[0])*60+Integer.parseInt(p[1]);}catch(Exception e){return 0;}}
    static long at(long day,String t){return dayStart(day)+toMin(t)*60000L;}
    static long dayStart(long time){Calendar c=Calendar.getInstance();c.setTimeInMillis(time);c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);return c.getTimeInMillis();}
    static long addDay(long d){return addDays(d,1);}
    static long addDays(long d,int n){Calendar c=Calendar.getInstance();c.setTimeInMillis(d);c.add(Calendar.DAY_OF_MONTH,n);return dayStart(c.getTimeInMillis());}
    static String cap(String s){return s==null||s.isEmpty()?s:s.substring(0,1).toUpperCase()+s.substring(1);}
}
