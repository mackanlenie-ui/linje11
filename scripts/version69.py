from pathlib import Path

exec(Path('scripts/version68.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V69: keep the proven navigation engine and add safer course-up/follow CSS only.
# The previous implementation injected a raw multiline <script> inside a Java
# string literal, which broke javac. All additions here stay inside that string.
css=r'''#map{transition:transform .35s ease;transform-origin:50% 62%}body.freeLook #map{transform:none!important}'''
if '</style>' not in s:
    raise SystemExit('v69 style end not found')
s=s.replace('</style>',css+'</style>',1)

# Improve common maneuver wording while keeping existing turn engine intact.
s=s.replace("'FÖLJ VÄGEN'","'FÖLJ VÄGEN FRAMÅT'")
s=s.replace('"FÖLJ VÄGEN"','"FÖLJ VÄGEN FRAMÅT"')
s=s.replace('VERSION 68 • MINDRE NAVIGERINGSRUTA','VERSION 69 • SMART KÖRNAVIGERING')
for n in range(1,69):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 69 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 69 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 69 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 68','versionCode 69').replace('versionName "68.0"','versionName "69.0"')
b.write_text(t,encoding='utf-8')
print('Version 69 applied: safe navigation improvements without breaking Java string literals')
