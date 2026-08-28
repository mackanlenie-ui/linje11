from pathlib import Path

# Build on the proven Version 27 stack.
exec(Path('scripts/version27.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Larger, clearer driving arrow.
s = s.replace(
    "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px",
    "width:50px;height:50px;line-height:50px;text-align:center;font-size:41px",
    1
)
s = s.replace("iconSize:[44,44],iconAnchor:[22,22]", "iconSize:[50,50],iconAnchor:[25,25]")

# 2) Smoother camera movement and slightly smarter distance-aware zoom.
old_follow = "if(follow){var sp=lastSpeed;var tgt=(phase==='start'?start:(idx<stops.length?stops[idx]:end));var dn=null;if(tgt){var tla=(tgt.navLat!=null?tgt.navLat:tgt.lat),tlo=(tgt.navLon!=null?tgt.navLon:tgt.lon);dn=km(lastGps,[tla,tlo])*1000;}var z=(dn!=null&&dn<180)?18:((dn!=null&&dn<450)?17:(sp>80?14:sp>45?15:16));var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=(dn!=null&&dn<350)?.0012:(sp>80?.0065:sp>45?.0045:.0028);center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}"
new_follow = "if(follow){var sp=lastSpeed;var tgt=(phase==='start'?start:(idx<stops.length?stops[idx]:end));var dn=null;if(tgt){var tla=(tgt.navLat!=null?tgt.navLat:tgt.lat),tlo=(tgt.navLon!=null?tgt.navLon:tgt.lon);dn=km(lastGps,[tla,tlo])*1000;}var z=(dn!=null&&dn<160)?18:((dn!=null&&dn<420)?17:((dn!=null&&dn<1200)?16:(sp>80?14:sp>45?15:16)));var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=(dn!=null&&dn<300)?.0010:(sp>80?.0062:sp>45?.0042:.0025);center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.flyTo(center,z,{animate:true,duration:.65});}"
if old_follow not in s:
    raise SystemExit('v28 follow camera point not found')
s = s.replace(old_follow, new_follow, 1)

# 3) Compact START/SLUT and other Leaflet labels so long place names do not
# run far across the overview map.
style_insert = ".leaflet-tooltip{max-width:180px;white-space:normal;line-height:1.15;padding:5px 8px;font-size:15px}.leaflet-tooltip-pane{pointer-events:none}"
if "</style>" in s:
    s = s.replace("</style>", style_insert + "</style>", 1)

# Version labels.
s = s.replace('VERSION 27 • RUTTBIBLIOTEK', 'VERSION 28 • RUTTBIBLIOTEK')
s = s.replace('VERSION 27 • \\"+selectedDay.toUpperCase()', 'VERSION 28 • \\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 27', 'versionCode 28').replace('versionName "27.0"', 'versionName "28.0"')
b.write_text(t, encoding='utf-8')

print('Version 28 applied successfully')
