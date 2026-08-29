from pathlib import Path

# Build on Version 34.
exec(Path('scripts/version34.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# Heading-up map using the Leaflet Rotate plugin.
leaflet_js = "<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>"
rotate_js = leaflet_js + "<script src='https://unpkg.com/leaflet-rotate@0.2.8/dist/leaflet-rotate-src.js'></script>"
if leaflet_js not in s:
    raise SystemExit('v35 Leaflet script point not found')
s = s.replace(leaflet_js, rotate_js, 1)

old_map = "var map=L.map('map',{zoomControl:false});"
new_map = "var map=L.map('map',{zoomControl:false,rotate:true,bearing:0,touchRotate:false,rotateControl:false});"
if old_map not in s:
    raise SystemExit('v35 map options point not found')
s = s.replace(old_map, new_map, 1)

# Keep the vehicle arrow pointing upward while the map rotates with travel direction.
s = s.replace("transform:rotate('+(lastHeading||0)+'deg)", "transform:rotate('+(follow?0:(lastHeading||0))+'deg)", 1)

# Reject clearly poor GPS fixes and implausible low-speed jumps before they affect navigation.
watch_old = "navigator.geolocation.watchPosition(function(pos){lastGps=[pos.coords.latitude,pos.coords.longitude];"
watch_new = "navigator.geolocation.watchPosition(function(pos){var rawAcc=pos.coords.accuracy||999;if(rawAcc>85)return;var rawGps=[pos.coords.latitude,pos.coords.longitude];if(lastGps&&km(lastGps,rawGps)*1000>180&&(pos.coords.speed||0)<15)return;lastGps=rawGps;"
if watch_old not in s:
    raise SystemExit('v35 GPS filter point not found')
s = s.replace(watch_old, watch_new, 1)

# Rotate the map so the current heading points toward the top of the screen.
heading_old = "lastSpeed=(pos.coords.speed||0)*3.6;"
heading_new = "lastSpeed=(pos.coords.speed||0)*3.6;if(follow&&lastHeading!=null&&lastSpeed>6&&typeof map.setBearing==='function')map.setBearing((360-lastHeading)%360);"
if heading_old not in s:
    raise SystemExit('v35 heading-up point not found')
s = s.replace(heading_old, heading_new, 1)

# Clear rotation when showing the complete route, then resume heading-up from Min GPS.
s = s.replace("function showRoute(){follow=false;", "function showRoute(){follow=false;if(typeof map.setBearing==='function')map.setBearing(0);", 1)
s = s.replace("function myGps(){follow=true;if(lastGps)", "function myGps(){follow=true;if(lastHeading!=null&&typeof map.setBearing==='function')map.setBearing((360-lastHeading)%360);if(lastGps)", 1)

# More visible arrival state when approaching the next target.
style_old = ".controls{position:absolute;"
style_new = "#top.arrival{border-left-color:#2e7d32;box-shadow:0 3px 16px #2e7d3288}.controls{position:absolute;"
if style_old not in s:
    raise SystemExit('v35 arrival style point not found')
s = s.replace(style_old, style_new, 1)

info_old = "function info(){var t=target(),lab=document.getElementById('label'),st=document.getElementById('status');"
info_new = "function info(){var t=target(),lab=document.getElementById('label'),st=document.getElementById('status'),topBox=document.getElementById('top');var nearD=999;if(t&&lastGps){var nla=(t.navLat!=null?t.navLat:t.lat),nlo=(t.navLon!=null?t.navLon:t.lon);nearD=km(lastGps,[nla,nlo])*1000;}if(topBox)topBox.classList.toggle('arrival',nearD<180);"
if info_old not in s:
    raise SystemExit('v35 info point not found')
s = s.replace(info_old, info_new, 1)

route_label_old = "else{lab.textContent='NÄSTA STOPP • '+(idx+1)+'/'+stops.length;st.textContent='Nästa: '+t.label+(t.name?' • '+t.name:'');}"
route_label_new = "else{lab.textContent=(nearD<180?'NÄRMAR DIG • ':'NÄSTA STOPP • ')+(idx+1)+'/'+stops.length;st.textContent='Nästa: '+t.label+(nearD<180?' • '+Math.max(0,Math.round(nearD))+' m':'')+(t.name?' • '+t.name:'');}"
if route_label_old not in s:
    raise SystemExit('v35 arrival label point not found')
s = s.replace(route_label_old, route_label_new, 1)

s = s.replace('VERSION 34 • RUTTBIBLIOTEK', 'VERSION 35 • RUTTBIBLIOTEK')
s = s.replace('VERSION 34 • \\\"+selectedDay.toUpperCase()', 'VERSION 35 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 34', 'versionCode 35').replace('versionName "34.0"', 'versionName "35.0"')
b.write_text(t, encoding='utf-8')

print('Version 35 applied: heading-up map, GPS jump filtering and clearer arrival state')
