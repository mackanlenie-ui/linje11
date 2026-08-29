from pathlib import Path

# Version 45 builds on Version 44 and fixes stale version labels on route pages.
exec(Path('scripts/version44.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Main/day chooser label.
s = s.replace('VERSION 44 • OFFLINE + SVÄNGAR', 'VERSION 45 • OFFLINE + SVÄNGAR')

# Some older route chooser strings survived the long version chain. Normalize
# all known dynamic weekday labels so restored routes never show an old version.
for n in range(1, 45):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 45 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 45 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 45 • \\\"+selectedDay.toUpperCase()')

# Also catch the current dynamic label if V44 managed to update it.
s = s.replace('VERSION 44 • "+selectedDay.toUpperCase()', 'VERSION 45 • "+selectedDay.toUpperCase()')
s = s.replace('VERSION 44 • \\"+selectedDay.toUpperCase()', 'VERSION 45 • \\"+selectedDay.toUpperCase()')
s = s.replace('VERSION 44 • \\\"+selectedDay.toUpperCase()', 'VERSION 45 • \\\"+selectedDay.toUpperCase()')

main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 44', 'versionCode 45').replace('versionName "44.0"', 'versionName "45.0"')
b.write_text(t, encoding='utf-8')

print('Version 45 applied: normalized stale version labels on day/route chooser')
