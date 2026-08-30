from pathlib import Path

exec(Path('scripts/version70.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V71 integrates with the existing v40 ACTION_SEND handler instead of adding a
# second onNewIntent. Recognized editor JSON is consumed there before Maps UI.
old='private void handleSharedRouteIntent(Intent intent){if(intent==null||!Intent.ACTION_SEND.equals(intent.getAction()))return;String type=intent.getType();if(type!=null&&!type.startsWith("text/"))return;String shared=intent.getStringExtra(Intent.EXTRA_TEXT);if(shared==null||shared.trim().isEmpty())return;intent.removeExtra(Intent.EXTRA_TEXT);final String text=shared.trim();new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->showSharedGoogleMapsImport(text),250);}'
new='private void handleSharedRouteIntent(Intent intent){if(intent==null||!Intent.ACTION_SEND.equals(intent.getAction()))return;String type=intent.getType();if(type!=null&&!type.startsWith("text/"))return;String shared=intent.getStringExtra(Intent.EXTRA_TEXT);if(shared==null||shared.trim().isEmpty())return;final String text=shared.trim();if(text.startsWith("{")&&handleEditorRouteJson(text)){intent.removeExtra(Intent.EXTRA_TEXT);intent.setAction(null);return;}intent.removeExtra(Intent.EXTRA_TEXT);new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->showSharedGoogleMapsImport(text),250);}'
if old not in s:
    raise SystemExit('v71 existing shared intent handler not found')
s=s.replace(old,new,1)

anchor=' private void chooseFile(){'
if anchor not in s: raise SystemExit('v71 chooseFile anchor not found')
helper=''' private boolean handleEditorRouteJson(String raw){
  try{
   JSONObject root=new JSONObject(raw);
   if(!"gps-ruttinspelare".equals(root.optString("format")))return false;
   JSONArray pts=root.optJSONArray("points");
   if(pts==null||pts.length()<2){Toast.makeText(this,"Rutten saknar GPS-punkter",Toast.LENGTH_LONG).show();return true;}
   JSONArray routes=load(selectedDay);
   JSONObject item=new JSONObject();
   item.put("name","Redigerad rutt");
   item.put("route",root);
   routes.put(item); save(selectedDay,routes); refresh();
   Toast.makeText(this,"Rutten mottagen från Ruttredigeraren och sparad under "+selectedDay,Toast.LENGTH_LONG).show();
   return true;
  }catch(Exception e){Toast.makeText(this,"Kunde inte läsa rutten från Ruttredigeraren",Toast.LENGTH_LONG).show();return true;}
 }
'''
s=s.replace(anchor,helper+anchor,1)

# V70 also invokes its own direct handler from onCreate. Remove that call: the
# established onResume share pipeline above now owns all ACTION_SEND handling.
s=s.replace('handleIncomingRoute(getIntent());','',1)
s=s.replace('VERSION 70 •','VERSION 71 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 70','versionCode 71').replace('versionName "70.0"','versionName "71.0"')
b.write_text(t,encoding='utf-8')
print('Version 71 applied: Ruttredigeraren JSON handled before Google Maps share import')
