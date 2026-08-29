from pathlib import Path

exec(Path('scripts/version60.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# True off-route rerouting from the CURRENT GPS position to the current target.
anchor="function checkOffRoute(){"
helper=r'''async function forceRerouteFromGps(){try{if(!lastGps||!navigator.onLine)return false;var tgt=(phase==='start'?start:(idx<stops.length?stops[idx]:end));if(!tgt)return false;var tla=(tgt.navLat!=null?tgt.navLat:tgt.lat),tlo=(tgt.navLon!=null?tgt.navLon:tgt.lon);if(tla==null||tlo==null)return false;var rs=document.getElementById('routeStatus');if(rs)rs.textContent='⚠️ KÖR FEL • RÄKNAR OM RUTTEN…';rerouteCameraHoldUntil=Date.now()+9000;var u='https://router.project-osrm.org/route/v1/driving/'+lastGps[1]+','+lastGps[0]+';'+tlo+','+tla+'?overview=full&geometries=geojson&steps=true';var r=await fetch(u);var d=await r.json();if(!d.routes||!d.routes.length||!d.routes[0].geometry||!d.routes[0].geometry.coordinates||d.routes[0].geometry.coordinates.length<2){if(rs)rs.textContent='⚠️ KUNDE INTE RÄKNA OM RUTTEN';return false;}var rr=d.routes[0],legPts=rr.geometry.coordinates.map(function(x){return[x[1],x[0]];});activePts=legPts;activeCasing.setLatLngs(legPts);activeLine.setLatLngs(legPts);activeCasing.bringToFront();activeLine.bringToFront();roadKm=rr.distance/1000;roadSec=rr.duration;nextTurn=turnText(rr);if(nextTurn)lastGoodTurn=nextTurn;buildPlan(rr);offHits=0;rerouteNotice=Date.now();smartZoomLevel=map.getZoom();rerouteCameraHoldUntil=Date.now()+6000;if(rs)rs.textContent='✅ NY RUTT KLAR';info();ensureRemainingVisible();return true;}catch(e){var rs2=document.getElementById('routeStatus');if(rs2)rs2.textContent='⚠️ OMDIRIGERING MISSLYCKADES';return false;}}'''
if anchor not in s: raise SystemExit('v61 checkOffRoute anchor not found')
s=s.replace(anchor,helper+anchor,1)

# Make off-route detection call the dedicated GPS->target rerouter, not generic updateRoad().
old="if(navigator.onLine&&Date.now()-rerouteNotice>3000){rerouteNotice=Date.now();rerouteCameraHoldUntil=Date.now()+8000;nextTurn=null;updateRoad(true);}}}"
new="if(navigator.onLine&&Date.now()-rerouteNotice>3000){rerouteNotice=Date.now();rerouteCameraHoldUntil=Date.now()+8000;nextTurn=null;forceRerouteFromGps();}}}"
if old not in s: raise SystemExit('v61 off-route call point not found')
s=s.replace(old,new,1)

# Generic periodic updateRoad must no longer claim a successful reroute. Only the
# dedicated forceRerouteFromGps() function may show NY RUTT KLAR.
old_success="if(offHits>=2){offHits=0;rerouteCameraHoldUntil=Date.now()+6000;smartZoomLevel=map.getZoom();var rrs=document.getElementById('routeStatus');if(rrs)rrs.textContent='✅ NY RUTT KLAR';}"
if old_success in s:
    s=s.replace(old_success,"",1)

s=s.replace('VERSION 60 • MJUK OMDIRIGERING','VERSION 61 • RIKTIG GPS-OMDIRIGERING')
for n in range(1,61):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 61 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 61 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 61 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 60','versionCode 61').replace('versionName "60.0"','versionName "61.0"')
b.write_text(t,encoding='utf-8')
print('Version 61 applied: dedicated OSRM reroute from live GPS to current target')
