from pathlib import Path
import re

# Keep every improvement through Version 72, then add route/area selection.
exec(Path('scripts/version72.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# 1) Add route/area state before day selection.
old = 'private final String[] days={"Måndag","Tisdag","Onsdag","Torsdag","Fredag"};'
new = 'private final String[] areas={"Lenninge–Kilafors","Röste–Rengsjö"};\n private final String[] days={"Måndag","Tisdag","Onsdag","Torsdag","Fredag"};'
if old not in s:
    raise SystemExit('v73 days anchor missing')
s = s.replace(old, new, 1)

old = 'private LinearLayout routeList; private Spinner daySpinner; private String selectedDay="Måndag"; private JSONObject pendingRoute;'
new = 'private LinearLayout routeList; private Spinner areaSpinner,daySpinner; private String selectedArea="Lenninge–Kilafors",selectedDay="Måndag"; private JSONObject pendingRoute;'
if old not in s:
    raise SystemExit('v73 state anchor missing')
s = s.replace(old, new, 1)

# 2) Wire the new area spinner before the existing day spinner.
old = 'daySpinner=findViewById(R.id.daySpinner);routeList=findViewById(R.id.routeList);ArrayAdapter<String>a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);'
new = '''areaSpinner=findViewById(R.id.areaSpinner);daySpinner=findViewById(R.id.daySpinner);routeList=findViewById(R.id.routeList);
 ArrayAdapter<String> areaAdapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,areas);areaSpinner.setAdapter(areaAdapter);int areaPos=java.util.Arrays.asList(areas).indexOf(selectedArea);areaSpinner.setSelection(Math.max(0,areaPos));areaSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onItemSelected(android.widget.AdapterView<?>p,android.view.View v,int pos,long id){selectedArea=areas[pos];refresh();}public void onNothingSelected(android.widget.AdapterView<?>p){}});
 ArrayAdapter<String>a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);'''
if old not in s:
    raise SystemExit('v73 showMain anchor missing')
s = s.replace(old, new, 1)

# 3) Make the empty state and import confirmations show both area and day.
s = s.replace('"Inga rutter för "+selectedDay+" ännu."', '"Inga körturer för "+selectedArea+" • "+selectedDay+" ännu."')
s = s.replace('"Importerad till "+selectedDay', '"Importerad till "+selectedArea+" • "+selectedDay')
s = s.replace('"Rutten mottagen från Ruttredigeraren och sparad under "+selectedDay', '"Rutten mottagen från Ruttredigeraren och sparad under "+selectedArea+" • "+selectedDay')

# 4) Store routes separately per area + day. Old Version 72 routes automatically
#    remain visible under Lenninge–Kilafors for backwards compatibility.
old_load = 'private JSONArray load(String day){try{return new JSONArray(getPreferences(MODE_PRIVATE).getString("routes_"+day,"[]"));}catch(Exception e){return new JSONArray();}}'
new_load = '''private String routeKey(String day){return "routes_"+selectedArea.replace("–","-").replace(" ","_")+"_"+day;}
 private JSONArray load(String day){try{android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String key=routeKey(day);String raw=p.getString(key,null);if(raw==null&&"Lenninge–Kilafors".equals(selectedArea))raw=p.getString("routes_"+day,"[]");if(raw==null)raw="[]";return new JSONArray(raw);}catch(Exception e){return new JSONArray();}}'''
if old_load not in s:
    raise SystemExit('v73 load anchor missing')
s = s.replace(old_load, new_load, 1)

old_save = 'private void save(String day,JSONArray a){android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String key="routes_"+day;String old=p.getString(key,"[]");p.edit().putString("backup_"+key,old).putString(key,a.toString()).putLong("backup_time_"+day,System.currentTimeMillis()).apply();}'
new_save = 'private void save(String day,JSONArray a){android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String key=routeKey(day);String old=p.getString(key,"[]");p.edit().putString("backup_"+key,old).putString(key,a.toString()).putLong("backup_time_"+key,System.currentTimeMillis()).apply();}'
if old_save not in s:
    raise SystemExit('v73 save anchor missing')
s = s.replace(old_save, new_save, 1)

s = s.replace('VERSION 72 •', 'VERSION 73 •')
main.write_text(s, encoding='utf-8')

# 5) Update the main screen: area first, then day, then the available driving routes.
layout = Path('app/src/main/res/layout/activity_main.xml')
x = layout.read_text(encoding='utf-8')
x = x.replace('android:text="Välj dag och rutt"', 'android:text="Välj rutt/område, dag och körtur"')
anchor = ' <Spinner android:id="@+id/daySpinner" android:layout_width="match_parent" android:layout_height="52dp"/>'
area_ui = ''' <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="1. Välj rutt / område" android:textStyle="bold" android:textSize="16sp" android:paddingTop="8dp"/>
 <Spinner android:id="@+id/areaSpinner" android:layout_width="match_parent" android:layout_height="52dp"/>
 <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:text="2. Välj dag" android:textStyle="bold" android:textSize="16sp" android:paddingTop="6dp"/>
'''+anchor
if anchor not in x:
    raise SystemExit('v73 layout daySpinner anchor missing')
x = x.replace(anchor, area_ui, 1)
x = x.replace('android:text="Importera rutt till vald dag"', 'android:text="Importera körtur till valt område och dag"')
x = x.replace('android:text="VERSION 1 • Flera rutter per dag"', 'android:text="VERSION 73 • Område → dag → körtur"')
layout.write_text(x, encoding='utf-8')

# 6) Version bump after v72 has normalized Gradle to Version 72.
b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 72','versionCode 73').replace('versionName "72.0"','versionName "73.0"')
b.write_text(t, encoding='utf-8')

print('Version 73 applied: route/area -> day -> driving route, with separate storage per area/day')
