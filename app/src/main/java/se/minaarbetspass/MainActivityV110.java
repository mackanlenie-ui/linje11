package se.minaarbetspass;

import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV110 extends MainActivityV19 {

    @Override void showMyHome(){
        screen=0;title.setText("Mina arbetspass");content.removeAllViews();nav(0);
        long now=System.currentTimeMillis(),today=dayStart(now);
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        ArrayList<Shift> month=ownerMonth(0,now);
        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Arbetat i månaden",formatHours(statusMinutes(month,true)));
        stat(stats,"Planerat i månaden",formatHours(statusMinutes(month,false)));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(smartMyTodayCard(),mp(-1,-2,0,0,0,16));
        content.addView(section("Gemensamt lediga"));
        content.addView(sharedFreeCard());

        content.addView(section("Veckan i korthet"));
        content.addView(weekSummaryCard(0,"Min vecka",TEAL));
        content.addView(weekStrip(today));
        content.addView(section("Veckoplan"));
        content.addView(weeklyPlan(0,"Mitt schema",TEAL));
        content.addView(section("Kommande pass"));
        addUpcomingDays(0,5);
        wideHome();
    }

    @Override void showBothHome(){
        screen=0;title.setText("Våra scheman");content.removeAllViews();nav(0);
        long now=System.currentTimeMillis(),today=dayStart(now);
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Mitt · timmar i månaden",formatHours(totalMinutes(ownerMonth(0,now))));
        stat(stats,"Lenie · timmar i månaden",formatHours(totalMinutes(ownerMonth(1,now))));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(todayStatusCard(0,"Mitt",TEAL),mp(-1,-2,0,0,0,10));
        content.addView(todayStatusCard(1,"Lenie",LENIE),mp(-1,-2,0,0,0,14));
        content.addView(section("Gemensamt lediga"));
        content.addView(sharedFreeCard());

        content.addView(section("Veckan i korthet"));
        LinearLayout pair=new LinearLayout(this);pair.setOrientation(LinearLayout.VERTICAL);
        pair.addView(weekSummaryCard(0,"Min vecka",TEAL),mp(-1,-2,0,0,0,8));
        pair.addView(weekSummaryCard(1,"Lenies vecka",LENIE));
        content.addView(pair);
        content.addView(weekStrip(today));
        content.addView(section("Vår veckoplan"));
        content.addView(combinedWeekPlan());
        content.addView(section("Kommande pass"));
        addUpcomingDays(-1,5);
        wideHome();
    }

    LinearLayout smartMyTodayCard(){
        long now=System.currentTimeMillis(),today=dayStart(now);
        ArrayList<Shift> items=ownerDay(0,today);Shift active=null,nextToday=null;
        for(Shift x:items){
            if(startAt(x)<=now&&endAt(x)>now){active=x;break;}
            if(startAt(x)>now&&nextToday==null)nextToday=x;
        }

        LinearLayout box=card();
        if(active!=null){
            final Shift current=active;
            box.addView(text("DU JOBBAR NU",12,TEAL,true));
            box.addView(text(remaining(endAt(current)),26,TEXT,true),mp(-1,-2,0,7,0,3));
            box.addView(text(current.start+"–"+current.end+" · "+formatHours(current.minutes()),16,TEAL,true));
            String info=join(current.service,current.line);if(!info.isEmpty())box.addView(text(info,14,MUTED,false),mp(-1,-2,0,5,0,0));
            Shift after=nextStartingAfter(endAt(current));
            if(after!=null)box.addView(text("Nästa: "+nextLine(after),13,MUTED,false),mp(-1,-2,0,10,0,0));
            box.setOnClickListener(v->editDialog(current,false));
            return box;
        }

        if(nextToday!=null){
            final Shift upcoming=nextToday;
            box.addView(text("DU BÖRJAR SENARE IDAG",12,TEAL,true));
            box.addView(text(cap(timeUntil(startAt(upcoming))),26,TEXT,true),mp(-1,-2,0,7,0,3));
            box.addView(text(upcoming.start+"–"+upcoming.end+" · "+formatHours(upcoming.minutes()),16,TEAL,true));
            String info=join(upcoming.service,upcoming.line);if(!info.isEmpty())box.addView(text(info,14,MUTED,false),mp(-1,-2,0,5,0,0));
            box.setOnClickListener(v->editDialog(upcoming,false));
            return box;
        }

        final Shift next=nextForOwner(0);
        if(items.isEmpty()){
            box.addView(text("LEDIG IDAG",12,TEAL,true));
            box.addView(text("Du har inget arbetspass idag.",23,TEXT,true),mp(-1,-2,0,7,0,3));
        }else{
            box.addView(text("KLAR FÖR IDAG",12,TEAL,true));
            box.addView(text("Dagens pass är avslutade.",23,TEXT,true),mp(-1,-2,0,7,0,3));
        }
        if(next==null)box.addView(text("Inga fler pass är inlagda.",13,MUTED,false),mp(-1,-2,0,8,0,0));
        else{
            box.addView(text("Nästa: "+nextLine(next),14,TEAL,true),mp(-1,-2,0,10,0,0));
            box.addView(text(countdown(next),13,MUTED,false),mp(-1,-2,0,3,0,0));
            box.setOnClickListener(v->editDialog(next,false));
        }
        return box;
    }

    String remaining(long target){
        long diff=Math.max(0,target-System.currentTimeMillis());long min=Math.max(1,(diff+59999)/60000);
        if(min>=60)return (min/60)+" h "+(min%60)+" min kvar";
        return min+" min kvar";
    }

    Shift nextStartingAfter(long after){
        Shift best=null;for(Shift x:shifts)if(x.owner==0&&startAt(x)>=after&&(best==null||startAt(x)<startAt(best)))best=x;return best;
    }

    String nextLine(Shift x){
        return cap(dateFmt.format(new Date(x.date)))+" · "+x.start+"–"+x.end;
    }

    LinearLayout sharedFreeCard(){
        long today=dayStart(System.currentTimeMillis()),limit=dayStart(addDays(today,14));
        ArrayList<Long> candidates=new ArrayList<>();HashSet<Long> mine=new HashSet<>(),hers=new HashSet<>();
        for(int i=0;i<14;i++)candidates.add(dayStart(addDays(today,i)));
        for(Shift x:shifts){long d=dayStart(x.date);if(d<today||d>=limit)continue;if(x.owner==1)hers.add(d);else mine.add(d);}
        List<Long> free=ScheduleInsights.sharedFreeDays(candidates,mine,hers,4);
        LinearLayout box=card();box.addView(text("NÄSTA 14 DAGAR",12,TEXT,true));
        if(free.isEmpty()){
            box.addView(text("Ingen helt gemensam ledig dag är inlagd de kommande två veckorna.",17,TEXT,true),mp(-1,-2,0,8,0,3));
            box.addView(text("Beräkningen utgår från passen som finns i appen.",12,MUTED,false));
            return box;
        }
        for(Long d:free){
            final long day=d;
            TextView row=text(freeDayLabel(day),16,TEAL,true);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(12),dp(11),dp(12),dp(11));row.setBackground(round(CARD2,10));
            row.setOnClickListener(v->{personView=2;selectedDay=day;showCalendar();});
            box.addView(row,mp(-1,-2,0,7,0,0));
        }
        box.addView(text("Helt ledig = ingen av er har ett inlagt pass den dagen.",12,MUTED,false),mp(-1,-2,0,9,0,0));
        return box;
    }

    String freeDayLabel(long day){
        long today=dayStart(System.currentTimeMillis()),tomorrow=dayStart(addDays(today,1));
        String prefix=day==today?"Idag":day==tomorrow?"Imorgon":cap(new SimpleDateFormat("EEEE",new Locale("sv","SE")).format(new Date(day)));
        return prefix+" · "+cap(dateFmt.format(new Date(day)));
    }

    @Override LinearLayout weekSummaryCard(int owner,String heading,int accent){
        ArrayList<Shift> week=ownerWeek(owner,System.currentTimeMillis());int workDays=workDayCount(week),freeDays=ScheduleInsights.freeDaysInWeek(workDays);
        LinearLayout box=card();box.addView(text(heading.toUpperCase(new Locale("sv","SE")),12,accent,true));
        box.addView(text(week.size()+" pass · "+workDays+" arbetsdagar · "+freeDays+" lediga",18,TEXT,true),mp(-1,-2,0,7,0,3));
        box.addView(text(formatHours(totalMinutes(week))+" schemalagt denna vecka",14,accent,true));
        if(owner==0)box.addView(text("Arbetat "+formatHours(statusMinutes(week,true))+" · Planerat "+formatHours(statusMinutes(week,false)),13,MUTED,false),mp(-1,-2,0,5,0,0));
        else box.addView(text("Översikt för måndag–söndag",13,MUTED,false),mp(-1,-2,0,5,0,0));
        return box;
    }
}
