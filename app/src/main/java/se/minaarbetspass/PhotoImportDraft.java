package se.minaarbetspass;

import java.util.*;

final class PhotoImportDraft {
    int day;
    String start,end;
    boolean uncertain;
    boolean selected;

    PhotoImportDraft(PhotoScheduleParser.Candidate c){
        day=c.day;start=c.start;end=c.end;uncertain=c.uncertain;selected=!uncertain&&canImport();
    }

    boolean applyEdit(int newDay,String newStart,String newEnd){
        String a=normalizeTime(newStart),b=normalizeTime(newEnd);
        if(newDay<1||newDay>31||a==null||b==null||a.equals(b))return false;
        day=newDay;start=a;end=b;uncertain=false;selected=true;return true;
    }

    boolean canImport(){
        return day>=1&&day<=31&&normalizeTime(start)!=null&&normalizeTime(end)!=null&&!normalizeTime(start).equals(normalizeTime(end));
    }

    static String normalizeTime(String raw){
        if(raw==null)return null;
        String s=raw.trim().replace('.',':').replace(',',':').replaceAll("\\s+","");
        int h,m;
        try{
            if(s.matches("\\d{1,2}")){h=Integer.parseInt(s);m=0;}
            else if(s.matches("\\d{3,4}")){
                if(s.length()==3){h=Integer.parseInt(s.substring(0,1));m=Integer.parseInt(s.substring(1));}
                else {h=Integer.parseInt(s.substring(0,2));m=Integer.parseInt(s.substring(2));}
            }else if(s.matches("\\d{1,2}:\\d{1,2}")){
                String[] p=s.split(":");h=Integer.parseInt(p[0]);m=Integer.parseInt(p[1]);
            }else return null;
        }catch(Exception e){return null;}
        if(h<0||h>23||m<0||m>59)return null;
        return String.format(Locale.US,"%02d:%02d",h,m);
    }

    static String signature(long date,String start,String end){
        Calendar c=Calendar.getInstance();c.setTimeInMillis(date);
        c.set(Calendar.HOUR_OF_DAY,0);c.set(Calendar.MINUTE,0);c.set(Calendar.SECOND,0);c.set(Calendar.MILLISECOND,0);
        String a=normalizeTime(start),b=normalizeTime(end);
        return c.getTimeInMillis()+"|"+(a==null?"":a)+"|"+(b==null?"":b);
    }
}
