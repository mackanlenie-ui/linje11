from pathlib import Path

# Version 50 is the corrected build of V49. V49's generated Java string had
# unescaped quotes around the simulated GPS marker HTML.
exec(Path('scripts/version49.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')
s = s.replace('class="gpsDot"', 'class=\\"gpsDot\\"')
s = s.replace('VERSION 49 • TEST + OMDIRIGERING', 'VERSION 50 • TEST + OMDIRIGERING')
for n in range(1, 50):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 50 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 50 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 50 • \\\"+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 49', 'versionCode 50').replace('versionName "49.0"', 'versionName "50.0"')
b.write_text(t, encoding='utf-8')
print('Version 50 applied: corrected test-mode HTML escaping')
