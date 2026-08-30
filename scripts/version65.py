from pathlib import Path

exec(Path('scripts/version64.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Make the driving information card substantially smaller while keeping the
# turn instruction readable at a glance. Disable WebView text autosizing so
# long street names do not unexpectedly blow up the whole card.
style_end='</style>'
css=r'''html{-webkit-text-size-adjust:100%!important;text-size-adjust:100%!important}#top{padding:5px 9px!important;border-radius:15px!important;line-height:1.02!important;max-height:38vh!important;overflow:hidden!important}#top h1,#top .title{font-size:22px!important;line-height:1.02!important;margin:0 0 1px!important}#top .label{font-size:15px!important;line-height:1.02!important;margin:0!important}#turn{font-size:20px!important;line-height:1.04!important;padding:4px 6px!important;margin:2px 0!important;border-radius:12px!important;max-height:4.25em!important;overflow:hidden!important}#eta,#routeStatus,#gpsStatus{font-size:14px!important;line-height:1.04!important;margin:1px 0 0!important}'''
if style_end not in s: raise SystemExit('v65 style end not found')
s=s.replace(style_end,css+style_end,1)

# "NY RUTT KLAR" is useful as a short confirmation, but should not permanently
# consume a row in the navigation card. Clear it after a few seconds unless a
# newer warning/status has replaced it.
old="if(rs)rs.textContent='✅ NY RUTT KLAR';info();ensureRemainingVisible();return true;"
new="if(rs){rs.textContent='✅ NY RUTT KLAR';setTimeout(function(){try{if(rs.textContent.indexOf('NY RUTT KLAR')>=0)rs.textContent='';}catch(e){}},3200);}info();ensureRemainingVisible();return true;"
if old in s:s=s.replace(old,new,1)

s=s.replace('VERSION 64 • KÖRBAR INFART','VERSION 65 • KOMPAKT NAVIGERING')
for n in range(1,65):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 65 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 65 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 65 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 64','versionCode 65').replace('versionName "64.0"','versionName "65.0"')
b.write_text(t,encoding='utf-8')
print('Version 65 applied: compact navigation card, fixed WebView text sizing and transient reroute status')
