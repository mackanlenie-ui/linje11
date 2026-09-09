from pathlib import Path

exec(Path('scripts/version76.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Version 77: long-press a route/area on the first screen to rename or delete it.
# Renaming migrates all saved day routes. Deleting removes the area and all its saved routes.

insert_anchor=' private void showAreaChooser(){\n'
if insert_anchor not in s:
    raise SystemExit('v77 area chooser anchor missing')

manage_code=r''' private String areaStorageKey(String area,String day){return "routes_"+area.replace("–","-").replace(" ","_")+"_"+day;}
 private void manageAreaDialog(final String area){
  new androidx.appcompat.app.AlertDialog.Builder(this)
   .setTitle(area)
   .setItems(new String[]{"✏️ Byt namn","🗑️ Ta bort rutt / område"},(d,which)->{if(which==0)renameAreaDialog(area);else confirmDeleteArea(area);})
   .setNegativeButton("Avbryt",null).show();
 }
 private void renameAreaDialog(final String oldName){
  final EditText e=new EditText(this);e.setSingleLine(true);e.setText(oldName);e.setSelectAllOnFocus(true);e.setTextSize(18);int pad=dp(18);e.setPadding(pad,pad,pad,pad);
  new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Byt namn").setView(e).setNegativeButton("Avbryt",null).setPositiveButton("Spara",(d,w)->{
   String n=e.getText().toString().trim();if(n.isEmpty()){Toast.makeText(this,"Namnet får inte vara tomt",Toast.LENGTH_LONG).show();return;}
   JSONArray a=loadAreas();for(int i=0;i<a.length();i++){String x=a.optString(i);if(!x.equals(oldName)&&n.equalsIgnoreCase(x)){Toast.makeText(this,"Det namnet finns redan",Toast.LENGTH_LONG).show();return;}}
   android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);android.content.SharedPreferences.Editor ed=p.edit();String[] ds={"Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"};
   for(String day:ds){String oldKey=areaStorageKey(oldName,day),newKey=areaStorageKey(n,day);String raw=p.getString(oldKey,null);if(raw!=null){ed.putString(newKey,raw).remove(oldKey);}String bk="backup_"+oldKey,bn="backup_"+newKey;String br=p.getString(bk,null);if(br!=null){ed.putString(bn,br).remove(bk);}long bt=p.getLong("backup_time_"+oldKey,-1);if(bt>=0){ed.putLong("backup_time_"+newKey,bt).remove("backup_time_"+oldKey);}}
   for(int i=0;i<a.length();i++)if(oldName.equals(a.optString(i))){try{a.put(i,n);}catch(Exception ignored){}break;}ed.putString("route_areas",a.toString()).apply();selectedArea=n;showAreaChooser();Toast.makeText(this,"Namnet är ändrat",Toast.LENGTH_SHORT).show();
  }).show();
 }
 private void confirmDeleteArea(final String area){
  new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Ta bort rutt / område?").setMessage("Ta bort "+area+" och alla tillhörande körturer? Detta går inte att ångra.").setNegativeButton("Avbryt",null).setPositiveButton("Ta bort",(d,w)->deleteArea(area)).show();
 }
 private void deleteArea(String area){
  JSONArray old=loadAreas(),n=new JSONArray();for(int i=0;i<old.length();i++){String x=old.optString(i);if(!area.equals(x))n.put(x);}if(n.length()==0){Toast.makeText(this,"Minst ett område måste finnas",Toast.LENGTH_LONG).show();return;}
  android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);android.content.SharedPreferences.Editor ed=p.edit();String[] ds={"Måndag","Tisdag","Onsdag","Torsdag","Fredag","Lördag","Söndag"};for(String day:ds){String key=areaStorageKey(area,day);ed.remove(key).remove("backup_"+key).remove("backup_time_"+key);}ed.putString("route_areas",n.toString()).apply();selectedArea=n.optString(0,"Lenninge–Kilafors");showAreaChooser();Toast.makeText(this,"Området är borttaget",Toast.LENGTH_SHORT).show();
 }
'''
s=s.replace(insert_anchor,manage_code+insert_anchor,1)

old='b.setOnClickListener(v->{selectedArea=area;showDayChooserForArea();});list.addView(b,lp);'
new='b.setOnClickListener(v->{selectedArea=area;showDayChooserForArea();});b.setOnLongClickListener(v->{manageAreaDialog(area);return true;});list.addView(b,lp);'
if old not in s:
    raise SystemExit('v77 area button anchor missing')
s=s.replace(old,new,1)

s=s.replace('VERSION 76 • VÄLJ RUTT / OMRÅDE','VERSION 77 • VÄLJ RUTT / OMRÅDE',1)
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 76','versionCode 77').replace('versionName "76.0"','versionName "77.0"')
b.write_text(t,encoding='utf-8')
print('Version 77 applied: long-press route/area to rename or delete with confirmation')
