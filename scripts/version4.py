from pathlib import Path
exec(Path('scripts/version3.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
# Route rename button alongside stop naming.
old='names.setOnClickListener(v->editStopNames(idx));row.addView(names);Button del=new Button(this);'
new='names.setOnClickListener(v->editStopNames(idx));row.addView(names);Button rename=new Button(this);rename.setAllCaps(false);rename.setText("✏ Byt ruttnamn");rename.setOnClickListener(v->renameRoute(idx));row.addView(rename);Button del=new Button(this);'
s=s.replace(old,new)
needle=' private void editStopNames(int index){'
method=''' private void renameRoute(int index){try{JSONArray routes=load(selectedDay);JSONObject item=routes.getJSONObject(index);EditText e=new EditText(this);e.setSingleLine(true);e.setText(item.optString("name","Rutt "+(index+1)));e.setSelectAllOnFocus(true);new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Byt namn på rutten").setView(e).setNegativeButton("Avbryt",null).setPositiveButton("Spara",(d,w)->{try{String n=e.getText().toString().trim();if(!n.isEmpty()){item.put("name",n);save(selectedDay,routes);refresh();}}catch(Exception ignored){}}).show();}catch(Exception e){Toast.makeText(this,"Kunde inte byta ruttnamn",Toast.LENGTH_LONG).show();}}
'''
s=s.replace(needle,method+needle)
# Floating map controls: whole route + current GPS/follow.
s=s.replace("<style>html,body,#map{height:100%;margin:0}","<style>html,body,#map{height:100%;margin:0}#controls{position:absolute;z-index:9999;left:10px;right:10px;bottom:18px;display:flex;gap:8px;pointer-events:none}#controls button{pointer-events:auto;flex:1;padding:13px 8px;border:0;border-radius:10px;background:white;font:bold 15px sans-serif;box-shadow:0 2px 8px #555;color:#17365d}")
s=s.replace("</style></head><body><div id='map'></div>","</style></head><body><div id='map'></div><div id='controls'><button onclick='showRoute()'>🗺 Visa hela rutten</button><button onclick='myGps()'>📍 Min GPS</button></div>")
old="var gps=null,acc=null,first=true;navigator.geolocation.watchPosition(function(pos){var ll=[pos.coords.latitude,pos.coords.longitude];"
new="var gps=null,acc=null,first=true,lastGps=null,followGps=true;function showRoute(){followGps=false;map.fitBounds(line.getBounds(),{padding:[35,35]});}function myGps(){followGps=true;if(lastGps)map.setView(lastGps,17,{animate:true});}navigator.geolocation.watchPosition(function(pos){var ll=[pos.coords.latitude,pos.coords.longitude];lastGps=ll;"
s=s.replace(old,new)
s=s.replace("if(first){map.setView(ll,17);first=false}else map.panTo(ll,{animate:true});","if(first){map.setView(ll,17);first=false}else if(followGps)map.panTo(ll,{animate:true});")
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 3','versionCode 4').replace('versionName "3.0"','versionName "4.0"');b.write_text(t,encoding='utf-8')
