from pathlib import Path
import re

# Version 44 builds on Version 43.
exec(Path('scripts/version43.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Prefer cached web resources/map tiles when connectivity disappears.
old_web = 's.setGeolocationEnabled(true);web.setWebViewClient(new WebViewClient());'
new_web = 's.setGeolocationEnabled(true);s.setCacheMode(WebSettings.LOAD_CACHE_ELSE_NETWORK);s.setDatabaseEnabled(true);web.setWebViewClient(new WebViewClient());'
if old_web not in s:
    raise SystemExit('v44 WebView cache point not found')
s = s.replace(old_web, new_web, 1)

# Keep more already-viewed OSM tiles around the driven route.
old_tiles = "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);"
new_tiles = "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap',keepBuffer:10,updateWhenIdle:true}).addTo(map);"
if old_tiles in s:
    s = s.replace(old_tiles, new_tiles, 1)

# Replace the old OSRM turn parser. The previous code used the length of the
# maneuver step itself as distance-to-turn. V44 accumulates the distance from
# the live GPS/depart step to the next real maneuver, which restores reliable
# left/right distance and arrows.
start = s.find('function turnText(rr){')
end = s.find('function fmt(t){', start)
if start < 0 or end < 0:
    raise SystemExit('v44 turnText point not found')
new_turn = r'''function turnText(rr){try{var ss=rr.legs[0].steps||[],walk=0;for(var i=0;i<ss.length;i++){var q=ss[i],type=((q.maneuver&&q.maneuver.type)||'').toLowerCase(),mod=((q.maneuver&&q.maneuver.modifier)||'').toLowerCase(),qd=Number(q.distance||0);if(type!=='depart'&&type!=='arrive'&&qd>=5){var icon='⬆️',txt='Fortsätt rakt fram',real=false;if(type.indexOf('roundabout')>=0||type.indexOf('rotary')>=0){icon='🔄';txt='Kör in i rondellen';if(q.maneuver&&q.maneuver.exit)txt+=' och ta avfart '+q.maneuver.exit;real=true;}else if(mod.indexOf('left')>=0){icon=mod.indexOf('slight')>=0?'↖️':'⬅️';txt=mod.indexOf('slight')>=0?'Håll svagt vänster':'Sväng vänster';real=true;}else if(mod.indexOf('right')>=0){icon=mod.indexOf('slight')>=0?'↗️':'➡️';txt=mod.indexOf('slight')>=0?'Håll svagt höger':'Sväng höger';real=true;}else if(mod.indexOf('straight')>=0){real=true;}if(real){if(q.name)txt+=' mot '+q.name;return{icon:icon,text:txt,d:Math.max(0,walk),key:type+'|'+mod+'|'+q.name};}}walk+=qd;}}catch(e){}return null;}'''
s = s[:start] + new_turn + s[end:]

# Offline maneuver engine. Uses the already stored route geometry (or the most
# recently downloaded active road geometry) and GPS only, so basic left/right
# guidance continues even when OSRM cannot be reached.
anchor = 'function nearestActive(p){'
if anchor not in s:
    raise SystemExit('v44 offline helper point not found')
offline_helpers = r'''function bearing(a,b){var y=Math.sin((b[1]-a[1])*Math.PI/180)*Math.cos(b[0]*Math.PI/180),x=Math.cos(a[0]*Math.PI/180)*Math.sin(b[0]*Math.PI/180)-Math.sin(a[0]*Math.PI/180)*Math.cos(b[0]*Math.PI/180)*Math.cos((b[1]-a[1])*Math.PI/180);return(Math.atan2(y,x)*180/Math.PI+360)%360;}function turnDelta(a,b){return((b-a+540)%360)-180;}function offlineTurn(){try{var a=(activePts&&activePts.length>18)?activePts:pts;if(!lastGps||!a||a.length<18)return null;var bi=0,bd=1e12;for(var i=0;i<a.length;i+=Math.max(1,Math.floor(a.length/300))){var dd=km(lastGps,a[i])*1000;if(dd<bd){bd=dd;bi=i;}}var lo=Math.max(0,bi-5),hi=Math.min(a.length-1,bi+8);for(var z=lo;z<=hi;z++){var dz=km(lastGps,a[z])*1000;if(dz<bd){bd=dz;bi=z;}}var dist=0,last=a[bi];for(var j=bi+1;j<a.length-7;j++){dist+=km(last,a[j])*1000;last=a[j];if(dist<35)continue;if(dist>1800)break;var back=Math.max(bi,j-5),fwd=Math.min(a.length-1,j+6);if(back===j||fwd===j)continue;var d=turnDelta(bearing(a[back],a[j]),bearing(a[j],a[fwd]));if(Math.abs(d)>=38){var right=d>0;return{icon:right?'➡️':'⬅️',text:right?'Sväng höger':'Sväng vänster',d:dist,key:'offline|'+j+'|'+(right?'R':'L'),offline:true};}}return null;}catch(e){return null;}}'''
s = s.replace(anchor, offline_helpers + anchor, 1)

# When the online router fails, preserve navigation and calculate the next
# maneuver from local geometry instead of blanking the turn instruction.
old_catch = '}catch(e){roadKm=null;roadSec=null;nextTurn=null;activePts=[];activeCasing.setLatLngs([]);activeLine.setLatLngs([]);}info();}'
new_catch = "}catch(e){var ot=target();roadKm=(lastGps&&ot)?km(lastGps,[ot.navLat!=null?ot.navLat:ot.lat,ot.navLon!=null?ot.navLon:ot.lon]):null;roadSec=null;nextTurn=offlineTurn();var rs=document.getElementById('routeStatus');if(rs)rs.textContent='📴 Offline • sparad rutt + GPS';}info();}"
if old_catch not in s:
    raise SystemExit('v44 updateRoad catch point not found')
s = s.replace(old_catch, new_catch, 1)

# Show local guidance immediately while an online refresh is pending.
old_watch = 'arrived();updateRoad(false);},function(){document.getElementById(\'gpsStatus\').textContent=\'GPS kunde inte hämtas\';}'
new_watch = "arrived();if(!nextTurn)nextTurn=offlineTurn();info();updateRoad(false);},function(){document.getElementById('gpsStatus').textContent='GPS kunde inte hämtas';}"
if old_watch not in s:
    raise SystemExit('v44 GPS watch point not found')
s = s.replace(old_watch, new_watch, 1)

# Connectivity indicator. GPS and local route logic keep running offline.
old_tail = 'info();</script></body></html>";'
new_tail = "window.addEventListener('offline',function(){var r=document.getElementById('routeStatus');if(r)r.textContent='📴 Offline • sparad rutt + GPS';nextTurn=offlineTurn()||nextTurn;info();});window.addEventListener('online',function(){var r=document.getElementById('routeStatus');if(r)r.textContent='📶 Online • uppdaterar väg';updateRoad(true);});if(!navigator.onLine){var r0=document.getElementById('routeStatus');if(r0)r0.textContent='📴 Offline • sparad rutt + GPS';}info();</script></body></html>\";"
if old_tail not in s:
    raise SystemExit('v44 connectivity tail point not found')
s = s.replace(old_tail, new_tail, 1)

s = s.replace('VERSION 43 • TRYGGARE NAVIGATION', 'VERSION 44 • OFFLINE + SVÄNGAR')
s = s.replace('VERSION 43 • "+selectedDay.toUpperCase()', 'VERSION 44 • "+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 43', 'versionCode 44').replace('versionName "43.0"', 'versionName "44.0"')
b.write_text(t, encoding='utf-8')

print('Version 44 applied: cached map resources, offline GPS/route fallback and restored left/right turn guidance')
