from pathlib import Path

# Version 46 builds on V45 and makes visual turn guidance clearer and more resilient.
exec(Path('scripts/version45.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Larger, glanceable maneuver banner while driving.
s = s.replace("#turn{font-size:22px", "#turn{font-size:28px", 1)
style_anchor = ".controls{position:absolute;"
turn_styles = "#turn.turnLeft,#turn.turnRight{background:#eef6ff;border-radius:12px;padding:8px 10px;margin-top:7px}#turn.turnRound{background:#fff3e0;border-radius:12px;padding:8px 10px;margin-top:7px;border:2px solid #ef6c00}"
if turn_styles not in s and style_anchor in s:
    s = s.replace(style_anchor, turn_styles + style_anchor, 1)

# Keep explicit metadata for roundabouts, including exit number when OSRM provides it.
old_return = "return{icon:icon,text:txt,d:Math.max(0,walk),key:type+'|'+mod+'|'+q.name};"
new_return = "return{icon:icon,text:txt,d:Math.max(0,walk),key:type+'|'+mod+'|'+q.name,roundabout:(type.indexOf('roundabout')>=0||type.indexOf('rotary')>=0),exit:(q.maneuver&&q.maneuver.exit)?q.maneuver.exit:null};"
if old_return not in s:
    raise SystemExit('v46 maneuver metadata point not found')
s = s.replace(old_return, new_return, 1)

# Make the wording unmistakable, especially in roundabouts.
fmt_start = s.find('function fmt(t){')
fmt_end = s.find('function eta(', fmt_start)
if fmt_start < 0 or fmt_end < 0:
    raise SystemExit('v46 fmt point not found')
new_fmt = r'''function fmt(t){if(!t)return'⬆️ FÖLJ VÄGEN';var d=t.d<1000?Math.round(t.d)+' m':(t.d/1000).toFixed(1)+' km';if(t.roundabout){var ex=t.exit?(' • TA AVFART '+t.exit):'';return'🔄 OM '+d+' • RONDELL'+ex;}var tx=(t.text||'Fortsätt rakt fram').toUpperCase();return t.icon+' OM '+d+' • '+tx;}'''
s = s[:fmt_start] + new_fmt + s[fmt_end:]

# Track the last valid online instruction so a roundabout exit does not vanish
# immediately during a short connectivity loss.
s = s.replace('nextTurn=null,nearHits=0', 'nextTurn=null,lastGoodTurn=null,nearHits=0', 1)
s = s.replace('nextTurn=turnText(rr);if(rr.geometry', 'nextTurn=turnText(rr);if(nextTurn)lastGoodTurn=nextTurn;if(rr.geometry', 1)
old_offline = "nextTurn=offlineTurn();var rs=document.getElementById('routeStatus');"
new_offline = "var localTurn=offlineTurn();if(lastGoodTurn&&lastGoodTurn.roundabout){if(localTurn&&localTurn.d!=null)lastGoodTurn.d=localTurn.d;nextTurn=lastGoodTurn;}else nextTurn=localTurn;var rs=document.getElementById('routeStatus');"
if old_offline not in s:
    raise SystemExit('v46 offline turn point not found')
s = s.replace(old_offline, new_offline, 1)

# Apply a visual class to the current maneuver banner.
old_turn_line = "document.getElementById('turn').textContent=fmt(nextTurn);"
new_turn_line = "var turnEl=document.getElementById('turn');turnEl.textContent=fmt(nextTurn);turnEl.className=nextTurn?(nextTurn.roundabout?'turnRound':((nextTurn.text||'').toLowerCase().indexOf('vänster')>=0?'turnLeft':((nextTurn.text||'').toLowerCase().indexOf('höger')>=0?'turnRight':''))):'';"
if old_turn_line not in s:
    raise SystemExit('v46 turn display point not found')
s = s.replace(old_turn_line, new_turn_line, 1)

# Version labels and package version.
s = s.replace('VERSION 45 • OFFLINE + SVÄNGAR', 'VERSION 46 • TYDLIGA SVÄNGAR')
for n in range(1, 46):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 46 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 46 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 46 • \\\"+selectedDay.toUpperCase()')

main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 45', 'versionCode 46').replace('versionName "45.0"', 'versionName "46.0"')
b.write_text(t, encoding='utf-8')

print('Version 46 applied: larger turn banner, explicit roundabout exits, cached roundabout guidance')
