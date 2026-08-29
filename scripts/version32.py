from pathlib import Path

# Build on the proven Version 31 navigation stack.
exec(Path('scripts/version31.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Smoother heading. Small compass changes are filtered more strongly so the
# arrow/map stay calm on straight roads while still following real turns.
if "smoothHeading=(smoothHeading+hd*.22+360)%360" not in s:
    raise SystemExit('v32 heading point not found')
s = s.replace("smoothHeading=(smoothHeading+hd*.22+360)%360",
              "smoothHeading=(smoothHeading+hd*.16+360)%360", 1)

# 2) Smooth the visual snapped GPS position. Raw lastGps is still kept for
# arrival checks and off-route detection, so safety logic is unaffected.
state_old = "lastHeading=null,smoothHeading=null,lastSpeed=0,activeCasing=L.polyline([],{color:'#fff',weight:13,opacity:.95}).addTo(map),activeLine=L.polyline([],{color:'#1976d2',weight:8,opacity:1}).addTo(map),activePts=[];"
state_new = "lastHeading=null,smoothHeading=null,lastSpeed=0,displayGps=null,lastAccuracy=999,activeCasing=L.polyline([],{color:'#fff',weight:13,opacity:.95}).addTo(map),activeLine=L.polyline([],{color:'#1976d2',weight:8,opacity:1}).addTo(map),activePts=[];"
if state_old not in s:
    raise SystemExit('v32 GPS state point not found')
s = s.replace(state_old, state_new, 1)

marker_old = "var displayGps=snapToActive(lastGps);trimActiveTo(lastGps);var arrow='<div style=\\\"width:46px;height:46px;line-height:46px;text-align:center;font-size:38px;transform:rotate('+(lastHeading||0)+'deg);filter:drop-shadow(0 2px 2px #555)\\\">⬆️</div>';"
marker_new = "lastAccuracy=pos.coords.accuracy||999;var snapGps=snapToActive(lastGps);if(displayGps==null)displayGps=snapGps;else{var blend=lastAccuracy>35?.20:(lastSpeed>45?.58:lastSpeed>12?.42:.28);displayGps=[displayGps[0]+(snapGps[0]-displayGps[0])*blend,displayGps[1]+(snapGps[1]-displayGps[1])*blend];}trimActiveTo(lastGps);var arrow='<div style=\\\"width:46px;height:46px;line-height:46px;text-align:center;font-size:38px;transform:rotate('+(lastHeading||0)+'deg);filter:drop-shadow(0 2px 2px #555)\\\">⬆️</div>';"
if marker_old not in s:
    raise SystemExit('v32 smoothed marker point not found')
s = s.replace(marker_old, marker_new, 1)

# 3) Clearer next-turn banner: put the distance first so it can be read faster
# at a glance while driving.
fmt_old = "function fmt(t){if(!t)return'⬆️ Följ vägen';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';return t.icon+' '+t.text+' om '+d;}"
fmt_new = "function fmt(t){if(!t)return'⬆️ Följ vägen';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';return t.icon+' OM '+d+' • '+t.text;}"
if fmt_old not in s:
    raise SystemExit('v32 turn format point not found')
s = s.replace(fmt_old, fmt_new, 1)

# 4) Next-stop distance and ETA together in the main status, plus a shorter ETA
# line underneath. OSRM distance/duration are already updated for the active leg.
status_old = "if(roadKm!=null)st.textContent+=' • 🚗 '+(roadKm<1?Math.round(roadKm*1000)+' m':roadKm.toFixed(1)+' km')+' bilväg';document.getElementById('turn').textContent=fmt(nextTurn);document.getElementById('eta').textContent=eta(roadSec);"
status_new = "if(roadKm!=null){var distTxt=(roadKm<1?Math.round(roadKm*1000)+' m':roadKm.toFixed(1)+' km');var minTxt=roadSec!=null?Math.max(1,Math.round(roadSec/60))+' min':'';st.textContent+=' • 🚗 '+distTxt+(minTxt?' • '+minTxt:'');}document.getElementById('turn').textContent=fmt(nextTurn);document.getElementById('eta').textContent=roadSec!=null?'⏱️ Till nästa stopp: '+Math.max(1,Math.round(roadSec/60))+' min':'';"
if status_old not in s:
    raise SystemExit('v32 next-stop status point not found')
s = s.replace(status_old, status_new, 1)

# 5) Smarter follow camera. Center from the smoothed/snapped visual position and
# look farther ahead on open roads, but shorten look-ahead near the next turn or stop.
s = s.replace("var center=lastGps;", "var center=(displayGps||lastGps);", 1)
lead_old = "var lead=(dn!=null&&dn<260)?.00085:(sp>80?.0058:sp>45?.0039:.0022);center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];"
lead_new = "var lead=(nextTurn&&nextTurn.d<220)?.0012:((dn!=null&&dn<260)?.0010:(sp>80?.0064:sp>45?.0045:.0027));var base=(displayGps||lastGps);center=[base[0]+Math.cos(rad)*lead,base[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(base[0]*Math.PI/180))];"
if lead_old not in s:
    raise SystemExit('v32 smart camera point not found')
s = s.replace(lead_old, lead_new, 1)

# Version labels.
s = s.replace('VERSION 31 • RUTTBIBLIOTEK', 'VERSION 32 • RUTTBIBLIOTEK')
s = s.replace('VERSION 31 • \\\"+selectedDay.toUpperCase()', 'VERSION 32 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 31', 'versionCode 32').replace('versionName "31.0"', 'versionName "32.0"')
b.write_text(t, encoding='utf-8')

print('Version 32 applied: clearer turns, next-stop distance/ETA, smoother GPS and smarter follow camera')
