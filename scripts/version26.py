from pathlib import Path
import re
exec(Path('scripts/version25.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V26 changes presentation only; preserve V25 route/GPS/arrival logic.
# More compact top card when matching tokens are present.
s=s.replace("padding:14px 16px","padding:10px 14px",1)
s=s.replace(".instruction{font-size:29px", ".instruction{font-size:31px",1)

# Center slightly ahead of the car so the vehicle appears lower on screen.
new_follow="if(follow){var sp=lastSpeed||((pos.coords.speed||0)*3.6);var z=sp>80?14:sp>45?15:16;var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=sp>80?.0065:sp>45?.0045:.0028;center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}"
patterns=[
 r"if\(follow\)\{var sp=lastSpeed;var z=sp>80\?14:sp>45\?15:16;map\.setView\(lastGps,z,\{animate:true\}\);\}",
 r"if\(follow\)\{var sp=\(pos\.coords\.speed\|\|0\)\*3\.6;var z=sp>70\?14:sp>35\?15:(?:16|17);map\.setView\(lastGps,z(?:,\{animate:true\})?\);\}"
]
for pat in patterns:
    s2,n=re.subn(pat,new_follow,s,count=1)
    if n:
        s=s2
        break
else:
    print('V26: camera token not found; retaining stable V25 camera')

# Larger directional car arrow.
s=s.replace("width:38px;height:38px;line-height:38px;text-align:center;font-size:31px", "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px",1)
s=s.replace("iconSize:[38,38],iconAnchor:[19,19]", "iconSize:[44,44],iconAnchor:[22,22]")

s=s.replace('VERSION 25 • RUTTBIBLIOTEK','VERSION 26 • RUTTBIBLIOTEK').replace('VERSION 25 • \"+selectedDay.toUpperCase()','VERSION 26 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 25','versionCode 26').replace('versionName \"25.0\"','versionName \"26.0\"')
b.write_text(t,encoding='utf-8')
