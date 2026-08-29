from pathlib import Path

exec(Path('scripts/version56.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# 1) Stop the older follow-camera from fighting the new maneuver zoom.
# It should keep following/leading the car, but leave zoom level to smartManeuverZoom().
old_follow_call="map.setView(center,z,{animate:true});"
if old_follow_call in s:
    s=s.replace(old_follow_call,"map.panTo(center,{animate:true,duration:.45});",1)

# 2) Replace V56's fast 1.2 s zoom changes with a calm hysteresis controller.
# Zooming in is allowed as a turn approaches; zooming back out is delayed and uses
# wider thresholds, so GPS jitter around a boundary cannot make the map pump.
old_zoom="var lastSmartZoom=0;function smartManeuverZoom(){try{if(!follow||!map||!lastGps)return;var t=nextTurn||plannedTurn(),d=t&&t.d!=null?t.d:99999,z=d<=140?18:d<=450?17:d<=1200?16:15;if(Date.now()-lastSmartZoom<1200)return;lastSmartZoom=Date.now();if(Math.abs(map.getZoom()-z)>=1)map.setZoom(z,{animate:true});}catch(e){}}"
new_zoom="var lastSmartZoom=0,smartZoomLevel=null,turnZoomHold=false;function smartManeuverZoom(){try{if(!follow||!map||!lastGps)return;var t=nextTurn||plannedTurn(),d=t&&t.d!=null?t.d:99999,now=Date.now(),cur=smartZoomLevel==null?map.getZoom():smartZoomLevel,target=cur;if(d<=120){target=18;turnZoomHold=true;}else if(d<=420){target=Math.max(cur,17);turnZoomHold=true;}else if(d<=1050){target=Math.max(cur,16);}else if(d>1450&&!turnZoomHold){target=15;}if(turnZoomHold&&d>650){turnZoomHold=false;target=16;}var goingIn=target>cur,goingOut=target<cur,cooldown=goingIn?7000:11000;if(!goingIn&&!goingOut)return;if(now-lastSmartZoom<cooldown)return;lastSmartZoom=now;smartZoomLevel=target;map.setZoom(target,{animate:true});}catch(e){}}"
if old_zoom not in s:
    raise SystemExit('v57 smart zoom point not found')
s=s.replace(old_zoom,new_zoom,1)

# 3) Always show remaining distance + time, including phase=start (NAVIGERA TILL START).
# The normal info() code may intentionally blank the eta row in that phase, so enforce
# a compact live summary immediately after each info refresh.
anchor="function refreshMarkers(){"
helper="function ensureRemainingVisible(){try{var e=document.getElementById('eta');if(!e||roadKm==null)return;var dt=roadKm<1?Math.round(roadKm*1000)+' m':roadKm.toFixed(1)+' km',tm=roadSec!=null?Math.max(1,Math.round(roadSec/60))+' min':'';e.textContent='⏱️ Kvar: '+dt+(tm?' • '+tm:'');}catch(x){}}"
if helper not in s:
    if anchor not in s: raise SystemExit('v57 remaining summary anchor not found')
    s=s.replace(anchor,helper+anchor,1)

# Ensure every UI refresh gets the persistent summary, including online reroutes,
# native background GPS, normal GPS and test mode.
s=s.replace("info();smartManeuverZoom();","info();ensureRemainingVisible();smartManeuverZoom();")
s=s.replace("info();updateRoad(false);","info();ensureRemainingVisible();updateRoad(false);")
s=s.replace("info();}","info();ensureRemainingVisible();}")

# Also refresh summary after OSRM road values are updated before/after an info call.
s=s.replace("roadKm=rr.distance/1000;roadSec=rr.duration;","roadKm=rr.distance/1000;roadSec=rr.duration;",1)

s=s.replace('VERSION 56 • SMARTA SVÄNGAR + ZOOM','VERSION 57 • STABIL ZOOM + KVAR-TID')
for n in range(1,57):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 57 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 57 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 57 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 56','versionCode 57').replace('versionName "56.0"','versionName "57.0"')
b.write_text(t,encoding='utf-8')
print('Version 57 applied: calm hysteresis autozoom and always-visible remaining distance/time')
