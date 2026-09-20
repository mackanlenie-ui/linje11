package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class RecurrencePlannerTest {
    private long day(int y,int m,int d){
        Calendar c=Calendar.getInstance();c.clear();c.set(y,m-1,d,0,0,0);return c.getTimeInMillis();
    }

    @Test public void createsWeeklyDates(){
        List<Long> out=RecurrencePlanner.dates(day(2026,10,1),1,4);
        assertEquals(Arrays.asList(day(2026,10,1),day(2026,10,8),day(2026,10,15),day(2026,10,22)),out);
    }

    @Test public void createsEveryOtherWeekDates(){
        List<Long> out=RecurrencePlanner.dates(day(2026,10,3),2,3);
        assertEquals(Arrays.asList(day(2026,10,3),day(2026,10,17),day(2026,10,31)),out);
    }

    @Test public void rejectsInvalidRecurrence(){
        assertTrue(RecurrencePlanner.dates(day(2026,10,1),0,4).isEmpty());
        assertTrue(RecurrencePlanner.dates(day(2026,10,1),1,0).isEmpty());
    }
}
