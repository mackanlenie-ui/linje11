from pathlib import Path
exec(Path('scripts/version8.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8').replace('Linje11 Rutt GPS','Rutt GPS').replace('VERSION 8 • RUTTBIBLIOTEK','VERSION 9 • RUTTBIBLIOTEK').replace('VERSION 8 • "+selectedDay.toUpperCase()','VERSION 9 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 8','versionCode 9').replace('versionName "8.0"','versionName "9.0"');b.write_text(t,encoding='utf-8')
