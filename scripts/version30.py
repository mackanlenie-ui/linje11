from pathlib import Path

# Build on the proven Version 29 navigation stack.
exec(Path('scripts/version29.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Faster active-leg recalculation so a wrong turn is reflected sooner.
s = s.replace("Date.now()-lastRoad<4000", "Date.now()-lastRoad<2500")

# 2) Smoother heading: reduce small GPS compass jumps without making turns feel slow.
s = s.replace("smoothHeading=(smoothHeading+hd*.28+360)%360", "smoothHeading=(smoothHeading+hd*.22+360)%360")

# 3) Safer automatic stop arrival. Require a tighter position, lower speed,
# better GPS accuracy and four consecutive good fixes before advancing.
s = s.replace(
    "if(d<40&&lastSpeed<18&&accNow<45)nearHits++;else if(d>60||lastSpeed>25||accNow>70)nearHits=0;if(nearHits<3)return;",
    "if(d<34&&lastSpeed<15&&accNow<40)nearHits++;else if(d>55||lastSpeed>22||accNow>60)nearHits=0;if(nearHits<4)return;",
    1
)

# 4) Refine the follow camera: slightly closer near the next stop, a shorter
# look-ahead at low speed, and quicker animation so the map follows naturally.
s = s.replace("dn<160)?18", "dn<140)?18")
s = s.replace("dn<420)?17", "dn<380)?17")
s = s.replace("dn<300)?.0010", "dn<260)?.00085")
s = s.replace("sp>80?.0062:sp>45?.0042:.0025", "sp>80?.0058:sp>45?.0039:.0022")
s = s.replace("map.flyTo(center,z,{animate:true,duration:.65});", "map.flyTo(center,z,{animate:true,duration:.5});")

# 5) Make the next-turn line easier to read at a glance while driving.
s = s.replace("#turn{font-size:20px", "#turn{font-size:21px")

# Version labels.
s = s.replace('VERSION 29 • RUTTBIBLIOTEK', 'VERSION 30 • RUTTBIBLIOTEK')
s = s.replace('VERSION 29 • \\\"+selectedDay.toUpperCase()', 'VERSION 30 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 29', 'versionCode 30').replace('versionName "29.0"', 'versionName "30.0"')
b.write_text(t, encoding='utf-8')

print('Version 30 applied: faster reroute, smoother heading/camera, safer arrivals and clearer turn guidance')
