from pathlib import Path

exec(Path('scripts/version70.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Replace the v70 onCreate call so a recognized editor share is consumed.
needle='handleIncomingRoute(getIntent());'
if needle not in s:
    raise SystemExit('v71 incoming route call not found')
s=s.replace(needle,'if(handleIncomingRouteV71(getIntent())){getIntent().setAction(null);getIntent().removeExtra(Intent.EXTRA_TEXT);}',1)

# Keep v70's handler untouched for build safety; add a stricter V71 handler and
# use it from onCreate/onNewIntent. JSON is recognized before any URL logic.
anchor=' private void chooseFile(){'
if anchor not in s:
    raise SystemExit('v71 chooseFile anchor not found')
methods=''' @Override protected void onNewIntent(Intent i){
  super.onNewIntent(i); setIntent(i); showMain();
  if(handleIncomingRouteV71(i)){i.setAction(null);i.removeExtra(Intent.EXTRA_TEXT);}
 }
 private boolean handleIncomingRouteV71(Intent i){
  if(i==null||!Intent.ACTION_SEND.equals(i.getAction()))return false;
  String text=i.getStringExtra(Intent.EXTRA_TEXT);
  if(text==null||text.trim().isEmpty())return false;
  String raw=text.trim();
  if(!raw.startsWith("{"))return false;
  try{
   JSONObject root=new JSONObject(raw);
   if(!"gps-ruttinspelare".equals(root.optString("format")))return false;
   JSONArray pts=root.optJSONArray("points");
   if(pts==null||pts.length()<2){Toast.makeText(this,"Rutten saknar GPS-punkter",Toast.LENGTH_LONG).show();return true;}
   JSONArray routes=load(selectedDay);
   JSONObject item=new JSONObject();
   item.put("name","Redigerad rutt");
   item.put("route",root);
   routes.put(item);
   save(selectedDay,routes);
   refresh();
   Toast.makeText(this,"Rutten mottagen från Ruttredigeraren och sparad under "+selectedDay,Toast.LENGTH_LONG).show();
   return true;
  }catch(Exception e){Toast.makeText(this,"Kunde inte läsa rutten från Ruttredigeraren",Toast.LENGTH_LONG).show();return true;}
 }
'''
s=s.replace(anchor,methods+anchor,1)
s=s.replace('VERSION 70 •','VERSION 71 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 70','versionCode 71').replace('versionName "70.0"','versionName "71.0"')
b.write_text(t,encoding='utf-8')
print('Version 71 applied: editor JSON share handled before legacy import')
