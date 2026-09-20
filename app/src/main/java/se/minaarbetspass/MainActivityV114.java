package se.minaarbetspass;

import android.app.*;
import android.content.*;
import android.net.Uri;
import android.view.*;
import android.widget.*;
import androidx.core.content.FileProvider;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV114 extends MainActivityV113 {
    static final int BOTH_WORK_COLOR=0xfff8fafc;

    @Override void save(){
        super.save();
        WorkWidgetProvider.updateAll(this);
    }

    void createRecurringShift(){
        final Shift draft=new Shift();draft.owner=personView==1?1:0;draft.date=screen==1?selectedDay:dayStart(System.currentTimeMillis());draft.done=false;
        LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(22),dp(4),dp(22),0);

        Spinner owner=new Spinner(this);String[] owners={"Mitt schema","Lenies schema"};owner.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,owners));owner.setSelection(draft.owner);
        Button date=styledButton();date.setText(fullDate(draft.date));
        Button start=styledButton(),end=styledButton();start.setText(draft.start);end.setText(draft.end);
        LinearLayout times=new LinearLayout(this);times.addView(start,new LinearLayout.LayoutParams(0,dp(52),1));times.addView(end,new LinearLayout.LayoutParams(0,dp(52),1));
        EditText br=input(String.valueOf(draft.breakMin),"Rast i minuter");br.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);br.setSingleLine(true);
        Spinner interval=new Spinner(this);interval.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,new String[]{"Varje vecka","Varannan vecka"}));
        EditText count=input("4","Antal tillfällen");count.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);count.setSingleLine(true);
        EditText note=input("","Valfri anteckning");note.setMinLines(2);

        form.addView(label("Schema"));form.addView(owner);form.addView(label("Första datum"));form.addView(date);
        form.addView(label("Starttid                              Sluttid"));form.addView(times);
        form.addView(label("Rast (minuter)"));form.addView(br);form.addView(label("Upprepning"));form.addView(interval);
        form.addView(label("Antal tillfällen"));form.addView(count);form.addView(label("Anteckning"));form.addView(note);

        date.setOnClickListener(v->{Calendar c=Calendar.getInstance();c.setTimeInMillis(draft.date);new DatePickerDialog(this,(x,y,m,d)->{c.set(y,m,d,0,0,0);c.set(Calendar.MILLISECOND,0);draft.date=c.getTimeInMillis();date.setText(fullDate(draft.date));},c.get(Calendar.YEAR),c.get(Calendar.MONTH),c.get(Calendar.DAY_OF_MONTH)).show();});
        start.setOnClickListener(v->pickTime(draft.start,t->{draft.start=t;start.setText(t);}));
        end.setOnClickListener(v->pickTime(draft.end,t->{draft.end=t;end.setText(t);}));

        ScrollView scroll=new ScrollView(this);scroll.addView(form);
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Återkommande pass").setView(scroll).setNegativeButton("Avbryt",null).setPositiveButton("Lägg in",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            int breakMin,n;
            try{breakMin=Integer.parseInt(br.getText().toString().trim());n=Integer.parseInt(count.getText().toString().trim());}catch(Exception e){Toast.makeText(this,"Kontrollera rast och antal tillfällen",Toast.LENGTH_LONG).show();return;}
            if(breakMin<0||n<2||n>52){Toast.makeText(this,"Antal tillfällen måste vara 2–52",Toast.LENGTH_LONG).show();return;}
            draft.owner=owner.getSelectedItemPosition()==1?1:0;draft.breakMin=breakMin;draft.note=note.getText().toString().trim();draft.kind="Ordinarie";draft.done=false;
            if(draft.minutes()<=0){Toast.makeText(this,"Kontrollera tider och rast",Toast.LENGTH_LONG).show();return;}
            int weeks=interval.getSelectedItemPosition()==1?2:1,added=0,skipped=0;long first=0;
            for(long d:RecurrencePlanner.dates(draft.date,weeks,n)){
                Shift s=draft.copy();s.date=d;
                boolean conflict=false;for(Shift other:shifts)if(other.owner==s.owner&&startAt(s)<endAt(other)&&startAt(other)<endAt(s)){conflict=true;break;}
                if(conflict){skipped++;continue;}shifts.add(s);if(first==0)first=d;added++;
            }
            if(added>0){save();personView=draft.owner;getPreferences(0).edit().putInt("personView",personView).apply();selectedDay=first;dialog.dismiss();showCalendar();}
            Toast.makeText(this,added+" pass tillagda"+(skipped>0?" · "+skipped+" överlapp hoppades över":""),Toast.LENGTH_LONG).show();
        }));dialog.show();
    }

    void exportCalendarDialog(){
        String[] choices={"Vald dag","Visad vecka","Visad månad"};
        new AlertDialog.Builder(this).setTitle("Exportera till kalender").setMessage("Exporten innehåller det schema som är valt: Mitt, Lenie eller Båda.")
            .setItems(choices,(d,w)->exportCalendar(w)).setNegativeButton("Avbryt",null).show();
    }

    void exportCalendar(int mode){
        long anchor=screen==1?selectedDay:dayStart(System.currentTimeMillis()),from,to;
        if(mode==0){from=dayStart(anchor);to=addDays(from,1);}
        else if(mode==1){from=weekStart(anchor);to=addDays(from,7);}
        else {Calendar c=Calendar.getInstance();c.setTimeInMillis(anchor);c.set(Calendar.DAY_OF_MONTH,1);from=dayStart(c.getTimeInMillis());c.add(Calendar.MONTH,1);to=dayStart(c.getTimeInMillis());}
        ArrayList<CalendarIcsBuilder.Event> events=new ArrayList<>();
        for(Shift x:shifts)if(visible(x)&&x.date>=from&&x.date<to){
            String who=x.owner==1?"Lenie":"Mitt";String summary=who+" · "+(x.service.isEmpty()?"Arbetspass":x.service);
            String desc=x.kind+(x.line.isEmpty()?"":" · "+x.line)+(x.note.isEmpty()?"":" · "+x.note)+" · Rast "+x.breakMin+" min";
            events.add(new CalendarIcsBuilder.Event(x.date,x.start,x.end,summary,desc));
        }
        Collections.sort(events,(a,b)->a.day==b.day?a.start.compareTo(b.start):Long.compare(a.day,b.day));
        if(events.isEmpty()){Toast.makeText(this,"Det finns inga pass att exportera i perioden",Toast.LENGTH_LONG).show();return;}
        try{
            File out=new File(getCacheDir(),"mina-arbetspass-kalender.ics");
            try(FileOutputStream f=new FileOutputStream(out)){f.write(CalendarIcsBuilder.build(events).getBytes(StandardCharsets.UTF_8));}
            Uri uri=FileProvider.getUriForFile(this,getPackageName()+".fileprovider",out);
            Intent send=new Intent(Intent.ACTION_SEND);send.setType("text/calendar");send.putExtra(Intent.EXTRA_STREAM,uri);send.putExtra(Intent.EXTRA_SUBJECT,"Mina arbetspass");send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            startActivity(Intent.createChooser(send,"Öppna/importera kalenderfil"));
        }catch(Exception e){Toast.makeText(this,"Kalenderfilen kunde inte skapas",Toast.LENGTH_LONG).show();}
    }

    @Override void showCalendar(){
        if(personView!=2){super.showCalendar();return;}
        showCombinedCalendar();
    }

    void showCombinedCalendar(){
        screen=1;title.setText("Vår kalender");content.removeAllViews();nav(1);
        LinearLayout controls=new LinearLayout(this);Button prev=styledButton(),mode=styledButton(),next=styledButton();prev.setText("‹");next.setText("›");mode.setText(weekView?"Vecka · byt till månad":"Månad · byt till vecka");
        controls.addView(prev,new LinearLayout.LayoutParams(dp(50),dp(52)));LinearLayout.LayoutParams mpMode=new LinearLayout.LayoutParams(0,dp(52),1);mpMode.setMargins(dp(8),0,dp(8),0);controls.addView(mode,mpMode);controls.addView(next,new LinearLayout.LayoutParams(dp(50),dp(52)));
        prev.setOnClickListener(v->moveCalendar(-1));next.setOnClickListener(v->moveCalendar(1));mode.setOnClickListener(v->{weekView=!weekView;showCalendar();});content.addView(controls);
        Button today=styledButton();today.setText("Idag");today.setOnClickListener(v->{selectedDay=dayStart(System.currentTimeMillis());showCalendar();});content.addView(today,mp(-1,dp(48),0,8,0,0));
        content.addView(text("Turkos = bara jag   •   Lila = bara Lenie   •   Vit = båda jobbar   •   Grå = båda lediga",12,MUTED,false),mp(-1,-2,0,10,0,8));
        content.addView(section(cap(new SimpleDateFormat("MMMM yyyy",new Locale("sv","SE")).format(new Date(selectedDay)))));
        if(weekView)combinedWeekView();else combinedMonthView();
    }

    void combinedWeekView(){
        content.addView(combinedWeekStrip(selectedDay));
        long monday=weekStart(selectedDay);
        for(int i=0;i<7;i++){long d=addDays(monday,i);content.addView(combinedDaySummary(d),mp(-1,-2,0,0,0,7));}
    }

    LinearLayout combinedWeekStrip(long day){
        LinearLayout strip=new LinearLayout(this);long monday=weekStart(day);
        for(int i=0;i<7;i++){
            final long d=addDays(monday,i);int state=combinedState(d);
            String shortLabel=state==CombinedDayState.BOTH_FREE?"Lediga":state==CombinedDayState.MINE_ONLY?"Jag":state==CombinedDayState.LENIE_ONLY?"Lenie":"Båda";
            TextView cell=text(new SimpleDateFormat("EE",new Locale("sv","SE")).format(new Date(d))+"\n"+new SimpleDateFormat("d",Locale.US).format(new Date(d))+"\n"+shortLabel,12,stateColor(state),true);
            cell.setGravity(Gravity.CENTER);cell.setBackground(round(d==selectedDay?CARD2:CARD,12));cell.setOnClickListener(v->{selectedDay=d;showCalendar();});
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(82),1);lp.setMargins(dp(2),0,dp(2),dp(10));strip.addView(cell,lp);
        }return strip;
    }

    void combinedMonthView(){
        LinearLayout grid=card();Calendar c=Calendar.getInstance();c.setTimeInMillis(selectedDay);c.set(Calendar.DAY_OF_MONTH,1);int month=c.get(Calendar.MONTH);c.add(Calendar.DAY_OF_MONTH,-((c.get(Calendar.DAY_OF_WEEK)+5)%7));
        LinearLayout names=new LinearLayout(this);for(String n:new String[]{"M","T","O","T","F","L","S"}){TextView t=text(n,13,MUTED,true);t.setGravity(Gravity.CENTER);names.addView(t,new LinearLayout.LayoutParams(0,dp(30),1));}grid.addView(names);
        for(int row=0;row<6;row++){LinearLayout line=new LinearLayout(this);
            for(int col=0;col<7;col++){final long d=dayStart(c.getTimeInMillis());boolean current=c.get(Calendar.MONTH)==month;int state=combinedState(d);
                String mark=state==CombinedDayState.BOTH_FREE?"○":state==CombinedDayState.MINE_ONLY?"●":state==CombinedDayState.LENIE_ONLY?"●":"●●";
                TextView cell=text(c.get(Calendar.DAY_OF_MONTH)+"\n"+mark,14,current?stateColor(state):MUTED,true);cell.setGravity(Gravity.CENTER);if(d==selectedDay)cell.setBackground(round(CARD2,12));
                line.addView(cell,new LinearLayout.LayoutParams(0,dp(54),1));cell.setOnClickListener(v->{selectedDay=d;showCalendar();});c.add(Calendar.DAY_OF_MONTH,1);
            }grid.addView(line);
        }
        content.addView(grid);content.addView(section(cap(dateFmt.format(new Date(selectedDay)))));
        content.addView(combinedDaySummary(selectedDay));
    }

    LinearLayout combinedDaySummary(long day){
        ArrayList<Shift> mine=ownerDay(0,day),hers=ownerDay(1,day);int state=CombinedDayState.of(mine.size(),hers.size());
        LinearLayout box=card();box.addView(text(cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(day)))+" · "+CombinedDayState.label(state),15,stateColor(state),true));
        box.addView(text("Mitt: "+(mine.isEmpty()?"Ledig":times(mine)+" · "+formatHours(totalMinutes(mine))),14,mine.isEmpty()?MUTED:TEAL,true),mp(-1,-2,0,7,0,0));
        box.addView(text("Lenie: "+(hers.isEmpty()?"Ledig":times(hers)+" · "+formatHours(totalMinutes(hers))),14,hers.isEmpty()?MUTED:LENIE,true),mp(-1,-2,0,5,0,0));
        box.setOnClickListener(v->{selectedDay=day;});return box;
    }

    int combinedState(long d){return CombinedDayState.of(ownerDayCount(d,0),ownerDayCount(d,1));}
    int stateColor(int state){if(state==CombinedDayState.MINE_ONLY)return TEAL;if(state==CombinedDayState.LENIE_ONLY)return LENIE;if(state==CombinedDayState.BOTH_WORK)return BOTH_WORK_COLOR;return MUTED;}
}
