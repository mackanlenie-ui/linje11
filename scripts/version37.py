from pathlib import Path

# Build on the finished Version 36 navigation app.
exec(Path('scripts/version36.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Imports needed for Google Maps link import.
s = s.replace('import java.nio.charset.StandardCharsets;', '''import java.nio.charset.StandardCharsets;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;''', 1)

# Handle a Google Maps link shared directly to Rutt GPS.
old_create = '@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);}'
new_create = '''@Override protected void onCreate(Bundle b){super.onCreate(b);showMain();getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);handleSharedGoogleMaps(getIntent());}
 @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);handleSharedGoogleMaps(intent);}'''
if old_create not in s:
    raise SystemExit('v37 onCreate point not found')
s = s.replace(old_create, new_create, 1)

# Wire the new Google Maps import button.
old_show = 'findViewById(R.id.btnImport).setOnClickListener(v->chooseFile());refresh();}'
new_show = 'findViewById(R.id.btnImport).setOnClickListener(v->chooseFile());android.view.View gm=findViewById(R.id.btnGoogleMaps);if(gm!=null)gm.setOnClickListener(v->showGoogleMapsPasteDialog(null));refresh();}'
if old_show not in s:
    raise SystemExit('v37 showMain button point not found')
s = s.replace(old_show, new_show, 1)

# Insert complete Google Maps importer before the existing JSON file chooser.
anchor = ' private void chooseFile(){'
if anchor not in s:
    raise SystemExit('v37 importer insertion point not found')
helper = r''' private static class GPoint { double lat,lon; String name; GPoint(double a,double o,String n){lat=a;lon=o;name=n;} }
 private static class GRoute { final ArrayList<GPoint> points=new ArrayList<>(); String sourceUrl; }

 private void handleSharedGoogleMaps(Intent intent){
  if(intent==null||!Intent.ACTION_SEND.equals(intent.getAction())||!"text/plain".equals(intent.getType()))return;
  String text=intent.getStringExtra(Intent.EXTRA_TEXT);
  if(text!=null&&(text.contains("google.")||text.contains("goo.gl")||text.contains("maps.app")))showGoogleMapsPasteDialog(text);
 }

 private void showGoogleMapsPasteDialog(String preset){
  final LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);int pad=(int)(16*getResources().getDisplayMetrics().density);box.setPadding(pad,pad/2,pad,pad/2);
  final EditText input=new EditText(this);input.setHint("Klistra in Google Maps-länk");input.setSingleLine(false);input.setMinLines(2);if(preset!=null)input.setText(preset);box.addView(input);
  final TextView dayLabel=new TextView(this);dayLabel.setText("Spara rutten på dag:");dayLabel.setPadding(0,pad/2,0,0);box.addView(dayLabel);
  final Spinner sp=new Spinner(this);ArrayAdapter<String>a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);sp.setAdapter(a);int pos=java.util.Arrays.asList(days).indexOf(selectedDay);sp.setSelection(Math.max(0,pos));box.addView(sp);
  new android.app.AlertDialog.Builder(this).setTitle("Importera från Google Maps").setView(box).setNegativeButton("Avbryt",null).setPositiveButton("Importera",null).create().setOnShowListener(d->{android.app.AlertDialog ad=(android.app.AlertDialog)d;ad.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String link=input.getText().toString().trim();if(link.isEmpty()){input.setError("Klistra in en Google Maps-länk");return;}String day=days[sp.getSelectedItemPosition()];ad.dismiss();importGoogleMapsRoute(link,day);});});
  android.app.AlertDialog dialog=new android.app.AlertDialog.Builder(this).setTitle("Importera från Google Maps").setView(box).setNegativeButton("Avbryt",null).setPositiveButton("Importera",null).create();
  dialog.setOnShowListener(d->dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String link=input.getText().toString().trim();if(link.isEmpty()){input.setError("Klistra in en Google Maps-länk");return;}String day=days[sp.getSelectedItemPosition()];dialog.dismiss();importGoogleMapsRoute(link,day);}));
  dialog.show();
 }

 private void importGoogleMapsRoute(String sharedText,String day){
  final android.app.ProgressDialog pd=new android.app.ProgressDialog(this);pd.setMessage("Importerar Google Maps-rutt…");pd.setCancelable(false);pd.show();
  new Thread(()->{try{
    String link=extractGoogleMapsUrl(sharedText);String resolved=resolveRedirects(link);GRoute gr=parseGoogleRoute(resolved);if(gr.points.size()<2)throw new Exception("Hittade inte minst två platser i länken");
    JSONObject route=buildImportedRoute(gr);String name="Google Maps • "+new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm",Locale.getDefault()).format(new java.util.Date());
    runOnUiThread(()->{pd.dismiss();try{JSONArray routes=load(day);JSONObject item=new JSONObject();item.put("name",name);item.put("route",route);routes.put(item);save(day,routes);selectedDay=day;showMain();Toast.makeText(this,"Google Maps-rutten importerades till "+day,Toast.LENGTH_LONG).show();}catch(Exception e){Toast.makeText(this,"Kunde inte spara den importerade rutten",Toast.LENGTH_LONG).show();}});
  }catch(Exception e){runOnUiThread(()->{pd.dismiss();new android.app.AlertDialog.Builder(this).setTitle("Importen misslyckades").setMessage(e.getMessage()==null?"Kunde inte läsa Google Maps-rutten.":e.getMessage()).setPositiveButton("OK",null).show();});}}).start();
 }

 private String extractGoogleMapsUrl(String text)throws Exception{
  java.util.regex.Matcher m=java.util.regex.Pattern.compile("https?://[^\\s]+",java.util.regex.Pattern.CASE_INSENSITIVE).matcher(text);
  if(!m.find())throw new Exception("Ingen webblänk hittades.");String u=m.group();while(u.endsWith(")")||u.endsWith(".")||u.endsWith(","))u=u.substring(0,u.length()-1);return u;
 }

 private String resolveRedirects(String input)throws Exception{
  String cur=input;for(int i=0;i<8;i++){HttpURLConnection c=(HttpURLConnection)new URL(cur).openConnection();c.setInstanceFollowRedirects(false);c.setConnectTimeout(10000);c.setReadTimeout(10000);c.setRequestProperty("User-Agent","Mozilla/5.0 RuttGPS/37");int code=c.getResponseCode();String loc=c.getHeaderField("Location");c.disconnect();if(code>=300&&code<400&&loc!=null){cur=new URL(new URL(cur),loc).toString();continue;}break;}return cur;
 }

 private GRoute parseGoogleRoute(String url)throws Exception{
  GRoute out=new GRoute();out.sourceUrl=url;Uri u=Uri.parse(url);ArrayList<String> names=new ArrayList<>();String origin=u.getQueryParameter("origin"),destination=u.getQueryParameter("destination"),way=u.getQueryParameter("waypoints");
  if(destination!=null){if(origin!=null&&!origin.trim().isEmpty())names.add(origin);else{GPoint p=getLastKnownPoint();if(p!=null)out.points.add(p);}if(way!=null&&!way.trim().isEmpty())for(String w:way.split("\\|"))if(!w.trim().isEmpty())names.add(w);names.add(destination);}else{
   String decoded=URLDecoder.decode(url,"UTF-8");int di=decoded.indexOf("/maps/dir/");if(di>=0){String tail=decoded.substring(di+10);int q=tail.indexOf('?');if(q>=0)tail=tail.substring(0,q);String[] seg=tail.split("/");for(String x:seg){String z=x.trim();if(z.isEmpty())continue;if(z.startsWith("@")||z.startsWith("data="))break;if(z.startsWith("data!"))break;names.add(z.replace('+',' '));}}
  }
  for(String n:names)out.points.add(resolvePlace(n));
  if(out.points.size()<2)throw new Exception("Google Maps-länken innehåller inte en komplett rutt. Dela en vägbeskrivning med start och destination.");return out;
 }

 private GPoint getLastKnownPoint(){
  try{if(android.os.Build.VERSION.SDK_INT>=23&&checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)return null;android.location.LocationManager lm=(android.location.LocationManager)getSystemService(LOCATION_SERVICE);android.location.Location best=null;for(String p:lm.getProviders(true)){android.location.Location l=lm.getLastKnownLocation(p);if(l!=null&&(best==null||l.getTime()>best.getTime()))best=l;}return best==null?null:new GPoint(best.getLatitude(),best.getLongitude(),"Min plats");}catch(Exception e){return null;}
 }

 private GPoint resolvePlace(String raw)throws Exception{
  String s=raw.trim();java.util.regex.Matcher m=java.util.regex.Pattern.compile("^\\s*(-?\\d+(?:\\.\\d+)?)\\s*,\\s*(-?\\d+(?:\\.\\d+)?)\\s*$").matcher(s);if(m.matches())return new GPoint(Double.parseDouble(m.group(1)),Double.parseDouble(m.group(2)),s);
  String q=URLEncoder.encode(s,"UTF-8");String json=httpGet("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&countrycodes=se&q="+q);JSONArray a=new JSONArray(json);if(a.length()==0){json=httpGet("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q="+q);a=new JSONArray(json);}if(a.length()==0)throw new Exception("Hittade inte platsen: "+s);JSONObject o=a.getJSONObject(0);return new GPoint(o.getDouble("lat"),o.getDouble("lon"),s);
 }

 private String httpGet(String url)throws Exception{HttpURLConnection c=(HttpURLConnection)new URL(url).openConnection();c.setConnectTimeout(12000);c.setReadTimeout(20000);c.setRequestProperty("User-Agent","RuttGPS/37 Android route importer");InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream();byte[]b=new byte[8192];int n;while((n=in.read(b))>0)out.write(b,0,n);in.close();c.disconnect();return new String(out.toByteArray(),StandardCharsets.UTF_8);}

 private JSONObject buildImportedRoute(GRoute gr)throws Exception{
  StringBuilder cs=new StringBuilder();for(int i=0;i<gr.points.size();i++){if(i>0)cs.append(';');GPoint p=gr.points.get(i);cs.append(p.lon).append(',').append(p.lat);}String osrm="https://router.project-osrm.org/route/v1/driving/"+cs+"?overview=full&geometries=geojson&steps=false";JSONObject r=new JSONObject(httpGet(osrm));JSONArray rr=r.optJSONArray("routes");if(rr==null||rr.length()==0)throw new Exception("Kunde inte beräkna körvägen mellan stoppen.");JSONArray coords=rr.getJSONObject(0).getJSONObject("geometry").getJSONArray("coordinates");
  JSONObject root=new JSONObject();root.put("format","gps-ruttinspelare");root.put("version",37);root.put("source","google-maps");root.put("source_url",gr.sourceUrl);JSONArray pts=new JSONArray();for(int i=0;i<coords.length();i++){JSONArray c=coords.getJSONArray(i);JSONObject p=new JSONObject();p.put("lat",c.getDouble(1));p.put("lon",c.getDouble(0));pts.put(p);}root.put("points",pts);
  GPoint first=gr.points.get(0),last=gr.points.get(gr.points.size()-1);JSONObject st=new JSONObject();st.put("label","START");st.put("lat",first.lat);st.put("lon",first.lon);st.put("name",first.name);root.put("start",st);JSONObject en=new JSONObject();en.put("label","SLUT");en.put("lat",last.lat);en.put("lon",last.lon);en.put("name",last.name);root.put("end",en);
  JSONArray stops=new JSONArray();for(int i=1;i<gr.points.size()-1;i++){GPoint p=gr.points.get(i);JSONObject o=new JSONObject();o.put("label",String.valueOf((char)('A'+Math.min(i-1,25))));o.put("lat",p.lat);o.put("lon",p.lon);o.put("name",p.name);stops.put(o);}root.put("stops",stops);return root;
 }

'''
s = s.replace(anchor, helper + anchor, 1)

# Version labels produced by Version 36.
s = s.replace('VERSION 36 • RUTTBIBLIOTEK', 'VERSION 37 • GOOGLE MAPS-IMPORT')
s = s.replace('VERSION 36 • \\\"+selectedDay.toUpperCase()', 'VERSION 37 • \\\"+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

# Add a dedicated Google Maps button on the route library screen.
layout = Path('app/src/main/res/layout/activity_main.xml')
x = layout.read_text(encoding='utf-8')
needle = '<Button android:id="@+id/btnImport" android:layout_width="match_parent" android:layout_height="52dp" android:text="Importera rutt till vald dag" android:textAllCaps="false"/>'
insert = needle + '\n <Button android:id="@+id/btnGoogleMaps" android:layout_width="match_parent" android:layout_height="52dp" android:text="🗺️ Importera från Google Maps" android:textAllCaps="false"/>'
if needle not in x: raise SystemExit('v37 layout import button point not found')
x = x.replace(needle, insert, 1)
x = x.replace('VERSION 1 • Flera rutter per dag', 'VERSION 37 • Google Maps-import + ruttbibliotek')
layout.write_text(x, encoding='utf-8')

# Register Rutt GPS as a share target for Google Maps text links.
manifest = Path('app/src/main/AndroidManifest.xml')
m = manifest.read_text(encoding='utf-8')
needle = '''            <intent-filter>\n                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />\n            </intent-filter>'''
share = needle + '''\n            <intent-filter>\n                <action android:name="android.intent.action.SEND" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <data android:mimeType="text/plain" />\n            </intent-filter>'''
if needle not in m: raise SystemExit('v37 manifest launcher point not found')
m = m.replace(needle, share, 1)
manifest.write_text(m, encoding='utf-8')

build = Path('app/build.gradle')
b = build.read_text(encoding='utf-8')
b = b.replace('versionCode 36', 'versionCode 37').replace('versionName "36.0"', 'versionName "37.0"')
build.write_text(b, encoding='utf-8')

print('Version 37 applied: Google Maps share/paste import, geocoding, road routing and day selection')
