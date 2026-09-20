package se.minaarbetspass;

import java.util.*;

final class RecurrencePlanner {
    private RecurrencePlanner(){}

    static List<Long> dates(long firstDay,int intervalWeeks,int count){
        ArrayList<Long> out=new ArrayList<>();
        if(intervalWeeks<1||count<1)return out;
        Calendar c=Calendar.getInstance();c.setTimeInMillis(firstDay);
        c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);
        for(int i=0;i<count;i++){
            out.add(c.getTimeInMillis());
            c.add(Calendar.DAY_OF_MONTH,intervalWeeks*7);
        }
        return out;
    }
}
