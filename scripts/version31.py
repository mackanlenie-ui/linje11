from pathlib import Path

# Build on Version 30.
exec(Path('scripts/version30.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# Keep the current OSRM leg in memory. This lets us snap the vehicle to the
# driven road, trim the blue line behind the vehicle and detect real deviations.
state_old = "activeCasing=L.polyline([],{color:'#fff',weight:13,opacity:.95}).addTo(map),activeLine=L.polyline([],{color:'#1976d2',weight:8,opacity:1}).addTo(map);"
state_new = "activeCasing=L.polyline([],{color:'#fff',weight:13,opacity:.95}).addTo(map),activeLine=L.polyline([],{color:'#1976d2',weight:8,opacity:1}).addTo(map),activePts=[];"
if state_old not in s:
    raise SystemExit('v31 active route state point not found')
s = s.replace(state_old, state_new, 1)

geom_old = "var legPts=rr.geometry.coordinates.map(function(x){return[x[1],x[0]];});activeCasing.setLatLngs(legPts);activeLine.setLatLngs(legPts);activeCasing.bringToFront();activeLine.bringToFront();"
geom_new = "var legPts=rr.geometry.coordinates.map(function(x){return[x[1],x[0]];});activePts=legPts;activeCasing.setLatLngs(legPts);activeLine.setLatLngs(legPts);activeCasing.bringToFront();activeLine.bringToFront();"
if geom_old not in s:
    raise SystemExit('v31 active route geometry point not found')
s = s.replace(geom_old, geom_new, 1)

s = s.replace("activeCasing.setLatLngs([]);activeLine.setLatLngs([]);", "activePts=[];activeCasing.setLatLngs([]);activeLine.setLatLngs([]);", 1)

# Route helpers:
# - nearestActive(): closest OSRM geometry point to live GPS
# - snapToActive(): keep the vehicle arrow visually on the road when GPS drifts
# - isOffRoute(): only trigger rapid rerouting after a genuine deviation
# - trimActiveTo(): remove the already-driven part of the blue route continuously
helper = """function nearestActive(p){if(!p||!activePts||!activePts.length)return null;var bi=-1,bd=1e12;for(var i=0;i<activePts.length;i+=Math.max(1,Math.floor(activePts.length/220))){var d=km(p,activePts[i])*1000;if(d<bd){bd=d;bi=i;}}if(bi<0)return null;var from=Math.max(0,bi-4),to=Math.min(activePts.length-1,bi+4);for(var j=from;j<=to;j++){var d2=km(p,activePts[j])*1000;if(d2<bd){bd=d2;bi=j;}}return{idx:bi,d:bd,p:activePts[bi]};}function snapToActive(p){var n=nearestActive(p);return(n&&n.d<55)?n.p:p;}function isOffRoute(p){var n=nearestActive(p);return !!(n&&n.d>65);}function trimActiveTo(p){var n=nearestActive(p);if(!n||n.d>70||n.idx<=0)return;activePts=activePts.slice(n.idx);if(activePts.length){activePts[0]=n.p;}activeCasing.setLatLngs(activePts);activeLine.setLatLngs(activePts);activeCasing.bringToFront();activeLine.bringToFront();}"
anchor = "function refreshMarkers(){"
if anchor not in s:
    raise SystemExit('v31 helper insertion point not found')
s = s.replace(anchor, helper + anchor, 1)

# True deviation-aware cadence: relaxed updates while following the route,
# rapid recalculation when the GPS position is actually away from the active road.
if "Date.now()-lastRoad<2500" not in s:
    raise SystemExit('v31 reroute cadence point not found')
s = s.replace("Date.now()-lastRoad<2500", "Date.now()-lastRoad<(isOffRoute(lastGps)?1200:5500)", 1)

# Snap only the visual vehicle marker; retain raw lastGps for distance/arrival logic.
marker_old = "var arrow='<div style=\\\"width:46px;height:46px;line-height:46px;text-align:center;font-size:38px;transform:rotate('+(lastHeading||0)+'deg);filter:drop-shadow(0 2px 2px #555)\\\">⬆️</div>';if(!gps)gps=L.marker(lastGps,{icon:L.divIcon({className:'',html:arrow,iconSize:[46,46],iconAnchor:[23,23]})}).addTo(map);else{gps.setLatLng(lastGps);gps.setIcon(L.divIcon({className:'',html:arrow,iconSize:[46,46],iconAnchor:[23,23]}));}"
marker_new = "var displayGps=snapToActive(lastGps);trimActiveTo(lastGps);var arrow='<div style=\\\"width:46px;height:46px;line-height:46px;text-align:center;font-size:38px;transform:rotate('+(lastHeading||0)+'deg);filter:drop-shadow(0 2px 2px #555)\\\">⬆️</div>';if(!gps)gps=L.marker(displayGps,{icon:L.divIcon({className:'',html:arrow,iconSize:[46,46],iconAnchor:[23,23]})}).addTo(map);else{gps.setLatLng(displayGps);gps.setIcon(L.divIcon({className:'',html:arrow,iconSize:[46,46],iconAnchor:[23,23]}));}"
if marker_old not in s:
    raise SystemExit('v31 GPS marker point not found')
s = s.replace(marker_old, marker_new, 1)

# Improve the final approach to each stop. navLat/navLon remain authoritative,
# and the closer threshold reduces premature completion near parallel roads/driveways.
arrival_old = "if(d<34&&lastSpeed<15&&accNow<40)nearHits++;else if(d>55||lastSpeed>22||accNow>60)nearHits=0;if(nearHits<4)return;"
arrival_new = "var hasNav=(tgt&&tgt.navLat!=null&&tgt.navLon!=null);var arriveR=hasNav?28:34;if(d<arriveR&&lastSpeed<13&&accNow<38)nearHits++;else if(d>50||lastSpeed>20||accNow>58)nearHits=0;if(nearHits<4)return;"
if arrival_old not in s:
    raise SystemExit('v31 arrival point not found')
s = s.replace(arrival_old, arrival_new, 1)

# Version labels.
s = s.replace('VERSION 30 • RUTTBIBLIOTEK', 'VERSION 31 • RUTTBIBLIOTEK')
s = s.replace('VERSION 30 • \\\"+selectedDay.toUpperCase()', 'VERSION 31 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 30', 'versionCode 31').replace('versionName "30.0"', 'versionName "31.0"')
b.write_text(t, encoding='utf-8')

print('Version 31 applied: road snap, trimmed remaining route, deviation-aware reroute and tighter final approach')
