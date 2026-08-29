from pathlib import Path

exec(Path('scripts/version54.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Recalculate the remaining road distance along the CURRENT active route geometry
# from the nearest point to the GPS position. Keep an OSRM-derived seconds/km
# factor so ETA falls together with the remaining distance without a network call.
anchor="function refreshMarkers(){"
helper="function refreshRemainingSummary(){try{if(!lastGps||!activePts||activePts.length<2)return;var n=nearestActive(lastGps);if(!n||n.idx<0)return;var rem=km(lastGps,activePts[n.idx]);for(var i=n.idx;i<activePts.length-1;i++)rem+=km(activePts[i],activePts[i+1]);var secPerKm=(roadKm!=null&&roadKm>.05&&roadSec!=null&&roadSec>0)?roadSec/roadKm:null;roadKm=rem;if(secPerKm!=null&&isFinite(secPerKm))roadSec=Math.max(1,rem*secPerKm);}catch(e){}}"
if helper not in s:
    if anchor not in s: raise SystemExit('v55 helper anchor not found')
    s=s.replace(anchor,helper+anchor,1)

# Standard foreground GPS callback from V53/V54.
old="checkOffRoute();info();updateRoad(false);"
new="checkOffRoute();refreshRemainingSummary();info();updateRoad(false);"
if old not in s: raise SystemExit('v55 foreground summary point not found')
s=s.replace(old,new,1)

# Native foreground-service location bridge from V54.
old_native="checkOffRoute();info();}catch(e){}}"
new_native="checkOffRoute();refreshRemainingSummary();info();}catch(e){}}"
if old_native in s:
    s=s.replace(old_native,new_native,1)

# Test/simulation mode also gets live distance + ETA so it can be verified safely.
old_sim="checkOffRoute();info();"
if old_sim in s:
    s=s.replace(old_sim,"checkOffRoute();refreshRemainingSummary();info();",1)

s=s.replace('VERSION 54 • BAKGRUNDSNAVIGATION','VERSION 55 • LIVE KM + ETA')
for n in range(1,55):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 55 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 55 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 55 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 54','versionCode 55').replace('versionName "54.0"','versionName "55.0"')
b.write_text(t,encoding='utf-8')
print('Version 55 applied: live remaining road distance and ETA from current GPS position')
