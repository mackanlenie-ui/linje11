from pathlib import Path

exec(Path('scripts/version55.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# 1) Keep route progress monotonic so GPS jitter or parallel roads do not make an
# already-passed maneuver become the "next" maneuver again.
state_old="simTimer=null,simIndex=0,nearHits=0"
state_new="simTimer=null,simIndex=0,planProgressIdx=-1,nearHits=0"
if state_old not in s:
    raise SystemExit('v56 navigation state point not found')
s=s.replace(state_old,state_new,1)

old_plan="function plannedTurn(){try{if(!preloadPlan||!preloadPts.length||!lastGps)return null;var ci=nearestIdx(preloadPts,lastGps),turns=preloadPlan.turns||[];for(var k=0;k<turns.length;k++){var t=turns[k];if(t.i>ci+2){var d=distAlong(preloadPts,ci,t.i);if(d<15)continue;return{icon:t.icon,text:t.text+(t.name?' mot '+t.name:''),d:d,key:t.key,roundabout:!!t.roundabout,exit:t.exit,offline:true};}}return null;}catch(e){return null;}}"
new_plan="function plannedTurn(){try{if(!preloadPlan||!preloadPts.length||!lastGps)return null;var raw=nearestIdx(preloadPts,lastGps);if(raw<0)return null;if(planProgressIdx<0)planProgressIdx=raw;else if(raw>=planProgressIdx-3)planProgressIdx=Math.max(planProgressIdx,raw);var ci=planProgressIdx,turns=preloadPlan.turns||[];for(var k=0;k<turns.length;k++){var t=turns[k];if(t.i>ci+2){var d=distAlong(preloadPts,ci,t.i);if(d<12)continue;return{icon:t.icon,text:t.text+(t.name?' mot '+t.name:''),d:d,key:t.key,roundabout:!!t.roundabout,exit:t.exit,offline:true};}}return null;}catch(e){return null;}}"
if old_plan not in s:
    raise SystemExit('v56 plannedTurn point not found')
s=s.replace(old_plan,new_plan,1)

# Reset progress when a new offline plan is built, so a rerouted/new route starts cleanly.
s=s.replace("preloadPlan={pts:pp,turns:tt,ts:Date.now()};preloadPts=pp;savePlan();",
            "preloadPlan={pts:pp,turns:tt,ts:Date.now()};preloadPts=pp;planProgressIdx=-1;savePlan();",1)

# 2) Stronger distance-aware maneuver warning. Near the junction it says NU instead
# of continuing to show a small 'om X m' message.
old_fmt="function fmt(t){if(!t){var p=plannedTurn();if(p&&p.d!=null){var pd=p.d<1000?Math.round(p.d)+' m':(p.d/1000).toFixed(1)+' km';return'⬆️ FÖLJ VÄGEN • '+pd;}return'⬆️ FÖLJ VÄGEN';}var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';if(t.roundabout){var ex=t.exit?(' • TA AVFART '+t.exit):'';return'🔄 OM '+d+' • RONDELL'+ex;}var tx=(t.text||'Fortsätt rakt fram').toUpperCase();return t.icon+' OM '+d+' • '+tx;}"
new_fmt="function fmt(t){if(!t){var p=plannedTurn();if(p&&p.d!=null){var pd=p.d<1000?Math.round(p.d)+' m':(p.d/1000).toFixed(1)+' km';return'⬆️ FÖLJ VÄGEN • '+pd;}return'⬆️ FÖLJ VÄGEN';}var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km',near=t.d<=55;if(t.roundabout){var ex=t.exit?(' • TA AVFART '+t.exit):'';return near?'🔄 RONDELL NU'+ex:'🔄 OM '+d+' • RONDELL'+ex;}var tx=(t.text||'Fortsätt rakt fram').toUpperCase();return near?t.icon+' '+tx+' NU':t.icon+' OM '+d+' • '+tx;}"
if old_fmt not in s:
    raise SystemExit('v56 fmt point not found')
s=s.replace(old_fmt,new_fmt,1)

# 3) Automatic maneuver zoom. Long straight sections stay wider; upcoming turns zoom
# progressively closer. A small cooldown avoids camera twitching on every GPS fix.
anchor="function refreshMarkers(){"
zoom_helper="var lastSmartZoom=0;function smartManeuverZoom(){try{if(!follow||!map||!lastGps)return;var t=nextTurn||plannedTurn(),d=t&&t.d!=null?t.d:99999,z=d<=140?18:d<=450?17:d<=1200?16:15;if(Date.now()-lastSmartZoom<1200)return;lastSmartZoom=Date.now();if(Math.abs(map.getZoom()-z)>=1)map.setZoom(z,{animate:true});}catch(e){}}"
if anchor not in s:
    raise SystemExit('v56 zoom helper anchor not found')
s=s.replace(anchor,zoom_helper+anchor,1)

# Call smart zoom after the live navigation state has been refreshed.
old_live="checkOffRoute();refreshRemainingSummary();info();updateRoad(false);"
new_live="checkOffRoute();refreshRemainingSummary();info();smartManeuverZoom();updateRoad(false);"
if old_live not in s:
    raise SystemExit('v56 live GPS point not found')
s=s.replace(old_live,new_live,1)

old_native="checkOffRoute();refreshRemainingSummary();info();}catch(e){}}"
new_native="checkOffRoute();refreshRemainingSummary();info();smartManeuverZoom();}catch(e){}}"
if old_native in s:
    s=s.replace(old_native,new_native,1)

# Simulation/test mode should demonstrate the same behavior.
s=s.replace("checkOffRoute();refreshRemainingSummary();info();",
            "checkOffRoute();refreshRemainingSummary();info();smartManeuverZoom();",1)

s=s.replace('VERSION 55 • LIVE KM + ETA','VERSION 56 • SMARTA SVÄNGAR + ZOOM')
for n in range(1,56):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 56 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 56 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 56 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 55','versionCode 56').replace('versionName "55.0"','versionName "56.0"')
b.write_text(t,encoding='utf-8')
print('Version 56 applied: stronger near-turn warnings, smart maneuver zoom and monotonic passed-turn tracking')
