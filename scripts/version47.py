from pathlib import Path

# Version 47 builds on V46. It fixes START->SLUT routes with zero intermediate
# stops and suppresses tiny routing/geometry artifacts that can look like a
# false immediate left/right turn.
exec(Path('scripts/version46.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# 1) Online maneuver parser: ignore tiny connector maneuvers very close to the
# current GPS point. These are common when OSRM snaps the live GPS to a nearby
# road segment and were the cause of e.g. "SVÄNG HÖGER OM 2 m" while driving
# straight. Roundabouts are never suppressed by this guard.
start = s.find('function turnText(rr){')
end = s.find('function fmt(t){', start)
if start < 0 or end < 0:
    raise SystemExit('v47 turnText point not found')
new_turn = r'''function turnText(rr){try{var ss=rr.legs[0].steps||[],walk=0;for(var i=0;i<ss.length;i++){var q=ss[i],type=((q.maneuver&&q.maneuver.type)||'').toLowerCase(),mod=((q.maneuver&&q.maneuver.modifier)||'').toLowerCase(),qd=Number(q.distance||0);if(type==='depart'){walk+=qd;continue;}if(type==='arrive'){walk+=qd;continue;}if(qd<5){walk+=qd;continue;}var isRound=(type.indexOf('roundabout')>=0||type.indexOf('rotary')>=0);var icon='⬆️',txt='Fortsätt rakt fram',real=false;if(isRound){icon='🔄';txt='Kör in i rondellen';if(q.maneuver&&q.maneuver.exit)txt+=' och ta avfart '+q.maneuver.exit;real=true;}else if(mod.indexOf('left')>=0){icon=mod.indexOf('slight')>=0?'↖️':'⬅️';txt=mod.indexOf('slight')>=0?'Håll svagt vänster':'Sväng vänster';real=true;}else if(mod.indexOf('right')>=0){icon=mod.indexOf('slight')>=0?'↗️':'➡️';txt=mod.indexOf('slight')>=0?'Håll svagt höger':'Sväng höger';real=true;}else if(mod.indexOf('straight')>=0){real=true;}if(real){var micro=!isRound&&walk<18&&qd<35;if(micro){walk+=qd;continue;}if(q.name)txt+=' mot '+q.name;return{icon:icon,text:txt,d:Math.max(0,walk),key:type+'|'+mod+'|'+q.name,roundabout:isRound,exit:(q.maneuver&&q.maneuver.exit)?q.maneuver.exit:null};}walk+=qd;}}catch(e){}return null;}'''
s = s[:start] + new_turn + s[end:]

# 2) Conservative offline maneuver engine. A local turn now requires a strong
# direction change over a meaningful distance on both sides of the bend. This
# deliberately prefers "FÖLJ VÄGEN" over guessing at normal curves.
off_start = s.find('function offlineTurn(){')
off_end = s.find('function nearestActive(', off_start)
if off_start < 0 or off_end < 0:
    raise SystemExit('v47 offlineTurn point not found')
new_offline = r'''function offlineTurn(){try{var a=(activePts&&activePts.length>24)?activePts:pts;if(!lastGps||!a||a.length<24)return null;var bi=0,bd=1e12,step=Math.max(1,Math.floor(a.length/320));for(var i=0;i<a.length;i+=step){var dd=km(lastGps,a[i])*1000;if(dd<bd){bd=dd;bi=i;}}for(var z=Math.max(0,bi-6);z<=Math.min(a.length-1,bi+10);z++){var dz=km(lastGps,a[z])*1000;if(dz<bd){bd=dz;bi=z;}}var dist=0,last=a[bi];for(var j=bi+1;j<a.length-10;j++){dist+=km(last,a[j])*1000;last=a[j];if(dist<45)continue;if(dist>1600)break;var back=j,fwd=j,backDist=0,fwdDist=0;while(back>bi&&backDist<45){backDist+=km(a[back-1],a[back])*1000;back--;}while(fwd<a.length-1&&fwdDist<55){fwdDist+=km(a[fwd],a[fwd+1])*1000;fwd++;}if(backDist<35||fwdDist<40||back===j||fwd===j)continue;var d=turnDelta(bearing(a[back],a[j]),bearing(a[j],a[fwd]));if(Math.abs(d)>=62){var right=d>0;return{icon:right?'➡️':'⬅️',text:right?'Sväng höger':'Sväng vänster',d:Math.max(0,dist),key:'offline47|'+j+'|'+(right?'R':'L'),offline:true};}}return null;}catch(e){return null;}}'''
s = s[:off_start] + new_offline + s[off_end:]

# 3) Correct navigation card for routes containing only START and SLUT. Never
# show impossible progress such as "NÄSTA STOPP • 1/0".
old_label = "else{lab.textContent=(nearD<90?'FRAMME SNART • ':(nearD<180?'NÄRMAR DIG • ':'NÄSTA STOPP • '))+(idx+1)+'/'+stops.length;st.textContent='Nästa: '+t.label+(nearD<180?' • '+Math.max(0,Math.round(nearD))+' m':'')+(t.name?' • '+t.name:'');}"
new_label = "else{if(stops.length===0){lab.textContent=nearD<90?'FRAMME SNART • SLUTPUNKT':(nearD<180?'NÄRMAR DIG • SLUTPUNKT':'KÖR TILL SLUTPUNKT');st.textContent='Nästa: SLUT'+(nearD<180?' • '+Math.max(0,Math.round(nearD))+' m':'')+(t.name?' • '+t.name:'');}else{lab.textContent=(nearD<90?'FRAMME SNART • ':(nearD<180?'NÄRMAR DIG • ':'NÄSTA STOPP • '))+(idx+1)+'/'+stops.length;st.textContent='Nästa: '+t.label+(nearD<180?' • '+Math.max(0,Math.round(nearD))+' m':'')+(t.name?' • '+t.name:'');}}"
if old_label not in s:
    raise SystemExit('v47 zero-stop navigation label point not found')
s = s.replace(old_label, new_label, 1)

# Also make the route status say destination instead of "0 stops kvar".
old_status = "var rem=Math.max(0,stops.length-idx);var nxt=(idx<stops.length?stops[idx]:end);var nt=nxt?((nxt.label||nxt.name||nxt.address||'SLUT')):'SLUT';document.getElementById('routeStatus').textContent='📍 Nästa: '+nt+' • '+rem+' stopp kvar • 🚗 Till infart ✓ • ↩ AUTO';"
new_status = "var rem=Math.max(0,stops.length-idx);var nxt=(idx<stops.length?stops[idx]:end);var nt=nxt?((nxt.label||nxt.name||nxt.address||'SLUT')):'SLUT';document.getElementById('routeStatus').textContent=stops.length===0?'📍 Destination: SLUT • 🚗 Bilväg ✓':'📍 Nästa: '+nt+' • '+rem+' stopp kvar • 🚗 Till infart ✓ • ↩ AUTO';"
if old_status in s:
    s = s.replace(old_status, new_status, 1)
else:
    # Different older wording can survive the long version chain; normalize the
    # common current form without making the build fail.
    s = s.replace("document.getElementById('routeStatus').textContent='📍 Nästa: '+nt+' • '+rem+' stopp kvar • 🛣️ Bilväg ✓';", "document.getElementById('routeStatus').textContent=stops.length===0?'📍 Destination: SLUT • 🛣️ Bilväg ✓':'📍 Nästa: '+nt+' • '+rem+' stopp kvar • 🛣️ Bilväg ✓';", 1)

# Version labels and package version.
s = s.replace('VERSION 46 • TYDLIGA SVÄNGAR', 'VERSION 47 • SÄKRA SVÄNGAR')
for n in range(1, 47):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 47 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 47 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 47 • \\\"+selectedDay.toUpperCase()')

main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 46', 'versionCode 47').replace('versionName "46.0"', 'versionName "47.0"')
b.write_text(t, encoding='utf-8')

print('Version 47 applied: zero-stop START/SLUT display and conservative false-turn suppression')
