package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class ScheduleInsightsTest {
    @Test public void sharedFreeDays_skipsDaysEitherPersonWorks(){
        List<Long> days=Arrays.asList(1L,2L,3L,4L,5L);
        Set<Long> mine=new HashSet<>(Arrays.asList(2L,5L));
        Set<Long> lenie=new HashSet<>(Collections.singletonList(3L));
        assertEquals(Arrays.asList(1L,4L),ScheduleInsights.sharedFreeDays(days,mine,lenie,5));
    }

    @Test public void sharedFreeDays_respectsMaxResults(){
        List<Long> days=Arrays.asList(10L,11L,12L,13L);
        assertEquals(Arrays.asList(10L,11L),ScheduleInsights.sharedFreeDays(days,Collections.emptySet(),Collections.emptySet(),2));
    }

    @Test public void freeDaysInWeek_isClampedToSevenDayWeek(){
        assertEquals(3,ScheduleInsights.freeDaysInWeek(4));
        assertEquals(7,ScheduleInsights.freeDaysInWeek(0));
        assertEquals(0,ScheduleInsights.freeDaysInWeek(9));
    }

    @Test public void sharedEveningStart_usesLatestFinishButNeverBeforeFive(){
        assertEquals(17*60,ScheduleInsights.sharedEveningStart(16*60,15*60+30));
        assertEquals(17*60+45,ScheduleInsights.sharedEveningStart(17*60+45,16*60));
    }

    @Test public void sharedEveningStart_rejectsTooLateOrOvernight(){
        assertEquals(-1,ScheduleInsights.sharedEveningStart(20*60+1,18*60));
        assertEquals(-1,ScheduleInsights.sharedEveningStart(25*60,16*60));
    }

    @Test public void overlaps_detectsRealOverlapButAllowsTouchingEdges(){
        assertTrue(ScheduleInsights.overlaps(100,200,150,250));
        assertFalse(ScheduleInsights.overlaps(100,200,200,300));
        assertFalse(ScheduleInsights.overlaps(300,400,100,200));
    }
}
