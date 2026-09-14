package se.minaarbetspass;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.view.*;
import android.view.inputmethod.InputMethodManager;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.*;
import java.util.*;

public class MainActivity extends Activity {
    static final int BG=Color.rgb(7,17,31), CARD=Color.rgb(18,33,52), CARD2=Color.rgb(25,45,67);
    static final int TEXT=Color.WHITE, MUTED=Color.rgb(166,185,205), TEAL=Color.rgb(45,212,191), RED=Color.rgb(248,113,113);
    final ArrayList<Shift> shifts=new ArrayList<>();
    LinearLayout content, nav; TextView title, monthHours, weekHours;
    int screen=0; long selectedDay=dayStart(System.currentTimeMillis());
    final SimpleDateFormat keyFmt=new SimpleDateFormat("yyyy-MM-dd",new Locale("sv","SE"));
    final SimpleDateFormat dateFmt=new SimpleDateFormat("EEE d MMM",new Locale("sv","SE"));
    static final int EXPORT=20, IMPORT=21;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(BG); getWindow().setNavigationBarColor(BG);
        load(); buildShell(); showHome();
    }

    void buildShell(){
        LinearLayout root=new LinearLayout(this); root.setOrientation(LinearLayout.VERTICAL); root.setBackgroundColor(BG);
        root.setPadding(dp(16),dp(10),dp(16),dp(8));
        root.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(dp(16),insets.getSystemWindowInsetTop()+dp(6),dp(16),Math.max(dp(8),insets.getSystemWindowInsetBottom()));return insets;});
        LinearLayout header=new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL);
        title=text("Mina arbetspass",25,TEXT,true); header.addView(title,new LinearLayout.LayoutParams(0,dp(60),1));
        TextView menu=text("⋮",30,TEXT,true); menu.setGravity(Gravity.CENTER); menu.setOnClickListener(v->showMenu(menu));
        header.addView(menu,new LinearLayout.LayoutParams(dp(48),dp(48))); root.addView(header);
        ScrollView scroll=new ScrollView(this); scroll.setFillViewport(true);
        content=new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL); content.setPadding(0,dp(4),0,dp(16));
        scroll.addView(content); root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        nav=new LinearLayout(this); nav.setGravity(Gravity.CENTER); nav.setPadding(0,dp(6),0,0);
        root.addView(nav,new LinearLayout.LayoutParams(-1,dp(66)));
        setContentView(root);
    }

    void nav(int active){
        nav.removeAllViews();
        String[] labels={"⌂\nÖversikt","▦\nKalender","☷\nAlla pass"};
        for(int i=0;i<labels.length;i++){
            final int n=i; TextView v=text(labels[i],13,i==active?TEAL:MUTED,i==active);
            v.setGravity(Gravity.CENTER); v.setOnClickListener(x->{screen=n;if(n==0)showHome();else if(n==1)showCalendar();else showAll();});
            nav.addView(v,new LinearLayout.LayoutParams(0,-1,1));
        }
        TextView add=text("+",34,BG,true); add.setGravity(Gravity.CENTER); add.setBackground(round(TEAL,30));
        add.setOnClickListener(v->editDialog(null,false)); LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(dp(58),dp(58)); nav.addView(add,p);
    }

    void showHome(){
        screen=0; title.setText("Mina arbetspass"); content.removeAllViews(); nav(0);
        TextView hello=text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false);
        content.addView(hello,mp(-1,-2,0,0,0,12));
        LinearLayout stats=new LinearLayout(this);
        monthHours=stat(stats,"Denna månad",formatHours(sumMonth(System.currentTimeMillis())));
        weekHours=stat(stats,"Denna vecka",formatHours(sumWeek(System.currentTimeMillis())));
        content.addView(stats,mp(-1,dp(108),0,0,0,14));
        Shift next=nextShift();
        LinearLayout hero=card();
        hero.addView(text(next==null?"Inga kommande pass":"NÄSTA ARBETSPASS",12,TEAL,true));
        if(next==null) hero.addView(text("Tryck på + för att lägga in ditt första pass.",18,TEXT,true),mp(-1,-2,0,12,0,0));
        else {
            hero.addView(text(cap(dateFmt.format(new Date(next.date))),22,TEXT,true),mp(-1,-2,0,10,0,3));
            hero.addView(text(next.start+"–"+next.end+"  •  "+formatHours(next.minutes()),18,TEXT,true));
            String sub=join(next.service,next.line);
            if(!sub.isEmpty()) hero.addView(text(sub,14,MUTED,false),mp(-1,-2,0,7,0,0));
            hero.setOnClickListener(v->editDialog(next,false));
        }
        content.addView(hero,mp(-1,-2,0,0,0,16));
        content.addView(section("Kommande pass"));
        ArrayList<Shift> upcoming=new ArrayList<>();
        long today=dayStart(System.currentTimeMillis());
        for(Shift s:sorted()) if(s.date>=today) upcoming.add(s);
        if(upcoming.isEmpty()) empty("Du har inga inlagda pass.");
        else for(int i=0;i<Math.min(5,upcoming.size());i++) content.addView(shiftCard(upcoming.get(i)));
    }

    TextView stat(LinearLayout parent,String label,String value){
        LinearLayout box=card(); TextView val=text(value,27,TEXT,true); box.addView(val); box.addView(text(label,13,MUTED,false),mp(-1,-2,0,6,0,0));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,1); p.setMargins(0,0,dp(7),0); parent.addView(box,p); return val;
    }

    void showCalendar(){
        screen=1; title.setText("Kalender"); content.removeAllViews(); nav(1);
        CalendarView cv=new CalendarView(this); cv.setFirstDayOfWeek(Calendar.MONDAY); cv.setDate(selectedDay,false,true);
        cv.setOnDateChangeListener((view,y,m,d)->{Calendar c=Calendar.getInstance();c.set(y,m,d,0,0,0);c.set(Calendar.MILLISECOND,0);selectedDay=c.getTimeInMillis();showCalendar();});
        LinearLayout wrap=card(); wrap.addView(cv,new LinearLayout.LayoutParams(-1,dp(330))); content.addView(wrap,mp(-1,-2,0,0,0,14));
        content.addView(section(cap(dateFmt.format(new Date(selectedDay)))));
        boolean any=false; for(Shift s:sorted()) if(s.date==selectedDay){content.addView(shiftCard(s));any=true;}
        if(!any) empty("Inga pass denna dag.");
    }

    void showAll(){
        screen=2; title.setText("Alla pass"); content.removeAllViews(); nav(2);
        TextView summary=text(shifts.size()+" pass  •  Totalt "+formatHours(sumAll()),15,MUTED,false);
        content.addView(summary,mp(-1,-2,0,0,0,14));
        if(shifts.isEmpty()){empty("Här visas alla dina arbetspass.");return;}
        String last="";
        for(Shift s:sorted()){
            String month=new SimpleDateFormat("MMMM yyyy",new Locale("sv","SE")).format(new Date(s.date));
            if(!month.equals(last)){content.addView(section(cap(month)));last=month;}
            content.addView(shiftCard(s));
        }
    }

    LinearLayout shiftCard(Shift s){
        LinearLayout row=card(); row.setOrientation(LinearLayout.HORIZONTAL); row.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout left=new LinearLayout(this); left.setOrientation(LinearLayout.VERTICAL);
        left.addView(text(cap(dateFmt.format(new Date(s.date))),16,TEXT,true));
        left.addView(text(s.start+"–"+s.end+"  •  rast "+s.breakMin+" min",14,MUTED,false),mp(-1,-2,0,4,0,0));
        String sub=join(s.service,s.line); if(!sub.isEmpty()) left.addView(text(sub,13,MUTED,false),mp(-1,-2,0,4,0,0));
        row.addView(left,new LinearLayout.LayoutParams(0,-2,1));
        TextView hrs=text(formatHours(s.minutes()),16,TEAL,true); hrs.setGravity(Gravity.CENTER); row.addView(hrs,new LinearLayout.LayoutParams(dp(80),dp(48)));
        row.setOnClickListener(v->editDialog(s,false)); row.setOnLongClickListener(v->{actions(s);return true;});
        LinearLayout.LayoutParams p=mp(-1,-2,0,0,0,9); row.setLayoutParams(p); return row;
    }

    void actions(Shift s){
        new AlertDialog.Builder(this).setTitle("Arbetspass")
          .setItems(new String[]{"Redigera","Kopiera till annat datum","Radera"},(d,w)->{
              if(w==0)editDialog(s,false); else if(w==1)editDialog(s,true); else confirmDelete(s);
          }).show();
    }

    void confirmDelete(Shift s){
        new AlertDialog.Builder(this).setTitle("Radera passet?").setMessage(cap(dateFmt.format(new Date(s.date)))+" "+s.start+"–"+s.end)
          .setNegativeButton("Avbryt",null).setPositiveButton("Radera",(d,w)->{shifts.remove(s);save();refresh();}).show();
    }

    void editDialog(Shift existing,boolean copy){
        Shift draft=existing==null?new Shift():existing.copy();
        if(existing==null){draft.date=selectedDay;draft.start="08:00";draft.end="16:00";draft.breakMin=30;}
        if(copy) draft.date=dayStart(System.currentTimeMillis());
        LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(22),dp(6),dp(22),0);
        Button dateBtn=new Button(this); dateBtn.setText(fullDate(draft.date)); form.addView(label("Datum"));form.addView(dateBtn);
        LinearLayout times=new LinearLayout(this);
        Button startBtn=new Button(this);startBtn.setText(draft.start); Button endBtn=new Button(this);endBtn.setText(draft.end);
        times.addView(startBtn,new LinearLayout.LayoutParams(0,dp(54),1));times.addView(endBtn,new LinearLayout.LayoutParams(0,dp(54),1));form.addView(label("Starttid                              Sluttid"));form.addView(times);
        EditText br=input(String.valueOf(draft.breakMin),"Rast i minuter");br.setInputType(2);form.addView(label("Rast (minuter)"));form.addView(br);
        EditText service=input(draft.service,"T.ex. 4102");form.addView(label("Tjänstenummer"));form.addView(service);
        EditText line=input(draft.line,"Linje eller omlopp");form.addView(label("Linje / omlopp"));form.addView(line);
        EditText note=input(draft.note,"Valfri anteckning");note.setMinLines(2);form.addView(label("Anteckning"));form.addView(note);
        dateBtn.setOnClickListener(v->{Calendar c=Calendar.getInstance();c.setTimeInMillis(draft.date);new DatePickerDialog(this,(x,y,m,day)->{c.set(y,m,day,0,0,0);c.set(Calendar.MILLISECOND,0);draft.date=c.getTimeInMillis();dateBtn.setText(fullDate(draft.date));},c.get(Calendar.YEAR),c.get(Calendar.MONTH),c.get(Calendar.DAY_OF_MONTH)).show();});
        startBtn.setOnClickListener(v->pickTime(draft.start,t->{draft.start=t;startBtn.setText(t);}));
        endBtn.setOnClickListener(v->pickTime(draft.end,t->{draft.end=t;endBtn.setText(t);}));
        String heading=existing==null?"Nytt arbetspass":copy?"Kopiera arbetspass":"Redigera arbetspass";
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle(heading).setView(form).setNegativeButton("Avbryt",null)
          .setPositiveButton("Spara",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{draft.breakMin=Math.max(0,Integer.parseInt(br.getText().toString().trim()));}catch(Exception e){draft.breakMin=0;}
            draft.service=service.getText().toString().trim();draft.line=line.getText().toString().trim();draft.note=note.getText().toString().trim();
            if(draft.minutes()<=0){Toast.makeText(this,"Kontrollera tider och rast",Toast.LENGTH_LONG).show();return;}
            if(existing!=null&&!copy)shifts.remove(existing);shifts.add(draft);save();dialog.dismiss();refresh();
        })); dialog.getWindow();dialog.show();
    }

    interface TimeDone{void set(String t);}
    void pickTime(String value,TimeDone done){
        String[] p=value.split(":"); int h=Integer.parseInt(p[0]),m=Integer.parseInt(p[1]);
        new TimePickerDialog(this,(v,hh,mm)->done.set(String.format(Locale.US,"%02d:%02d",hh,mm)),h,m,true).show();
    }

    void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);p.getMenu().add("Säkerhetskopiera");p.getMenu().add("Återställ säkerhetskopia");p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{String s=i.getTitle().toString();if(s.startsWith("Säker"))exportData();else if(s.startsWith("Åter"))importData();else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.1\n\nDina uppgifter sparas endast lokalt i telefonen.").setPositiveButton("OK",null).show();return true;});p.show();
    }

    void exportData(){
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"mina-arbetspass-"+keyFmt.format(new Date())+".json");startActivityForResult(i,EXPORT);
    }
    void importData(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("application/json");startActivityForResult(i,IMPORT);}
    @Override protected void onActivityResult(int req,int result,Intent data){
        super.onActivityResult(req,result,data);if(result!=RESULT_OK||data==null)return;
        try{
            Uri uri=data.getData();
            if(req==EXPORT){OutputStream o=getContentResolver().openOutputStream(uri);o.write(toJson().toString(2).getBytes(StandardCharsets.UTF_8));o.close();Toast.makeText(this,"Säkerhetskopian är sparad",Toast.LENGTH_LONG).show();}
            else {InputStream in=getContentResolver().openInputStream(uri);ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buf=new byte[4096];int n;while((n=in.read(buf))>0)b.write(buf,0,n);in.close();fromJson(new JSONArray(b.toString("UTF-8")));save();refresh();Toast.makeText(this,"Schemat är återställt",Toast.LENGTH_LONG).show();}
        }catch(Exception e){Toast.makeText(this,"Filen kunde inte läsas",Toast.LENGTH_LONG).show();}
    }

    void refresh(){if(screen==0)showHome();else if(screen==1)showCalendar();else showAll();}
    void load(){try{fromJson(new JSONArray(getPreferences(0).getString("shifts","[]")));}catch(Exception ignored){}}
    void save(){getPreferences(0).edit().putString("shifts",toJson().toString()).apply();}
    JSONArray toJson(){JSONArray a=new JSONArray();for(Shift s:shifts)a.put(s.json());return a;}
    void fromJson(JSONArray a)throws JSONException{shifts.clear();for(int i=0;i<a.length();i++)shifts.add(Shift.from(a.getJSONObject(i)));}
    ArrayList<Shift> sorted(){ArrayList<Shift>a=new ArrayList<>(shifts);Collections.sort(a,(x,y)->x.date==y.date?x.start.compareTo(y.start):Long.compare(x.date,y.date));return a;}
    Shift nextShift(){long now=System.currentTimeMillis();for(Shift s:sorted()){long t=s.date+toMin(s.start)*60000L;if(t+24*3600000L>=now)return s;}return null;}
    int sumAll(){int x=0;for(Shift s:shifts)x+=s.minutes();return x;}
    int sumMonth(long when){Calendar q=Calendar.getInstance();q.setTimeInMillis(when);int y=q.get(Calendar.YEAR),m=q.get(Calendar.MONTH),x=0;for(Shift s:shifts){q.setTimeInMillis(s.date);if(q.get(Calendar.YEAR)==y&&q.get(Calendar.MONTH)==m)x+=s.minutes();}return x;}
    int sumWeek(long when){Calendar c=Calendar.getInstance();c.setFirstDayOfWeek(Calendar.MONDAY);c.setMinimalDaysInFirstWeek(4);c.setTimeInMillis(when);int y=c.getWeekYear(),w=c.get(Calendar.WEEK_OF_YEAR),x=0;for(Shift s:shifts){c.setTimeInMillis(s.date);if(c.getWeekYear()==y&&c.get(Calendar.WEEK_OF_YEAR)==w)x+=s.minutes();}return x;}
    static int toMin(String t){String[]p=t.split(":");return Integer.parseInt(p[0])*60+Integer.parseInt(p[1]);}
    static long dayStart(long t){Calendar c=Calendar.getInstance();c.setTimeInMillis(t);c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);return c.getTimeInMillis();}
    String formatHours(int min){return String.format(new Locale("sv","SE"),"%d h %02d min",min/60,min%60);}
    String fullDate(long d){return cap(new SimpleDateFormat("EEEE d MMMM yyyy",new Locale("sv","SE")).format(new Date(d)));}
    static String cap(String s){return s.length()==0?s:s.substring(0,1).toUpperCase()+s.substring(1);}
    static String join(String a,String b){if(a.isEmpty())return b;if(b.isEmpty())return a;return a+"  •  "+b;}
    TextView section(String s){TextView v=text(s,18,TEXT,true);v.setPadding(0,dp(9),0,dp(10));return v;}
    void empty(String s){LinearLayout e=card();e.addView(text(s,15,MUTED,false));content.addView(e);}
    TextView label(String s){TextView v=text(s,13,Color.DKGRAY,true);v.setPadding(0,dp(10),0,0);return v;}
    EditText input(String value,String hint){EditText e=new EditText(this);e.setText(value);e.setHint(hint);e.setSingleLine(false);return e;}
    TextView text(String s,int sp,int color,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(color);if(bold)v.setTypeface(null,1);return v;}
    LinearLayout card(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);l.setPadding(dp(16),dp(15),dp(16),dp(15));l.setBackground(round(CARD,18));return l;}
    GradientDrawable round(int color,int radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));return g;}
    LinearLayout.LayoutParams mp(int w,int h,int l,int t,int r,int b){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w,h);p.setMargins(dp(l),dp(t),dp(r),dp(b));return p;}
    int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}

    static class Shift {
        long date=dayStart(System.currentTimeMillis()); String start="08:00",end="16:00",service="",line="",note="";int breakMin=30;
        int minutes(){int a=toMin(start),b=toMin(end);if(b<a)b+=1440;return Math.max(0,b-a-breakMin);}
        Shift copy(){Shift x=new Shift();x.date=date;x.start=start;x.end=end;x.breakMin=breakMin;x.service=service;x.line=line;x.note=note;return x;}
        JSONObject json(){JSONObject o=new JSONObject();try{o.put("date",date);o.put("start",start);o.put("end",end);o.put("break",breakMin);o.put("service",service);o.put("line",line);o.put("note",note);}catch(Exception ignored){}return o;}
        static Shift from(JSONObject o){Shift s=new Shift();s.date=o.optLong("date",s.date);s.start=o.optString("start","08:00");s.end=o.optString("end","16:00");s.breakMin=o.optInt("break",0);s.service=o.optString("service","");s.line=o.optString("line","");s.note=o.optString("note","");return s;}
    }
}
