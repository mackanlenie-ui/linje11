package se.minaarbetspass;

import android.app.*;
import android.graphics.Color;
import android.view.*;
import android.widget.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV18 extends MainActivity {

    @Override void showHome(){
        if(personView==0){super.showHome();return;}
        if(personView==1){showLenieHome();return;}
        showBothHome();
    }

    void showLenieHome(){
        screen=0;title.setText("Lenies schema");content.removeAllViews();nav(0);
        long today=dayStart(System.currentTimeMillis());
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        ArrayList<Shift> month=ownerMonth(1,System.currentTimeMillis());
        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Lenie · pass i månaden",month.size()+" st");
        stat(stats,"Lenie · timmar i månaden",formatHours(totalMinutes(month)));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(todayStatusCard(1,"Lenie",LENIE),mp(-1,-2,0,0,0,14));

        Shift next=nextForOwner(1);
        LinearLayout hero=card();
        hero.addView(text(next==null?"INGA KOMMANDE PASS":"NÄSTA PASS FÖR LENIE",12,LENIE,true));
        if(next==null){
            hero.addView(text("Det finns inget framtida pass inlagt för Lenie.",17,TEXT,true),mp(-1,-2,0,10,0,0));
        }else{
            hero.addView(text(countdown(next),14,LENIE,true),mp(-1,-2,0,6,0,0));
            hero.addView(text(cap(dateFmt.format(new Date(next.date))),22,TEXT,true),mp(-1,-2,0,8,0,3));
            hero.addView(text(next.start+"–"+next.end+"  •  "+formatHours(next.minutes()),18,TEXT,true));
            String sub=join(next.service,next.line);if(!sub.isEmpty())hero.addView(text(sub,14,MUTED,false),mp(-1,-2,0,7,0,0));
            hero.setOnClickListener(v->editDialog(next,false));
        }
        content.addView(hero,mp(-1,-2,0,0,0,16));

        content.addView(section("Veckan i korthet"));
        content.addView(weekStrip(today));
        content.addView(text("Veckan: "+weekSummary(),13,MUTED,false),mp(-1,-2,0,0,0,10));
        content.addView(section("Kommande pass"));
        addUpcomingDays(1,5);
        wideHome();
    }

    void showBothHome(){
        screen=0;title.setText("Våra scheman");content.removeAllViews();nav(0);
        long now=System.currentTimeMillis();
        content.addView(text(cap(new SimpleDateFormat("EEEE d MMMM",new Locale("sv","SE")).format(new Date())),15,MUTED,false),mp(-1,-2,0,0,0,12));

        LinearLayout stats=new LinearLayout(this);
        stat(stats,"Mitt · timmar i månaden",formatHours(totalMinutes(ownerMonth(0,now))));
        stat(stats,"Lenie · timmar i månaden",formatHours(totalMinutes(ownerMonth(1,now))));
        content.addView(stats,mp(-1,dp(98),0,0,0,14));

        content.addView(todayStatusCard(0,"Mitt",TEAL),mp(-1,-2,0,0,0,10));
        content.addView(todayStatusCard(1,"Lenie",LENIE),mp(-1,-2,0,0,0,14));

        content.addView(section("Veckan i korthet"));
        content.addView(weekStrip(now));
        content.addView(text("Veckan: "+weekSummary(),13,MUTED,false),mp(-1,-2,0,0,0,10));
        content.addView(section("Kommande pass"));
        addUpcomingDays(-1,5);
        wideHome();
    }

    void addUpcomingDays(int owner,int maxDays){
        long today=dayStart(System.currentTimeMillis());
        LinkedHashSet<Long> days=new LinkedHashSet<>();
        ArrayList<Shift> all=new ArrayList<>();
        for(Shift x:shifts){
            if(owner>=0&&x.owner!=owner)continue;
            if(x.date<today||endAt(x)<=System.currentTimeMillis())continue;
            all.add(x);
        }
        Collections.sort(all,(a,b)->a.date==b.date?a.start.compareTo(b.start):Long.compare(a.date,b.date));
        for(Shift x:all){days.add(x.date);if(days.size()>=maxDays)break;}
        if(days.isEmpty()){empty(owner==1?"Inga kommande pass för Lenie.":"Inga kommande pass inlagda.");return;}
        for(long day:days)content.addView(dayCard(day));
    }

    ArrayList<Shift> ownerMonth(int owner,long when){
        String month=monthKey(when);ArrayList<Shift> result=new ArrayList<>();
        for(Shift x:shifts)if(x.owner==owner&&monthKey(x.date).equals(month))result.add(x);
        return result;
    }

    int totalMinutes(List<Shift> items){int total=0;for(Shift x:items)total+=x.minutes();return total;}

    ArrayList<Shift> ownerDay(int owner,long day){
        ArrayList<Shift> result=new ArrayList<>();for(Shift x:shifts)if(x.owner==owner&&x.date==day)result.add(x);
        Collections.sort(result,(a,b)->a.start.compareTo(b.start));return result;
    }

    LinearLayout todayStatusCard(int owner,String name,int accent){
        long today=dayStart(System.currentTimeMillis()),now=System.currentTimeMillis();
        ArrayList<Shift> items=ownerDay(owner,today);Shift active=null,next=null;
        for(Shift x:items){if(startAt(x)<=now&&endAt(x)>now){active=x;break;}if(startAt(x)>now&&next==null)next=x;}
        LinearLayout box=card();
        if(items.isEmpty()){
            box.addView(text(name.toUpperCase(new Locale("sv","SE"))+" · LEDIG IDAG",12,accent,true));
            box.addView(text("Inget arbetspass inlagt idag.",17,TEXT,true),mp(-1,-2,0,7,0,0));
            return box;
        }
        String state=active!=null?"JOBBAR NU":next!=null?"JOBBAR SENARE IDAG":"KLAR FÖR IDAG";
        box.addView(text(name.toUpperCase(new Locale("sv","SE"))+" · "+state,12,accent,true));
        if(active!=null)box.addView(text(active.start+"–"+active.end+" · slutar "+timeUntil(endAt(active)),18,TEXT,true),mp(-1,-2,0,7,0,3));
        else if(next!=null)box.addView(text(next.start+"–"+next.end+" · börjar "+timeUntil(startAt(next)),18,TEXT,true),mp(-1,-2,0,7,0,3));
        else box.addView(text("Dagens pass är avslutade.",17,TEXT,true),mp(-1,-2,0,7,0,3));
        if(items.size()>1){
            StringBuilder b=new StringBuilder();for(int i=0;i<items.size();i++){if(i>0)b.append("  •  ");b.append(items.get(i).start).append("–").append(items.get(i).end);}
            box.addView(text(b.toString(),13,MUTED,false),mp(-1,-2,0,6,0,0));
        }
        return box;
    }

    String timeUntil(long target){
        long diff=Math.max(0,target-System.currentTimeMillis());long min=(diff+59999)/60000;
        if(min>=60)return "om "+(min/60)+" h "+(min%60)+" min";
        return "om "+min+" min";
    }

    Shift nextForOwner(int owner){
        long now=System.currentTimeMillis();ArrayList<Shift> all=new ArrayList<>();for(Shift x:shifts)if(x.owner==owner&&endAt(x)>now)all.add(x);
        Collections.sort(all,(a,b)->Long.compare(startAt(a),startAt(b)));return all.isEmpty()?null:all.get(0);
    }

    @Override int dayCount(long day){int count=0;for(Shift x:shifts)if(visible(x)&&x.date==day)count++;return count;}

    int ownerDayCount(long day,int owner){int count=0;for(Shift x:shifts)if(x.owner==owner&&x.date==day)count++;return count;}

    @Override LinearLayout weekStrip(long day){
        LinearLayout strip=new LinearLayout(this);Calendar c=Calendar.getInstance();c.setTimeInMillis(dayStart(day));
        c.add(Calendar.DAY_OF_MONTH,-((c.get(Calendar.DAY_OF_WEEK)+5)%7));
        for(int i=0;i<7;i++){
            final long d=c.getTimeInMillis();int mine=ownerDayCount(d,0),hers=ownerDayCount(d,1);
            boolean showMine=personView!=1&&mine>0,showHers=personView!=0&&hers>0;
            String dots=showMine&&showHers?"● ●":showMine||showHers?"●":"·";
            String label=new SimpleDateFormat("EE",new Locale("sv","SE")).format(c.getTime())+"\n"+c.get(Calendar.DAY_OF_MONTH)+"\n"+dots;
            TextView cell=text(label,13,(!showMine&&showHers)?LENIE:(showMine?TEAL:MUTED),true);
            if(showMine&&showHers){
                android.text.SpannableString s=new android.text.SpannableString(label);int first=label.indexOf('●'),second=label.lastIndexOf('●');
                s.setSpan(new android.text.style.ForegroundColorSpan(TEAL),first,first+1,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
                s.setSpan(new android.text.style.ForegroundColorSpan(LENIE),second,second+1,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);cell.setText(s);
            }
            cell.setGravity(Gravity.CENTER);cell.setBackground(round(d==dayStart(day)?CARD2:CARD,12));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(78),1);lp.setMargins(dp(2),0,dp(2),dp(10));strip.addView(cell,lp);
            cell.setOnClickListener(v->{selectedDay=d;showCalendar();});c.add(Calendar.DAY_OF_MONTH,1);
        }return strip;
    }

    @Override String totals(List<Shift> items){
        if(personView==1)return lenieTotals(items);
        if(personView==2){
            ArrayList<Shift> mine=new ArrayList<>(),hers=new ArrayList<>();for(Shift x:items)(x.owner==1?hers:mine).add(x);
            return "Mitt: "+plainTotals(mine)+"\nLenie: "+lenieTotals(hers);
        }
        return super.totals(items);
    }

    String lenieTotals(List<Shift> items){return items.size()+" pass · "+formatHours(totalMinutes(items));}

    @Override LinearLayout dayCard(long day,ArrayList<Shift> items){
        if(items.isEmpty())return super.dayCard(day,items);
        boolean allLenie=true;for(Shift x:items)if(x.owner!=1){allLenie=false;break;}
        if(!allLenie)return super.dayCard(day,items);
        Collections.sort(items,(a,b)->a.start.compareTo(b.start));
        LinearLayout box=card();box.setLayoutParams(mp(-1,-2,0,8,0,12));
        box.addView(text("Lenie · "+cap(dateFmt.format(new Date(day)))+(items.size()>1?" · Delade pass":""),17,LENIE,true));
        if(items.size()==1){
            Shift x=items.get(0);box.addView(text(x.start+"–"+x.end+(toMin(x.end)<toMin(x.start)?" (+1 dag)":"")+" · "+formatHours(x.minutes()),18,TEXT,true),mp(-1,-2,0,7,0,5));
            box.addView(text(x.kind+" · Rast "+x.breakMin+" min",13,LENIE,false));
            String info=join(x.service,x.line);if(!info.isEmpty())box.addView(text(info,14,MUTED,false),mp(-1,-2,0,6,0,0));
            if(!x.note.isEmpty())box.addView(text(x.note,13,MUTED,false),mp(-1,-2,0,6,0,0));
            box.setOnClickListener(v->actions(x));return box;
        }
        box.addView(text("Totalt "+formatHours(totalMinutes(items))+" · "+items.size()+" pass",16,LENIE,true),mp(-1,-2,0,5,0,4));
        Shift previous=null;
        for(Shift x:items){
            if(previous!=null){long gap=(startAt(x)-endAt(previous))/60000;if(gap>0)box.addView(text("Uppehåll "+formatHours((int)gap),12,MUTED,false),mp(-1,-2,0,10,0,4));else if(gap<0)box.addView(text("Överlappande pass – kontrollera tiderna",12,RED,true));}
            LinearLayout part=new LinearLayout(this);part.setOrientation(1);part.setPadding(dp(12),dp(12),dp(12),dp(12));part.setBackground(round(CARD2,12));
            part.addView(text(x.start+"–"+x.end+(toMin(x.end)<toMin(x.start)?" (+1 dag)":"")+" · "+formatHours(x.minutes()),16,TEXT,true));
            part.addView(text(x.kind+" · Rast "+x.breakMin+" min",12,LENIE,false),mp(-1,-2,0,4,0,0));
            String info=join(x.service,x.line);if(!info.isEmpty())part.addView(text(info,14,MUTED,false),mp(-1,-2,0,4,0,0));
            if(!x.note.isEmpty())part.addView(text(x.note,13,MUTED,false),mp(-1,-2,0,4,0,0));
            part.setOnClickListener(v->actions(x));box.addView(part,mp(-1,-2,0,10,0,0));previous=x;
        }
        return box;
    }

    @Override void actions(Shift s){
        if(s.owner!=1){super.actions(s);return;}
        new AlertDialog.Builder(this).setTitle("Lenies pass")
            .setItems(new String[]{"Redigera passet","Kopiera till flera datum","Lägg till delpass","Spara som mall","Radera"},(d,w)->{
                if(w==0)editDialog(s,false);else if(w==1)copyDates(s);else if(w==2){selectedDay=s.date;personView=1;showCalendar();editDialog(null,false);}else if(w==3)saveTemplate(s);else confirmDelete(s);
            }).show();
    }

    @Override void editDialog(Shift existing,boolean copy){
        if((existing!=null&&existing.owner==1)||(existing==null&&personView==1)){editLenieDialog(existing,copy);return;}
        super.editDialog(existing,copy);
    }

    void editLenieDialog(Shift existing,boolean copy){
        Shift draft=existing==null?new Shift():existing.copy();draft.owner=1;draft.done=false;
        if(existing==null){draft.date=screen==0?dayStart(System.currentTimeMillis()):selectedDay;draft.start="08:00";draft.end="16:00";draft.breakMin=30;}
        if(copy){draft.date=screen==1?selectedDay:dayStart(System.currentTimeMillis());}

        LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(22),dp(6),dp(22),0);
        form.addView(text("Lenies schema är en översikt. Passet får inga arbetad-statusar eller påminnelser.",13,LENIE,false),mp(-1,-2,0,0,0,8));
        Button dateBtn=styledButton();dateBtn.setText(fullDate(draft.date));form.addView(label("Datum"));form.addView(dateBtn);
        Spinner category=new Spinner(this);String[] kinds={"Ordinarie","Utbildning","Extra pass"};category.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,kinds));for(int k=0;k<kinds.length;k++)if(kinds[k].equals(draft.kind))category.setSelection(k);form.addView(label("Typ av pass"));form.addView(category);
        LinearLayout times=new LinearLayout(this);Button startBtn=styledButton(),endBtn=styledButton();startBtn.setText(draft.start);endBtn.setText(draft.end);times.addView(startBtn,new LinearLayout.LayoutParams(0,dp(54),1));times.addView(endBtn,new LinearLayout.LayoutParams(0,dp(54),1));form.addView(label("Starttid                              Sluttid"));form.addView(times);
        EditText br=input(String.valueOf(draft.breakMin),"Rast i minuter");br.setInputType(2);form.addView(label("Rast (minuter)"));form.addView(br);
        EditText service=input(draft.service,"Valfritt");form.addView(label("Tjänst / arbetsplats"));form.addView(service);
        EditText line=input(draft.line,"Valfritt");form.addView(label("Linje / omlopp"));form.addView(line);
        EditText note=input(draft.note,"Valfri anteckning");note.setMinLines(2);form.addView(label("Anteckning"));form.addView(note);

        dateBtn.setOnClickListener(v->{Calendar c=Calendar.getInstance();c.setTimeInMillis(draft.date);new DatePickerDialog(this,(x,y,m,day)->{c.set(y,m,day,0,0,0);c.set(Calendar.MILLISECOND,0);draft.date=c.getTimeInMillis();dateBtn.setText(fullDate(draft.date));},c.get(Calendar.YEAR),c.get(Calendar.MONTH),c.get(Calendar.DAY_OF_MONTH)).show();});
        startBtn.setOnClickListener(v->pickTime(draft.start,t->{draft.start=t;startBtn.setText(t);}));endBtn.setOnClickListener(v->pickTime(draft.end,t->{draft.end=t;endBtn.setText(t);}));
        ScrollView scroll=new ScrollView(this);scroll.addView(form);scroll.setPadding(0,0,0,dp(16));
        String heading=existing==null?"Nytt pass för Lenie":copy?"Kopiera Lenies pass":"Redigera Lenies pass";
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle(heading).setView(scroll).setNegativeButton("Avbryt",null).setPositiveButton("Spara",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{draft.breakMin=Integer.parseInt(br.getText().toString().trim());if(draft.breakMin<0)throw new Exception();}catch(Exception e){br.setError("Ange rast i hela minuter, minst 0");return;}
            draft.kind=category.getSelectedItem().toString();draft.service=service.getText().toString().trim();draft.line=line.getText().toString().trim();draft.note=note.getText().toString().trim();draft.owner=1;draft.done=false;
            if(draft.minutes()<=0){Toast.makeText(this,"Kontrollera tider och rast",Toast.LENGTH_LONG).show();return;}
            for(Shift other:shifts){if(other==existing&&!copy)continue;if(other.owner==1&&startAt(draft)<endAt(other)&&startAt(other)<endAt(draft)){Toast.makeText(this,"Passet överlappar ett annat av Lenies pass",Toast.LENGTH_LONG).show();return;}}
            if(existing!=null&&!copy)shifts.remove(existing);shifts.add(draft);save();dialog.dismiss();refresh();
        }));dialog.show();dialog.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    }

    @Override void showCalendar(){super.showCalendar();if(personView==1)title.setText("Lenies kalender");else if(personView==2)title.setText("Vår kalender");}
    @Override void showAll(){super.showAll();if(personView==1)title.setText("Lenies pass");else if(personView==2)title.setText("Våra pass");}
}
