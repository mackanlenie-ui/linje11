from pathlib import Path
import re
exec(Path('scripts/version18.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Native Android location bridge. This removes WebView geolocation as the
# single point of failure while keeping it as a fallback.
s=s.replace('import android.net.Uri;\n','import android.net.Uri;\nimport android.location.Location;\nimport android.location.LocationListener;\nimport android.location.LocationManager;\n',1)
s=s.replace('private LinearLayout routeList; private Spinner daySpinner; private String selectedDay="Måndag"; private JSONObject pendingRoute;',
'''private LinearLayout routeList; private Spinner daySpinner; private String selectedDay="Måndag"; private JSONObject pendingRoute;
 private WebView navWeb; private LocationManager locationManager; private LocationListener nativeLocationListener;''',1)

# Patch the existing generated showMap method in small, stable pieces.
s=s.replace('WebView web=new WebView(this);WebSettings s=web.getSettings();','WebView web=new WebView(this);navWeb=web;WebSettings s=web.getSettings();',1)
s=s.replace('s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);','s.setDomStorageEnabled(true);s.setDatabaseEnabled(true);s.setGeolocationEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setAllowUniversalAccessFromFileURLs(true);',1)
s=s.replace('web.setWebViewClient(new WebViewClient());','web.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView v,String url){super.onPageFinished(v,url);startNativeGps();}});',1)
s=s.replace('web.loadDataWithBaseURL("https://linje11.local/",mapHtml(route),"text/html","UTF-8",null);','web.loadDataWithBaseURL("file:///android_asset/",mapHtml(route),"text/html","UTF-8",null);',1)

# Add native GPS delivery method before mapHtml.
needle=' private String mapHtml(JSONObject route)throws Exception{'
bridge=''' private void startNativeGps(){
  if(navWeb==null)return;
  if(android.os.Build.VERSION.SDK_INT>=23&&checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)return;
  try{
   locationManager=(LocationManager)getSystemService(LOCATION_SERVICE);
   if(nativeLocationListener!=null)try{locationManager.removeUpdates(nativeLocationListener);}catch(Exception ignored){}
   nativeLocationListener=new LocationListener(){@Override public void onLocationChanged(Location l){if(navWeb==null)return;final double lat=l.getLatitude(),lon=l.getLongitude();final float acc=l.hasAccuracy()?l.getAccuracy():10f,sp=l.hasSpeed()?l.getSpeed():0f,br=l.hasBearing()?l.getBearing():0f;runOnUiThread(()->navWeb.evaluateJavascript("if(window.nativeGps){window.nativeGps("+lat+","+lon+","+acc+","+sp+","+br+");}",null));}};
   try{locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER,1000,1,nativeLocationListener);}catch(Exception ignored){}
   try{locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,1500,2,nativeLocationListener);}catch(Exception ignored){}
   Location l=null;try{l=locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER);}catch(Exception ignored){}if(l==null)try{l=locationManager.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);}catch(Exception ignored){}if(l!=null)nativeLocationListener.onLocationChanged(l);
  }catch(Exception ignored){}
 }
'''
if needle not in s: raise SystemExit('v20 mapHtml point not found')
s=s.replace(needle,bridge+needle,1)

# Leaflet is bundled inside the APK by the workflow, so navigation no longer
# depends on a CDN being reachable when the route opens.
s=s.replace("<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'>","<link rel='stylesheet' href='leaflet.css'>",1)
s=s.replace("<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>","<script src='leaflet.js'></script>",1)

# Remove any remaining voice calls completely.
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\s*\}\s*catch\(e\)\{\}","",s)
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\}\s*catch\(e\)\{\}","",s)

# Both native Android GPS and navigator.geolocation feed the same handler.
if 'navigator.geolocation.watchPosition(function(pos){' not in s: raise SystemExit('v20 GPS watcher start not found')
s=s.replace('navigator.geolocation.watchPosition(function(pos){','function handleGps(pos){',1)
old_tail="},function(){document.getElementById('gpsStatus').textContent='GPS kunde inte hämtas';},{enableHighAccuracy:true,maximumAge:1000,timeout:10000});info();"
new_tail="}window.nativeGps=function(lat,lon,accuracy,speed,heading){handleGps({coords:{latitude:lat,longitude:lon,accuracy:accuracy||10,speed:speed||0,heading:heading}});};try{navigator.geolocation.watchPosition(handleGps,function(){document.getElementById('gpsStatus').textContent='🛰️ Android GPS startas…';},{enableHighAccuracy:true,maximumAge:1000,timeout:15000});}catch(e){}info();"
if old_tail not in s: raise SystemExit('v20 GPS watcher end not found')
s=s.replace(old_tail,new_tail,1)

# Route is rendered immediately; GPS status becomes explicit if the first fix
# takes a moment.
s=s.replace('loadRoadLine();function handleGps(pos){',"loadRoadLine();setTimeout(function(){try{map.invalidateSize();}catch(e){}if(!lastGps){document.getElementById('gpsStatus').textContent='🛰️ Väntar på Android GPS…';document.getElementById('status').textContent='Rutten visas medan GPS startar';}},1800);function handleGps(pos){",1)

s=s.replace('VERSION 18 • RUTTBIBLIOTEK','VERSION 20 • RUTTBIBLIOTEK')
s=s.replace('VERSION 18 • \"+selectedDay.toUpperCase()','VERSION 20 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 18','versionCode 20').replace('versionName \"18.0\"','versionName \"20.0\"')
b.write_text(t,encoding='utf-8')
