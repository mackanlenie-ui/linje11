from pathlib import Path

# Final driving polish on top of the proven Version 35 build.
exec(Path('scripts/version35.py').read_text(encoding='utf-8'))

p = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = p.read_text(encoding='utf-8')

# 1) Keep more road visible ahead of the vehicle while following.
for old_lead in [
    "var lead=(dn!=null&&dn<260)?.00085:(sp>80?.0058:sp>45?.0039:.0022);",
    "var lead=(dn!=null&&dn<260)?.00085:(sp>80?.0058:sp>45?.0039:.0022);center=",
    "var lead=(dn!=null&&dn<260)?.00085:(sp>80?.0058:sp>45?.0039:.0022)"
]:
    if old_lead in s:
        s = s.replace(old_lead, old_lead.replace(".00085", ".00115").replace(".0058", ".0065").replace(".0039", ".0046").replace(".0022", ".0030"), 1)
        break

# 2) Make close turns slightly easier to read without enlarging the whole card.
s = s.replace("#turn{font-size:21px", "#turn{font-size:22px", 1)

# 3) Stronger final-approach state inside 90 m.
style_old = "#top.arrival{border-left-color:#2e7d32;box-shadow:0 3px 16px #2e7d3288}.controls{position:absolute;"
style_new = "#top.arrival{border-left-color:#2e7d32;box-shadow:0 3px 16px #2e7d3288}#top.arrivalNear{border-left-color:#1b5e20;box-shadow:0 4px 18px #1b5e2099}.controls{position:absolute;"
if style_old in s:
    s = s.replace(style_old, style_new, 1)

arrival_toggle_old = "if(topBox)topBox.classList.toggle('arrival',nearD<180);"
arrival_toggle_new = "if(topBox){topBox.classList.toggle('arrival',nearD<180);topBox.classList.toggle('arrivalNear',nearD<90);}"
if arrival_toggle_old in s:
    s = s.replace(arrival_toggle_old, arrival_toggle_new, 1)

label_old = "lab.textContent=(nearD<180?'NÄRMAR DIG • ':'NÄSTA STOPP • ')+(idx+1)+'/'+stops.length;"
label_new = "lab.textContent=(nearD<90?'FRAMME SNART • ':(nearD<180?'NÄRMAR DIG • ':'NÄSTA STOPP • '))+(idx+1)+'/'+stops.length;"
if label_old in s:
    s = s.replace(label_old, label_new, 1)

# 4) Show a warning only when GPS accuracy is actually weak.
gps_old = "document.getElementById('gpsStatus').textContent='🔵 GPS hittad • ±'+Math.round(pos.coords.accuracy)+' m';"
gps_new = "document.getElementById('gpsStatus').textContent=(rawAcc>35?'🟠 GPS osäker':'🔵 GPS hittad')+' • ±'+Math.round(rawAcc)+' m';"
if gps_old in s:
    s = s.replace(gps_old, gps_new, 1)

# 5) Return to north-up while standing still. Heading-up resumes automatically
# when the vehicle is moving, making map labels easier to read at stops.
heading_old = "lastSpeed=(pos.coords.speed||0)*3.6;if(follow&&lastHeading!=null&&lastSpeed>6&&typeof map.setBearing==='function')map.setBearing((360-lastHeading)%360);"
heading_new = "lastSpeed=(pos.coords.speed||0)*3.6;if(follow&&typeof map.setBearing==='function'){if(lastHeading!=null&&lastSpeed>8)map.setBearing((360-lastHeading)%360);else if(lastSpeed<4)map.setBearing(0);}"
if heading_old in s:
    s = s.replace(heading_old, heading_new, 1)

# 6) Resume progress per route rather than sharing one progress value between all routes.
progress_old = "phase=start?'start':'route',idx=parseInt(localStorage.getItem('rutt_idx')||'0')"
progress_new = "routeKey='rutt_'+stops.length+'_'+(start?start.lat.toFixed(5):'x')+'_'+(end?end.lat.toFixed(5):'x'),phase=localStorage.getItem(routeKey+'_phase')||(start?'start':'route'),idx=parseInt(localStorage.getItem(routeKey+'_idx')||'0')"
if progress_old in s:
    s = s.replace(progress_old, progress_new, 1)
    s = s.replace("localStorage.setItem('rutt_idx',String(idx));", "localStorage.setItem(routeKey+'_idx',String(idx));", 1)
    s = s.replace("phase='route';idx=0;lastSpoken='';", "phase='route';idx=0;localStorage.setItem(routeKey+'_phase',phase);localStorage.setItem(routeKey+'_idx','0');lastSpoken='';", 1)
    s = s.replace("phase='end';if(end)", "phase='end';localStorage.setItem(routeKey+'_phase',phase);if(end)", 1)
    s = s.replace("phase='done';try", "phase='done';localStorage.setItem(routeKey+'_phase',phase);try", 1)

s = s.replace('VERSION 35 • RUTTBIBLIOTEK', 'VERSION 36 • RUTTBIBLIOTEK')
s = s.replace('VERSION 35 • \\\"+selectedDay.toUpperCase()', 'VERSION 36 • \\\"+selectedDay.toUpperCase()')
p.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8')
t = t.replace('versionCode 35', 'versionCode 36').replace('versionName "35.0"', 'versionName "36.0"')
b.write_text(t, encoding='utf-8')

print('Version 36 applied: final follow view, close-stop guidance, GPS quality and per-route resume')
