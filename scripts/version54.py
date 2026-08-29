from pathlib import Path

exec(Path('scripts/version53.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Keep a live reference to the navigation WebView and receive native foreground-service GPS fixes.
class_anchor='public class MainActivity extends AppCompatActivity {'
fields=r'''public class MainActivity extends AppCompatActivity {
 private WebView activeWeb;
 private boolean navReceiverRegistered=false;
 private final android.content.BroadcastReceiver navLocationReceiver=new android.content.BroadcastReceiver(){@Override public void onReceive(android.content.Context c,android.content.Intent i){if(i==null||!NavigationService.ACTION_LOCATION.equals(i.getAction()))return;pushNativeLocation(i.getDoubleExtra("lat",0),i.getDoubleExtra("lon",0),i.getFloatExtra("acc",999f),i.getFloatExtra("speed",0f),i.getFloatExtra("bearing",-1f));}};
 private void registerNavigationReceiver(){if(navReceiverRegistered)return;android.content.IntentFilter f=new android.content.IntentFilter(NavigationService.ACTION_LOCATION);if(android.os.Build.VERSION.SDK_INT>=33)registerReceiver(navLocationReceiver,f,android.content.Context.RECEIVER_NOT_EXPORTED);else registerReceiver(navLocationReceiver,f);navReceiverRegistered=true;}
 private void startNavigationService(){try{android.content.Intent i=new android.content.Intent(this,NavigationService.class);if(android.os.Build.VERSION.SDK_INT>=26)startForegroundService(i);else startService(i);}catch(Exception ignored){}}
 private void pushNativeLocation(double lat,double lon,float acc,float speed,float bearing){if(activeWeb==null)return;final String js=String.format(java.util.Locale.US,"if(typeof applyNativeLocation==='function')applyNativeLocation(%.7f,%.7f,%.2f,%.3f,%.2f);",lat,lon,acc,speed,bearing);activeWeb.post(()->{try{activeWeb.evaluateJavascript(js,null);}catch(Exception ignored){}});}
 private void pushLatestNativeLocation(){try{android.content.SharedPreferences p=getSharedPreferences("nav_bg",MODE_PRIVATE);long t=p.getLong("time",0);if(t>0&&System.currentTimeMillis()-t<120000)pushNativeLocation(p.getFloat("lat",0),p.getFloat("lon",0),p.getFloat("acc",999),p.getFloat("speed",0),p.getFloat("bearing",-1));}catch(Exception ignored){}}
'''
if class_anchor not in s: raise SystemExit('v54 class anchor not found')
s=s.replace(class_anchor,fields,1)

# Register receiver as soon as the activity is created.
s=s.replace('super.onCreate(b);','super.onCreate(b);registerNavigationReceiver();',1)

# Start foreground navigation whenever a route map is opened.
old_web='WebView web=new WebView(this);'
new_web='WebView web=new WebView(this);activeWeb=web;startNavigationService();'
if old_web not in s: raise SystemExit('v54 WebView anchor not found')
s=s.replace(old_web,new_web,1)

# Existing Google Maps sharing onResume from V40: also fully wake WebView timers and inject
# the latest native GPS fix immediately when returning from background.
old_resume='@Override protected void onResume(){super.onResume();handleSharedRouteIntent(getIntent());}'
new_resume='@Override protected void onResume(){super.onResume();handleSharedRouteIntent(getIntent());if(activeWeb!=null){try{activeWeb.onResume();activeWeb.resumeTimers();}catch(Exception ignored){}pushLatestNativeLocation();}}'
if old_resume not in s: raise SystemExit('v54 onResume anchor not found')
s=s.replace(old_resume,new_resume,1)

# Feed native service fixes into the same navigation state used by the foreground GPS watcher.
watch='preloadRouteData();navigator.geolocation.watchPosition(function(pos){'
helper=r'''function applyNativeLocation(lat,lon,acc,speed,bearing){try{if(!isFinite(lat)||!isFinite(lon))return;var rawAcc=Number(acc||999);if(rawAcc>70)return;var rawGps=[Number(lat),Number(lon)],sp=Number(speed||0);if(lastGps&&km(lastGps,rawGps)*1000>180&&sp<15)return;lastGps=rawGps;lastAccuracy=rawAcc;lastSpeed=sp*3.6;if(bearing!=null&&Number(bearing)>=0)lastHeading=Number(bearing);var livePlanned=plannedTurn();if(livePlanned)nextTurn=livePlanned;else if(!nextTurn)nextTurn=offlineTurn();checkOffRoute();info();}catch(e){}}'''
if watch not in s: raise SystemExit('v54 watcher anchor not found')
s=s.replace(watch,helper+watch,1)

# Clean up only the activity receiver. The START_STICKY foreground service deliberately remains
# alive so navigation continues while Rutt GPS is in the background.
back_anchor='@Override public void onBackPressed()'
cleanup='@Override protected void onDestroy(){if(navReceiverRegistered){try{unregisterReceiver(navLocationReceiver);}catch(Exception ignored){}navReceiverRegistered=false;}super.onDestroy();}\n '
if back_anchor not in s: raise SystemExit('v54 onBackPressed anchor not found')
s=s.replace(back_anchor,cleanup+back_anchor,1)

s=s.replace('VERSION 53 • LIVE NEDRÄKNING','VERSION 54 • BAKGRUNDSNAVIGATION')
for n in range(1,54):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 54 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 54 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 54 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

manifest=Path('app/src/main/AndroidManifest.xml')
m=manifest.read_text(encoding='utf-8')
perm='    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />'
extra='''    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />\n    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />\n    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />'''
if 'android.permission.FOREGROUND_SERVICE_LOCATION' not in m:
    if perm not in m: raise SystemExit('v54 manifest permission anchor not found')
    m=m.replace(perm,extra,1)
service='        <service android:name=".NavigationService" android:exported="false" android:foregroundServiceType="location" />\n'
if '.NavigationService' not in m:
    if '    </application>' not in m: raise SystemExit('v54 application anchor not found')
    m=m.replace('    </application>',service+'    </application>',1)
manifest.write_text(m,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 53','versionCode 54').replace('versionName "53.0"','versionName "54.0"')
b.write_text(t,encoding='utf-8')
print('Version 54 applied: native foreground GPS service, background location bridge and WebView resume sync')
