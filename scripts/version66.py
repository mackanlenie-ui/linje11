from pathlib import Path

exec(Path('scripts/version65.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Ultra-compact driving card: maximize visible map while retaining the next turn.
# Hide the redundant large product heading during navigation, collapse metadata,
# and make the turn instruction fit its box instead of being clipped.
css=r'''#top{padding:3px 7px!important;border-radius:13px!important;max-height:25vh!important;overflow:hidden!important}#top h1,#top .title{display:none!important}#top .label{font-size:12px!important;line-height:1!important;margin:0!important}#turn{font-size:16px!important;line-height:1.02!important;padding:3px 5px!important;margin:1px 0!important;border-radius:10px!important;max-height:3.2em!important;overflow:hidden!important}#eta,#routeStatus,#gpsStatus{font-size:11px!important;line-height:1!important;margin:0!important;display:inline!important}#eta:after,#routeStatus:after{content:'  •  '}'''
if '</style>' not in s: raise SystemExit('v66 style end not found')
s=s.replace('</style>',css+'</style>',1)

# Dynamically shrink the maneuver text only when needed, preserving the full
# street name in the compact box rather than cutting it off.
fit=r'''<script>(function(){function fitTurn(){var e=document.getElementById('turn');if(!e)return;var fs=16;e.style.fontSize=fs+'px';while(fs>11&&e.scrollHeight>e.clientHeight){fs--;e.style.fontSize=fs+'px';}}var mo=new MutationObserver(function(){setTimeout(fitTurn,0)});document.addEventListener('DOMContentLoaded',function(){var e=document.getElementById('turn');if(e){mo.observe(e,{childList:true,subtree:true,characterData:true});fitTurn();}});window.addEventListener('resize',fitTurn);})();</script>'''
s=s.replace('</body>',fit+'</body>',1)

s=s.replace('VERSION 65 • KOMPAKT NAVIGERING','VERSION 66 • EXTRA KOMPAKT NAVIGERING')
for n in range(1,66):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 66 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 66 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 66 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 65','versionCode 66').replace('versionName "65.0"','versionName "66.0"')
b.write_text(t,encoding='utf-8')
print('Version 66 applied: ultra compact navigation card with adaptive full maneuver text')
