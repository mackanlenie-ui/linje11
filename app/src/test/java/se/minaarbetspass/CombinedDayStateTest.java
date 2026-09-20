package se.minaarbetspass;

import org.junit.Test;
import static org.junit.Assert.*;

public class CombinedDayStateTest {
    @Test public void classifiesAllFourCombinedStates(){
        assertEquals(CombinedDayState.BOTH_FREE,CombinedDayState.of(0,0));
        assertEquals(CombinedDayState.MINE_ONLY,CombinedDayState.of(1,0));
        assertEquals(CombinedDayState.LENIE_ONLY,CombinedDayState.of(0,2));
        assertEquals(CombinedDayState.BOTH_WORK,CombinedDayState.of(1,1));
    }

    @Test public void labelsAreSwedishAndClear(){
        assertEquals("Båda lediga",CombinedDayState.label(CombinedDayState.BOTH_FREE));
        assertEquals("Bara jag",CombinedDayState.label(CombinedDayState.MINE_ONLY));
        assertEquals("Bara Lenie",CombinedDayState.label(CombinedDayState.LENIE_ONLY));
        assertEquals("Båda jobbar",CombinedDayState.label(CombinedDayState.BOTH_WORK));
    }
}
