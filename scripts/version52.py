from pathlib import Path

exec(Path('scripts/version51.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Keep a persistent blue full-route line visible underneath the GPS marker.
old="var line=L.polyline(pts,{color:'#607d8b',weight:6,opacity:.55}).addTo(map);"
new="var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.92}).addTo(map);"
if old in s:
    s=s.replace(old,new,1)
else:
    s=s.replace("var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);",new,1)

# Do not trim the active blue line away behind the car; retain the whole visible route.
s=s.replace("trimActiveTo(lastGps);var arrow=", "var arrow=", 1)

# When no explicit turn object is currently selected, show distance to the next
# planned real maneuver instead of only 'FÖLJ VÄGEN'.
old_fmt="function fmt(t){if(!t)return'⬆️ FÖLJ VÄGEN';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';if(t.roundabout){var ex=t.exit?(' • TA AVFART '+t.exit):'';return'🔄 OM '+d+' • RONDELL'+ex;}var tx=(t.text||'Fortsätt rakt fram').toUpperCase();return t.icon+' OM '+d+' • '+tx;}"
new_fmt="function fmt(t){if(!t){var p=plannedTurn();if(p&&p.d!=null){var pd=p.d<1000?Math.round(p.d)+' m':(p.d/1000).toFixed(1)+' km';return'⬆️ FÖLJ VÄGEN • '+pd;}return'⬆️ FÖLJ VÄGEN';}var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';if(t.roundabout){var ex=t.exit?(' • TA AVFART '+t.exit):'';return'🔄 OM '+d+' • RONDELL'+ex;}var tx=(t.text||'Fortsätt rakt fram').toUpperCase();return t.icon+' OM '+d+' • '+tx;}"
if old_fmt not in s:
    raise SystemExit('v52 fmt point not found')
s=s.replace(old_fmt,new_fmt,1)

# Ensure the route lines remain above map tiles after GPS updates, while the marker
# remains naturally above vector layers in Leaflet's marker pane.
needle="if(!gps)gps=L.marker(displayGps"
if needle in s:
    s=s.replace(needle,"line.bringToFront();activeCasing.bringToFront();activeLine.bringToFront();if(!gps)gps=L.marker(displayGps",1)

s=s.replace('VERSION 51 • TESTKNAPP FIXAD','VERSION 52 • BLÅ RUTT + MANÖVERAVSTÅND')
for n in range(1,52):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 52 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 52 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 52 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 51','versionCode 52').replace('versionName "51.0"','versionName "52.0"')
b.write_text(t,encoding='utf-8')
print('Version 52 applied: persistent blue route line and distance to next planned maneuver')
