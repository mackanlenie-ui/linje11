from pathlib import Path

exec(Path('scripts/version69.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Handle a route sent directly from Ruttredigeraren after the normal main UI exists.
oncreate='@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);}'
if oncreate in s:
    s=s.replace(oncreate,'@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);handleIncomingRoute(getIntent());}',1)
else:
    marker='getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);'
    if marker not in s: raise SystemExit('v70 onCreate marker not found')
    s=s.replace(marker,marker+'handleIncomingRoute(getIntent());',1)

anchor=' private void chooseFile(){'
if anchor not in s: raise SystemExit('v70 chooseFile anchor not found')
methods=''' private void handleIncomingRoute(Intent i){\n  if(i==null||!Intent.ACTION_SEND.equals(i.getAction()))return;\n  String text=i.getStringExtra(Intent.EXTRA_TEXT);\n  if(text==null||text.trim().isEmpty())return;\n  try{\n   JSONObject root=new JSONObject(text.trim());\n   if(!\"gps-ruttinspelare\".equals(root.optString(\"format\"))){Toast.makeText(this,\"Rutten har fel format\",Toast.LENGTH_LONG).show();return;}\n   JSONArray routes=load(selectedDay);\n   JSONObject item=new JSONObject();\n   item.put(\"name\",\"Redigerad rutt\");\n   item.put(\"route\",root);\n   routes.put(item);\n   save(selectedDay,routes);\n   refresh();\n   Toast.makeText(this,\"Rutten mottagen från Ruttredigeraren och sparad under \"+selectedDay,Toast.LENGTH_LONG).show();\n  }catch(Exception e){Toast.makeText(this,\"Kunde inte ta emot rutten\",Toast.LENGTH_LONG).show();}\n }\n'''
s=s.replace(anchor,methods+anchor,1)

s=s.replace('VERSION 69 •','VERSION 70 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 69','versionCode 70').replace('versionName "69.0"','versionName "70.0"')
b.write_text(t,encoding='utf-8')
print('Version 70 applied: direct route import from Ruttredigeraren')
