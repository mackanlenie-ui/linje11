package se.minaarbetspass;

import java.util.*;

final class LenieOctober2026Seed {
    static final class Entry {
        final int day;
        final String start,end,note;
        Entry(int day,String start,String end,String note){this.day=day;this.start=start;this.end=end;this.note=note;}
    }

    private LenieOctober2026Seed(){}

    static List<Entry> entries(){
        return Collections.unmodifiableList(Arrays.asList(
            new Entry(1,"14:30","21:40",""),
            new Entry(2,"15:30","20:30",""),
            new Entry(3,"07:30","20:30",""),
            new Entry(7,"07:00","16:00","Reserv"),
            new Entry(12,"13:00","21:40",""),
            new Entry(13,"14:30","20:30",""),
            new Entry(15,"15:00","20:30",""),
            new Entry(16,"08:00","14:00",""),
            new Entry(20,"15:30","20:30",""),
            new Entry(21,"08:00","15:00",""),
            new Entry(23,"15:00","20:30",""),
            new Entry(24,"07:30","20:30",""),
            new Entry(25,"07:30","20:30",""),
            new Entry(27,"15:00","21:40",""),
            new Entry(28,"15:30","21:40",""),
            new Entry(29,"14:30","21:40","")
        ));
    }
}
