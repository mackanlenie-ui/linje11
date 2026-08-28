from pathlib import Path
exec(Path('scripts/version18.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 19: make map/GPS startup much more tolerant on Android WebView.
# Keep Version 18's silent navigation and all Version 16 routing/entrance logic.

# Use jsDelivr first with unpkg fallback for Leaflet. A CDN hiccup should no
# longer leave the whole map area white.
s=s.replace("<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'>",
            "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css'>")
s=s.replace("<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>",
            "<script src='https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js' onerror=\"this.onerror=null;this.src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'\"></script>")

# Give the map a visible neutral background while tiles are loading.
s=s.replace("html,body,#map{height:100%;margin:0}","html,body,#map{height:100%;margin:0}#map{background:#e9eef3}",1)

# Force a Leaflet resize shortly after opening and show a useful GPS waiting
# message rather than appearing frozen. The route stays visible meanwhile.
needle="loadRoadLine();navigator.geolocation.watchPosition(function(pos){"
repl="loadRoadLine();setTimeout(function(){try{map.invalidateSize();}catch(e){}if(!lastGps){document.getElementById('gpsStatus').textContent='🛰️ Väntar på GPS-signal…';document.getElementById('status').textContent='GPS startar – rutten visas under tiden';}},2500);navigator.geolocation.watchPosition(function(pos){"
if needle not in s: raise SystemExit('v19 GPS startup point not found')
s=s.replace(needle,repl,1)

# More patient high-accuracy GPS settings and clearer error text.
s=s.replace("function(){document.getElementById('gpsStatus').textContent='GPS kunde inte hämtas';},{enableHighAccuracy:true,maximumAge:1000,timeout:10000});",
            "function(err){document.getElementById('gpsStatus').textContent='🛰️ GPS väntar på signal';document.getElementById('status').textContent='Rutten visas – inväntar GPS';},{enableHighAccuracy:true,maximumAge:0,timeout:30000});",1)

# Ensure the WebView has the storage/database features geolocation providers
# commonly expect on Android.
s=s.replace("s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);",
            "s.setDomStorageEnabled(true);s.setDatabaseEnabled(true);s.setGeolocationEnabled(true);",1)

s=s.replace('VERSION 18 • RUTTBIBLIOTEK','VERSION 19 • RUTTBIBLIOTEK')
s=s.replace('VERSION 18 • \"+selectedDay.toUpperCase()','VERSION 19 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 18','versionCode 19').replace('versionName \"18.0\"','versionName \"19.0\"')
b.write_text(t,encoding='utf-8')
