from pathlib import Path

exec(Path('scripts/version67.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Version 68: make the complete top navigation card about 35% smaller.
# zoom reduces both text and the actual layout footprint, giving the map more room.
css=r'''#top{zoom:.66!important;max-height:none!important;overflow:hidden!important;padding:3px 7px!important}#turn{font-size:15px!important;line-height:1.02!important;padding:3px 5px!important;margin:1px 0!important}#top h1,#top .title{font-size:18px!important;line-height:1!important;margin:0!important}#top .label{font-size:13px!important;line-height:1!important;margin:0!important}#routeStatus,#gpsStatus{font-size:9px!important;line-height:1!important;margin:0!important}'''
if '</style>' not in s: raise SystemExit('v68 style end not found')
s=s.replace('</style>',css+'</style>',1)

s=s.replace('VERSION 67 • MINIMAL KÖRVY','VERSION 68 • MINDRE NAVIGERINGSRUTA')
for n in range(1,68):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 68 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 68 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 68 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 67','versionCode 68').replace('versionName "67.0"','versionName "68.0"')
b.write_text(t,encoding='utf-8')
print('Version 68 applied: top navigation card reduced by about 35 percent')
