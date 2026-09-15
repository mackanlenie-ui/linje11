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
}
