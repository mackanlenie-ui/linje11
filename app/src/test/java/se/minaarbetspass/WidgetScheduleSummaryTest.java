package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class WidgetScheduleSummaryTest {
    @Test public void findsNextEntryForEachOwner(){
        long now=1000L;
        List<WidgetScheduleSummary.Entry> all=Arrays.asList(
            new WidgetScheduleSummary.Entry(0,900L,950L,"Gammalt"),
            new WidgetScheduleSummary.Entry(1,1200L,1400L,"Lenie 1"),
            new WidgetScheduleSummary.Entry(0,1100L,1300L,"Mitt 1"),
            new WidgetScheduleSummary.Entry(0,1500L,1700L,"Mitt 2")
        );
        assertEquals("Mitt 1",WidgetScheduleSummary.next(all,0,now).label);
        assertEquals("Lenie 1",WidgetScheduleSummary.next(all,1,now).label);
    }

    @Test public void activeEntryCountsAsNext(){
        long now=1000L;
        List<WidgetScheduleSummary.Entry> all=Collections.singletonList(
            new WidgetScheduleSummary.Entry(0,900L,1200L,"Pågår")
        );
        assertEquals("Pågår",WidgetScheduleSummary.next(all,0,now).label);
    }
}
