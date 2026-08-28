from pathlib import Path
exec(Path('scripts/version10.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
# Compact the navigation card while keeping text readable.
s=s.replace("padding:9px 12px;border-radius:14px", "padding:7px 11px;border-radius:14px")
s=s.replace("#title{font-size:19px", "#title{font-size:18px")
s=s.replace("#status{font-size:18px", "#status{font-size:17px")
s=s.replace("#turn{font-size:21px", "#turn{font-size:19px")
s=s.replace("#eta{font-size:13px", "#eta{font-size:12px")
s=s.replace("#routeStatus{font-size:13px", "#routeStatus{font-size:12px")
s=s.replace("#gpsStatus{font-size:13px", "#gpsStatus{font-size:12px")
# Make START phase unmistakable and only use NEXT STOP after START has been reached.
s=s.replace("lab.textContent='KÖR TILL STARTPUNKT';st.textContent='Nästa: START';", "lab.textContent='NAVIGERA TILL START';st.textContent='🟢 STARTPUNKT';")
s=s.replace("try{Android.speakMessage('Startpunkten är nådd. Ruttnavigeringen börjar.');}", "try{Android.speakMessage('Startpunkten är nådd. Nu börjar ruttnavigeringen. Nästa stopp '+(stops.length?stops[0].label:''));}")
s=s.replace('VERSION 10 • RUTTBIBLIOTEK','VERSION 11 • RUTTBIBLIOTEK').replace('VERSION 10 • "+selectedDay.toUpperCase()','VERSION 11 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 10','versionCode 11').replace('versionName "10.0"','versionName "11.0"');b.write_text(t,encoding='utf-8')
