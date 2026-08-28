from pathlib import Path
exec(Path('scripts/version25.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V26 only changes the presentation/follow camera. Route/GPS logic stays V25.
# Put the vehicle lower on screen by centering the map ahead of the car.
old="if(follow){var sp=lastSpeed;var z=sp>80?14:sp>45?15:16;map.setView(lastGps,z,{animate:true});}"
new="if(follow){var sp=lastSpeed;var z=sp>80?14:sp>45?15:16;var c=lastGps;if(lastHeading!=null&&sp>4){var r=sp>70?260:sp>35?180:110,br=lastHeading*Math.PI/180,lat=lastGps[0]+(r*Math.cos(br))/111320,lon=lastGps[1]+(r*Math.sin(br))/(111320*Math.cos(lastGps[0]*Math.PI/180));c=[lat,lon];}map.setView(c,z,{animate:true});}"
if old not in s: raise SystemExit('v26 follow camera point not found')
s=s.replace(old,new,1)

# Slightly smaller top navigation card to expose more map while driving.
s=s.replace("padding:14px 16px","padding:10px 14px",1)
s=s.replace("font-size:22px","font-size:20px",1)

# Make the immediate turn distance stand out more without touching directions logic.
s=s.replace(".instruction{font-size:29px", ".instruction{font-size:31px",1)

# Make the car arrow a little larger/easier to see.
s=s.replace("width:38px;height:38px;line-height:38px;text-align:center;font-size:31px", "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px",1)
s=s.replace("iconSize:[38,38],iconAnchor:[19,19]", "iconSize:[44,44],iconAnchor:[22,22]",2)

s=s.replace('VERSION 25 • RUTTBIBLIOTEK','VERSION 26 • RUTTBIBLIOTEK').replace('VERSION 25 • \"+selectedDay.toUpperCase()','VERSION 26 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 25','versionCode 26').replace('versionName \"25.0\"','versionName \"26.0\"')
b.write_text(t,encoding='utf-8')
