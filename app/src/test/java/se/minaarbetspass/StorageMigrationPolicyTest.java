package se.minaarbetspass;

import org.junit.Test;
import java.util.*;
import static org.junit.Assert.*;

public class StorageMigrationPolicyTest {
    @Test public void legacyNames_prioritizeCurrentActivityThenOlderAndReminderFile(){
        assertEquals(Arrays.asList(
            "MainActivityCurrent",
            "MainActivity",
            "MainActivityV110",
            "MainActivityV19",
            "MainActivityV18",
            "se.minaarbetspass_preferences"
        ),StorageMigrationPolicy.legacyNames("se.minaarbetspass"));
    }
}
