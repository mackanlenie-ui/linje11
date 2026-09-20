package se.minaarbetspass;

import java.util.*;

final class WidgetScheduleSummary {
    static final class Entry {
        final int owner;final long start,end;final String label;
        Entry(int owner,long start,long end,String label){this.owner=owner;this.start=start;this.end=end;this.label=label;}
    }
    private WidgetScheduleSummary(){}

    static Entry next(List<Entry> all,int owner,long now){
        Entry best=null;if(all==null)return null;
        for(Entry e:all)if(e.owner==owner&&e.end>now&&(best==null||e.start<best.start))best=e;
        return best;
    }
}
