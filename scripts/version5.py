from pathlib import Path
exec(Path('scripts/version4.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')
# Add Android bridge so map button can return to route/day selection.
s=s.replace("web.setWebViewClient(new WebViewClient());", "web.setWebViewClient(new WebViewClient());web.addJavascriptInterface(new Object(){@JavascriptInterface public void chooseRoute(){runOnUiThread(()->showRouteChooser());}},\"Android\");")
# Add helper to rebuild the normal route/day chooser.
needle=' private void deleteRoute(int index){'
method=''' private void showRouteChooser(){setContentView(R.layout.activity_main);daySpinner=findViewById(R.id.daySpinner);routeList=findViewById(R.id.routeList);ArrayAdapter<String>a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);daySpinner.setAdapter(a);int pos=java.util.Arrays.asList(days).indexOf(selectedDay);daySpinner.setSelection(Math.max(0,pos));daySpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onItemSelected(android.widget.AdapterView<?>p,android.view.View v,int x,long id){selectedDay=days[x];refresh();}public void onNothingSelected(android.widget.AdapterView<?>p){}});findViewById(R.id.btnImport).setOnClickListener(v->chooseFile());refresh();}
'''
s=s.replace(needle,method+needle)
# Reuse helper from Android back button as well.
old='@Override public void onBackPressed(){if(routeList==null||routeList.getParent()==null){setContentView(R.layout.activity_main);daySpinner=findViewById(R.id.daySpinner);routeList=findViewById(R.id.routeList);ArrayAdapter<String>a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);daySpinner.setAdapter(a);int pos=java.util.Arrays.asList(days).indexOf(selectedDay);daySpinner.setSelection(Math.max(0,pos));daySpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){public void onItemSelected(android.widget.AdapterView<?>p,android.view.View v,int x,long id){selectedDay=days[x];refresh();}public void onNothingSelected(android.widget.AdapterView<?>p){}});findViewById(R.id.btnImport).setOnClickListener(v->chooseFile());refresh();}else super.onBackPressed();}'
new='@Override public void onBackPressed(){if(routeList==null||routeList.getParent()==null)showRouteChooser();else super.onBackPressed();}'
s=s.replace(old,new)
# Add third map control button.
s=s.replace("<button onclick='myGps()'>📍 Min GPS</button></div>","<button onclick='myGps()'>📍 Min GPS</button><button onclick='Android.chooseRoute()'>🔄 Byt rutt / dag</button></div>")
p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle');t=b.read_text(encoding='utf-8').replace('versionCode 4','versionCode 5').replace('versionName \"4.0\"','versionName \"5.0\"');b.write_text(t,encoding='utf-8')
