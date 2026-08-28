from pathlib import Path
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
# Add edit button for stop names under each route.
old='open.setOnClickListener(v->openRoute(idx));row.addView(open);Button del=new Button(this);'
new='open.setOnClickListener(v->openRoute(idx));row.addView(open);Button names=new Button(this);names.setAllCaps(false);names.setText("✏ Namnge stopp");names.setOnClickListener(v->editStopNames(idx));row.addView(names);Button del=new Button(this);'
s=s.replace(old,new)
# Add native stop-name editor. Names are stored inside the route JSON and persist with the day/route.
needle=' private void openRoute(int index){'
method=''' private void editStopNames(int index){try{JSONArray routes=load(selectedDay);JSONObject item=routes.getJSONObject(index);JSONObject route=item.getJSONObject("route");JSONArray stops=route.optJSONArray("stops");if(stops==null||stops.length()==0){Toast.makeText(this,"Rutten har inga stopp",Toast.LENGTH_SHORT).show();return;}LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);int pad=(int)(12*getResources().getDisplayMetrics().density);box.setPadding(pad,0,pad,0);final EditText[] fields=new EditText[stops.length()];for(int i=0;i<stops.length();i++){JSONObject st=stops.getJSONObject(i);String label=st.optString("label",String.valueOf((char)(65+i)));TextView l=new TextView(this);l.setText("Stopp "+label);l.setTextSize(16);box.addView(l);EditText e=new EditText(this);e.setSingleLine(true);e.setHint("Namn för "+label);e.setText(st.optString("name",""));fields[i]=e;box.addView(e);}new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Namnge stopp").setView(box).setNegativeButton("Avbryt",null).setPositiveButton("Spara",(d,w)->{try{for(int i=0;i<stops.length();i++){String n=fields[i].getText().toString().trim();if(n.isEmpty())stops.getJSONObject(i).remove("name");else stops.getJSONObject(i).put("name",n);}save(selectedDay,routes);refresh();Toast.makeText(this,"Stoppnamnen är sparade",Toast.LENGTH_SHORT).show();}catch(Exception e){Toast.makeText(this,"Kunde inte spara namnen",Toast.LENGTH_LONG).show();}}).show();}catch(Exception e){Toast.makeText(this,"Kunde inte öppna stoppnamn",Toast.LENGTH_LONG).show();}}
'''
s=s.replace(needle,method+needle)
# Include escaped name in map data and show it beside marker.
old=".append(o.optString(\"label\",String.valueOf((char)('A'+i)))).append(\"'}\");"
new=".append(o.optString(\"label\",String.valueOf((char)('A'+i)))).append(\"',name:'\").append(o.optString(\"name\",\"\").replace(\"\\\\\",\"\\\\\\\\\").replace(\"'\",\"\\\\'\")).append(\"'}\");"
s=s.replace(old,new)
s=s.replace(".gps{background:#1687ff", ".stopname{background:white;border:1px solid #777;border-radius:5px;padding:3px 7px;font:bold 14px sans-serif;white-space:nowrap;box-shadow:0 1px 3px #777}.gps{background:#1687ff")
oldjs="stops.forEach(function(s){L.marker([s.lat,s.lon],{icon:L.divIcon({className:'',html:'<div class=stop>'+s.label+'</div>',iconSize:[48,48],iconAnchor:[24,24]})}).addTo(map)});"
newjs="stops.forEach(function(s){var mk=L.marker([s.lat,s.lon],{icon:L.divIcon({className:'',html:'<div class=stop>'+s.label+'</div>',iconSize:[48,48],iconAnchor:[24,24]})}).addTo(map);if(s.name){mk.bindTooltip(s.name,{permanent:true,direction:'right',offset:[25,0],className:'stopname'}).openTooltip();}});"
s=s.replace(oldjs,newjs)
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 2','versionCode 3').replace('versionName "2.0"','versionName "3.0"');b.write_text(t,encoding='utf-8')
