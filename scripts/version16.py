from pathlib import Path
exec(Path('scripts/version15.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 16: keep the true address marker, but use OSRM's snapped driveable
# waypoint for navigation/arrival. Draw a short dashed connector between the
# driveable point and the address when they differ, so entrances are clear.
old="var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);map.fitBounds(line.getBounds(),{padding:[35,35]});function routeWaypoints(){var a=[];if(start)a.push([start.lat,start.lon]);if(stops&&stops.length)stops.forEach(function(x){a.push([x.lat,x.lon]);});if(end)a.push([end.lat,end.lon]);if(a.length<2&&pts&&pts.length>=2){a=[pts[0],pts[pts.length-1]];}return a;}async function loadRoadLine(){var w=routeWaypoints();if(w.length<2)return;try{var coords=w.map(function(x){return x[1]+','+x[0];}).join(';');var u='https://router.project-osrm.org/route/v1/driving/'+coords+'?overview=full&geometries=geojson&steps=false';var r=await fetch(u);if(!r.ok)throw Error('route');var d=await r.json();if(!d.routes||!d.routes.length||!d.routes[0].geometry)throw Error('geometry');var roadPts=d.routes[0].geometry.coordinates.map(function(x){return[x[1],x[0]];});if(roadPts.length<2)throw Error('empty');line.setLatLngs(roadPts);"
new="var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);var entranceLines=[];map.fitBounds(line.getBounds(),{padding:[35,35]});function routeObjects(){var a=[];if(start)a.push(start);if(stops&&stops.length)stops.forEach(function(x){a.push(x);});if(end)a.push(end);return a;}function routeWaypoints(){var objs=routeObjects(),a=objs.map(function(x){return[x.lat,x.lon];});if(a.length<2&&pts&&pts.length>=2){a=[pts[0],pts[pts.length-1]];}return a;}function clearEntranceLines(){entranceLines.forEach(function(x){map.removeLayer(x);});entranceLines=[];}function setNavWaypoints(d){clearEntranceLines();var objs=routeObjects();if(!d.waypoints||d.waypoints.length!==objs.length)return;d.waypoints.forEach(function(w,i){if(!w.location)return;var o=objs[i],navLat=w.location[1],navLon=w.location[0];o.navLat=navLat;o.navLon=navLon;var dist=km([o.lat,o.lon],[navLat,navLon])*1000;if(dist>6){entranceLines.push(L.polyline([[navLat,navLon],[o.lat,o.lon]],{color:'#555',weight:4,opacity:.8,dashArray:'7,7'}).addTo(map));}});}async function loadRoadLine(){var w=routeWaypoints();if(w.length<2)return;try{var coords=w.map(function(x){return x[1]+','+x[0];}).join(';');var u='https://router.project-osrm.org/route/v1/driving/'+coords+'?overview=full&geometries=geojson&steps=false';var r=await fetch(u);if(!r.ok)throw Error('route');var d=await r.json();if(!d.routes||!d.routes.length||!d.routes[0].geometry)throw Error('geometry');setNavWaypoints(d);var roadPts=d.routes[0].geometry.coordinates.map(function(x){return[x[1],x[0]];});if(roadPts.length<2)throw Error('empty');line.setLatLngs(roadPts);"
if old not in s: raise SystemExit('v16 road-line point not found')
s=s.replace(old,new,1)

# Navigation calls use the driveable waypoint once it is known.
old2="async function road(a,b){var u='https://router.project-osrm.org/route/v1/driving/'+a[1]+','+a[0]+';'+b.lon+','+b.lat+'?overview=full&geometries=geojson&steps=true';"
new2="async function road(a,b){var blon=(b.navLon!=null?b.navLon:b.lon),blat=(b.navLat!=null?b.navLat:b.lat);var u='https://router.project-osrm.org/route/v1/driving/'+a[1]+','+a[0]+';'+blon+','+blat+'?overview=full&geometries=geojson&steps=true';"
if old2 not in s: raise SystemExit('v16 road target point not found')
s=s.replace(old2,new2,1)

# Arrival is measured against the snapped driveable point, not the house pin.
old3="var d=km(lastGps,[t.lat,t.lon])*1000;"
new3="var d=km(lastGps,[t.navLat!=null?t.navLat:t.lat,t.navLon!=null?t.navLon:t.lon])*1000;"
if old3 not in s: raise SystemExit('v16 arrival point not found')
s=s.replace(old3,new3,1)

# Slightly less aggressive low-speed zoom than Version 15.
s=s.replace("var z=sp>70?14:sp>35?15:17;","var z=sp>70?14:sp>35?15:16;")

# Explain the entrance-aware behavior in the status card.
s=s.replace("' • 🛣️ Bilväg ✓'","' • 🚗 Till infart ✓'")

s=s.replace('VERSION 15 • RUTTBIBLIOTEK','VERSION 16 • RUTTBIBLIOTEK').replace('VERSION 15 • \"+selectedDay.toUpperCase()','VERSION 16 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 15','versionCode 16').replace('versionName \"15.0\"','versionName \"16.0\"')
b.write_text(t,encoding='utf-8')
