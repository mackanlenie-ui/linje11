from pathlib import Path

exec(Path('scripts/version66.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Minimal driving HUD: only the maneuver and a tiny single-line status area.
# The old title/start guidance remains in the DOM for logic compatibility but
# is hidden visually, freeing substantially more map space.
css=r'''#top{padding:2px 5px!important;border-radius:11px!important;max-height:19vh!important;overflow:hidden!important}#top h1,#top .title,#top .label{display:none!important}#turn{font-size:15px!important;line-height:1!important;padding:2px 4px!important;margin:0!important;border-radius:8px!important;max-height:2.25em!important;overflow:hidden!important}#eta{display:none!important}#routeStatus,#gpsStatus{font-size:9px!important;line-height:1!important;margin:0!important;display:inline!important;white-space:nowrap!important}#routeStatus:after{content:' • '}'''
if '</style>' not in s: raise SystemExit('v67 style end not found')
s=s.replace('</style>',css+'</style>',1)

# Smaller floating direction arrow so it does not cover the road ahead.
css2=r'''#dirArrow,#directionArrow,#headingArrow,.direction-arrow,.heading-arrow{transform:scale(.68)!important;transform-origin:center center!important}'''
s=s.replace('</style>',css2+'</style>',1)

s=s.replace('VERSION 66 • EXTRA KOMPAKT NAVIGERING','VERSION 67 • MINIMAL KÖRVY')
for n in range(1,67):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 67 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 67 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 67 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 66','versionCode 67').replace('versionName "66.0"','versionName "67.0"')
b.write_text(t,encoding='utf-8')
print('Version 67 applied: minimal driving HUD and smaller map direction arrow')
