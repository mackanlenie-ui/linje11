package se.minaarbetspass;

import android.app.AlertDialog;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV111 extends MainActivityV110 {
    long homeWeekAnchor=0L;

    long homeWeek(){
        if(homeWeekAnchor==0L)homeWeekAnchor=weekStart(System.currentTimeMillis());
        return homeWeekAnchor;
    }

    void moveHomeWeek(int weeks){
        homeWeekAnchor=weekStart(addDays(homeWeek(),weeks*7));
        showHome();
    }

    String weekRange(long monday){
        long sunday=addDays(monday,6);
        SimpleDateFormat day=new SimpleDateFormat("d",new Locale("sv","SE"));
        SimpleDateFormat month=new SimpleDateFormat("MMM",new Locale("sv","SE"));
        Calendar a=Calendar.getInstance(),b=Calendar.getInstance();a.setTimeInMillis(monday);b.setTimeInMillis(sunday);
        if(a.get(Calendar.MONTH)==b.get(Calendar.MONTH))return day.format(new Date(monday))+"–"+day.format(new Date(sunday))+" "+month.format(new Date(sunday));
        return day.format(new Date(monday))+" "+month.format(new Date(monday))+" – "+day.format(new Date(sunday))+" "+month.format(new Date(sunday));
    }

    LinearLayout homeWeekControls(){
        LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);
        Button prev=styledButton(),center=styledButton(),next=styledButton();prev.setText("‹");next.setText("›");
        boolean current=homeWeek()==weekStart(System.currentTimeMillis());
        center.setText((current?"Denna vecka · ":"")+weekRange(homeWeek()));
        prev.setOnClickListener(v->moveHomeWeek(-1));next.setOnClickListener(v->moveHomeWeek(1));
        center.setOnClickListener(v->{homeWeekAnchor=weekStart(System.currentTimeMillis());showHome();});
        row.addView(prev,new LinearLayout.LayoutParams(dp(52),dp(48)));
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,dp(48),1);cp.setMargins(dp(7),0,dp(7),0);row.addView(center,cp);
        row.addView(next,new LinearLayout.LayoutParams(dp(52),dp(48)));return row;
    }

    boolean primaryWeekCard(int owner){
        return (personView==0&&owner==0)||(personView==1&&owner==1)||(personView==2&&owner==0);
    }

    @Override LinearLayout weekStrip(long day){return super.weekStrip(screen==0?homeWeek():day);}

    @Override LinearLayout weekSummaryCard(int owner,String heading,int accent){
        ArrayList<Shift> week=ownerWeek(owner,homeWeek());int workDays=workDayCount(week),freeDays=ScheduleInsights.freeDaysInWeek(workDays);
        LinearLayout box=card();
        if(primaryWeekCard(owner))box.addView(homeWeekControls(),mp(-1,-2,0,0,0,12));
        box.addView(text(heading.toUpperCase(new Locale("sv","SE")),12,accent,true));
        box.addView(text(week.size()+" pass · "+workDays+" arbetsdagar · "+freeDays+" lediga",18,TEXT,true),mp(-1,-2,0,7,0,3));
        box.addView(text(formatHours(totalMinutes(week))+" schemalagt · "+weekRange(homeWeek()),14,accent,true));
        if(owner==0)box.addView(text("Arbetat "+formatHours(statusMinutes(week,true))+" · Planerat "+formatHours(statusMinutes(week,false)),13,MUTED,false),mp(-1,-2,0,5,0,0));
        else box.addView(text("Översikt för måndag–söndag",13,MUTED,false),mp(-1,-2,0,5,0,0));
        if(personView==0&&owner==0){
            Button copy=styledButton();copy.setText("Kopiera veckan → nästa");copy.setOnClickListener(v->copyDisplayedWeek());box.addView(copy,mp(-1,dp(48),0,12,0,0));
        }
        return box;
    }

    @Override LinearLayout weeklyPlan(int owner,String heading,int accent){
        LinearLayout box=card();box.addView(text(heading.toUpperCase(new Locale("sv","SE")),12,accent,true));
        long monday=homeWeek(),today=dayStart(System.currentTimeMillis());
        for(int i=0;i<7;i++){
            final long d=addDays(monday,i);ArrayList<Shift> items=ownerDay(owner,d);
            LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(10),dp(8),dp(10),dp(8));row.setBackground(round(d==today?CARD2:BG,10));
            String dayName=cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(d)));
            TextView day=text(dayName,14,d==today?TEXT:MUTED,true);row.addView(day,new LinearLayout.LayoutParams(dp(105),-2));
            LinearLayout info=new LinearLayout(this);info.setOrientation(LinearLayout.VERTICAL);
            if(items.isEmpty())info.addView(text("Ledig",14,MUTED,true));
            else{info.addView(text(times(items),15,accent,true));info.addView(text(formatHours(totalMinutes(items))+(items.size()>1?" · "+items.size()+" pass":""),12,MUTED,false));}
            row.addView(info,new LinearLayout.LayoutParams(0,-2,1));
            row.setOnClickListener(v->{personView=owner;getPreferences(0).edit().putInt("personView",owner).apply();selectedDay=d;showCalendar();});
            box.addView(row,mp(-1,-2,0,6,0,0));
        }
        return box;
    }

    @Override LinearLayout combinedWeekPlan(){
        LinearLayout box=card();box.addView(text("MÅNDAG–SÖNDAG · "+weekRange(homeWeek()),12,TEXT,true));
        long monday=homeWeek(),today=dayStart(System.currentTimeMillis());
        for(int i=0;i<7;i++){
            final long d=addDays(monday,i);ArrayList<Shift> mine=ownerDay(0,d),hers=ownerDay(1,d);
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.VERTICAL);row.setPadding(dp(10),dp(9),dp(10),dp(9));row.setBackground(round(d==today?CARD2:BG,10));
            row.addView(text(cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(d))),14,d==today?TEXT:MUTED,true));
            row.addView(text("Mitt: "+(mine.isEmpty()?"Ledig":times(mine)+" · "+formatHours(totalMinutes(mine))),13,mine.isEmpty()?MUTED:TEAL,true),mp(-1,-2,0,4,0,0));
            row.addView(text("Lenie: "+(hers.isEmpty()?"Ledig":times(hers)+" · "+formatHours(totalMinutes(hers))),13,hers.isEmpty()?MUTED:LENIE,true),mp(-1,-2,0,3,0,0));
            row.setOnClickListener(v->{personView=2;getPreferences(0).edit().putInt("personView",2).apply();selectedDay=d;showCalendar();});
            box.addView(row,mp(-1,-2,0,6,0,0));
        }
        return box;
    }

    void copyDisplayedWeek(){
        long from=homeWeek(),to=addDays(from,7);ArrayList<Shift> source=new ArrayList<>();
        for(Shift x:shifts)if(x.owner==0&&x.date>=from&&x.date<to)source.add(x);
        Collections.sort(source,(a,b)->Long.compare(startAt(a),startAt(b)));
        if(source.isEmpty()){Toast.makeText(this,"Det finns inga av dina pass att kopiera den veckan",Toast.LENGTH_LONG).show();return;}
        new AlertDialog.Builder(this).setTitle("Kopiera veckan?")
            .setMessage(weekRange(from)+" → "+weekRange(to)+"\n\n"+source.size()+" pass kopieras som planerade pass.")
            .setNegativeButton("Avbryt",null).setPositiveButton("Kopiera",(d,w)->copyWeekNow(source,to)).show();
    }

    void copyWeekNow(List<Shift> source,long targetWeek){
        ArrayList<Shift> copies=new ArrayList<>();
        for(Shift original:source){
            Shift copy=original.copy();copy.date=dayStart(addDays(original.date,7));copy.done=false;
            for(Shift existing:shifts)if(existing.owner==0&&ScheduleInsights.overlaps(startAt(copy),endAt(copy),startAt(existing),endAt(existing))){
                new AlertDialog.Builder(this).setTitle("Veckan kunde inte kopieras").setMessage(fullDate(copy.date)+" "+copy.start+"–"+copy.end+" överlappar ett pass som redan finns. Inget kopierades.").setPositiveButton("OK",null).show();return;
            }
            for(Shift other:copies)if(ScheduleInsights.overlaps(startAt(copy),endAt(copy),startAt(other),endAt(other))){
                new AlertDialog.Builder(this).setTitle("Veckan kunde inte kopieras").setMessage("Två kopierade pass skulle överlappa. Inget kopierades.").setPositiveButton("OK",null).show();return;
            }
            copies.add(copy);
        }
        shifts.addAll(copies);save();homeWeekAnchor=targetWeek;showHome();Toast.makeText(this,copies.size()+" pass kopierade till nästa vecka",Toast.LENGTH_LONG).show();
    }

    @Override LinearLayout sharedFreeCard(){
        long today=dayStart(System.currentTimeMillis()),limit=dayStart(addDays(today,14));
        ArrayList<Long> candidates=new ArrayList<>();HashSet<Long> mineDays=new HashSet<>(),hersDays=new HashSet<>();
        for(int i=0;i<14;i++)candidates.add(dayStart(addDays(today,i)));
        for(Shift x:shifts){long d=dayStart(x.date);if(d<today||d>=limit)continue;if(x.owner==1)hersDays.add(d);else mineDays.add(d);}
        List<Long> free=ScheduleInsights.sharedFreeDays(candidates,mineDays,hersDays,4);
        LinearLayout box=card();box.addView(text("NÄSTA 14 DAGAR",12,TEXT,true));
        box.addView(text("Hela lediga dagar",14,TEAL,true),mp(-1,-2,0,9,0,2));
        if(free.isEmpty())box.addView(text("Ingen helt gemensam ledig dag är inlagd.",14,MUTED,false));
        else for(Long d:free){final long day=d;TextView row=text(freeDayLabel(day),15,TEAL,true);row.setPadding(dp(12),dp(10),dp(12),dp(10));row.setBackground(round(CARD2,10));row.setOnClickListener(v->{personView=2;getPreferences(0).edit().putInt("personView",2).apply();selectedDay=day;showCalendar();});box.addView(row,mp(-1,-2,0,6,0,0));}

        box.addView(text("Gemensamt lediga kvällar",14,LENIE,true),mp(-1,-2,0,14,0,2));
        int shown=0;
        for(Long day:candidates){
            ArrayList<Shift> mine=ownerDay(0,day),hers=ownerDay(1,day);if(mine.isEmpty()&&hers.isEmpty())continue;
            int start=ScheduleInsights.sharedEveningStart(latestEndMinutes(mine),latestEndMinutes(hers));if(start<0)continue;
            final long selected=day;String label=freeDayLabel(day)+" · båda lediga från "+clock(start);
            TextView row=text(label,15,LENIE,true);row.setPadding(dp(12),dp(10),dp(12),dp(10));row.setBackground(round(CARD2,10));row.setOnClickListener(v->{personView=2;getPreferences(0).edit().putInt("personView",2).apply();selectedDay=selected;showCalendar();});box.addView(row,mp(-1,-2,0,6,0,0));
            if(++shown>=4)break;
        }
        if(shown==0)box.addView(text("Ingen gemensam kväll där båda är fria senast 20:00 hittades bland de inlagda passen.",14,MUTED,false));
        box.addView(text("Kväll = båda är fria från angiven tid resten av dagen. Beräkningen utgår från passen i appen.",12,MUTED,false),mp(-1,-2,0,10,0,0));
        return box;
    }

    int latestEndMinutes(List<Shift> items){
        int latest=0;for(Shift x:items){int start=toMin(x.start),end=toMin(x.end);if(end<start)end+=1440;latest=Math.max(latest,end);}return latest;
    }

    String clock(int minutes){return String.format(Locale.US,"%02d:%02d",(minutes/60)%24,minutes%60);}
}
