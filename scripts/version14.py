from pathlib import Path
exec(Path('scripts/version13.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 14: make every A/B/C... stop an explicit routing waypoint and make
# the active leg visually clearer. The complete road line remains visible,
# while a red overlay shows the current GPS -> next target leg.
old="var gps=null,acc=null,lastGps=null,follow=true,phase=start?'start':'route',idx=0,lastRoad=0,roadKm=null,roadSec=null,nextTurn=null,nearHits=0,lastSpoken='';"
new="var gps=null,acc=null,lastGps=null,follow=true,phase=start?'start':'route',idx=0,lastRoad=0,roadKm=null,roadSec=null,nextTurn=null,nearHits=0,lastSpoken='',activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
if old not in s: raise SystemExit('v14 state insertion point not found')
s=s.replace(old,new,1)

old2="async function road(a,b){var u='https://router.project-osrm.org/route/v1/driving/'+a[1]+','+a[0]+';'+b.lon+','+b.lat+'?overview=false&steps=true';var r=await fetch(u),d=await r.json();if(!d.routes||!d.routes.length)throw Error();return d.routes[0];}"
new2="async function road(a,b){var u='https://router.project-osrm.org/route/v1/driving/'+a[1]+','+a[0]+';'+b.lon+','+b.lat+'?overview=full&geometries=geojson&steps=true';var r=await fetch(u),d=await r.json();if(!d.routes||!d.routes.length)throw Error();return d.routes[0];}"
if old2 not in s: raise SystemExit('v14 road insertion point not found')
s=s.replace(old2,new2,1)

old3="roadKm=rr.distance/1000;roadSec=rr.duration;nextTurn=turnText(rr);"
new3="roadKm=rr.distance/1000;roadSec=rr.duration;nextTurn=turnText(rr);if(rr.geometry&&rr.geometry.coordinates){activeLine.setLatLngs(rr.geometry.coordinates.map(function(x){return[x[1],x[0]];}));}"
if old3 not in s: raise SystemExit('v14 active line insertion point not found')
s=s.replace(old3,new3,1)

old4="}catch(e){roadKm=null;roadSec=null;nextTurn=null;}info();}"
new4="}catch(e){roadKm=null;roadSec=null;nextTurn=null;activeLine.setLatLngs([]);}info();}"
if old4 not in s: raise SystemExit('v14 catch insertion point not found')
s=s.replace(old4,new4,1)

# Make waypoint purpose explicit in the route status.
s=s.replace("document.getElementById('routeStatus').textContent='🛣️ Bilvägen visas ✓';","document.getElementById('routeStatus').textContent='🛣️ Bilväg via alla stopp ✓';")
s=s.replace('VERSION 13 • RUTTBIBLIOTEK','VERSION 14 • RUTTBIBLIOTEK').replace('VERSION 13 • \"+selectedDay.toUpperCase()','VERSION 14 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 13','versionCode 14').replace('versionName \"13.0\"','versionName \"14.0\"')
b.write_text(t,encoding='utf-8')
