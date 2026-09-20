package se.minaarbetspass;

import java.text.SimpleDateFormat;
import java.util.*;

final class CalendarIcsBuilder {
    static final class Event {
        final long day;
        final String start,end,summary,description;
        Event(long day,String start,String end,String summary,String description){
            this.day=day;this.start=start;this.end=end;this.summary=summary==null?"":summary;this.description=description==null?"":description;
        }
    }

    private CalendarIcsBuilder(){}

    static String build(List<Event> events){
        StringBuilder b=new StringBuilder();
        b.append("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Mina arbetspass//SV\r\nCALSCALE:GREGORIAN\r\n");
        if(events!=null)for(Event e:events){
            long startAt=at(e.day,e.start,false),endAt=endAt(e.day,e.start,e.end);
            String uid=Integer.toHexString((e.day+"|"+e.start+"|"+e.end+"|"+e.summary).hashCode())+"@mina-arbetspass";
            b.append("BEGIN:VEVENT\r\n");
            b.append("UID:").append(uid).append("\r\n");
            b.append("DTSTART:").append(stamp(startAt)).append("\r\n");
            b.append("DTEND:").append(stamp(endAt)).append("\r\n");
            b.append("SUMMARY:").append(escape(e.summary)).append("\r\n");
            if(!e.description.isEmpty())b.append("DESCRIPTION:").append(escape(e.description)).append("\r\n");
            b.append("END:VEVENT\r\n");
        }
        b.append("END:VCALENDAR\r\n");return b.toString();
    }

    static String escape(String s){
        if(s==null)return "";
        return s.replace("\\","\\\\").replace("\r","").replace("\n","\\n").replace(";","\\;").replace(",","\\,");
    }

    private static long at(long day,String time,boolean end){
        int min=minutes(time);Calendar c=Calendar.getInstance();c.setTimeInMillis(day);
        c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);
        if(end&&min<0)min=0;
        c.add(Calendar.MINUTE,min);
        return c.getTimeInMillis();
    }

    static long endAt(long day,String start,String end){
        Calendar c=Calendar.getInstance();c.setTimeInMillis(day);
        c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);
        int a=minutes(start),z=minutes(end);if(z<a)c.add(Calendar.DAY_OF_MONTH,1);c.add(Calendar.MINUTE,z);return c.getTimeInMillis();
    }

    private static int minutes(String t){
        try{String[] p=t.split(":");return Integer.parseInt(p[0])*60+Integer.parseInt(p[1]);}catch(Exception e){return 0;}
    }

    private static String stamp(long time){return new SimpleDateFormat("yyyyMMdd'T'HHmmss",Locale.US).format(new Date(time));}
}
