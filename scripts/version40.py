from pathlib import Path

# Version 40 builds on the proven Version 39 Google Maps link importer.
exec(Path('scripts/version39.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

old_oncreate = '@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);}'
new_oncreate = '@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);handleSharedRouteIntent(getIntent());}'
if old_oncreate not in s:
    raise SystemExit('v40 onCreate point not found')
s = s.replace(old_oncreate, new_oncreate, 1)

anchor = ' private void showMain(){'
if anchor not in s:
    raise SystemExit('v40 showMain point not found')

helper = r''' @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);handleSharedRouteIntent(intent);}
 private void handleSharedRouteIntent(Intent intent){if(intent==null||!Intent.ACTION_SEND.equals(intent.getAction()))return;String type=intent.getType();if(type!=null&&!type.startsWith("text/"))return;String shared=intent.getStringExtra(Intent.EXTRA_TEXT);if(shared==null||shared.trim().isEmpty())return;intent.removeExtra(Intent.EXTRA_TEXT);final String text=shared.trim();new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(()->showSharedGoogleMapsImport(text),250);}
 private void showSharedGoogleMapsImport(String text){final int[]pick={Math.max(0,java.util.Arrays.asList(days).indexOf(selectedDay))};new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Importera Google Maps-rutt").setMessage("Välj vilken dag rutten ska sparas på.").setSingleChoiceItems(days,pick[0],(d,w)->pick[0]=w).setNegativeButton("Avbryt",null).setPositiveButton("Importera",(d,w)->{selectedDay=days[pick[0]];if(daySpinner!=null)daySpinner.setSelection(pick[0]);importGoogleMaps(text);}).show();}
'''
s = s.replace(anchor, helper + anchor, 1)

s = s.replace('VERSION 39 • GOOGLE MAPS-IMPORT', 'VERSION 40 • DIREKT FRÅN GOOGLE MAPS')
s = s.replace('VERSION 39 • "+selectedDay.toUpperCase()', 'VERSION 40 • "+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

manifest = Path('app/src/main/AndroidManifest.xml')
m = manifest.read_text(encoding='utf-8')
m = m.replace('<activity android:name=".MainActivity" android:exported="true">', '<activity android:name=".MainActivity" android:exported="true" android:launchMode="singleTop">', 1)
launcher = '''            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>'''
share = launcher + '''\n            <intent-filter>\n                <action android:name="android.intent.action.SEND" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <data android:mimeType="text/plain" />\n            </intent-filter>'''
if launcher not in m:
    raise SystemExit('v40 manifest launcher filter not found')
m = m.replace(launcher, share, 1)
manifest.write_text(m, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 39', 'versionCode 40').replace('versionName "39.0"', 'versionName "40.0"')
b.write_text(t, encoding='utf-8')

print('Version 40 applied: share Google Maps directions directly to Rutt GPS and choose weekday')
