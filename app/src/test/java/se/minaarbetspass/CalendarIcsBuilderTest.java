package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class CalendarIcsBuilderTest {
    private long day(int y,int m,int d){
        Calendar c=Calendar.getInstance();c.clear();c.set(y,m-1,d,0,0,0);return c.getTimeInMillis();
    }

    @Test public void buildsStandardCalendarWithVisibleShift(){
        CalendarIcsBuilder.Event e=new CalendarIcsBuilder.Event(day(2026,10,1),"14:30","21:40","Lenie · Arbetspass","Ordinarie");
        String out=CalendarIcsBuilder.build(Collections.singletonList(e));
        assertTrue(out.startsWith("BEGIN:VCALENDAR\r\nVERSION:2.0"));
        assertTrue(out.contains("DTSTART:20261001T143000"));
        assertTrue(out.contains("DTEND:20261001T214000"));
        assertTrue(out.contains("SUMMARY:Lenie · Arbetspass"));
        assertTrue(out.endsWith("END:VCALENDAR\r\n"));
    }

    @Test public void movesOvernightEndToNextDay(){
        CalendarIcsBuilder.Event e=new CalendarIcsBuilder.Event(day(2026,10,2),"22:00","05:30","Mitt · Arbetspass","");
        String out=CalendarIcsBuilder.build(Collections.singletonList(e));
        assertTrue(out.contains("DTSTART:20261002T220000"));
        assertTrue(out.contains("DTEND:20261003T053000"));
    }

    @Test public void escapesCalendarText(){
        String escaped=CalendarIcsBuilder.escape("A, B; C\nRad 2");
        assertEquals("A\\, B\\; C\\nRad 2",escaped);
    }
}
