from pathlib import Path

exec(Path('scripts/version50.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Move test mode to its own clearly visible button above the normal bottom controls.
s = s.replace("right:10px;bottom:112px", "right:18px;bottom:190px")
s = s.replace("padding:8px 11px;font-size:13px", "padding:10px 14px;font-size:14px")

s = s.replace('VERSION 50 • TEST + OMDIRIGERING', 'VERSION 51 • TESTKNAPP FIXAD')
for n in range(1, 51):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 51 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 51 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 51 • \\\"+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 50', 'versionCode 51').replace('versionName "50.0"', 'versionName "51.0"')
b.write_text(t, encoding='utf-8')
print('Version 51 applied: test button moved clear of Byt rutt/dag')
