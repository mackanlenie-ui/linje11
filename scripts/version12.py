from pathlib import Path
exec(Path('scripts/version11.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
s=s.replace('private final String[] days={"Måndag","Tisdag","Onsdag","Torsdag","Fredag"};','private final String[] days={"Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"};')
s=s.replace('VERSION 11 • RUTTBIBLIOTEK','VERSION 12 • RUTTBIBLIOTEK').replace('VERSION 11 • "+selectedDay.toUpperCase()','VERSION 12 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 11','versionCode 12').replace('versionName "11.0"','versionName "12.0"');b.write_text(t,encoding='utf-8')
