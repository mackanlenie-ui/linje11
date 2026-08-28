from pathlib import Path
exec(Path('scripts/version18.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Native Android location bridge. This removes the WebView geolocation API as
# a single point of failure while keeping it as a fallback.
s=s.replace('import android.net.Uri;\n','import android.net.Uri;\nimport android.location.Location;\nimport android.location.LocationListener;\nimport android.location.LocationManager;\n')
s=s.replace(' private LinearLayout routeList; private Spinner daySpinner; private String selectedDay="Måndag"; private JSONObject pendingRoute;',
''' private LinearLayout routeList; private Spinner daySpinner; private String selectedDay="Måndag"; private JSONObject pendingRoute;
 private WebView navWeb; private LocationManager locationManager; private LocationListener nativeLocationListener;''')

old_show=''' private void showMap(JSONObject route)throws Exception{WebView web=new WebView(this);WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);web.setWebViewClient(new WebViewClient());web.setWebChromeClient(new WebChromeClient(){@Override public void onGeolocationPermissionsShowPrompt(String origin,GeolocationPermissions.Callback cb){cb.invoke(origin,true,false);}});web.addJavascriptInterface(new Object(){@JavascriptInterface public void chooseRoute(){runOnUiThread(()->showMain());}@JavascriptInterface public void speakMessage(String m){runOnUiThread(()->{if(tts!=null)tts.speak(m,TextToSpeech.QUEUE_FLUSH,null,"nav");});}},"Android");web.loadDataWithBaseURL("https://linje11.local/",mapHtml(route),"text/html","UTF-8",null);setContentView(web);}'''
if old_show not in s:
    # Version 18 has voice removed from the bridge.
    old_show=''' private void showMap(JSONObject route)throws Exception{WebView web=new WebView(this);WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setGeolocationEnabled(true);web.setWebViewClient(new WebViewClient());web.setWebChromeClient(new WebChromeClient(){@Override public void onGeolocationPermissionsShowPrompt(String origin,GeolocationPermissions.Callback cb){cb.invoke(origin,true,false);}});web.addJavascriptInterface(new Object(){@JavascriptInterface public void chooseRoute(){runOnUiThread(()->showMain());}},"Android");web.loadDataWithBaseURL("https://linje11.local/",mapHtml(route),"text/html","UTF-8",null);setContentView(web);}'''
new_show=''' private void showMap(JSONObject route)throws Exception{WebView web=new WebView(this);navWeb=web;WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setDatabaseEnabled(true);s.setGeolocationEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(true);s.setAllowUniversalAccessFromFileURLs(true);web.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView v,String url){super.onPageFinished(v,url);startNativeGps();}});web.setWebChromeClient(new WebChromeClient(){@Override public void onGeolocationPermissionsShowPrompt(String origin,GeolocationPermissions.Callback cb){cb.invoke(origin,true,false);}});web.addJavascriptInterface(new Object(){@JavascriptInterface public void chooseRoute(){runOnUiThread(()->showMain());}},"Android");web.loadDataWithBaseURL("file:///android_asset/",mapHtml(route),"text/html","UTF-8",null);setContentView(web);}'''
if old_show not in s: raise SystemExit('v20 showMap point not found')
s=s.replace(old_show,new_show,1)

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

# Bundle Leaflet inside the APK, avoiding CDN failures that leave the map blank.
s=s.replace("<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'>","<link rel='stylesheet' href='leaflet.css'>")
s=s.replace("<script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>","<script src='leaflet.js'></script>")

# Refactor GPS success callback so both native Android GPS and WebView GPS feed
# exactly the same navigation code.
s=s.replace('navigator.geolocation.watchPosition(function(pos){','function handleGps(pos){',1)
old_tail="},function(){document.getElementById('gpsStatus').textContent='GPS kunde inte hämtas';},{enableHighAccuracy:true,maximumAge:1000,timeout:10000});info();"
new_tail="}window.nativeGps=function(lat,lon,accuracy,speed,heading){handleGps({coords:{latitude:lat,longitude:lon,accuracy:accuracy||10,speed:speed||0,heading:heading}});};try{navigator.geolocation.watchPosition(handleGps,function(){document.getElementById('gpsStatus').textContent='🛰️ Android GPS startas…';},{enableHighAccuracy:true,maximumAge:1000,timeout:15000});}catch(e){}info();"
if old_tail not in s: raise SystemExit('v20 GPS callback tail not found')
s=s.replace(old_tail,new_tail,1)

# Visible startup fallback: if native GPS is slow, route/map still remain usable.
s=s.replace('loadRoadLine();function handleGps(pos){',"loadRoadLine();setTimeout(function(){try{map.invalidateSize();}catch(e){}if(!lastGps){document.getElementById('gpsStatus').textContent='🛰️ Väntar på Android GPS…';document.getElementById('status').textContent='Rutten visas medan GPS startar';}},1800);function handleGps(pos){",1)

s=s.replace('VERSION 18 • RUTTBIBLIOTEK','VERSION 20 • RUTTBIBLIOTEK')
s=s.replace('VERSION 18 • \"+selectedDay.toUpperCase()','VERSION 20 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 18','versionCode 20').replace('versionName \"18.0\"','versionName \"20.0\"')
b.write_text(t,encoding='utf-8')
