from pathlib import Path

exec(Path('scripts/version73.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# Version 74: dynamic route/area library, clear back button on weekday screen,
# and taller controls so long Swedish labels are never clipped.
old_decl='private final String[] routeAreas={"Lenninge–Kilafors","Röste–Rengsjö"};'
if old_decl not in s: raise SystemExit('v74 area declaration missing')
s=s.replace(old_decl,'private final String[] defaultRouteAreas={"Lenninge–Kilafors","Röste–Rengsjö"};',1)

start=s.index(' private void showAreaChooser(){')
end=s.index(' private void showDayChooserForArea(){',start)
area_code=r''' private JSONArray loadAreas(){
  try{
   android.content.SharedPreferences p=getPreferences(MODE_PRIVATE);
   String raw=p.getString("route_areas",null);
   if(raw!=null){JSONArray a=new JSONArray(raw);if(a.length()>0)return a;}
   JSONArray a=new JSONArray();for(String x:defaultRouteAreas)a.put(x);p.edit().putString("route_areas",a.toString()).apply();return a;
  }catch(Exception e){JSONArray a=new JSONArray();for(String x:defaultRouteAreas)a.put(x);return a;}
 }
 private void saveAreas(JSONArray a){getPreferences(MODE_PRIVATE).edit().putString("route_areas",a.toString()).apply();}
 private void addAreaDialog(){
  final EditText e=new EditText(this);e.setSingleLine(true);e.setHint("Exempel: Hofors–Falun");e.setTextSize(18);int pad=dp(18);e.setPadding(pad,pad,pad,pad);
  new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Lägg till ny rutt / område").setMessage("Den nya rutten får automatiskt Måndag–Söndag. Sedan kan du lägga in körturer under varje dag.").setView(e).setNegativeButton("Avbryt",null).setPositiveButton("Lägg till",(d,w)->{String n=e.getText().toString().trim();if(n.isEmpty()){Toast.makeText(this,"Skriv ett namn på rutten",Toast.LENGTH_LONG).show();return;}JSONArray a=loadAreas();for(int i=0;i<a.length();i++)if(n.equalsIgnoreCase(a.optString(i))){Toast.makeText(this,"Den rutten finns redan",Toast.LENGTH_LONG).show();return;}a.put(n);saveAreas(a);selectedArea=n;showDayChooserForArea();}).show();
 }
 private void showAreaChooser(){
  selectedDay="Måndag";routeList=null;daySpinner=null;
  LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(18),dp(10),dp(18));
  TextView title=titleText("Rutt GPS",29,true);root.addView(title,new LinearLayout.LayoutParams(-1,dp(54)));
  TextView ver=titleText("VERSION 74 • VÄLJ RUTT / OMRÅDE",17,true);ver.setTextColor(android.graphics.Color.rgb(25,105,185));root.addView(ver,new LinearLayout.LayoutParams(-1,dp(38)));
  TextView sub=titleText("1. Välj vilken rutt / vilket område du ska köra.",20,false);LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(66));sp.setMargins(0,0,0,dp(8));root.addView(sub,sp);
  ScrollView scroll=new ScrollView(this);LinearLayout list=new LinearLayout(this);list.setOrientation(LinearLayout.VERTICAL);JSONArray a=loadAreas();for(int i=0;i<a.length();i++){final String area=a.optString(i).trim();if(area.isEmpty())continue;Button b=cleanButton(area,62);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(72));lp.setMargins(0,dp(5),0,dp(5));b.setOnClickListener(v->{selectedArea=area;showDayChooserForArea();});list.addView(b,lp);}scroll.addView(list,new ScrollView.LayoutParams(-1,-2));root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1f));
  Button add=cleanButton("＋ Lägg till ny rutt / område",56);add.setTextSize(18);add.setOnClickListener(v->addAreaDialog());LinearLayout.LayoutParams alp=new LinearLayout.LayoutParams(-1,dp(68));alp.setMargins(0,dp(8),0,0);root.addView(add,alp);
  setContentView(root);
 }
'''
s=s[:start]+area_code+s[end:]

# Put a visible return-to-area button at the top of the weekday chooser.
day_start=s.index(' private void showDayChooserForArea(){')
title_at=s.index('TextView title=',day_start)
back_code='Button areaBack=cleanButton("← Välj annan rutt",48);areaBack.setTextSize(18);areaBack.setOnClickListener(v->showAreaChooser());LinearLayout.LayoutParams abp=new LinearLayout.LayoutParams(-1,dp(58));abp.setMargins(0,0,0,dp(5));root.addView(areaBack,abp);'
s=s[:title_at]+back_code+s[title_at:]

# Give the route import button enough room for two lines on smaller screens.
s=s.replace('LinearLayout.LayoutParams ilp=new LinearLayout.LayoutParams(-1,dp(58));ilp.setMargins(0,dp(6),0,0);root.addView(imp,ilp);','LinearLayout.LayoutParams ilp=new LinearLayout.LayoutParams(-1,dp(86));ilp.setMargins(0,dp(6),0,0);root.addView(imp,ilp);',1)
# The instruction text at the bottom also needs room for two lines.
s=s.replace('root.addView(hint,new LinearLayout.LayoutParams(-1,dp(45)));','root.addView(hint,new LinearLayout.LayoutParams(-1,dp(70)));',1)
# Slightly smaller import label improves readability with long area names.
s=s.replace('Button imp=cleanButton("＋ Importera körtur till "+selectedArea+" • "+selectedDay,48);imp.setTextSize(16);','Button imp=cleanButton("＋ Importera körtur till "+selectedArea+" • "+selectedDay,58);imp.setTextSize(15);',1)

s=s.replace('VERSION 73 •','VERSION 74 •')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 73','versionCode 74').replace('versionName "73.0"','versionName "74.0"')
b.write_text(t,encoding='utf-8')
print('Version 74 applied: dynamic route areas, area back button, Monday-Sunday via existing day chooser, unclipped route-screen text')
