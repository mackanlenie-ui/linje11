from pathlib import Path
import re

exec(Path('scripts/version74.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V75: do not draw/navigate a connector from the phone's current position
# to the beginning/next point of the saved work route. The current GPS marker
# is still shown, but only the imported/saved route is rendered.

# Older map implementations followed the GPS immediately and could make it
# look as if the app was navigating from the current position to the route.
s=s.replace('map.panTo(ll);','',1)

# Disable known connector/approach functions if they exist in newer map code.
s=re.sub(r'async function updateConnector\([^)]*\)\{.*?\}(?=function|map\.on|const gpsCtl|const routeCtl|drawRoute|navigator\.geolocation)',
         "async function updateConnector(force){return;}", s, count=1, flags=re.S)
s=re.sub(r'async function updateApproachRoute\(\)\{.*?\}(?=function|map\.on|const gpsCtl|const routeCtl|navigator\.geolocation)',
         "async function updateApproachRoute(){return;}", s, count=1, flags=re.S)

# Never frame the map between the phone and the route start/next stop.
s=re.sub(r'map\.fitBounds\(\[user,coords\[currentNext\]\].*?\);','',s,count=1)

# If a connector layer variable exists, ensure it is always removed and never drawn.
s=s.replace("document.getElementById('routeStatus').textContent='Bilväg till arbetsrutten visas ✓';",
            "document.getElementById('routeStatus').textContent='Arbetsrutten visas ✓';")

# Update visible version text and Android version metadata.
s=s.replace('VERSION 74 •','VERSION 75 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 74','versionCode 75').replace('versionName "74.0"','versionName "75.0"')
b.write_text(t,encoding='utf-8')
print('Version 75 applied: route-only start, no connector from current GPS position')
