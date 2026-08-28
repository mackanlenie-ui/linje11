from pathlib import Path
exec(Path('scripts/version20.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V21: start native Android GPS immediately when the WebView is created,
# instead of waiting for WebView/Leaflet onPageFinished. This breaks the
# startup deadlock seen on-device while keeping the existing JS bridge.
s=s.replace('web.loadDataWithBaseURL("file:///android_asset/",mapHtml(route),"text/html","UTF-8",null);setContentView(web);',
'''setContentView(web);startNativeGps();web.loadDataWithBaseURL("file:///android_asset/",mapHtml(route),"text/html","UTF-8",null);''',1)

# Cache the newest native fix until JavaScript has fully initialized.
s=s.replace('private WebView navWeb; private LocationManager locationManager; private LocationListener nativeLocationListener;',
'''private WebView navWeb; private LocationManager locationManager; private LocationListener nativeLocationListener; private Location lastNativeLocation;''',1)
s=s.replace('@Override public void onLocationChanged(Location l){if(navWeb==null)return;final double lat=l.getLatitude()',
'''@Override public void onLocationChanged(Location l){lastNativeLocation=l;if(navWeb==null)return;final double lat=l.getLatitude()''',1)

# onPageFinished replays the latest Android fix after Leaflet/JS is ready.
s=s.replace('onPageFinished(WebView v,String url){super.onPageFinished(v,url);startNativeGps();}',
'''onPageFinished(WebView v,String url){super.onPageFinished(v,url);startNativeGps();if(lastNativeLocation!=null){Location l=lastNativeLocation;final double lat=l.getLatitude(),lon=l.getLongitude();final float acc=l.hasAccuracy()?l.getAccuracy():10f,sp=l.hasSpeed()?l.getSpeed():0f,br=l.hasBearing()?l.getBearing():0f;v.evaluateJavascript("if(window.nativeGps){window.nativeGps("+lat+","+lon+","+acc+","+sp+","+br+");}",null);}}''',1)

# Make JS readiness visible and prevent a silent blank state.
s=s.replace("var map=L.map('map',{zoomControl:true});", "document.getElementById('gpsStatus').textContent='🗺️ Kartan startad • väntar på GPS';var map=L.map('map',{zoomControl:true});",1)
s=s.replace("document.getElementById('gpsStatus').textContent='🔵 GPS hittad • ±'+Math.round(pos.coords.accuracy)+' m';", "document.getElementById('gpsStatus').textContent='🔵 Android GPS • ±'+Math.round(pos.coords.accuracy)+' m';document.getElementById('status').textContent='GPS klar';",1)

s=s.replace('VERSION 20 • RUTTBIBLIOTEK','VERSION 21 • RUTTBIBLIOTEK').replace('VERSION 20 • \"+selectedDay.toUpperCase()','VERSION 21 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 20','versionCode 21').replace('versionName \"20.0\"','versionName \"21.0\"')
b.write_text(t,encoding='utf-8')
