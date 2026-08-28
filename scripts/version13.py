from pathlib import Path
exec(Path('scripts/version12.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 13: draw the work route along real drivable roads instead of straight
# lines between route coordinates. OSRM geometry is used for the blue route,
# with the recorded polyline kept as a safe fallback if routing is unavailable.
old="var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);map.fitBounds(line.getBounds(),{padding:[35,35]});var markers=[];"
new="var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);map.fitBounds(line.getBounds(),{padding:[35,35]});function routeWaypoints(){var a=[];if(start)a.push([start.lat,start.lon]);if(stops&&stops.length)stops.forEach(function(x){a.push([x.lat,x.lon]);});if(end)a.push([end.lat,end.lon]);if(a.length<2&&pts&&pts.length>=2){a=[pts[0],pts[pts.length-1]];}return a;}async function loadRoadLine(){var w=routeWaypoints();if(w.length<2)return;try{var coords=w.map(function(x){return x[1]+','+x[0];}).join(';');var u='https://router.project-osrm.org/route/v1/driving/'+coords+'?overview=full&geometries=geojson&steps=false';var r=await fetch(u);if(!r.ok)throw Error('route');var d=await r.json();if(!d.routes||!d.routes.length||!d.routes[0].geometry)throw Error('geometry');var roadPts=d.routes[0].geometry.coordinates.map(function(x){return[x[1],x[0]];});if(roadPts.length<2)throw Error('empty');line.setLatLngs(roadPts);document.getElementById('routeStatus').textContent='🛣️ Bilvägen visas ✓';if(!lastGps)map.fitBounds(line.getBounds(),{paddingTopLeft:[30,260],paddingBottomRight:[30,90]});}catch(e){document.getElementById('routeStatus').textContent='Arbetsrutten visas ✓';}}var markers=[];"
if old not in s:
    raise SystemExit('Version 13 route-line insertion point not found')
s=s.replace(old,new,1)

# Start road geometry loading only after all JS state has been declared, so it
# can safely check lastGps while the GPS watcher starts in parallel.
old2="navigator.geolocation.watchPosition(function(pos){lastGps=[pos.coords.latitude,pos.coords.longitude];"
new2="loadRoadLine();navigator.geolocation.watchPosition(function(pos){lastGps=[pos.coords.latitude,pos.coords.longitude];"
if old2 not in s:
    raise SystemExit('Version 13 GPS watcher insertion point not found')
s=s.replace(old2,new2,1)

s=s.replace('VERSION 12 • RUTTBIBLIOTEK','VERSION 13 • RUTTBIBLIOTEK').replace('VERSION 12 • \"+selectedDay.toUpperCase()','VERSION 13 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 12','versionCode 13').replace('versionName \"12.0\"','versionName \"13.0\"')
b.write_text(t,encoding='utf-8')
