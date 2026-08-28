from pathlib import Path

# Build Version 27 directly on the proven Version 25 stack.
# This avoids depending on Version 26's optional camera substitution.
exec(Path('scripts/version25.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# Smooth heading.
s = s.replace(
    "lastHeading=null,lastSpeed=0,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);",
    "lastHeading=null,smoothHeading=null,lastSpeed=0,activeLine=L.polyline([],{color:'#d32f2f',weight:9,opacity:.88}).addTo(map);",
    1
)
s = s.replace(
    "lastGps=[pos.coords.latitude,pos.coords.longitude];lastHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:lastHeading;lastSpeed=(pos.coords.speed||0)*3.6;",
    "lastGps=[pos.coords.latitude,pos.coords.longitude];var rawHeading=(typeof pos.coords.heading==='number'&&!isNaN(pos.coords.heading))?pos.coords.heading:null;if(rawHeading!=null){if(smoothHeading==null)smoothHeading=rawHeading;else{var hd=((rawHeading-smoothHeading+540)%360)-180;smoothHeading=(smoothHeading+hd*.28+360)%360;}lastHeading=smoothHeading;}lastSpeed=(pos.coords.speed||0)*3.6;",
    1
)

# Smart follow camera: adaptive zoom, extra zoom near next stop and look-ahead
# so the vehicle appears lower on screen.
old_follow = "if(follow){var sp=lastSpeed;var z=sp>80?14:sp>45?15:16;map.setView(lastGps,z,{animate:true});}"
new_follow = "if(follow){var sp=lastSpeed;var tgt=(phase==='start'?start:(idx<stops.length?stops[idx]:end));var dn=null;if(tgt){var tla=(tgt.navLat!=null?tgt.navLat:tgt.lat),tlo=(tgt.navLon!=null?tgt.navLon:tgt.lon);dn=km(lastGps,[tla,tlo])*1000;}var z=(dn!=null&&dn<180)?18:((dn!=null&&dn<450)?17:(sp>80?14:sp>45?15:16));var center=lastGps;if(lastHeading!=null&&sp>5){var rad=lastHeading*Math.PI/180;var lead=(dn!=null&&dn<350)?.0012:(sp>80?.0065:sp>45?.0045:.0028);center=[lastGps[0]+Math.cos(rad)*lead,lastGps[1]+Math.sin(rad)*lead/Math.max(.35,Math.cos(lastGps[0]*Math.PI/180))];}map.setView(center,z,{animate:true});}"
s = s.replace(old_follow, new_follow, 1)

# Safer automatic stop completion using GPS accuracy too.
s = s.replace(
    "if(d<40&&lastSpeed<18)nearHits++;else if(d>60||lastSpeed>25)nearHits=0;if(nearHits<3)return;",
    "var accNow=pos.coords.accuracy||999;if(d<40&&lastSpeed<18&&accNow<45)nearHits++;else if(d>60||lastSpeed>25||accNow>70)nearHits=0;if(nearHits<3)return;",
    1
)

# Slightly larger directional arrow.
s = s.replace("width:38px;height:38px;line-height:38px;text-align:center;font-size:31px", "width:44px;height:44px;line-height:44px;text-align:center;font-size:36px", 1)
s = s.replace("iconSize:[38,38],iconAnchor:[19,19]", "iconSize:[44,44],iconAnchor:[22,22]")

s = s.replace('VERSION 25 • RUTTBIBLIOTEK', 'VERSION 27 • RUTTBIBLIOTEK')
s = s.replace('VERSION 25 • \"+selectedDay.toUpperCase()', 'VERSION 27 • \"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 25', 'versionCode 27').replace('versionName \"25.0\"', 'versionName \"27.0\"')
b.write_text(t, encoding='utf-8')

print('Version 27 applied successfully')
