from pathlib import Path

# Build on Version 32. Only move the upper navigation card down a little.
exec(Path('scripts/version32.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

old = "#top{position:absolute;z-index:9999;top:10px;"
new = "#top{position:absolute;z-index:9999;top:34px;"
if old not in s:
    raise SystemExit('v33 top card position point not found')
s = s.replace(old, new, 1)

s = s.replace('VERSION 32 • RUTTBIBLIOTEK', 'VERSION 33 • RUTTBIBLIOTEK')
s = s.replace('VERSION 32 • \\\"+selectedDay.toUpperCase()', 'VERSION 33 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 32', 'versionCode 33').replace('versionName "32.0"', 'versionName "33.0"')
b.write_text(t, encoding='utf-8')

print('Version 33 applied: navigation card moved below status bar')
