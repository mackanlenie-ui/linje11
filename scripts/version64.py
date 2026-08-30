from pathlib import Path

exec(Path('scripts/version63.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Keep Google's exact place coordinate for the visible marker, but use OSRM's
# snapped waypoint on the routable road network as the navigation coordinate.
# This makes the final blue driving line end at the usable vehicle approach
# instead of trying to navigate onto a field, footpath or non-routable POI point.
old='JSONArray rs=os.optJSONArray("routes");if(rs==null||rs.length()==0)throw new Exception("Kunde inte beräkna bilvägen.");JSONArray c=rs.getJSONObject(0).getJSONObject("geometry").getJSONArray("coordinates");JSONObject r=new JSONObject();'
new='JSONArray rs=os.optJSONArray("routes");if(rs==null||rs.length()==0)throw new Exception("Kunde inte beräkna bilvägen.");JSONArray snap=os.optJSONArray("waypoints");JSONArray c=rs.getJSONObject(0).getJSONObject("geometry").getJSONArray("coordinates");JSONObject r=new JSONObject();'
if old not in s: raise SystemExit('v64 OSRM response anchor not found')
s=s.replace(old,new,1)

old_start='st.put("lat",a.lat);st.put("lon",a.lon);st.put("navLat",a.lat);st.put("navLon",a.lon);st.put("label","START");st.put("name",a.name);r.put("start",st);'
new_start='st.put("lat",a.lat);st.put("lon",a.lon);double sna=a.lat,sno=a.lon;if(snap!=null&&snap.length()>0){JSONArray sl=snap.getJSONObject(0).optJSONArray("location");if(sl!=null&&sl.length()>=2){sno=sl.getDouble(0);sna=sl.getDouble(1);}}st.put("navLat",sna);st.put("navLon",sno);st.put("label","START");st.put("name",a.name);r.put("start",st);'
if old_start not in s: raise SystemExit('v64 start nav anchor not found')
s=s.replace(old_start,new_start,1)

old_end='en.put("lat",z.lat);en.put("lon",z.lon);en.put("navLat",z.lat);en.put("navLon",z.lon);en.put("label","SLUT");en.put("name",z.name);r.put("end",en);'
new_end='en.put("lat",z.lat);en.put("lon",z.lon);double ena=z.lat,eno=z.lon;if(snap!=null&&snap.length()>=w.size()){JSONArray el=snap.getJSONObject(w.size()-1).optJSONArray("location");if(el!=null&&el.length()>=2){eno=el.getDouble(0);ena=el.getDouble(1);}}en.put("navLat",ena);en.put("navLon",eno);en.put("label","SLUT");en.put("name",z.name);r.put("end",en);'
if old_end not in s: raise SystemExit('v64 end nav anchor not found')
s=s.replace(old_end,new_end,1)

old_stop='o.put("lat",p.lat);o.put("lon",p.lon);o.put("label",String.valueOf((char)(\'A\'+Math.min(i-1,25))));o.put("name",p.name);stops.put(o);'
new_stop='o.put("lat",p.lat);o.put("lon",p.lon);double nlat=p.lat,nlon=p.lon;if(snap!=null&&snap.length()>i){JSONArray ml=snap.getJSONObject(i).optJSONArray("location");if(ml!=null&&ml.length()>=2){nlon=ml.getDouble(0);nlat=ml.getDouble(1);}}o.put("navLat",nlat);o.put("navLon",nlon);o.put("label",String.valueOf((char)(\'A\'+Math.min(i-1,25))));o.put("name",p.name);stops.put(o);'
if old_stop not in s: raise SystemExit('v64 stop nav anchor not found')
s=s.replace(old_stop,new_stop,1)

s=s.replace('VERSION 63 • EXAKT MAPS-MÅL','VERSION 64 • KÖRBAR INFART')
for n in range(1,64):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 64 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 64 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 64 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 63','versionCode 64').replace('versionName "63.0"','versionName "64.0"')
b.write_text(t,encoding='utf-8')
print('Version 64 applied: exact place markers with OSRM-snapped driveable navigation entrances')
