from pathlib import Path

exec(Path('scripts/version59.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Smooth rerouting: route replacement must not fight the GPS camera/marker.
# Freeze automatic zoom briefly while a replacement route is being installed.
old="var lastSmartZoom=0,smartZoomLevel=null,turnZoomHold=false;function smartManeuverZoom(){try{if(!follow||!map||!lastGps)return;"
new="var lastSmartZoom=0,smartZoomLevel=null,turnZoomHold=false,rerouteCameraHoldUntil=0;function smartManeuverZoom(){try{if(!follow||!map||!lastGps||Date.now()<rerouteCameraHoldUntil)return;"
if old not in s: raise SystemExit('v60 smart zoom anchor not found')
s=s.replace(old,new,1)

# When off-route rerouting begins, hold camera zoom until the new line has settled.
old2="rerouteNotice=Date.now();nextTurn=null;updateRoad(true);"
new2="rerouteNotice=Date.now();rerouteCameraHoldUntil=Date.now()+8000;nextTurn=null;updateRoad(true);"
if old2 not in s: raise SystemExit('v60 reroute start anchor not found')
s=s.replace(old2,new2,1)

# After a fresh route arrives, keep the GPS marker/camera position authoritative and
# prevent route geometry changes from immediately causing another zoom transition.
old3="if(offHits>=2){offHits=0;var rrs=document.getElementById('routeStatus');if(rrs)rrs.textContent='✅ NY RUTT KLAR';}"
new3="if(offHits>=2){offHits=0;rerouteCameraHoldUntil=Date.now()+6000;smartZoomLevel=map.getZoom();var rrs=document.getElementById('routeStatus');if(rrs)rrs.textContent='✅ NY RUTT KLAR';}"
if old3 not in s: raise SystemExit('v60 reroute success anchor not found')
s=s.replace(old3,new3,1)

s=s.replace('VERSION 59 • REN KOMPAKT VY','VERSION 60 • MJUK OMDIRIGERING')
for n in range(1,60):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 60 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 60 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 60 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 59','versionCode 60').replace('versionName "59.0"','versionName "60.0"')
b.write_text(t,encoding='utf-8')
print('Version 60 applied: smooth rerouting with camera/zoom hold')
