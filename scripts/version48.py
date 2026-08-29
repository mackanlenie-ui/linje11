from pathlib import Path

# Version 48 builds on V47 and makes the maneuver banner adaptive: compact when
# the maneuver is far away, increasingly prominent as the driver approaches it.
exec(Path('scripts/version47.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Add distance-sensitive visual classes. Far maneuvers leave substantially more
# map visible; near maneuvers remain large and glanceable.
anchor = '#turn.turnLeft,#turn.turnRight{background:#eef6ff;border-radius:12px;padding:8px 10px;margin-top:7px}'
extra = '#turn.turnFar{font-size:20px!important;line-height:1.12;padding:5px 8px!important;margin-top:5px!important}#turn.turnMid{font-size:24px!important;line-height:1.15;padding:7px 9px!important}#turn.turnNear{font-size:30px!important;line-height:1.12;padding:10px 11px!important}'
if extra not in s:
    if anchor not in s:
        raise SystemExit('v48 turn style anchor not found')
    s = s.replace(anchor, extra + anchor, 1)

old = "var turnEl=document.getElementById('turn');turnEl.textContent=fmt(nextTurn);turnEl.className=nextTurn?(nextTurn.roundabout?'turnRound':((nextTurn.text||'').toLowerCase().indexOf('vänster')>=0?'turnLeft':((nextTurn.text||'').toLowerCase().indexOf('höger')>=0?'turnRight':''))):'';"
new = "var turnEl=document.getElementById('turn');turnEl.textContent=fmt(nextTurn);var baseClass=nextTurn?(nextTurn.roundabout?'turnRound':((nextTurn.text||'').toLowerCase().indexOf('vänster')>=0?'turnLeft':((nextTurn.text||'').toLowerCase().indexOf('höger')>=0?'turnRight':''))):'';var distClass=nextTurn&&nextTurn.d!=null?(nextTurn.d>3000?'turnFar':(nextTurn.d>1000?'turnMid':'turnNear')):'';turnEl.className=(baseClass+' '+distClass).trim();"
if old not in s:
    raise SystemExit('v48 turn display point not found')
s = s.replace(old, new, 1)

s = s.replace('VERSION 47 • SÄKRA SVÄNGAR', 'VERSION 48 • ADAPTIV NAVIGATION')
for n in range(1, 48):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 48 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 48 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 48 • \\\"+selectedDay.toUpperCase()')

main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 47', 'versionCode 48').replace('versionName "47.0"', 'versionName "48.0"')
b.write_text(t, encoding='utf-8')

print('Version 48 applied: adaptive maneuver banner (far compact, near large)')
