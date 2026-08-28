from pathlib import Path
exec(Path('scripts/version16.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# V24: keep Version 16 JavaScript byte-for-byte intact. The V22 voice-removal
# regex broke an `if(end) try{...}catch(e){}` construct and caused the
# Unexpected token '}' error. Silence speech only in the Android bridge.
old='@JavascriptInterface public void speakMessage(String m){runOnUiThread(()->{if(tts!=null)tts.speak(m,TextToSpeech.QUEUE_FLUSH,null,"nav");});}'
new='@JavascriptInterface public void speakMessage(String m){}'
if old not in s:
    raise SystemExit('v24 speakMessage bridge not found')
s=s.replace(old,new,1)

s=s.replace('VERSION 16 • RUTTBIBLIOTEK','VERSION 24 • RUTTBIBLIOTEK').replace('VERSION 16 • "+selectedDay.toUpperCase()','VERSION 24 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 16','versionCode 24').replace('versionName "16.0"','versionName "24.0"')
b.write_text(t,encoding='utf-8')
