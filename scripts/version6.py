from pathlib import Path
import re
exec(Path('scripts/version5.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Start on a clean Lenninge-style weekday chooser.
s=re.sub(r'@Override protected void onCreate\(Bundle b\)\{.*?\}\n private void chooseFile\(\)', '''@Override protected void onCreate(Bundle b){super.onCreate(b);getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);showDayChooser();}
 private int dp(int v){return (int)(v*getResources().getDisplayMetrics().density+0.5f);}
 private TextView titleText(String text,float size,boolean bold){TextView t=new TextView(this);t.setText(text);t.setTextSize(size);t.setGravity(android.view.Gravity.CENTER);t.setTextColor(android.graphics.Color.rgb(95,95,95));if(bold)t.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);return t;}
 private Button cleanButton(String text,int height){Button b=new Button(this);b.setAllCaps(false);b.setText(text);b.setTextSize(20);b.setTextColor(android.graphics.Color.rgb(35,35,35));b.setGravity(android.view.Gravity.CENTER);b.setMinHeight(dp(height));return b;}
 private void showDayChooser(){selectedDay="Måndag";routeList=null;daySpinner=null;LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(14),dp(10),dp(14));TextView title=titleText("Linje11 Rutt GPS",28,true);root.addView(title,new LinearLayout.LayoutParams(-1,dp(50)));TextView ver=titleText("VERSION 6 • RUTTBIBLIOTEK",18,true);ver.setTextColor(android.graphics.Color.rgb(25,105,185));root.addView(ver,new LinearLayout.LayoutParams(-1,dp(35)));TextView sub=titleText("Välj vilken dag du ska köra.",21,false);LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(55));sp.setMargins(0,0,0,dp(8));root.addView(sub,sp);for(String day:days){Button b=cleanButton(day,58);LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(64));lp.setMargins(0,dp(5),0,dp(5));b.setOnClickListener(v->{selectedDay=day;showRouteChooser();});root.addView(b,lp);}setContentView(root);}
 private void chooseFile()''',s,flags=re.S)

# Clean route list: one large button per route. Long-press opens management actions.
start=s.index(' private void refresh(){')
end=s.index(' private void renameRoute(', start)
new_refresh=''' private void refresh(){if(routeList==null)return;routeList.removeAllViews();JSONArray routes=load(selectedDay);if(routes.length()==0){TextView t=titleText("Inga rutter för "+selectedDay+" ännu.",17,false);t.setPadding(dp(8),dp(24),dp(8),dp(24));routeList.addView(t);return;}for(int i=0;i<routes.length();i++)try{JSONObject item=routes.getJSONObject(i),route=item.getJSONObject("route");JSONArray st=route.optJSONArray("stops");int stops=st==null?0:st.length();String name=item.optString("name","Rutt "+(i+1));Button open=cleanButton(name+"\\n"+stops+" stopp",62);open.setTextSize(18);final int idx=i;open.setOnClickListener(v->openRoute(idx));open.setOnLongClickListener(v->{showRouteMenu(idx);return true;});LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(78));lp.setMargins(0,dp(5),0,dp(5));routeList.addView(open,lp);}catch(Exception ignored){}}
 private void showRouteMenu(int index){try{JSONArray routes=load(selectedDay);String n=routes.getJSONObject(index).optString("name","Rutt "+(index+1));String[] opts={"✏ Byt ruttnamn","✏ Namnge stopp","🗑 Ta bort rutt"};new androidx.appcompat.app.AlertDialog.Builder(this).setTitle(n).setItems(opts,(d,w)->{if(w==0)renameRoute(index);else if(w==1)editStopNames(index);else new androidx.appcompat.app.AlertDialog.Builder(this).setTitle("Ta bort rutten?").setMessage(n).setNegativeButton("Avbryt",null).setPositiveButton("Ta bort",(x,y)->deleteRoute(index)).show();}).show();}catch(Exception e){Toast.makeText(this,"Kunde inte öppna ruttmenyn",Toast.LENGTH_LONG).show();}}
'''
s=s[:start]+new_refresh+s[end:]

# Replace V5 XML-based chooser with a Lenninge-style route chooser.
start=s.index(' private void showRouteChooser(){')
end=s.index(' private void deleteRoute(', start)
new_chooser=''' private void showRouteChooser(){LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(10),dp(10),dp(10));Button back=cleanButton("← Byt dag",48);back.setTextSize(18);back.setOnClickListener(v->showDayChooser());root.addView(back,new LinearLayout.LayoutParams(-1,dp(58)));TextView title=titleText("Linje11 Rutt GPS",27,true);root.addView(title,new LinearLayout.LayoutParams(-1,dp(55)));TextView ver=titleText("VERSION 6 • "+selectedDay.toUpperCase(),18,true);ver.setTextColor(android.graphics.Color.rgb(25,105,185));root.addView(ver,new LinearLayout.LayoutParams(-1,dp(38)));ScrollView scroll=new ScrollView(this);routeList=new LinearLayout(this);routeList.setOrientation(LinearLayout.VERTICAL);scroll.addView(routeList,new ScrollView.LayoutParams(-1,-2));root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1f));Button imp=cleanButton("＋ Importera rutt till "+selectedDay,48);imp.setTextSize(16);imp.setOnClickListener(v->chooseFile());LinearLayout.LayoutParams ilp=new LinearLayout.LayoutParams(-1,dp(58));ilp.setMargins(0,dp(6),0,0);root.addView(imp,ilp);TextView hint=titleText("Håll inne på en rutt för att byta namn, namnge stopp eller ta bort.",13,false);hint.setPadding(dp(8),dp(5),dp(8),0);root.addView(hint,new LinearLayout.LayoutParams(-1,dp(45)));setContentView(root);refresh();}
'''
s=s[:start]+new_chooser+s[end:]

# Back from route chooser goes to weekday chooser; back from map goes to route chooser.
s=re.sub(r'@Override public void onBackPressed\(\)\{.*?\}\n private void showRouteChooser', '@Override public void onBackPressed(){if(routeList==null)showDayChooser();else showRouteChooser();}\n private void showRouteChooser', s, flags=re.S)

p.write_text(s,encoding='utf-8')
b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 5','versionCode 6').replace('versionName "5.0"','versionName "6.0"')
b.write_text(t,encoding='utf-8')
