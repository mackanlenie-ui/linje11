from pathlib import Path
import re

exec(Path('scripts/version75.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V76: completely remove the old "navigate to START" phase.
# The saved work route remains visible, but no route/ETA/turn guidance is
# calculated from the phone's current position until the driver is close to
# the saved route itself.
s=s.replace("phase=start?'start':'route'","phase='route'",1)
s=s.replace("lab.textContent='NAVIGERA TILL START';st.textContent='🟢 STARTPUNKT';","lab.textContent='ARBETSRUTT';st.textContent='Rutten är vald';",1)
s=s.replace("lab.textContent='KÖR TILL STARTPUNKT';st.textContent='Nästa: START';","lab.textContent='ARBETSRUTT';st.textContent='Rutten är vald';",1)

# Keep rerouting available after joining the route, but suppress approach
# routing while the phone is far away from the saved route.
s=s.replace("var gps=null,acc=null,lastGps=null,follow=true,phase='route',idx=0", "var gps=null,acc=null,lastGps=null,follow=true,phase='route',idx=0,joinedRoute=false", 1)

# When GPS comes close to the stored route, navigation becomes active.
watch_anchor="document.getElementById('gpsStatus').textContent='🔵 GPS hittad • ±'+Math.round(pos.coords.accuracy)+' m';"
if watch_anchor in s:
    s=s.replace(watch_anchor, watch_anchor+"var joinD=distanceFromPlan();if(joinD!=null&&joinD<300)joinedRoute=true;",1)
else:
    # Newer text variant.
    m=re.search(r"document\.getElementById\('gpsStatus'\)\.textContent=[^;]+;",s)
    if m:
        s=s[:m.end()]+"var joinD=distanceFromPlan();if(joinD!=null&&joinD<300)joinedRoute=true;"+s[m.end():]

# Block OSRM/current-position route calculations until joinedRoute is true.
# This is what removes the long blue approach line and 100+ km ETA to START.
s=s.replace("async function updateRoad(force){var t=target();", "async function updateRoad(force){var t=target();if(!joinedRoute){roadKm=null;roadSec=null;nextTurn=null;try{if(typeof roadLine!=='undefined'&&roadLine){map.removeLayer(roadLine);roadLine=null;}}catch(e){}info();return;}", 1)

# Also do not trigger off-route rerouting before the route has been joined.
s=s.replace("function checkOffRoute(){if(!lastGps||!preloadPts.length)return;", "function checkOffRoute(){if(!joinedRoute||!lastGps||!preloadPts.length)return;",1)

# Ensure the top card does not claim START navigation on initial display.
s=s.replace("<div id='label'>STARTAR NAVIGATION</div>","<div id='label'>ARBETSRUTT</div>",1)
s=s.replace("<span id='turn'>🧭 Beräknar vägen…</span>","<span id='turn'>Följ den markerade rutten</span>",1)

s=s.replace('VERSION 75 •','VERSION 76 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 75','versionCode 76').replace('versionName "75.0"','versionName "76.0"')
b.write_text(t,encoding='utf-8')
print('Version 76 applied: no approach navigation to START; navigation activates near saved route')
