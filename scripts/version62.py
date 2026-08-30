from pathlib import Path

exec(Path('scripts/version61.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Google Maps directions URLs often contain a human-readable place name that
# differs from the name understood by Nominatim. Prefer coordinates embedded by
# Google in the URL (/data=...!3dLAT!4dLON), then use progressively more tolerant
# name searches instead of aborting the whole import on the first spelling/name.
old='ArrayList<GMPoint> out=new ArrayList<>();for(String n:names)out.add(geocodeGm(n));return out;}'
new='''ArrayList<GMPoint> out=new ArrayList<>();ArrayList<GMPoint> embedded=parseEmbeddedGmCoordinates(url);for(int i=0;i<names.size();i++){String n=names.get(i);GMPoint p=null;if(i<embedded.size())p=embedded.get(i);if(p==null){try{p=geocodeGm(n);}catch(Exception first){p=geocodeGmFlexible(n);}}if(p!=null){p.name=n;out.add(p);}}return out;}\n private ArrayList<GMPoint> parseEmbeddedGmCoordinates(String url){ArrayList<GMPoint> out=new ArrayList<>();try{String dec=URLDecoder.decode(url,"UTF-8");java.util.regex.Matcher m=java.util.regex.Pattern.compile("!3d(-?\\\\d+(?:\\\\.\\\\d+)?)!4d(-?\\\\d+(?:\\\\.\\\\d+)?)").matcher(dec);while(m.find())out.add(new GMPoint(Double.parseDouble(m.group(1)),Double.parseDouble(m.group(2)),"Google Maps"));}catch(Exception ignored){}return out;}\n private GMPoint geocodeGmFlexible(String raw)throws Exception{ArrayList<String> tries=new ArrayList<>();String q=raw==null?"":raw.trim();tries.add(q);String cleaned=q.replaceAll("(?i)\\\\s*/\\\\s*.*$","").replaceAll("(?i)\\\\b(SK|IP|IF|IK|BK|FK)\\\\b","").replaceAll("\\\\s{2,}"," ").trim();if(!cleaned.isEmpty()&&!cleaned.equals(q))tries.add(cleaned);if(!q.toLowerCase(Locale.ROOT).contains("gävle"))tries.add(q+", Gävle, Sverige");if(!cleaned.isEmpty()&&!cleaned.toLowerCase(Locale.ROOT).contains("gävle"))tries.add(cleaned+", Gävle, Sverige");for(String x:tries){try{return geocodeGm(x);}catch(Exception ignored){}}throw new Exception("Hittade inte platsen: "+raw); }'''
if old not in s: raise SystemExit('v62 parseGm anchor not found')
s=s.replace(old,new,1)

# If a Google URL exposes only one embedded destination coordinate, use it for
# the final waypoint (the common shared-directions case) rather than the origin.
old2='if(i<embedded.size())p=embedded.get(i);'
new2='if(embedded.size()==names.size()&&i<embedded.size())p=embedded.get(i);else if(embedded.size()==1&&i==names.size()-1)p=embedded.get(0);'
s=s.replace(old2,new2,1)

s=s.replace('VERSION 61 • RIKTIG GPS-OMDIRIGERING','VERSION 62 • SÄKRARE MAPS-IMPORT')
for n in range(1,62):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 62 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 62 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 62 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 61','versionCode 62').replace('versionName "61.0"','versionName "62.0"')
b.write_text(t,encoding='utf-8')
print('Version 62 applied: robust Google Maps import with embedded coordinates and flexible place lookup')
