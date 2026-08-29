from pathlib import Path

exec(Path('scripts/version57.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# 1) Remove the developer/test button completely from the driving UI.
test_button="<button id='testBtn' onclick='toggleTest()' style='position:absolute;z-index:9999;right:10px;bottom:112px;background:white;border:0;border-radius:12px;padding:8px 11px;font-size:13px;font-weight:bold;box-shadow:0 2px 8px #0004;color:#17365d'>🧪 Test</button>"
s=s.replace(test_button,'',1)

# 2) Compact the upper navigation card without sacrificing the important information.
# Use final CSS overrides so this remains robust against older inherited styles.
style_end='</style>'
compact_css="""#top{padding:8px 12px!important;border-radius:18px!important;line-height:1.08!important}#top h1,#top .title{margin:0 0 2px!important;line-height:1.05!important}#turn{font-size:25px!important;line-height:1.12!important;padding:6px 8px!important;margin-top:4px!important}#eta,#routeStatus,#gpsStatus{line-height:1.15!important;margin-top:2px!important}#top .label{margin-bottom:1px!important}"""
if style_end not in s: raise SystemExit('v58 style end not found')
s=s.replace(style_end,compact_css+style_end,1)

# 3) Stronger and clearer off-route handling. Two reliable fixes outside ~70 m trigger
# an immediate reroute, with a visible status until a fresh route has been received.
old_check="function checkOffRoute(){if(!lastGps||!preloadPts.length)return;var d=distanceFromPlan();if(d!=null&&d>80&&lastAccuracy<=45)offHits++;else offHits=Math.max(0,offHits-1);if(offHits>=2){var rs=document.getElementById('routeStatus');if(rs)rs.textContent='⚠️ Utanför rutten • räknar om…';if(navigator.onLine&&Date.now()-rerouteNotice>5000){rerouteNotice=Date.now();updateRoad(true);}}}"
new_check="function checkOffRoute(){if(!lastGps||!preloadPts.length)return;var d=distanceFromPlan();if(d!=null&&d>70&&lastAccuracy<=45)offHits++;else if(d!=null&&d<45)offHits=0;else offHits=Math.max(0,offHits-1);if(offHits>=2){var rs=document.getElementById('routeStatus');if(rs)rs.textContent=navigator.onLine?'⚠️ KÖR FEL • RÄKNAR OM RUTTEN…':'⚠️ UTANFÖR RUTTEN • OFFLINE';if(navigator.onLine&&Date.now()-rerouteNotice>3000){rerouteNotice=Date.now();nextTurn=null;updateRoad(true);}}}"
if old_check not in s: raise SystemExit('v58 checkOffRoute point not found')
s=s.replace(old_check,new_check,1)

# After OSRM has delivered a fresh route, clear deviation state and tell the driver
# that the replacement route is active. The usual info refresh will subsequently
# restore the normal route/offline status text.
road_update="roadKm=rr.distance/1000;roadSec=rr.duration;"
if road_update not in s: raise SystemExit('v58 route success point not found')
s=s.replace(road_update,road_update+"if(offHits>=2){offHits=0;var rrs=document.getElementById('routeStatus');if(rrs)rrs.textContent='✅ NY RUTT KLAR';}",1)

s=s.replace('VERSION 57 • STABIL ZOOM + KVAR-TID','VERSION 58 • OMDIRIGERING + KOMPAKT VY')
for n in range(1,58):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 58 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 58 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 58 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 57','versionCode 58').replace('versionName "57.0"','versionName "58.0"')
b.write_text(t,encoding='utf-8')
print('Version 58 applied: compact top card, test button removed and stronger automatic rerouting')
