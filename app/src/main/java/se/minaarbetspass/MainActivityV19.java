package se.minaarbetspass;

import android.graphics.Color;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV19 extends MainActivityV18 {

    @Override void showHome(){
        if(personView==0){showMyHome();return;}
        if(personView==1){showLenieHome();return;}
        showBothHome();
    }

    void showMyHome(){
        screen=0;title.setText("Mina arbetspass");content.removeAllViews();nav(0);
        long now=System.currentTimeMillis(),today=dayStart(now);
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        ArrayList<Shift> month=ownerMonth(0,now);
        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Arbetat i månaden",formatHours(statusMinutes(month,true)));
        stat(stats,"Planerat i månaden",formatHours(statusMinutes(month,false)));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(todayStatusCard(0,"Mitt",TEAL),mp(-1,-2,0,0,0,14));
        content.addView(nextHero(0),mp(-1,-2,0,0,0,16));

        content.addView(section("Veckan i korthet"));
        content.addView(weekSummaryCard(0,"Min vecka",TEAL));
        content.addView(weekStrip(today));
        content.addView(section("Veckoplan"));
        content.addView(weeklyPlan(0,"Mitt schema",TEAL));
        content.addView(section("Kommande pass"));
        addUpcomingDays(0,5);
        wideHome();
    }

    @Override void showLenieHome(){
        screen=0;title.setText("Lenies schema");content.removeAllViews();nav(0);
        long now=System.currentTimeMillis(),today=dayStart(now);
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        ArrayList<Shift> month=ownerMonth(1,now);
        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Lenie · pass i månaden",month.size()+" st");
        stat(stats,"Lenie · timmar i månaden",formatHours(totalMinutes(month)));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(todayStatusCard(1,"Lenie",LENIE),mp(-1,-2,0,0,0,14));
        content.addView(nextHero(1),mp(-1,-2,0,0,0,16));

        content.addView(section("Veckan i korthet"));
        content.addView(weekSummaryCard(1,"Lenies vecka",LENIE));
        content.addView(weekStrip(today));
        content.addView(section("Veckoplan"));
        content.addView(weeklyPlan(1,"Lenies schema",LENIE));
        content.addView(section("Kommande pass"));
        addUpcomingDays(1,5);
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

    LinearLayout nextHero(int owner){
        Shift next=nextForOwner(owner);long now=System.currentTimeMillis();int accent=owner==1?LENIE:TEAL;
        LinearLayout hero=card();
        if(next==null){
            hero.addView(text(owner==1?"INGA KOMMANDE PASS":"INGA KOMMANDE ARBETSPASS",12,accent,true));
            hero.addView(text(owner==1?"Det finns inget framtida pass inlagt för Lenie.":"Det finns inget framtida arbetspass inlagt.",17,TEXT,true),mp(-1,-2,0,10,0,0));
            return hero;
        }
        boolean active=startAt(next)<=now&&endAt(next)>now;
        String heading=owner==1?(active?"LENIE JOBBAR NU":"NÄSTA PASS FÖR LENIE"):(active?"PASS PÅGÅR":"NÄSTA ARBETSPASS");
        hero.addView(text(heading,12,accent,true));
        hero.addView(text(active?"Slutar "+timeUntil(endAt(next)):countdown(next),14,accent,true),mp(-1,-2,0,6,0,0));
        hero.addView(text(cap(dateFmt.format(new Date(next.date))),22,TEXT,true),mp(-1,-2,0,8,0,3));
        hero.addView(text(next.start+"–"+next.end+"  •  "+formatHours(next.minutes()),18,TEXT,true));
        String sub=join(next.service,next.line);if(!sub.isEmpty())hero.addView(text(sub,14,MUTED,false),mp(-1,-2,0,7,0,0));
        hero.setOnClickListener(v->editDialog(next,false));
        return hero;
    }

    ArrayList<Shift> ownerWeek(int owner,long when){
        long from=weekStart(when),to=addDays(from,7);ArrayList<Shift> result=new ArrayList<>();
        for(Shift x:shifts)if(x.owner==owner&&x.date>=from&&x.date<to)result.add(x);
        Collections.sort(result,(a,b)->Long.compare(startAt(a),startAt(b)));return result;
    }

    long weekStart(long when){
        Calendar c=Calendar.getInstance();c.setTimeInMillis(dayStart(when));c.add(Calendar.DAY_OF_MONTH,-((c.get(Calendar.DAY_OF_WEEK)+5)%7));return c.getTimeInMillis();
    }

    int statusMinutes(List<Shift> items,boolean done){int n=0;for(Shift x:items)if(x.done==done)n+=x.minutes();return n;}

    int workDayCount(List<Shift> items){HashSet<Long> days=new HashSet<>();for(Shift x:items)days.add(x.date);return days.size();}

    LinearLayout weekSummaryCard(int owner,String heading,int accent){
        ArrayList<Shift> week=ownerWeek(owner,System.currentTimeMillis());LinearLayout box=card();
        box.addView(text(heading.toUpperCase(new Locale("sv","SE")),12,accent,true));
        if(week.isEmpty()){
            box.addView(text("Inga pass denna vecka",18,TEXT,true),mp(-1,-2,0,7,0,0));
            return box;
        }
        box.addView(text(week.size()+" pass · "+workDayCount(week)+" arbetsdagar · "+formatHours(totalMinutes(week)),18,TEXT,true),mp(-1,-2,0,7,0,3));
        if(owner==0)box.addView(text("Arbetat "+formatHours(statusMinutes(week,true))+" · Planerat "+formatHours(statusMinutes(week,false)),13,MUTED,false));
        else box.addView(text("Översikt för måndag–söndag",13,MUTED,false));
        return box;
    }

    LinearLayout weeklyPlan(int owner,String heading,int accent){
        LinearLayout box=card();box.addView(text(heading.toUpperCase(new Locale("sv","SE")),12,accent,true));
        long monday=weekStart(System.currentTimeMillis()),today=dayStart(System.currentTimeMillis());
        for(int i=0;i<7;i++){
            final long d=addDays(monday,i);ArrayList<Shift> items=ownerDay(owner,d);
            LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(10),dp(8),dp(10),dp(8));row.setBackground(round(d==today?CARD2:BG,10));
            String dayName=cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(d)));
            TextView day=text(dayName,14,d==today?TEXT:MUTED,true);row.addView(day,new LinearLayout.LayoutParams(dp(105),-2));
            LinearLayout info=new LinearLayout(this);info.setOrientation(LinearLayout.VERTICAL);
            if(items.isEmpty())info.addView(text("Ledig",14,MUTED,true));
            else{
                info.addView(text(times(items),15,accent,true));
                info.addView(text(formatHours(totalMinutes(items))+(items.size()>1?" · "+items.size()+" pass":""),12,MUTED,false));
            }
            row.addView(info,new LinearLayout.LayoutParams(0,-2,1));
            row.setOnClickListener(v->{personView=owner;selectedDay=d;showCalendar();});
            box.addView(row,mp(-1,-2,0,6,0,0));
        }
        return box;
    }

    LinearLayout combinedWeekPlan(){
        LinearLayout box=card();box.addView(text("MÅNDAG–SÖNDAG",12,TEXT,true));
        long monday=weekStart(System.currentTimeMillis()),today=dayStart(System.currentTimeMillis());
        for(int i=0;i<7;i++){
            final long d=addDays(monday,i);ArrayList<Shift> mine=ownerDay(0,d),hers=ownerDay(1,d);
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.VERTICAL);row.setPadding(dp(10),dp(9),dp(10),dp(9));row.setBackground(round(d==today?CARD2:BG,10));
            row.addView(text(cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(d))),14,d==today?TEXT:MUTED,true));
            row.addView(text("Mitt: "+(mine.isEmpty()?"Ledig":times(mine)+" · "+formatHours(totalMinutes(mine))),13,mine.isEmpty()?MUTED:TEAL,true),mp(-1,-2,0,4,0,0));
            row.addView(text("Lenie: "+(hers.isEmpty()?"Ledig":times(hers)+" · "+formatHours(totalMinutes(hers))),13,hers.isEmpty()?MUTED:LENIE,true),mp(-1,-2,0,3,0,0));
            row.setOnClickListener(v->{personView=2;selectedDay=d;showCalendar();});
            box.addView(row,mp(-1,-2,0,6,0,0));
        }
        return box;
    }

    String times(List<Shift> items){
        StringBuilder b=new StringBuilder();for(int i=0;i<items.size();i++){if(i>0)b.append("  •  ");Shift x=items.get(i);b.append(x.start).append("–").append(x.end);}return b.toString();
    }
}
