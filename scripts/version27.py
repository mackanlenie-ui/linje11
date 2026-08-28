from pathlib import Path
import re

# Build on the stable Version 26 navigation stack.
exec(Path('scripts/version26.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Smooth the compass heading so the vehicle arrow does not jump around.
old_state = "lastHeading=null,lastSpeed=0,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
new_state = "lastHeading=null,smoothHeading=null,lastSpeed=0,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);"
if old_state not in s:
    raise SystemExit('v27 heading state point not found')
s = s.replace(old_state, new_state, 1)

old_gps = "lastGps=[pos.coords.latitude,pos.coords.longitude];lastHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:lastHeading;lastSpeed=(pos.coords.speed||0)*3.6;"
new_gps = "lastGps=[pos.coords.latitude,pos.coords.longitude];var rawHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:null;if(rawHeading!=null){if(smoothHeading==null)smoothHeading=rawHeading;else{var hd=((rawHeading-smoothHeading+540)%360)-180;smoothHeading=(smoothHeading+hd*.28+360)%360;}lastHeading=smoothHeading;}lastSpeed=(pos.coords.speed||0)*3.6;"
if old_gps not in s:
    raise SystemExit('v27 GPS heading point not found')
s = s.replace(old_gps, new_gps, 1)

# 2) Turn/arrival-aware automatic zoom. Version 26 may have retained the
# stable V25 camera, so accept either camera form.
new_follow = "if(follow){var sp=lastSpeed||((pos.coords.speed||0)*3.6);var tgt=(phase==='start'?start:(idx<stops.length?stops[idx]:end));var dn=null;if(tgt){var tla=(tgt.navLat!=null?tgt.navLat:tgt.lat),tlo=(tgt.navLon!=null?tgt.navLon:tgt.lon);dn=km(lastGps,[tla,tlo])*1000;}var z=(dn!=null&&dn<180)?18:((dn!=null&&dn<450)?17:(sp>80?14:sp>45?15:16));var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=(dn!=null&&dn<350)?.0012:(sp>80?.0065:sp>45?.0045:.0028);center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}"
follow_variants = [
    "if(follow){var sp=lastSpeed||((pos.coords.speed||0)*3.6);var z=sp>80?14:sp>45?15:16;var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=sp>80?.0065:sp>45?.0045:.0028;center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}",
    "if(follow){var sp=lastSpeed;var z=sp>80?14:sp>45?15:16;map.setView(lastGps,z,{animate:true});}"
]
for old_follow in follow_variants:
    if old_follow in s:
        s = s.replace(old_follow, new_follow, 1)
        break
else:
    raise SystemExit('v27 follow camera point not found')

# 3) More robust automatic stop completion: require useful GPS accuracy as
# well as low speed and consecutive near readings.
old_arrival = "if(d<40&&lastSpeed<18)nearHits++;else if(d>60||lastSpeed>25)nearHits=0;if(nearHits<3)return;"
new_arrival = "var accNow=pos.coords.accuracy||999;if(d<40&&lastSpeed<18&&accNow<45)nearHits++;else if(d>60||lastSpeed>25||accNow>70)nearHits=0;if(nearHits<3)return;"
if old_arrival not in s:
    raise SystemExit('v27 arrival stability point not found')
s = s.replace(old_arrival, new_arrival, 1)

s = s.replace('VERSION 26 • RUTTBIBLIOTEK', 'VERSION 27 • RUTTBIBLIOTEK')
s = s.replace('VERSION 26 • \"+selectedDay.toUpperCase()', 'VERSION 27 • \"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 26', 'versionCode 27').replace('versionName \"26.0\"', 'versionName \"27.0\"')
b.write_text(t, encoding='utf-8')

print('Version 27 applied: smoother heading, smarter close-stop zoom and safer auto-arrival')
