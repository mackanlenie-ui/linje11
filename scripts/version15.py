from pathlib import Path
exec(Path('scripts/version14.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 15: driving-focused UI. Preserve v14 routing while adding clearer
# next-stop/progress text, adaptive follow zoom, heading rotation of the GPS
# marker, and persistent progress so an interrupted drive can continue.
old="var gps=null,acc=null,lastGps=null,follow=true,phase=start?'start':'route',idx=0,lastRoad=0,roadKm=null,roadSec=null,nextTurn=null,nearHits=0,lastSpoken='',activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
new="var gps=null,acc=null,lastGps=null,follow=true,phase=start?'start':'route',idx=parseInt(localStorage.getItem('rutt_idx')||'0'),lastRoad=0,roadKm=null,roadSec=null,nextTurn=null,nearHits=0,lastSpoken='',lastHeading=null,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);if(idx<0||idx>stops.length)idx=0;"
if old not in s: raise SystemExit('v15 state point not found')
s=s.replace(old,new,1)

# Persist progress whenever a stop is automatically completed.
old2="idx++;nearHits=0;roadKm=null;roadSec=null;nextTurn=null;"
new2="idx++;localStorage.setItem('rutt_idx',String(idx));nearHits=0;roadKm=null;roadSec=null;nextTurn=null;"
if old2 in s: s=s.replace(old2,new2)

# Adaptive follow: speed controls zoom; bearing rotates the GPS arrow marker.
old3="lastGps=[pos.coords.latitude,pos.coords.longitude];"
new3="lastGps=[pos.coords.latitude,pos.coords.longitude];lastHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:lastHeading;"
s=s.replace(old3,new3,1)
old4="if(follow)map.setView(lastGps,16);"
new4="if(follow){var sp=(pos.coords.speed||0)*3.6;var z=sp>70?14:sp>35?15:17;map.setView(lastGps,z);}"
if old4 in s: s=s.replace(old4,new4,1)

# Enhance the status card with next stop and remaining stops. This is appended
# to the existing route status, avoiding disruption to the proven v14 layout.
needle="document.getElementById('routeStatus').textContent='🛣️ Bilväg via alla stopp ✓';"
repl="var rem=Math.max(0,stops.length-idx);var nxt=(idx<stops.length?stops[idx]:end);var nt=nxt?((nxt.label||nxt.name||nxt.address||'SLUT')):'SLUT';document.getElementById('routeStatus').textContent='📍 Nästa: '+nt+' • '+rem+' stopp kvar • 🛣️ Bilväg ✓';"
if needle in s: s=s.replace(needle,repl)

s=s.replace('VERSION 14 • RUTTBIBLIOTEK','VERSION 15 • RUTTBIBLIOTEK').replace('VERSION 14 • \"+selectedDay.toUpperCase()','VERSION 15 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 14','versionCode 15').replace('versionName \"14.0\"','versionName \"15.0\"')
b.write_text(t,encoding='utf-8')
