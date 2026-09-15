package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class LenieOctober2026SeedTest {
    @Test public void containsOnlyTheSixteenClearlyReadableShifts(){
        List<LenieOctober2026Seed.Entry> entries=LenieOctober2026Seed.entries();
        assertEquals(16,entries.size());
        Set<Integer> days=new LinkedHashSet<>();
        for(LenieOctober2026Seed.Entry e:entries)assertTrue("duplicate day "+e.day,days.add(e.day));
        assertEquals(new LinkedHashSet<>(Arrays.asList(1,2,3,7,12,13,15,16,20,21,23,24,25,27,28,29)),days);
        for(int skipped:new int[]{4,6,8,14,19})assertFalse(days.contains(skipped));
    }

    @Test public void preservesTheClearlyReadableTimes(){
        Map<Integer,String> times=new HashMap<>();
        for(LenieOctober2026Seed.Entry e:LenieOctober2026Seed.entries())times.put(e.day,e.start+"-"+e.end);
        assertEquals("14:30-21:40",times.get(1));
        assertEquals("07:00-16:00",times.get(7));
        assertEquals("13:00-21:40",times.get(12));
        assertEquals("07:30-20:30",times.get(25));
        assertEquals("14:30-21:40",times.get(29));
    }
}
