package se.minaarbetspass;

import java.util.*;

final class StorageMigrationPolicy {
    private StorageMigrationPolicy(){}

    static List<String> legacyNames(String packageName){
        return Arrays.asList(
            "MainActivityCurrent",
            "MainActivity",
            "MainActivityV110",
            "MainActivityV19",
            "MainActivityV18",
            packageName+"_preferences"
        );
    }
}
