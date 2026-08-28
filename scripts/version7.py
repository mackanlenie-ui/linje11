from pathlib import Path
exec(Path('scripts/version6.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
old='String name=item.optString("name","Rutt "+(i+1));Button open=cleanButton(name+"\\n"+stops+" stopp",62);'
new='String name=item.optString("name","Rutt "+(i+1));String time=item.optString("time","");String line=name+(time.isEmpty()?"":"\\n"+time)+" • "+stops+" stopp";Button open=cleanButton(line,62);'
s=s.replace(old,new)
s=s.replace('VERSION 6 • RUTTBIBLIOTEK','VERSION 7 • RUTTBIBLIOTEK').replace('VERSION 6 • "+selectedDay.toUpperCase()','VERSION 7 • "+selectedDay.toUpperCase()')
# Allow route name editor to include a Lenninge-style time line using "Namn | 07:05–07:30".
old='String n=e.getText().toString().trim();if(!n.isEmpty()){item.put("name",n);save(selectedDay,routes);refresh();}'
new='String n=e.getText().toString().trim();if(!n.isEmpty()){if(n.contains("|")){String[] parts=n.split("\\\\|",2);item.put("name",parts[0].trim());item.put("time",parts.length>1?parts[1].trim():"");}else item.put("name",n);save(selectedDay,routes);refresh();}'
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 6','versionCode 7').replace('versionName "6.0"','versionName "7.0"');b.write_text(t,encoding='utf-8')
