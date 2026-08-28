from pathlib import Path

# Build on the proven Version 28 navigation stack.
exec(Path('scripts/version28.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Make the active GPS -> next target leg unmistakable: a thick white casing
# underneath a strong blue road line. Keep it above the base route.
old_active = "activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
new_active = "activeCasing=L.polyline([],{color:'#fff',weight:13,opacity:.95}).addTo(map),activeLine=L.polyline([],{color:'#1976d2',weight:8,opacity:1}).addTo(map);"
if old_active not in s:
    raise SystemExit('v29 active line state point not found')
s = s.replace(old_active, new_active, 1)

# Whenever OSRM returns a new current-leg geometry, update both casing and blue line.
old_geom = "if(rr.geometry&&rr.geometry.coordinates){activeLine.setLatLngs(rr.geometry.coordinates.map(function(x){return[x[1],x[0]];}));}"
new_geom = "if(rr.geometry&&rr.geometry.coordinates){var legPts=rr.geometry.coordinates.map(function(x){return[x[1],x[0]];});activeCasing.setLatLngs(legPts);activeLine.setLatLngs(legPts);activeCasing.bringToFront();activeLine.bringToFront();}"
if old_geom not in s:
    raise SystemExit('v29 active geometry point not found')
s = s.replace(old_geom, new_geom, 1)

old_clear = "activeLine.setLatLngs([]);"
new_clear = "activeCasing.setLatLngs([]);activeLine.setLatLngs([]);"
if old_clear in s:
    s = s.replace(old_clear, new_clear)

# 2) Recalculate the remaining active leg more often so deviations are reflected
# quickly and the line always starts close to the live GPS position.
s = s.replace("Date.now()-lastRoad<6500", "Date.now()-lastRoad<4000")

# 3) De-emphasize the complete route while navigating so the current blue leg
# is the visual focus. The full route remains available for 'Visa hela rutten'.
s = s.replace("var line=L.polyline(pts,{color:'#1976d2',weight:7,opacity:.95}).addTo(map);",
              "var line=L.polyline(pts,{color:'#607d8b',weight:6,opacity:.55}).addTo(map);", 1)

# 4) Version 28 arrow was a little large on top of city streets. Reduce it just
# enough to reveal more road while keeping it clearly visible.
s = s.replace("width:50px;height:50px;line-height:50px;text-align:center;font-size:41px",
              "width:46px;height:46px;line-height:46px;text-align:center;font-size:38px")
s = s.replace("iconSize:[50,50],iconAnchor:[25,25]", "iconSize:[46,46],iconAnchor:[23,23]")

# 5) Make the turn instruction slightly more prominent without enlarging the
# whole top card.
s = s.replace("#turn{font-size:19px", "#turn{font-size:20px")

# Version labels.
s = s.replace('VERSION 28 • RUTTBIBLIOTEK', 'VERSION 29 • RUTTBIBLIOTEK')
s = s.replace('VERSION 28 • \\"+selectedDay.toUpperCase()', 'VERSION 29 • \\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 28', 'versionCode 29').replace('versionName "28.0"', 'versionName "29.0"')
b.write_text(t, encoding='utf-8')

print('Version 29 applied: active blue road line, white casing, faster reroute and smaller arrow')
