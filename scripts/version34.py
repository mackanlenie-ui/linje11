from pathlib import Path

# Build on Version 33. Remove Leaflet zoom controls for a cleaner driving view.
exec(Path('scripts/version33.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

old = "var map=L.map('map',{zoomControl:true});"
new = "var map=L.map('map',{zoomControl:false});"
if old not in s:
    raise SystemExit('v34 Leaflet zoom control point not found')
s = s.replace(old, new, 1)

s = s.replace('VERSION 33 • RUTTBIBLIOTEK', 'VERSION 34 • RUTTBIBLIOTEK')
s = s.replace('VERSION 33 • \\\"+selectedDay.toUpperCase()', 'VERSION 34 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 33', 'versionCode 34').replace('versionName "33.0"', 'versionName "34.0"')
b.write_text(t, encoding='utf-8')

print('Version 34 applied: Leaflet zoom controls removed')
