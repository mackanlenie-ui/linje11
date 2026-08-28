from pathlib import Path
import re
exec(Path('scripts/version25.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V26 focuses only on the driving presentation. Keep routing/GPS/arrival logic
# from the proven V25 base unchanged.

# Slightly more compact information card to expose more of the map.
s=s.replace("#top{position:absolute;z-index:9999;top:10px;left:10px;right:10px;background:#fff;padding:9px 12px;",
            "#top{position:absolute;z-index:9999;top:10px;left:10px;right:10px;background:#fff;padding:7px 11px;",1)
s=s.replace("#title{font-size:19px;font-weight:900}","#title{font-size:18px;font-weight:900}",1)
s=s.replace("#turn{font-size:21px;font-weight:900;display:block;margin-top:5px;color:#111}",
            "#turn{font-size:22px;font-weight:900;display:block;margin-top:4px;color:#111;line-height:1.08}",1)

# Robustly replace whichever V24/V25 follow-camera variant was generated.
new_follow="if(follow){var sp=lastSpeed||((pos.coords.speed||0)*3.6);var z=sp>80?14:sp>45?15:16;if(nextTurn&&nextTurn.d>900)z=Math.max(14,z-1);if(nextTurn&&nextTurn.d<180&&sp<55)z=16;var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=sp>80?.0065:sp>45?.0045:.0028;center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}"
patterns=[
 r"if\(follow\)\{var sp=lastSpeed;var z=sp>80\?14:sp>45\?15:16;map\.setView\(lastGps,z,\{animate:true\}\);\}",
 r"if\(follow\)\{var sp=\(pos\.coords\.speed\|\|0\)\*3\.6;var z=sp>70\?14:sp>35\?15:(?:16|17);map\.setView\(lastGps,z(?:,\{animate:true\})?\);\}",
 r"if\(follow\)map\.setView\(lastGps,16(?:,\{animate:true\})?\);"
]
changed=False
for pat in patterns:
    s2,n=re.subn(pat,new_follow,s,count=1)
    if n:
        s=s2; changed=True; break
if not changed: raise SystemExit('v26 follow camera point not found')

# Make the upcoming-turn distance easier to scan.
old_fmt="function fmt(t){if(!t)return'⬆️ Följ vägen';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';return t.icon+' '+t.text+' om '+d;}"
new_fmt="function fmt(t){if(!t)return'⬆️ Följ vägen';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';return t.icon+' '+t.text+'  •  '+d;}"
if old_fmt in s: s=s.replace(old_fmt,new_fmt,1)

# Larger car arrow where the V25 icon is present.
s=s.replace("width:38px;height:38px;line-height:38px;text-align:center;font-size:31px", "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px",1)
s=s.replace("iconSize:[38,38],iconAnchor:[19,19]", "iconSize:[44,44],iconAnchor:[22,22]",2)

s=s.replace('VERSION 25 • RUTTBIBLIOTEK','VERSION 26 • RUTTBIBLIOTEK').replace('VERSION 25 • \"+selectedDay.toUpperCase()','VERSION 26 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 25','versionCode 26').replace('versionName \"25.0\"','versionName \"26.0\"')
b.write_text(t,encoding='utf-8')
