package se.minaarbetspass;

import java.util.*;

final class ScheduleInsights {
    private ScheduleInsights(){}

    static List<Long> sharedFreeDays(List<Long> candidateDays, Set<Long> mineWorkDays, Set<Long> lenieWorkDays, int maxResults){
        ArrayList<Long> result=new ArrayList<>();
        if(maxResults<=0)return result;
        for(Long day:candidateDays){
            if(day==null)continue;
            if(!mineWorkDays.contains(day)&&!lenieWorkDays.contains(day)){
                result.add(day);
                if(result.size()>=maxResults)break;
            }
        }
        return result;
    }

    static int freeDaysInWeek(int workDayCount){
        int work=Math.max(0,Math.min(7,workDayCount));
        return 7-work;
    }

    static int sharedEveningStart(int mineLatestEndMinutes,int lenieLatestEndMinutes){
        int latest=Math.max(Math.max(0,mineLatestEndMinutes),Math.max(0,lenieLatestEndMinutes));
        if(latest>20*60)return -1;
        return Math.max(17*60,latest);
    }

    static boolean overlaps(long startA,long endA,long startB,long endB){
        return startA<endB&&startB<endA;
    }
}
