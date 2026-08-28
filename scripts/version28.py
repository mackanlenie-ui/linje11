from pathlib import Path

# Build on the proven Version 27 stack.
exec(Path('scripts/version27.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Larger, clearer driving arrow.
s = s.replace(
    "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px",
    "width:50px;height:50px;line-height:50px;text-align:center;font-size:41px"
)
s = s.replace("iconSize:[44,44],iconAnchor:[22,22]", "iconSize:[50,50],iconAnchor:[25,25]")

# 2) Refine the existing V27 follow camera without depending on one huge exact token.
# Extra zoom thresholds, slightly shorter look-ahead near stops, and smoother fly animation.
s = s.replace("dn<180)?18", "dn<160)?18")
s = s.replace("dn<450)?17", "dn<420)?17")
s = s.replace("dn<350)?.0012", "dn<300)?.0010")
s = s.replace("sp>80?.0065:sp>45?.0045:.0028", "sp>80?.0062:sp>45?.0042:.0025")
s = s.replace("map.setView(center,z,{animate:true});", "map.flyTo(center,z,{animate:true,duration:.65});")

# 3) Compact Leaflet labels so long START/SLUT place names wrap instead of
# stretching across the overview map.
style_insert = ".leaflet-tooltip{max-width:180px;white-space:normal;line-height:1.15;padding:5px 8px;font-size:15px}.leaflet-tooltip-pane{pointer-events:none}"
if style_insert not in s and "</style>" in s:
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
