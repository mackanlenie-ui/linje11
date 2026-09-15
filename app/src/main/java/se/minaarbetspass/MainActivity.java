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
    boolean weekView=false;
    Shift undoShift;
    int screen=0; long selectedDay=dayStart(System.currentTimeMillis());
    final SimpleDateFormat keyFmt=new SimpleDateFormat("yyyy-MM-dd",new Locale("sv","SE"));
    final SimpleDateFormat dateFmt=new SimpleDateFormat("EEE d MMM",new Locale("sv","SE"));
    static final int EXPORT=20, IMPORT=21;

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(BG); getWindow().setNavigationBarColor(BG);
        load(); buildShell(); showHome();
    }

    @Override public void onConfigurationChanged(android.content.res.Configuration c){super.onConfigurationChanged(c);buildShell();refresh();}
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
        monthHours=stat(stats,"Arbetat · månad",formatHours(monthStatus(true)));
        weekHours=stat(stats,"Planerat · månad",formatHours(monthStatus(false)));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));
        Button templates=styledButton();templates.setText("＋ Nytt pass från mall");templates.setOnClickListener(v->chooseTemplate());content.addView(templates,mp(-1,dp(52),0,0,0,12));
        if(undoShift!=null){Button undo=styledButton();undo.setText("Ångra senaste radering");undo.setOnClickListener(v->{shifts.add(undoShift);undoShift=null;save();refresh();});content.addView(undo);}
        content.addView(text("Veckans registrerade tid: "+formatHours(sumWeek(System.currentTimeMillis())),13,MUTED,false));
        Shift next=nextShift();
        LinearLayout hero=card();
        hero.addView(text(next==null?"Inga kommande pass":"NÄSTA ARBETSPASS",12,TEAL,true));
        if(next==null) hero.addView(text("Tryck på + för att lägga in ditt första pass.",18,TEXT,true),mp(-1,-2,0,12,0,0));
        else {
            hero.addView(text(countdown(next),14,TEAL,true));
            hero.addView(text(cap(dateFmt.format(new Date(next.date))),22,TEXT,true),mp(-1,-2,0,10,0,3));
            hero.addView(text(next.start+"–"+next.end+"  •  "+formatHours(next.minutes()),18,TEXT,true));
            String sub=join(next.service,next.line);
            if(!sub.isEmpty()) hero.addView(text(sub,14,MUTED,false),mp(-1,-2,0,7,0,0));
            hero.setOnClickListener(v->editDialog(next,false));
        }
        content.addView(hero,mp(-1,-2,0,0,0,16));
        content.addView(section("Veckan i korthet"));
        content.addView(weekStrip(System.currentTimeMillis()));
        content.addView(section("Kommande pass"));
        ArrayList<Shift> upcoming=new ArrayList<>();
        long today=dayStart(System.currentTimeMillis());
        for(Shift s:sorted()) if(!s.done&&s.date>=today) upcoming.add(s);
        if(upcoming.isEmpty()) empty("Du har inga inlagda pass.");
        else {LinkedHashSet<Long> days=new LinkedHashSet<>();for(Shift x:upcoming){days.add(x.date);if(days.size()==5)break;}for(long day:days)content.addView(dayCard(day));}
        wideHome();
    }

    void wideHome(){
        if(getResources().getConfiguration().screenWidthDp<840)return;
        ArrayList<View> children=new ArrayList<>();for(int i=0;i<content.getChildCount();i++)children.add(content.getChildAt(i));content.removeAllViews();
        LinearLayout columns=new LinearLayout(this),left=new LinearLayout(this),right=new LinearLayout(this);left.setOrientation(1);right.setOrientation(1);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);lp.setMargins(0,0,dp(20),0);columns.addView(left,lp);columns.addView(right,new LinearLayout.LayoutParams(0,-2,1));boolean second=false;
        for(View v:children){if(v instanceof TextView&&((TextView)v).getText().toString().equals("Veckan i korthet"))second=true;(second?right:left).addView(v);}
        content.addView(columns);
    }
    TextView stat(LinearLayout parent,String label,String value){
        LinearLayout box=card(); TextView val=text(value,22,TEXT,true); box.addView(val); box.addView(text(label,13,MUTED,false),mp(-1,-2,0,6,0,0));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,-1,1); p.setMargins(0,0,dp(7),0); parent.addView(box,p); return val;
    }

    long addDays(long day,int count){Calendar c=Calendar.getInstance();c.setTimeInMillis(day);c.add(Calendar.DAY_OF_MONTH,count);return c.getTimeInMillis();}
    int dayMinutes(long day){int total=0;for(Shift x:shifts)if(x.date==day)total+=x.minutes();return total;}
    int dayCount(long day){int count=0;for(Shift x:shifts)if(x.date==day)count++;return count;}
    LinearLayout weekStrip(long day){
        LinearLayout strip=new LinearLayout(this);
        Calendar c=Calendar.getInstance();c.setTimeInMillis(dayStart(day));
        c.add(Calendar.DAY_OF_MONTH,-((c.get(Calendar.DAY_OF_WEEK)+5)%7));
        for(int i=0;i<7;i++){
            final long d=c.getTimeInMillis();int count=dayCount(d);
            TextView cell=text(new SimpleDateFormat("EE",new Locale("sv","SE")).format(c.getTime())+"\n"+c.get(Calendar.DAY_OF_MONTH)+"\n"+(count>0?"●":"·"),13,count>0?TEAL:MUTED,true);
            cell.setGravity(Gravity.CENTER);cell.setBackground(round(d==dayStart(day)?CARD2:CARD,12));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(78),1);lp.setMargins(dp(2),0,dp(2),dp(10));strip.addView(cell,lp);
            cell.setOnClickListener(v->{selectedDay=d;showCalendar();});c.add(Calendar.DAY_OF_MONTH,1);
        }return strip;
    }
    String countdown(Shift x){
        long diff=x.date+toMin(x.start)*60000L-System.currentTimeMillis();
        if(diff<=0)return "Pågående pass";
        long min=(diff+59999)/60000, days=min/1440,hours=(min%1440)/60;
        return days>0?"Om "+days+" dagar och "+hours+" timmar":hours>0?"Om "+hours+" h "+min%60+" min":"Om "+min+" minuter";
    }
    void showCalendar(){
        screen=1; title.setText("Kalender"); content.removeAllViews(); nav(1);
        LinearLayout controls=new LinearLayout(this);
        Button previous=styledButton(),mode=styledButton(),next=styledButton();
        previous.setText("‹");next.setText("›");mode.setText(weekView?"Vecka · byt till månad":"Månad · byt till vecka");
        controls.addView(previous,new LinearLayout.LayoutParams(dp(50),dp(52)));
        LinearLayout.LayoutParams modeParams=new LinearLayout.LayoutParams(0,dp(52),1);modeParams.setMargins(dp(8),0,dp(8),0);controls.addView(mode,modeParams);controls.addView(next,new LinearLayout.LayoutParams(dp(50),dp(52)));
        previous.setOnClickListener(v->moveCalendar(-1));next.setOnClickListener(v->moveCalendar(1));
        mode.setOnClickListener(v->{weekView=!weekView;showCalendar();});content.addView(controls);
        content.addView(section(cap(new SimpleDateFormat("MMMM yyyy",new Locale("sv","SE")).format(new Date(selectedDay)))));
        if(weekView){
            content.addView(weekStrip(selectedDay));
            Calendar w=Calendar.getInstance();w.setTimeInMillis(selectedDay);w.add(Calendar.DAY_OF_MONTH,-((w.get(Calendar.DAY_OF_WEEK)+5)%7));
            for(int i=0;i<7;i++){final long d=w.getTimeInMillis();
                if(dayCount(d)==0){
                    LinearLayout quiet=new LinearLayout(this);quiet.setGravity(Gravity.CENTER_VERTICAL);quiet.setPadding(dp(12),0,dp(12),0);
                    quiet.setBackground(round(CARD,12));
                    quiet.addView(text(cap(dateFmt.format(new Date(d))),14,MUTED,true),new LinearLayout.LayoutParams(0,-2,1));
                    quiet.addView(text("Inga pass",13,MUTED,false));
                    quiet.setOnClickListener(v->{selectedDay=d;editDialog(null,false);});
                    quiet.setContentDescription(fullDate(d)+", inga pass. Lägg till pass");
                    content.addView(quiet,mp(-1,dp(48),0,0,0,7));
                }else{
                    content.addView(section(cap(dateFmt.format(new Date(d)))+" · "+formatHours(dayMinutes(d))));
                    content.addView(dayCard(d));
                }
                w.add(Calendar.DAY_OF_MONTH,1);
            }
        }else{
            LinearLayout grid=card();
            Calendar c=Calendar.getInstance();c.setTimeInMillis(selectedDay);c.set(Calendar.DAY_OF_MONTH,1);
            int month=c.get(Calendar.MONTH);c.add(Calendar.DAY_OF_MONTH,-((c.get(Calendar.DAY_OF_WEEK)+5)%7));
            LinearLayout names=new LinearLayout(this);for(String n:new String[]{"M","T","O","T","F","L","S"}){TextView t=text(n,13,MUTED,true);t.setGravity(Gravity.CENTER);names.addView(t,new LinearLayout.LayoutParams(0,dp(30),1));}grid.addView(names);
            for(int row=0;row<6;row++){LinearLayout line=new LinearLayout(this);
                for(int col=0;col<7;col++){final long d=c.getTimeInMillis();boolean current=c.get(Calendar.MONTH)==month;
                    TextView cell=text(c.get(Calendar.DAY_OF_MONTH)+"\n"+(dayCount(d)>0?"●":" "),15,current?TEXT:MUTED,true);cell.setGravity(Gravity.CENTER);
                    if(d==selectedDay)cell.setBackground(round(CARD2,12));
                    if(dayCount(d)>0)cell.setTextColor(TEAL);
                    line.addView(cell,new LinearLayout.LayoutParams(0,dp(48),1));cell.setOnClickListener(v->{selectedDay=d;showCalendar();});c.add(Calendar.DAY_OF_MONTH,1);
                }grid.addView(line);
            }content.addView(grid);
            content.addView(section(cap(dateFmt.format(new Date(selectedDay)))+" · "+formatHours(dayMinutes(selectedDay))));
            if(dayCount(selectedDay)==0)empty("Inga pass denna dag. Tryck + för att lägga till.");
            if(dayCount(selectedDay)>0)content.addView(dayCard(selectedDay));
        }
    }
    void moveCalendar(int amount){Calendar c=Calendar.getInstance();c.setTimeInMillis(selectedDay);c.add(weekView?Calendar.WEEK_OF_YEAR:Calendar.MONTH,amount);selectedDay=c.getTimeInMillis();showCalendar();}

    void showAll(){
        screen=2; title.setText("Alla pass"); content.removeAllViews(); nav(2);
        TextView summary=text(shifts.size()+" pass  •  Totalt "+formatHours(sumAll()),15,MUTED,false);
        content.addView(summary,mp(-1,-2,0,0,0,14));
        if(shifts.isEmpty()){empty("Här visas alla dina arbetspass.");return;}
        String last="";long lastDay=Long.MIN_VALUE;
        for(Shift s:sorted()){
            String month=new SimpleDateFormat("MMMM yyyy",new Locale("sv","SE")).format(new Date(s.date));
            if(!month.equals(last)){content.addView(section(cap(month)+" · "+formatHours(sumMonth(s.date))));last=month;}
            if(s.date!=lastDay){content.addView(dayCard(s.date));lastDay=s.date;}
        }
    }


    LinearLayout dayCard(long day){
        LinearLayout box=card();box.setLayoutParams(mp(-1,-2,0,0,0,12));
        ArrayList<Shift> items=new ArrayList<>();int worked=0,planned=0;
        for(Shift x:sorted())if(x.date==day){items.add(x);if(x.done)worked+=x.minutes();else planned+=x.minutes();}
        box.addView(text(cap(dateFmt.format(new Date(day)))+(items.size()>1?" · Delade pass":""),17,TEXT,true));
        box.addView(text("Totalt "+formatHours(worked+planned),16,TEAL,true),mp(-1,-2,0,5,0,4));
        box.addView(text("Arbetat "+formatHours(worked)+" · Planerat "+formatHours(planned),12,MUTED,false));
        Shift previous=null;
        for(Shift x:items){
            if(previous!=null){long gap=(startAt(x)-endAt(previous))/60000;
                if(gap>0)box.addView(text("Uppehåll "+formatHours((int)gap),12,MUTED,false),mp(-1,-2,0,10,0,4));
                else if(gap<0)box.addView(text("Överlappande pass – kontrollera tiderna",12,RED,true));
            }
            LinearLayout part=new LinearLayout(this);part.setOrientation(1);part.setPadding(dp(12),dp(12),dp(12),dp(12));part.setBackground(round(CARD2,12));
            part.addView(text(x.start+"–"+x.end+(toMin(x.end)<toMin(x.start)?" (+1 dag)":"")+" · "+formatHours(x.minutes()),16,TEXT,true));
            part.addView(text((x.done?"✓ Arbetat":"◷ Planerat")+" · "+x.kind+" · Rast "+x.breakMin+" min",12,x.done?TEAL:Color.rgb(251,191,36),false),mp(-1,-2,0,4,0,0));
            String info=join(x.service,x.line);if(!info.isEmpty())part.addView(text(info,14,MUTED,false),mp(-1,-2,0,4,0,0));
            if(!x.note.isEmpty())part.addView(text(x.note,13,MUTED,false),mp(-1,-2,0,4,0,0));
            part.setOnClickListener(v->actions(x));part.setContentDescription(x.start+" till "+x.end+". Tryck för att ändra passet.");
            box.addView(part,mp(-1,-2,0,10,0,0));previous=x;
        }return box;
    }
    void templateAction(Shift source){
        new AlertDialog.Builder(this).setTitle("Använd passmall")
            .setItems(new String[]{"Ett datum – redigera först","Flera datum"},(d,w)->{if(w==0)editDialog(source,true);else copyDates(source);}).show();
    }
    void copyDates(Shift source){
        TreeSet<Long> dates=new TreeSet<>();
        LinearLayout form=new LinearLayout(this);form.setOrientation(1);form.setPadding(dp(20),dp(8),dp(20),dp(8));
        form.addView(text(source.start+"–"+source.end+" · "+formatHours(source.minutes()),17,TEXT,true));
        form.addView(text("Välj datum. Kopiorna sparas som planerade pass. Tryck på ett valt datum för att ta bort det.",14,MUTED,false));
        Button add=styledButton();add.setText("＋ Välj datum");form.addView(add,mp(-1,dp(50),0,12,0,8));
        LinearLayout list=new LinearLayout(this);list.setOrientation(1);form.addView(list);
        TextView error=text("",13,RED,false);form.addView(error);
        Runnable render=()->{list.removeAllViews();for(long day:dates){Button row=styledButton();row.setText(fullDate(day)+" ×");row.setOnClickListener(v->{dates.remove(day);list.removeView(row);error.setText("");});list.addView(row,mp(-1,dp(52),0,0,0,6));}};
        add.setOnClickListener(v->{Calendar c=Calendar.getInstance();c.setTimeInMillis(dates.isEmpty()?selectedDay:dates.last());
            new DatePickerDialog(this,(view,y,m,d)->{Calendar chosen=Calendar.getInstance();chosen.clear();chosen.set(y,m,d);dates.add(chosen.getTimeInMillis());error.setText("");render.run();},c.get(Calendar.YEAR),c.get(Calendar.MONTH),c.get(Calendar.DAY_OF_MONTH)).show();});
        ScrollView scroll=new ScrollView(this);scroll.addView(form);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Kopiera till flera datum").setView(scroll).setNegativeButton("Avbryt",null).setPositiveButton("Spara alla",null).create();
        dialog.setOnShowListener(v->dialog.getButton(-1).setOnClickListener(button->{
            if(dates.isEmpty()){error.setText("Välj minst ett datum.");return;}
            if(!source.start.matches("([01][0-9]|2[0-3]):[0-5][0-9]")||!source.end.matches("([01][0-9]|2[0-3]):[0-5][0-9]")||source.breakMin<0||source.minutes()<=0){error.setText("Passmallens tider är ogiltiga. Redigera mallen först.");return;}
            ArrayList<Shift> copies=new ArrayList<>();
            for(long day:dates){Shift copy=source.copy();copy.date=day;copy.done=false;
                for(Shift other:shifts)if(startAt(copy)<endAt(other)&&startAt(other)<endAt(copy)){error.setText(fullDate(day)+": överlappar ett befintligt pass. Inget har sparats.");return;}
                for(Shift other:copies)if(startAt(copy)<endAt(other)&&startAt(other)<endAt(copy)){error.setText("De valda kopiorna överlappar. Inget har sparats.");return;}
                copies.add(copy);
            }
            shifts.addAll(copies);save();dialog.dismiss();refresh();Toast.makeText(this,copies.size()+" planerade pass sparade",Toast.LENGTH_LONG).show();
        }));dialog.show();
    }

    LinearLayout shiftCard(Shift s){
        LinearLayout row=card(); row.setOrientation(LinearLayout.HORIZONTAL); row.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout left=new LinearLayout(this); left.setOrientation(LinearLayout.VERTICAL);
        left.addView(text(cap(dateFmt.format(new Date(s.date))),16,TEXT,true));
        left.addView(text((s.done?"✓ Arbetat":"◷ Planerat")+" · "+s.kind,12,s.done?TEAL:Color.rgb(251,191,36),true));
        left.addView(text(s.start+"–"+s.end+"  •  rast "+s.breakMin+" min",14,MUTED,false),mp(-1,-2,0,4,0,0));
        if(dayCount(s.date)>1)left.addView(text("Delad dag · totalt "+formatHours(dayMinutes(s.date)),12,TEAL,true));
        String sub=join(s.service,s.line); if(!sub.isEmpty()) left.addView(text(sub,13,MUTED,false),mp(-1,-2,0,4,0,0));
        row.addView(left,new LinearLayout.LayoutParams(0,-2,1));
        TextView hrs=text(formatHours(s.minutes()),16,TEAL,true); hrs.setGravity(Gravity.CENTER); row.addView(hrs,new LinearLayout.LayoutParams(dp(80),dp(48)));
        row.setOnClickListener(v->actions(s)); row.setOnLongClickListener(v->{actions(s);return true;});
        LinearLayout.LayoutParams p=mp(-1,-2,0,0,0,9); row.setLayoutParams(p); return row;
    }

    void actions(Shift s){
        new AlertDialog.Builder(this).setTitle("Arbetspass")
          .setItems(new String[]{"Redigera tider / status","Kopiera till flera datum","Lägg till delpass","Spara som mall",s.done?"Markera som planerat":"Pass klart – kontrollera tiden","Radera"},(d,w)->{
              if(w==0)editDialog(s,false); else if(w==1)copyDates(s); else if(w==2){selectedDay=s.date;showCalendar();editDialog(null,false);} else if(w==3)saveTemplate(s);else if(w==4){Shift changed=s.copy();changed.done=!s.done;editCompletion(s,changed);}else confirmDelete(s);
          }).show();
    }

    void confirmDelete(Shift s){
        new AlertDialog.Builder(this).setTitle("Radera passet?").setMessage(cap(dateFmt.format(new Date(s.date)))+" "+s.start+"–"+s.end)
          .setNegativeButton("Avbryt",null).setPositiveButton("Radera",(d,w)->{undoShift=s;shifts.remove(s);save();refresh();}).show();
    }

    void editDialog(Shift existing,boolean copy){
        Shift draft=existing==null?new Shift():existing.copy();
        if(existing==null){draft.date=screen==0?dayStart(System.currentTimeMillis()):selectedDay;draft.start="08:00";draft.end="16:00";draft.breakMin=30;}
        if(copy){draft.date=screen==1?selectedDay:dayStart(System.currentTimeMillis());draft.done=false;}
        LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(22),dp(6),dp(22),0);
        Button dateBtn=styledButton(); dateBtn.setText(fullDate(draft.date)); form.addView(label("Datum"));form.addView(dateBtn);
        CheckBox completed=new CheckBox(this);completed.setText("Passet är arbetat (kontrollera faktisk tid)");completed.setChecked(draft.done);form.addView(completed);
        Spinner category=new Spinner(this);String[] kinds={"Ordinarie","Utbildning","Extra pass"};category.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,kinds));for(int k=0;k<kinds.length;k++)if(kinds[k].equals(draft.kind))category.setSelection(k);form.addView(label("Typ av pass"));form.addView(category);
        LinearLayout times=new LinearLayout(this);
        Button startBtn=styledButton();startBtn.setText(draft.start); Button endBtn=styledButton();endBtn.setText(draft.end);
        times.addView(startBtn,new LinearLayout.LayoutParams(0,dp(54),1));times.addView(endBtn,new LinearLayout.LayoutParams(0,dp(54),1));form.addView(label("Starttid                              Sluttid"));form.addView(times);
        EditText br=input(String.valueOf(draft.breakMin),"Rast i minuter");br.setInputType(2);form.addView(label("Rast (minuter)"));form.addView(br);
        EditText service=input(draft.service,"T.ex. 4102");form.addView(label("Tjänstenummer"));form.addView(service);
        EditText line=input(draft.line,"Linje eller omlopp");form.addView(label("Linje / omlopp"));form.addView(line);
        EditText note=input(draft.note,"Valfri anteckning");note.setMinLines(2);form.addView(label("Anteckning"));form.addView(note);
        dateBtn.setOnClickListener(v->{Calendar c=Calendar.getInstance();c.setTimeInMillis(draft.date);new DatePickerDialog(this,(x,y,m,day)->{c.set(y,m,day,0,0,0);c.set(Calendar.MILLISECOND,0);draft.date=c.getTimeInMillis();dateBtn.setText(fullDate(draft.date));},c.get(Calendar.YEAR),c.get(Calendar.MONTH),c.get(Calendar.DAY_OF_MONTH)).show();});
        startBtn.setOnClickListener(v->pickTime(draft.start,t->{draft.start=t;startBtn.setText(t);}));
        endBtn.setOnClickListener(v->pickTime(draft.end,t->{draft.end=t;endBtn.setText(t);}));
        ScrollView formScroll=new ScrollView(this);formScroll.addView(form);formScroll.setPadding(0,0,0,dp(16));
        String heading=existing==null?"Nytt arbetspass":copy?"Kopiera arbetspass":"Redigera arbetspass";
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle(heading).setView(formScroll).setNegativeButton("Avbryt",null)
          .setPositiveButton("Spara",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{draft.breakMin=Integer.parseInt(br.getText().toString().trim());if(draft.breakMin<0)throw new Exception();}catch(Exception e){br.setError("Ange rast i hela minuter, minst 0");return;}
            draft.done=completed.isChecked();draft.kind=category.getSelectedItem().toString();
            draft.service=service.getText().toString().trim();draft.line=line.getText().toString().trim();draft.note=note.getText().toString().trim();
            if(draft.done&&endAt(draft)>System.currentTimeMillis()){Toast.makeText(this,"Ett framtida pass kan inte markeras som arbetat",Toast.LENGTH_LONG).show();return;}
            if(draft.minutes()<=0){Toast.makeText(this,"Kontrollera tider och rast",Toast.LENGTH_LONG).show();return;}
            for(Shift other:shifts){if(other==existing&&!copy)continue;if(startAt(draft)<endAt(other)&&startAt(other)<endAt(draft)){Toast.makeText(this,"Passet överlappar ett annat pass",Toast.LENGTH_LONG).show();return;}}
            if(existing!=null&&!copy)shifts.remove(existing);shifts.add(draft);save();dialog.dismiss();refresh();
        })); dialog.show();dialog.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    }

    interface TimeDone{void set(String t);}
    void pickTime(String value,TimeDone done){
        String[] p=value.split(":"); int h=Integer.parseInt(p[0]),m=Integer.parseInt(p[1]);
        new TimePickerDialog(this,(v,hh,mm)->done.set(String.format(Locale.US,"%02d:%02d",hh,mm)),h,m,true).show();
    }

    void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);p.getMenu().add("Säkerhetskopiera");p.getMenu().add("Återställ säkerhetskopia");p.getMenu().add("Passmallar");p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{String s=i.getTitle().toString();if(s.startsWith("Säker"))exportData();else if(s.startsWith("Åter"))importData();else if(s.equals("Passmallar"))chooseTemplate();else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.5\n\nDina uppgifter sparas endast lokalt i telefonen.").setPositiveButton("OK",null).show();return true;});p.show();
    }

    void exportData(){
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"mina-arbetspass-"+keyFmt.format(new Date())+".json");startActivityForResult(i,EXPORT);
    }
    void importData(){new AlertDialog.Builder(this).setTitle("Återställ schema?").setMessage("Dina nuvarande pass ersätts av säkerhetskopian. Säkerhetskopiera först om du vill behålla dem.").setNegativeButton("Avbryt",null).setPositiveButton("Välj fil",(d,w)->chooseImport()).show();}
    void chooseImport(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.setType("application/json");startActivityForResult(i,IMPORT);}
    @Override protected void onActivityResult(int req,int result,Intent data){
        super.onActivityResult(req,result,data);if(result!=RESULT_OK||data==null)return;
        try{
            Uri uri=data.getData();
            if(req==EXPORT){OutputStream o=getContentResolver().openOutputStream(uri);JSONObject backup=new JSONObject();backup.put("version",2);backup.put("shifts",toJson());backup.put("templates",templates());o.write(backup.toString(2).getBytes(StandardCharsets.UTF_8));o.close();Toast.makeText(this,"Säkerhetskopian är sparad",Toast.LENGTH_LONG).show();}
            else {InputStream in=getContentResolver().openInputStream(uri);ByteArrayOutputStream b=new ByteArrayOutputStream();byte[] buf=new byte[4096];int n;while((n=in.read(buf))>0)b.write(buf,0,n);in.close();String raw=b.toString("UTF-8").trim();if(raw.startsWith("[")){fromJson(new JSONArray(raw));}else{JSONObject backup=new JSONObject(raw);JSONArray ts=backup.optJSONArray("templates");if(ts==null)ts=new JSONArray();for(int i=0;i<ts.length();i++)ts.getJSONObject(i);fromJson(backup.getJSONArray("shifts"));getPreferences(0).edit().putString("templates",ts.toString()).apply();}save();refresh();Toast.makeText(this,"Schemat är återställt",Toast.LENGTH_LONG).show();}
        }catch(Exception e){Toast.makeText(this,"Filen kunde inte läsas",Toast.LENGTH_LONG).show();}
    }


    long startAt(Shift x){return x.date+toMin(x.start)*60000L;}
    long endAt(Shift x){return (toMin(x.end)<toMin(x.start)?addDays(x.date,1):x.date)+toMin(x.end)*60000L;}
    int monthStatus(boolean done){int n=0;String month=new SimpleDateFormat("yyyy-MM",Locale.US).format(new Date());for(Shift x:shifts)if(x.done==done&&new SimpleDateFormat("yyyy-MM",Locale.US).format(new Date(x.date)).equals(month))n+=x.minutes();return n;}
    void editCompletion(Shift original,Shift changed){
        if(changed.done&&endAt(changed)>System.currentTimeMillis()){Toast.makeText(this,"Passet har inte slutat ännu. Redigera sluttiden först.",Toast.LENGTH_LONG).show();return;}
        new AlertDialog.Builder(this).setTitle(changed.done?"Bekräfta arbetad tid":"Markera som planerat")
        .setMessage(original.start+"–"+original.end+"\nRast "+original.breakMin+" min\n"+formatHours(original.minutes()))
        .setNeutralButton("Justera tider",(d,w)->editDialog(original,false)).setNegativeButton("Avbryt",null)
        .setPositiveButton("Bekräfta",(d,w)->{original.done=changed.done;save();refresh();}).show();
    }
    JSONArray templates(){try{return new JSONArray(getPreferences(0).getString("templates","[]"));}catch(Exception e){return new JSONArray();}}
    void saveTemplate(Shift x){
        EditText name=input(join(x.service,x.line),"Mallens namn");
        new AlertDialog.Builder(this).setTitle("Spara passmall").setView(name).setNegativeButton("Avbryt",null).setPositiveButton("Spara",(d,w)->{
            String n=name.getText().toString().trim();if(n.isEmpty())n=x.start+"–"+x.end;
            JSONArray all=templates();JSONObject o=x.json();try{o.put("templateName",n);o.put("done",false);}catch(Exception ignored){}
            all.put(o);getPreferences(0).edit().putString("templates",all.toString()).apply();Toast.makeText(this,"Mallen är sparad",Toast.LENGTH_SHORT).show();
        }).show();
    }
    void chooseTemplate(){
        JSONArray all=templates();if(all.length()==0){new AlertDialog.Builder(this).setTitle("Passmallar").setMessage("Lägg in ett vanligt pass först. Tryck sedan på passet och välj Spara som mall.").setPositiveButton("Nytt pass",(d,w)->editDialog(null,false)).setNegativeButton("Stäng",null).show();return;}
        String[] names=new String[all.length()];for(int i=0;i<all.length();i++){JSONObject o=all.optJSONObject(i);names[i]=o.optString("templateName")+" · "+o.optString("start")+"–"+o.optString("end");}
        new AlertDialog.Builder(this).setTitle("Välj passmall").setItems(names,(d,w)->templateAction(Shift.from(all.optJSONObject(w)))).setNeutralButton("Ta bort mall",(d,w)->new AlertDialog.Builder(this).setTitle("Ta bort mall").setItems(names,(a,b)->{all.remove(b);getPreferences(0).edit().putString("templates",all.toString()).apply();}).show()).setNegativeButton("Avbryt",null).show();
    }

    void refresh(){if(screen==0)showHome();else if(screen==1)showCalendar();else showAll();}
    void load(){try{fromJson(new JSONArray(getPreferences(0).getString("shifts","[]")));}catch(Exception ignored){}}
    void save(){getPreferences(0).edit().putString("shifts",toJson().toString()).apply();}
    JSONArray toJson(){JSONArray a=new JSONArray();for(Shift s:shifts)a.put(s.json());return a;}
    void fromJson(JSONArray a)throws JSONException{ArrayList<Shift> incoming=new ArrayList<>();for(int i=0;i<a.length();i++){Shift x=Shift.from(a.getJSONObject(i));if(!x.start.matches("([01][0-9]|2[0-3]):[0-5][0-9]")||!x.end.matches("([01][0-9]|2[0-3]):[0-5][0-9]")||x.breakMin<0||x.minutes()<=0)throw new JSONException("Ogiltigt pass");incoming.add(x);}shifts.clear();shifts.addAll(incoming);}
    ArrayList<Shift> sorted(){ArrayList<Shift>a=new ArrayList<>(shifts);Collections.sort(a,(x,y)->x.date==y.date?x.start.compareTo(y.start):Long.compare(x.date,y.date));return a;}
    Shift nextShift(){long now=System.currentTimeMillis();for(Shift s:sorted()){long t=s.date+toMin(s.end)*60000L;if(toMin(s.end)<toMin(s.start))t=addDays(s.date,1)+toMin(s.end)*60000L;if(!s.done&&t>now)return s;}return null;}
    int sumAll(){int x=0;for(Shift s:shifts)x+=s.minutes();return x;}
    int sumMonth(long when){Calendar q=Calendar.getInstance();q.setTimeInMillis(when);int y=q.get(Calendar.YEAR),m=q.get(Calendar.MONTH),x=0;for(Shift s:shifts){q.setTimeInMillis(s.date);if(q.get(Calendar.YEAR)==y&&q.get(Calendar.MONTH)==m)x+=s.minutes();}return x;}
    int sumWeek(long when){Calendar c=Calendar.getInstance();c.setFirstDayOfWeek(Calendar.MONDAY);c.setMinimalDaysInFirstWeek(4);c.setTimeInMillis(when);int y=c.getWeekYear(),w=c.get(Calendar.WEEK_OF_YEAR),x=0;for(Shift s:shifts){c.setTimeInMillis(s.date);if(c.getWeekYear()==y&&c.get(Calendar.WEEK_OF_YEAR)==w)x+=s.minutes();}return x;}
    static int toMin(String t){String[]p=t.split(":");return Integer.parseInt(p[0])*60+Integer.parseInt(p[1]);}
    static long dayStart(long t){Calendar c=Calendar.getInstance();c.setTimeInMillis(t);c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);return c.getTimeInMillis();}
    String formatHours(int min){return String.format(new Locale("sv","SE"),"%d h %02d min",min/60,min%60);}
    String fullDate(long d){return cap(new SimpleDateFormat("EEEE d MMMM yyyy",new Locale("sv","SE")).format(new Date(d)));}
    static String cap(String s){return s.length()==0?s:s.substring(0,1).toUpperCase()+s.substring(1);}
    static String join(String a,String b){if(a.isEmpty())return b;if(b.isEmpty())return a;return a+"  •  "+b;}
    Button styledButton(){
        Button b=new Button(this);b.setAllCaps(false);b.setTextSize(14);b.setTextColor(TEAL);b.setTypeface(null,1);
        b.setMinHeight(dp(48));b.setMinimumHeight(dp(48));b.setMinWidth(0);b.setMinimumWidth(0);
        b.setPadding(dp(12),dp(6),dp(12),dp(6));b.setBackgroundTintList(null);
        GradientDrawable normal=round(CARD2,14);normal.setStroke(dp(1),Color.rgb(40,78,91));
        b.setBackground(new android.graphics.drawable.RippleDrawable(android.content.res.ColorStateList.valueOf(0x443DD6C6),normal,null));
        b.setStateListAnimator(null);return b;
    }
    TextView section(String s){TextView v=text(s,18,TEXT,true);v.setPadding(0,dp(9),0,dp(10));return v;}
    void empty(String s){LinearLayout e=card();e.addView(text(s,15,MUTED,false));content.addView(e);}
    TextView label(String s){TextView v=text(s,13,MUTED,true);v.setPadding(0,dp(10),0,0);return v;}
    EditText input(String value,String hint){EditText e=new EditText(this);e.setTextColor(TEXT);e.setHintTextColor(MUTED);e.setText(value);e.setHint(hint);e.setSingleLine(false);return e;}
    TextView text(String s,int sp,int color,boolean bold){TextView v=new TextView(this);v.setText(s);v.setTextSize(sp);v.setTextColor(color);if(bold)v.setTypeface(null,1);return v;}
    LinearLayout card(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);l.setPadding(dp(16),dp(15),dp(16),dp(15));l.setBackground(round(CARD,18));return l;}
    GradientDrawable round(int color,int radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));return g;}
    LinearLayout.LayoutParams mp(int w,int h,int l,int t,int r,int b){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w,h);p.setMargins(dp(l),dp(t),dp(r),dp(b));return p;}
    int dp(int n){return (int)(n*getResources().getDisplayMetrics().density+.5f);}

    static class Shift {
        long date=dayStart(System.currentTimeMillis()); String start="08:00",end="16:00",service="",line="",note="";int breakMin=30; boolean done=false; String kind="Ordinarie";
        int minutes(){int a=toMin(start),b=toMin(end);if(b<a)b+=1440;return Math.max(0,b-a-breakMin);}
        Shift copy(){Shift x=new Shift();x.date=date;x.start=start;x.end=end;x.breakMin=breakMin;x.service=service;x.line=line;x.note=note;x.done=done;x.kind=kind;return x;}
        JSONObject json(){JSONObject o=new JSONObject();try{o.put("date",date);o.put("start",start);o.put("end",end);o.put("break",breakMin);o.put("service",service);o.put("line",line);o.put("note",note);o.put("done",done);o.put("kind",kind);}catch(Exception ignored){}return o;}
        static Shift from(JSONObject o){Shift s=new Shift();s.date=o.optLong("date",s.date);s.start=o.optString("start","08:00");s.end=o.optString("end","16:00");s.breakMin=o.optInt("break",0);s.service=o.optString("service","");s.line=o.optString("line","");s.note=o.optString("note","");s.done=o.optBoolean("done",false);s.kind=o.optString("kind","Ordinarie");return s;}
    }
}
