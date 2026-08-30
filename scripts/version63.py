from pathlib import Path

exec(Path('scripts/version62.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V62 could still fall back to text geocoding when Google Maps supplied several
# coordinate pairs. Google directions links often contain extra embedded places,
# so align from the END and always trust Google's final coordinate for destination.
old='if(embedded.size()==names.size()&&i<embedded.size())p=embedded.get(i);else if(embedded.size()==1&&i==names.size()-1)p=embedded.get(0);'
new='if(!embedded.isEmpty()){if(i==names.size()-1)p=embedded.get(embedded.size()-1);else if(embedded.size()>=names.size()){int off=embedded.size()-names.size();int ei=off+i;if(ei>=0&&ei<embedded.size())p=embedded.get(ei);}else if(i==0&&embedded.size()>1)p=embedded.get(0);}'
if old not in s: raise SystemExit('v63 embedded alignment anchor not found')
s=s.replace(old,new,1)

# Also understand the common Google Maps !1dLON!2dLAT encoding. Merge it with
# !3dLAT!4dLON points and discard near-duplicates while preserving URL order.
old_parser='private ArrayList<GMPoint> parseEmbeddedGmCoordinates(String url){ArrayList<GMPoint> out=new ArrayList<>();try{String dec=URLDecoder.decode(url,"UTF-8");java.util.regex.Matcher m=java.util.regex.Pattern.compile("!3d(-?\\\\d+(?:\\\\.\\\\d+)?)!4d(-?\\\\d+(?:\\\\.\\\\d+)?)").matcher(dec);while(m.find())out.add(new GMPoint(Double.parseDouble(m.group(1)),Double.parseDouble(m.group(2)),"Google Maps"));}catch(Exception ignored){}return out;}'
new_parser='''private ArrayList<GMPoint> parseEmbeddedGmCoordinates(String url){ArrayList<GMPoint> out=new ArrayList<>();try{String dec=URLDecoder.decode(url,"UTF-8");class Hit{int pos;double lat,lon;Hit(int p,double a,double o){pos=p;lat=a;lon=o;}}ArrayList<Hit> hits=new ArrayList<>();java.util.regex.Matcher a=java.util.regex.Pattern.compile("!3d(-?\\\\d+(?:\\\\.\\\\d+)?)!4d(-?\\\\d+(?:\\\\.\\\\d+)?)").matcher(dec);while(a.find())hits.add(new Hit(a.start(),Double.parseDouble(a.group(1)),Double.parseDouble(a.group(2))));java.util.regex.Matcher b=java.util.regex.Pattern.compile("!1d(-?\\\\d+(?:\\\\.\\\\d+)?)!2d(-?\\\\d+(?:\\\\.\\\\d+)?)").matcher(dec);while(b.find())hits.add(new Hit(b.start(),Double.parseDouble(b.group(2)),Double.parseDouble(b.group(1))));java.util.Collections.sort(hits,(x,y)->Integer.compare(x.pos,y.pos));for(Hit h:hits){boolean dup=false;for(GMPoint p:out){double dy=(p.lat-h.lat)*111000.0,dx=(p.lon-h.lon)*111000.0*Math.cos(Math.toRadians(h.lat));if(Math.sqrt(dx*dx+dy*dy)<25){dup=true;break;}}if(!dup&&Math.abs(h.lat)<=90&&Math.abs(h.lon)<=180)out.add(new GMPoint(h.lat,h.lon,"Google Maps"));}}catch(Exception ignored){}return out;}'''
if old_parser not in s: raise SystemExit('v63 coordinate parser anchor not found')
s=s.replace(old_parser,new_parser,1)

# Store the exact imported start/end coordinates as navigation coordinates too,
# so later road snapping/display logic cannot substitute a name-based point.
old_end='en.put("lat",z.lat);en.put("lon",z.lon);en.put("label","SLUT");en.put("name",z.name);r.put("end",en);'
new_end='en.put("lat",z.lat);en.put("lon",z.lon);en.put("navLat",z.lat);en.put("navLon",z.lon);en.put("label","SLUT");en.put("name",z.name);r.put("end",en);'
if old_end not in s: raise SystemExit('v63 end anchor not found')
s=s.replace(old_end,new_end,1)
old_start='st.put("lat",a.lat);st.put("lon",a.lon);st.put("label","START");st.put("name",a.name);r.put("start",st);'
new_start='st.put("lat",a.lat);st.put("lon",a.lon);st.put("navLat",a.lat);st.put("navLon",a.lon);st.put("label","START");st.put("name",a.name);r.put("start",st);'
if old_start in s:s=s.replace(old_start,new_start,1)

s=s.replace('VERSION 62 • SÄKRARE MAPS-IMPORT','VERSION 63 • EXAKT MAPS-MÅL')
for n in range(1,63):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 63 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 63 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 63 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 62','versionCode 63').replace('versionName "62.0"','versionName "63.0"')
b.write_text(t,encoding='utf-8')
print('Version 63 applied: exact final Google Maps coordinate wins over text geocoding')
