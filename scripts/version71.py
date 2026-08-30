from pathlib import Path

exec(Path('scripts/version70.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Version 71: consume the Ruttredigeraren JSON share before any legacy share/import
# handler can mistake it for a Google Maps share. Also handle delivery to an
# already-running Rutt GPS activity.
old='@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);handleIncomingRoute(getIntent());}'
new='@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);if(handleIncomingRoute(getIntent())){getIntent().setAction(null);getIntent().removeExtra(Intent.EXTRA_TEXT);}}'
if old not in s:
    raise SystemExit('v71 onCreate v70 block not found')
s=s.replace(old,new,1)

old_method=''' private void handleIncomingRoute(Intent i){
  if(i==null||!Intent.ACTION_SEND.equals(i.getAction()))return;
  String text=i.getStringExtra(Intent.EXTRA_TEXT);
  if(text==null||text.trim().isEmpty())return;
  try{
   JSONObject root=new JSONObject(text.trim());
   if(!"gps-ruttinspelare".equals(root.optString("format"))){Toast.makeText(this,"Rutten har fel format",Toast.LENGTH_LONG).show();return;}
   JSONArray routes=load(selectedDay);
   JSONObject item=new JSONObject();
   item.put("name","Redigerad rutt");
   item.put("route",root);
   routes.put(item);
   save(selectedDay,routes);
   refresh();
   Toast.makeText(this,"Rutten mottagen från Ruttredigeraren och sparad under "+selectedDay,Toast.LENGTH_LONG).show();
  }catch(Exception e){Toast.makeText(this,"Kunde inte ta emot rutten",Toast.LENGTH_LONG).show();}
 }
'''
new_method=''' @Override protected void onNewIntent(Intent i){
  super.onNewIntent(i); setIntent(i); showMain();
  if(handleIncomingRoute(i)){i.setAction(null);i.removeExtra(Intent.EXTRA_TEXT);}
 }
 private boolean handleIncomingRoute(Intent i){
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
if old_method not in s:
    raise SystemExit('v71 v70 handler not found')
s=s.replace(old_method,new_method,1)

s=s.replace('VERSION 70 •','VERSION 71 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 70','versionCode 71').replace('versionName "70.0"','versionName "71.0"')
b.write_text(t,encoding='utf-8')
print('Version 71 applied: Ruttredigeraren JSON shares consumed before legacy import')
