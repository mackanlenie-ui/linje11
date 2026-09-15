package se.minaarbetspass;

import java.util.*;
import java.util.regex.*;

final class PhotoScheduleParser {
    static final class Token {
        final String text; final int left,top,right,bottom;
        Token(String text,int left,int top,int right,int bottom){this.text=text==null?"":text;this.left=left;this.top=top;this.right=right;this.bottom=bottom;}
        int centerY(){return top+(bottom-top)/2;}
    }

    static final class Candidate {
        final int day; final String start,end;
        Candidate(int day,String start,String end){this.day=day;this.start=start;this.end=end;}
        String key(){return day+"|"+start+"|"+end;}
    }

    static final class MonthYear {
        final int year,month; final boolean detected;
        MonthYear(int year,int month,boolean detected){this.year=year;this.month=month;this.detected=detected;}
    }

    private static final Pattern COLON_TIME=Pattern.compile("(?<!\\d)(\\d{1,2})\\s*[:.]\\s*(\\d{2})(?!\\d)");
    private static final Pattern SPACE_TIME=Pattern.compile("(?<!\\d)(\\d{1,2})\\s+(\\d{2})(?!\\d)");
    private static final Pattern COMPACT_TIME=Pattern.compile("(?<!\\d)(\\d{3,4})(?!\\d)");
    private static final Pattern HOUR_TIME=Pattern.compile("(?<!\\d)(\\d{1,2})(?!\\d)");
    private PhotoScheduleParser(){}

    static MonthYear detectMonthYear(String raw,int defaultYear,int defaultMonth){
        String text=(raw==null?"":raw).toLowerCase(new Locale("sv","SE"));
        String[] months={"januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"};
        int month=defaultMonth;boolean monthFound=false;
        for(int i=0;i<months.length;i++)if(text.contains(months[i])){month=i+1;monthFound=true;break;}
        int year=defaultYear;Matcher y=Pattern.compile("\\b(20\\d{2})\\b").matcher(text);if(y.find())year=Integer.parseInt(y.group(1));
        return new MonthYear(year,month,monthFound);
    }

    static List<Candidate> parse(List<Token> tokens,int year,int month){
        ArrayList<Candidate> result=new ArrayList<>();if(tokens==null||tokens.isEmpty())return result;
        int minX=Integer.MAX_VALUE,maxX=Integer.MIN_VALUE;
        for(Token t:tokens){minX=Math.min(minX,t.left);maxX=Math.max(maxX,t.right);}
        int leftLimit=minX+(int)((maxX-minX)*0.22f);
        ArrayList<Token> dayTokens=new ArrayList<>();
        for(Token t:tokens){Integer day=dayNumber(t.text);if(day!=null&&t.right<=leftLimit)dayTokens.add(t);}
        Collections.sort(dayTokens,(a,b)->Integer.compare(a.centerY(),b.centerY()));
        LinkedHashMap<Integer,Candidate> found=new LinkedHashMap<>();HashSet<Integer> ambiguous=new HashSet<>();
        for(Token dayToken:dayTokens){
            int day=dayNumber(dayToken.text);if(ambiguous.contains(day))continue;
            int tolerance=Math.max(20,Math.max(1,dayToken.bottom-dayToken.top));
            ArrayList<Token> row=new ArrayList<>();
            for(Token t:tokens)if(t!=dayToken&&t.left>dayToken.right&&Math.abs(t.centerY()-dayToken.centerY())<=tolerance)row.add(t);
            Collections.sort(row,Comparator.comparingInt(a->a.left));
            StringBuilder joined=new StringBuilder();for(Token t:row){if(joined.length()>0)joined.append(' ');joined.append(t.text);}
            String[] range=parseOneRange(joined.toString());if(range==null)continue;
            Candidate candidate=new Candidate(day,range[0],range[1]);Candidate previous=found.get(day);
            if(previous==null)found.put(day,candidate);
            else if(!previous.key().equals(candidate.key())){found.remove(day);ambiguous.add(day);}
        }
        result.addAll(found.values());Collections.sort(result,Comparator.comparingInt(a->a.day));return result;
    }

    private static Integer dayNumber(String text){
        if(text==null)return null;String s=text.trim();if(!s.matches("\\d{1,2}"))return null;int d=Integer.parseInt(s);return d>=1&&d<=31?d:null;
    }

    private static String[] parseOneRange(String raw){
        String s=normalize(raw);int dashes=0;for(int i=0;i<s.length();i++)if(s.charAt(i)=='-')dashes++;
        if(dashes!=1)return null;String[] parts=s.split("-",-1);if(parts.length!=2)return null;
        int[] start=findTime(parts[0],true),end=findTime(parts[1],false);if(start==null||end==null)return null;
        if(start[0]==end[0]&&start[1]==end[1])return null;
        return new String[]{clock(start),clock(end)};
    }

    private static String normalize(String s){
        String r=s==null?"":s;r=r.replace('–','-').replace('—','-').replace('−','-');
        String supers="⁰¹²³⁴⁵⁶⁷⁸⁹";for(int i=0;i<10;i++)r=r.replace(supers.charAt(i),(char)('0'+i));
        return r.replaceAll("\\s+"," ").trim();
    }

    private static int[] findTime(String s,boolean last){
        int[] v=findByPattern(s,COLON_TIME,last,0);if(v!=null)return v;
        v=findByPattern(s,SPACE_TIME,last,0);if(v!=null)return v;
        v=findByPattern(s,COMPACT_TIME,last,1);if(v!=null)return v;
        return findByPattern(s,HOUR_TIME,last,2);
    }

    private static int[] findByPattern(String s,Pattern p,boolean last,int mode){
        Matcher m=p.matcher(s);int[] chosen=null;
        while(m.find()){
            int h,min;
            try{
                if(mode==0){h=Integer.parseInt(m.group(1));min=Integer.parseInt(m.group(2));}
                else if(mode==1){String n=m.group(1);if(n.length()==3){h=Integer.parseInt(n.substring(0,1));min=Integer.parseInt(n.substring(1));}else{h=Integer.parseInt(n.substring(0,2));min=Integer.parseInt(n.substring(2));}}
                else {h=Integer.parseInt(m.group(1));min=0;}
            }catch(Exception e){continue;}
            if(h<0||h>23||min<0||min>59)continue;chosen=new int[]{h,min};if(!last)return chosen;
        }
        return chosen;
    }

    private static String clock(int[] t){return String.format(Locale.US,"%02d:%02d",t[0],t[1]);}
}
