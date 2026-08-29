from pathlib import Path

# Version 42 builds on the user's approved Version 41.
exec(Path('scripts/version41.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# --- Backup / restore all weekday routes through Android's document picker ---
# Add two compact management buttons below the Google Maps import button.
old = 'root.addView(gm,glp);TextView hint=titleText("Håll inne på en rutt för att byta namn, namnge stopp eller ta bort.",13,false);'
new = '''root.addView(gm,glp);LinearLayout tools=new LinearLayout(this);tools.setOrientation(LinearLayout.HORIZONTAL);Button backup=cleanButton("💾 Backup",44);backup.setTextSize(15);backup.setOnClickListener(v->exportRoutesBackup());Button restore=cleanButton("📥 Återställ",44);restore.setTextSize(15);restore.setOnClickListener(v->chooseRoutesBackup());tools.addView(backup,new LinearLayout.LayoutParams(0,dp(52),1f));tools.addView(restore,new LinearLayout.LayoutParams(0,dp(52),1f));LinearLayout.LayoutParams tlp=new LinearLayout.LayoutParams(-1,dp(54));tlp.setMargins(0,dp(4),0,0);root.addView(tools,tlp);TextView hint=titleText("Håll inne på en rutt för att byta namn, namnge stopp, vända eller ta bort.",13,false);'''
if old not in s:
    raise SystemExit('v42 route chooser backup insertion point not found')
s = s.replace(old, new, 1)

anchor = ' private void chooseFile(){'
if anchor not in s:
    raise SystemExit('v42 chooseFile point not found')
backup_helpers = r''' private static final int EXPORT_BACKUP=420,IMPORT_BACKUP=421;
 private void exportRoutesBackup(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"Rutt-GPS-backup.json");startActivityForResult(i,EXPORT_BACKUP);}
 private void chooseRoutesBackup(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");startActivityForResult(i,IMPORT_BACKUP);}
 private JSONObject makeRoutesBackup()throws Exception{JSONObject root=new JSONObject();root.put("format","rutt-gps-backup");root.put("version",42);root.put("created",System.currentTimeMillis());JSONObject all=new JSONObject();for(String day:days)all.put(day,load(day));root.put("days",all);return root;}
 private void writeText(Uri u,String text)throws Exception{OutputStream out=getContentResolver().openOutputStream(u,"wt");if(out==null)throw new Exception("no output");out.write(text.getBytes(StandardCharsets.UTF_8));out.flush();out.close();}
 private void restoreRoutesBackup(Uri u)throws Exception{JSONObject root=new JSONObject(read(u));if(!"rutt-gps-backup".equals(root.optString("format")))throw new Exception("Fel backupformat");JSONObject all=root.optJSONObject("days");if(all==null)throw new Exception("Backupen saknar rutter");for(String day:days){JSONArray a=all.optJSONArray(day);if(a!=null)save(day,a);}refresh();}
'''
s = s.replace(anchor, backup_helpers + anchor, 1)

# Handle backup picker results before the existing single-route importer.
old_result = '@Override protected void onActivityResult(int r,int c,Intent data){super.onActivityResult(r,c,data);'
new_result = '''@Override protected void onActivityResult(int r,int c,Intent data){super.onActivityResult(r,c,data);if(r==EXPORT_BACKUP){if(c==RESULT_OK&&data!=null&&data.getData()!=null)try{writeText(data.getData(),makeRoutesBackup().toString(2));Toast.makeText(this,"Backup sparad ✓",Toast.LENGTH_LONG).show();}catch(Exception e){Toast.makeText(this,"Kunde inte spara backup",Toast.LENGTH_LONG).show();}return;}if(r==IMPORT_BACKUP){if(c==RESULT_OK&&data!=null&&data.getData()!=null)try{restoreRoutesBackup(data.getData());Toast.makeText(this,"Alla rutter återställda ✓",Toast.LENGTH_LONG).show();}catch(Exception e){Toast.makeText(this,"Kunde inte återställa backup",Toast.LENGTH_LONG).show();}return;}'''
if old_result not in s:
    raise SystemExit('v42 onActivityResult point not found')
s = s.replace(old_result, new_result, 1)

# --- Manual next / previous stop controls on the navigation map ---
old_controls = "<button onclick='Android.chooseRoute()'>🔄 Byt rutt / dag</button>"
new_controls = "<button onclick='manualPrev()'>◀ Förra</button><button onclick='manualNext()'>Nästa ▶</button><button onclick='Android.chooseRoute()'>🔄 Byt rutt / dag</button>"
if old_controls not in s:
    raise SystemExit('v42 map controls point not found')
s = s.replace(old_controls, new_controls, 1)

watch_anchor = 'navigator.geolocation.watchPosition(function(pos){'
if watch_anchor not in s:
    raise SystemExit('v42 navigation function insertion point not found')
manual_js = r'''function saveManualProgress(){try{localStorage.setItem(routeKey+'_phase',phase);localStorage.setItem(routeKey+'_idx',String(idx));}catch(e){}}function resetLeg(){nearHits=0;roadKm=null;roadSec=null;nextTurn=null;lastSpoken='';saveManualProgress();refreshMarkers();updateRoad(true);info();}function manualNext(){if(phase==='start'){phase='route';idx=0;}else if(phase==='route'){if(idx<stops.length-1)idx++;else phase=end?'end':'done';}else if(phase==='end')phase='done';resetLeg();}function manualPrev(){if(phase==='done'){if(end){phase='end';idx=Math.max(0,stops.length-1);}else{phase='route';idx=Math.max(0,stops.length-1);}}else if(phase==='end'){phase='route';idx=Math.max(0,stops.length-1);}else if(phase==='route'){if(idx>0)idx--;else if(start)phase='start';}resetLeg();}'''
s = s.replace(watch_anchor, manual_js + watch_anchor, 1)

# --- Safer GPS quality handling ---
# Keep clearly poor fixes from moving the map/navigation, while preserving rural usability.
s = s.replace('if(rawAcc>85)return;', 'if(rawAcc>70)return;', 1)
old_gps = "document.getElementById('gpsStatus').textContent=(rawAcc>35?'🟠 GPS osäker':'🔵 GPS hittad')+' • ±'+Math.round(rawAcc)+' m';"
new_gps = "document.getElementById('gpsStatus').textContent=(rawAcc<=15?'🟢 GPS mycket bra':rawAcc<=30?'🔵 GPS bra':rawAcc<=45?'🟠 GPS okej':'🔴 GPS svag')+' • ±'+Math.round(rawAcc)+' m';"
if old_gps not in s:
    raise SystemExit('v42 GPS status point not found')
s = s.replace(old_gps, new_gps, 1)
old_arrived = 'function arrived(){var t=target();if(!lastGps||!t)return;'
new_arrived = 'function arrived(){var t=target();if(!lastGps||!t||lastAccuracy>45)return;'
if old_arrived not in s:
    raise SystemExit('v42 arrival GPS quality point not found')
s = s.replace(old_arrived, new_arrived, 1)

# Version labels.
s = s.replace('VERSION 41 • VÄND RUTT', 'VERSION 42 • TRYGGARE NAVIGATION')
s = s.replace('VERSION 41 • "+selectedDay.toUpperCase()', 'VERSION 42 • "+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 41', 'versionCode 42').replace('versionName "41.0"', 'versionName "42.0"')
b.write_text(t, encoding='utf-8')

print('Version 42 applied: previous/next stop, GPS quality guard, full weekday backup/restore')
