from pathlib import Path
exec(Path('scripts/version22.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V23 diagnostic build: show WebView/JavaScript errors directly on screen.
# Keep V22/V16 navigation logic otherwise unchanged.
s=s.replace('web.setWebChromeClient(new WebChromeClient(){', '''web.setWebChromeClient(new WebChromeClient(){@Override public boolean onConsoleMessage(android.webkit.ConsoleMessage cm){final String msg="JS: "+cm.message()+" (rad "+cm.lineNumber()+")";runOnUiThread(()->Toast.makeText(MainActivity.this,msg,Toast.LENGTH_LONG).show());return true;}''',1)

# Add global JS error banner before the main script executes.
marker='<script>'
diag="""<script>window.onerror=function(msg,src,line,col,err){var d=document.getElementById('diag');if(d){d.style.display='block';d.textContent='JAVASCRIPT-FEL: '+msg+' • rad '+line+':'+col;}return false;};</script><div id='diag' style='display:none;position:fixed;z-index:99999;left:8px;right:8px;top:320px;background:#b71c1c;color:white;padding:12px;border-radius:10px;font:bold 15px sans-serif;white-space:normal'></div><script>"""
if marker not in s: raise SystemExit('v23 script marker not found')
s=s.replace(marker,diag,1)

s=s.replace('VERSION 22 • RUTTBIBLIOTEK','VERSION 23 • RUTTBIBLIOTEK').replace('VERSION 22 • "+selectedDay.toUpperCase()','VERSION 23 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 22','versionCode 23').replace('versionName "22.0"','versionName "23.0"')
b.write_text(t,encoding='utf-8')
