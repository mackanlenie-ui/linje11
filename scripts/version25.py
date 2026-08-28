from pathlib import Path
exec(Path('scripts/version24.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V25 keeps the now-proven V24/V16 navigation structure and only makes
# conservative, syntax-safe JavaScript substitutions.

# 1) Stronger stop states: next stop is red, completed stops get a green check.
s=s.replace(".next{border-color:#d32f2f;box-shadow:0 0 0 5px #d32f2f44}",
            ".next{border-color:#d32f2f;box-shadow:0 0 0 5px #d32f2f44}.done{background:#2e7d32;color:#fff;border-color:#fff}",1)
old_mk="function mkIcon(t,n){return L.divIcon({className:'',html:'<div class=\\\"pin '+(n?'next':'')+'\\\">'+t+'</div>',iconSize:[46,46],iconAnchor:[23,23]});}"
new_mk="function mkIcon(t,n,d){return L.divIcon({className:'',html:'<div class=\\\"pin '+(n?'next ':'')+(d?'done':'')+'\\\">'+(d?'✓':t)+'</div>',iconSize:[46,46],iconAnchor:[23,23]});}"
if old_mk not in s: raise SystemExit('v25 mkIcon point not found')
s=s.replace(old_mk,new_mk,1)
s=s.replace("icon:mkIcon(s.label,false)","icon:mkIcon(s.label,false,false)",1)
old_refresh="function refreshMarkers(){markers.forEach((m,i)=>m.setIcon(mkIcon(stops[i].label,phase==='route'&&i===idx)));}"
new_refresh="function refreshMarkers(){markers.forEach(function(m,i){m.setIcon(mkIcon(stops[i].label,phase==='route'&&i===idx,phase!=='start'&&i<idx));});}"
if old_refresh not in s: raise SystemExit('v25 refreshMarkers point not found')
s=s.replace(old_refresh,new_refresh,1)

# 2) Track speed and use a directional car arrow instead of only a blue dot.
old_state="lastSpoken='',lastHeading=null,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
new_state="lastSpoken='',lastHeading=null,lastSpeed=0,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
if old_state not in s: raise SystemExit('v25 state point not found')
s=s.replace(old_state,new_state,1)

old_gps="lastGps=[pos.coords.latitude,pos.coords.longitude];lastHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:lastHeading;"
new_gps="lastGps=[pos.coords.latitude,pos.coords.longitude];lastHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:lastHeading;lastSpeed=(pos.coords.speed||0)*3.6;"
if old_gps not in s: raise SystemExit('v25 gps update point not found')
s=s.replace(old_gps,new_gps,1)

old_marker="if(!gps)gps=L.marker(lastGps,{icon:L.divIcon({className:'',html:'<div class=\\\"gpsDot\\\"></div>',iconSize:[32,32],iconAnchor:[16,16]})}).addTo(map);else gps.setLatLng(lastGps);"
new_marker="var arrow='<div style=\\\"width:38px;height:38px;line-height:38px;text-align:center;font-size:31px;transform:rotate('+(lastHeading||0)+'deg);filter:drop-shadow(0 2px 2px #555)\\\">⬆️</div>';if(!gps)gps=L.marker(lastGps,{icon:L.divIcon({className:'',html:arrow,iconSize:[38,38],iconAnchor:[19,19]})}).addTo(map);else{gps.setLatLng(lastGps);gps.setIcon(L.divIcon({className:'',html:arrow,iconSize:[38,38],iconAnchor:[19,19]}));}"
if old_marker not in s: raise SystemExit('v25 gps marker point not found')
s=s.replace(old_marker,new_marker,1)

# 3) Smarter follow zoom. Accept either V15/V16 formatting variant.
zoom_variants=[
    "if(follow){var sp=(pos.coords.speed||0)*3.6;var z=sp>70?14:sp>35?15:16;map.setView(lastGps,z);}",
    "if(follow){var sp=(pos.coords.speed||0)*3.6;var z=sp>70?14:sp>35?15:16;map.setView(lastGps,z,{animate:true});}",
    "if(follow){var sp=(pos.coords.speed||0)*3.6;var z=sp>70?14:sp>35?15:17;map.setView(lastGps,z);}"
]
new_zoom="if(follow){var sp=lastSpeed;var z=sp>80?14:sp>45?15:16;map.setView(lastGps,z,{animate:true});}"
for zold in zoom_variants:
    if zold in s:
        s=s.replace(zold,new_zoom,1)
        break

# 4) More stable automatic arrival: close to the drivable point, low speed,
# and three consecutive GPS updates before advancing.
old_arr="if(d<45)nearHits++;else nearHits=0;if(nearHits<2)return;"
new_arr="if(d<40&&lastSpeed<18)nearHits++;else if(d>60||lastSpeed>25)nearHits=0;if(nearHits<3)return;"
if old_arr not in s: raise SystemExit('v25 arrival point not found')
s=s.replace(old_arr,new_arr,1)

# Make automatic rerouting visible. updateRoad already recalculates from the
# live GPS position every few seconds, so this labels the proven behavior.
s=s.replace("' • 🚗 Till infart ✓'","' • 🚗 Till infart ✓ • ↩ AUTO'",1)

s=s.replace('VERSION 24 • RUTTBIBLIOTEK','VERSION 25 • RUTTBIBLIOTEK').replace('VERSION 24 • \"+selectedDay.toUpperCase()','VERSION 25 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 24','versionCode 25').replace('versionName \"24.0\"','versionName \"25.0\"')
b.write_text(t,encoding='utf-8')
