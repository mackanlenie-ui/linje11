from pathlib import Path

# Keep every improvement through Version 72, then add route/area selection.
exec(Path('scripts/version72.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Area state is independent of the existing weekday array/chooser.
class_anchor='public class MainActivity extends AppCompatActivity {'
if class_anchor not in s: raise SystemExit('v73 class anchor missing')
s=s.replace(class_anchor,class_anchor+'\n private final String[] routeAreas={"Lenninge–Kilafors","Röste–Rengsjö"};\n private String selectedArea="Lenninge–Kilafors";',1)

# Preserve the proven weekday chooser as a second step.
old_sig=' private void showDayChooser(){'
if old_sig not in s: raise SystemExit('v73 day chooser signature missing')
s=s.replace(old_sig,' private void showDayChooserForArea(){',1)

# New first screen: choose route/area, then continue to weekday chooser.
insert_anchor=' private void showDayChooserForArea(){'
area_method=''' private void showAreaChooser(){selectedDay="Måndag";routeList=null;daySpinner=null;LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(18),dp(10),dp(18));TextView title=titleText("Rutt GPS",29,true);root.addView(title,new LinearLayout.LayoutParams(-1,dp(54)));TextView ver=titleText("VERSION 73 • VÄLJ RUTT / OMRÅDE",17,true);ver.setTextColor(android.graphics.Color.rgb(25,105,185));root.addView(ver,new LinearLayout.LayoutParams(-1,dp(38)));TextView sub=titleText("1. Välj vilken rutt / vilket område du ska köra.",20,false);LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(66));sp.setMargins(0,0,0,dp(10));root.addView(sub,sp);for(String area:routeAreas){Button b=cleanButton(area,62);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(72));lp.setMargins(0,dp(7),0,dp(7));b.setOnClickListener(v->{selectedArea=area;showDayChooserForArea();});root.addView(b,lp);}setContentView(root);}
'''
s=s.replace(insert_anchor,area_method+insert_anchor,1)

# App start should always begin with area selection. The exact onCreate grew over
# several versions, so only replace the first chooser call in the file.
first_call=s.find('showDayChooser();')
if first_call<0: raise SystemExit('v73 initial chooser call missing')
s=s[:first_call]+'showAreaChooser();'+s[first_call+len('showDayChooser();'):]

# Inside the route chooser, "Byt dag" should keep the current area and return
# only to the weekday step. Other old showDayChooser calls may still return to
# the area screen, which is safe and gives a way to switch area.
old_back='back.setOnClickListener(v->showDayChooser());'
if old_back in s:s=s.replace(old_back,'back.setOnClickListener(v->showDayChooserForArea());',1)

# Make chooser text show area context.
s=s.replace('TextView sub=titleText("Välj vilken dag du ska köra.",21,false);','TextView sub=titleText("2. Välj dag för "+selectedArea+".",21,false);',1)
s=s.replace('TextView title=titleText("Rutt GPS",27,true);','TextView title=titleText("Rutt GPS • "+selectedArea,27,true);',1)
s=s.replace('"＋ Importera rutt till "+selectedDay','"＋ Importera körtur till "+selectedArea+" • "+selectedDay')
s=s.replace('"Inga rutter för "+selectedDay+" ännu."','"Inga körturer för "+selectedArea+" • "+selectedDay+" ännu."')
s=s.replace('"Importerad till "+selectedDay','"Importerad till "+selectedArea+" • "+selectedDay')
s=s.replace('"Rutten mottagen från Ruttredigeraren och sparad under "+selectedDay','"Rutten mottagen från Ruttredigeraren och sparad under "+selectedArea+" • "+selectedDay')

# Separate storage per area + weekday. Old saved routes remain under
# Lenninge–Kilafors automatically.
old_load='private JSONArray load(String day){try{return new JSONArray(getPreferences(MODE_PRIVATE).getString("routes_"+day,"[]"));}catch(Exception e){return new JSONArray();}}'
new_load='private String routeKey(String day){return "routes_"+selectedArea.replace("–","-").replace(" ","_")+"_"+day;}\n private JSONArray load(String day){try{android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String raw=p.getString(routeKey(day),null);if(raw==null&&"Lenninge–Kilafors".equals(selectedArea))raw=p.getString("routes_"+day,"[]");if(raw==null)raw="[]";return new JSONArray(raw);}catch(Exception e){return new JSONArray();}}'
if old_load not in s: raise SystemExit('v73 load anchor missing')
s=s.replace(old_load,new_load,1)

old_save='private void save(String day,JSONArray a){android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String key="routes_"+day;String old=p.getString(key,"[]");p.edit().putString("backup_"+key,old).putString(key,a.toString()).putLong("backup_time_"+day,System.currentTimeMillis()).apply();}'
new_save='private void save(String day,JSONArray a){android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);String key=routeKey(day);String old=p.getString(key,"[]");p.edit().putString("backup_"+key,old).putString(key,a.toString()).putLong("backup_time_"+key,System.currentTimeMillis()).apply();}'
if old_save not in s: raise SystemExit('v73 save anchor missing')
s=s.replace(old_save,new_save,1)

# Navigation footer now makes it clear that route/area can also be changed.
s=s.replace('🔄 Byt rutt / dag','🔄 Byt rutt / dag / område')
s=s.replace('VERSION 72 •','VERSION 73 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 72','versionCode 73').replace('versionName "72.0"','versionName "73.0"')
b.write_text(t,encoding='utf-8')
print('Version 73 applied: route/area -> weekday -> driving route, separate storage per area/day')
