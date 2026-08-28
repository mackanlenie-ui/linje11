from pathlib import Path
exec(Path('scripts/version7.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java');s=p.read_text(encoding='utf-8')
s=s.replace('VERSION 7 • RUTTBIBLIOTEK','VERSION 8 • RUTTBIBLIOTEK').replace('VERSION 7 • "+selectedDay.toUpperCase()','VERSION 8 • "+selectedDay.toUpperCase()')
# Imported recorder V8/V9 files contain dedicated start/end points; render them on the map.
old='StringBuilder m=new StringBuilder("[");if(stops!=null)for(int i=0;i<stops.length();i++){'
new='StringBuilder m=new StringBuilder("[");JSONObject start=route.optJSONObject("start"),end=route.optJSONObject("end");if(stops!=null)for(int i=0;i<stops.length();i++){'
s=s.replace(old,new)
old="m.append(']');return \"<!doctype html>"
new="m.append(']');String special=\"[]\";if(start!=null||end!=null){StringBuilder q=new StringBuilder(\"[\");if(start!=null)q.append(\"{lat:\").append(start.getDouble(\"lat\")).append(\",lon:\").append(start.getDouble(\"lon\")).append(\",label:'START'}\");if(end!=null){if(start!=null)q.append(',');q.append(\"{lat:\").append(end.getDouble(\"lat\")).append(\",lon:\").append(end.getDouble(\"lon\")).append(\",label:'SLUT'}\");}q.append(']');special=q.toString();}return \"<!doctype html>"
s=s.replace(old,new)
s=s.replace('var pts="+p+",stops="+m+";','var pts="+p+",stops="+m+",special="+special+";')
s=s.replace("stops.forEach(function(s){L.marker([s.lat,s.lon]", "special.forEach(function(x){var c=x.label==='START'?'#2e7d32':'#c62828';L.marker([x.lat,x.lon],{icon:L.divIcon({className:'',html:'<div style=\\\"background:'+c+';color:white;border:4px solid white;border-radius:18px;padding:5px 9px;font:bold 12px sans-serif\\\">'+x.label+'</div>',iconSize:[64,32],iconAnchor:[32,16]})}).addTo(map)});stops.forEach(function(s){L.marker([s.lat,s.lon]")
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 7','versionCode 8').replace('versionName "7.0"','versionName "8.0"');b.write_text(t,encoding='utf-8')
