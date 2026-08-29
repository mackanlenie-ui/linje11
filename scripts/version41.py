from pathlib import Path

# Version 41 builds on Version 40 and adds in-place route reversing.
exec(Path('scripts/version40.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

old_menu = 'String[] opts={"✏ Byt ruttnamn","✏ Namnge stopp","🗑 Ta bort rutt"};new androidx.appcompat.app.AlertDialog.Builder(this).setTitle(n).setItems(opts,(d,w)->{if(w==0)renameRoute(index);else if(w==1)editStopNames(index);else new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Ta bort rutten?").setMessage(n).setNegativeButton("Avbryt",null).setPositiveButton("Ta bort",(x,y)->deleteRoute(index)).show();}).show();'
new_menu = 'String[] opts={"✏ Byt ruttnamn","✏ Namnge stopp","↔ Vänd rutt","🗑 Ta bort rutt"};new androidx.appcompat.app.AlertDialog.Builder(this).setTitle(n).setItems(opts,(d,w)->{if(w==0)renameRoute(index);else if(w==1)editStopNames(index);else if(w==2)new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Vänd rutten?").setMessage("Start och slut byter plats och stoppen körs i omvänd ordning.").setNegativeButton("Avbryt",null).setPositiveButton("Vänd rutt",(x,y)->reverseRoute(index)).show();else new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Ta bort rutten?").setMessage(n).setNegativeButton("Avbryt",null).setPositiveButton("Ta bort",(x,y)->deleteRoute(index)).show();}).show();'
if old_menu not in s:
    raise SystemExit('v41 route menu point not found')
s = s.replace(old_menu, new_menu, 1)

anchor = ' private void renameRoute('
if anchor not in s:
    raise SystemExit('v41 renameRoute point not found')

helper = r''' private void reverseRoute(int index){
  try{
   JSONArray routes=load(selectedDay);JSONObject item=routes.getJSONObject(index);JSONObject route=item.getJSONObject("route");
   JSONArray oldPts=route.optJSONArray("points");if(oldPts!=null){JSONArray revPts=new JSONArray();for(int i=oldPts.length()-1;i>=0;i--)revPts.put(oldPts.get(i));route.put("points",revPts);}
   JSONObject oldStart=route.optJSONObject("start"),oldEnd=route.optJSONObject("end");
   if(oldEnd!=null){JSONObject ns=new JSONObject(oldEnd.toString());ns.put("label","START");route.put("start",ns);}else route.remove("start");
   if(oldStart!=null){JSONObject ne=new JSONObject(oldStart.toString());ne.put("label","SLUT");route.put("end",ne);}else route.remove("end");
   JSONArray oldStops=route.optJSONArray("stops");JSONArray revStops=new JSONArray();
   if(oldStops!=null)for(int i=oldStops.length()-1,j=0;i>=0;i--,j++){JSONObject st=new JSONObject(oldStops.getJSONObject(i).toString());st.put("label",String.valueOf((char)('A'+Math.min(j,25))));revStops.put(st);}
   route.put("stops",revStops);item.put("route",route);routes.put(index,item);save(selectedDay,routes);refresh();Toast.makeText(this,"Rutten är vänd ✓",Toast.LENGTH_LONG).show();
  }catch(Exception e){Toast.makeText(this,"Kunde inte vända rutten",Toast.LENGTH_LONG).show();}
 }
'''
s = s.replace(anchor, helper + anchor, 1)

s = s.replace('VERSION 40 • DIREKT FRÅN GOOGLE MAPS', 'VERSION 41 • VÄND RUTT')
s = s.replace('VERSION 40 • "+selectedDay.toUpperCase()', 'VERSION 41 • "+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 40', 'versionCode 41').replace('versionName "40.0"', 'versionName "41.0"')
b.write_text(t, encoding='utf-8')

print('Version 41 applied: long-press route menu can reverse start/end, stops and fallback geometry')
