from pathlib import Path

exec(Path('scripts/version52.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Recompute the cached planned maneuver from the latest GPS fix on EVERY accepted
# position update. This makes 4.9 km -> 4.8 -> 4.7 ... instead of keeping the
# distance captured by an earlier routing response.
old="arrived();if(!nextTurn)nextTurn=plannedTurn()||offlineTurn();checkOffRoute();info();updateRoad(false);"
new="arrived();var livePlanned=plannedTurn();if(livePlanned)nextTurn=livePlanned;else if(!nextTurn)nextTurn=offlineTurn();checkOffRoute();info();updateRoad(false);"
if old not in s:
    raise SystemExit('v53 live GPS maneuver update point not found')
s=s.replace(old,new,1)

# Do the same in test/simulation mode so the countdown can be verified without driving.
old_sim="arrived();nextTurn=plannedTurn()||offlineTurn();checkOffRoute();info();"
new_sim="arrived();var livePlanned=plannedTurn();nextTurn=livePlanned||offlineTurn();checkOffRoute();info();"
if old_sim in s:
    s=s.replace(old_sim,new_sim,1)

# If a planned maneuver has just been passed, immediately move to the following one.
# plannedTurn() already selects the first maneuver ahead of the nearest route index,
# so refreshing it on every GPS fix also advances to the next turn automatically.

s=s.replace('VERSION 52 • BLÅ RUTT + MANÖVERAVSTÅND','VERSION 53 • LIVE NEDRÄKNING')
for n in range(1,53):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 53 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 53 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 53 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 52','versionCode 53').replace('versionName "52.0"','versionName "53.0"')
b.write_text(t,encoding='utf-8')
print('Version 53 applied: live maneuver distance recalculated on every GPS fix')
