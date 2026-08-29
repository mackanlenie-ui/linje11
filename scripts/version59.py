from pathlib import Path
import re

exec(Path('scripts/version58.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Remove the test button robustly regardless of style changes made by later versions.
s=re.sub(r"<button\s+id=['\"]testBtn['\"][^>]*>.*?</button>","",s,count=1,flags=re.S)

# Keep test helper code harmlessly available internally, but no visible test control.
# Make the navigation card another step more compact while retaining readability.
style_end='</style>'
compact_css="""#top{padding:6px 10px!important;border-radius:16px!important;line-height:1.04!important}#top h1,#top .title{margin:0 0 1px!important;line-height:1.02!important}#turn{font-size:23px!important;line-height:1.08!important;padding:5px 7px!important;margin-top:3px!important;margin-bottom:2px!important}#eta,#routeStatus,#gpsStatus{font-size:16px!important;line-height:1.08!important;margin-top:1px!important;margin-bottom:0!important}#top .label{margin:0!important;line-height:1.05!important}"""
if style_end not in s: raise SystemExit('v59 style end not found')
s=s.replace(style_end,compact_css+style_end,1)

s=s.replace('VERSION 58 • OMDIRIGERING + KOMPAKT VY','VERSION 59 • REN KOMPAKT VY')
for n in range(1,59):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 59 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 59 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 59 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 58','versionCode 59').replace('versionName "58.0"','versionName "59.0"')
b.write_text(t,encoding='utf-8')
print('Version 59 applied: test button fully removed and navigation card made smaller')
