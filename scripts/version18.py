from pathlib import Path

# Build Version 18 from the proven Version 16 base.
# This avoids the broken experimental Version 17 vehicle-marker patch while
# keeping road routing, entrance snapping, arrival logic and saved progress.
exec(Path('scripts/version16.py').read_text(encoding='utf-8'))

p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# No voice navigation/TTS in Version 18.
s=s.replace('import android.speech.tts.TextToSpeech;\n','')
s=s.replace('import java.util.Locale;\n','')
s=s.replace(' private TextToSpeech tts;','')
s=s.replace('tts=new TextToSpeech(this,x->{if(x==TextToSpeech.SUCCESS)tts.setLanguage(new Locale("sv","SE"));});','')
s=s.replace('@JavascriptInterface public void speakMessage(String m){runOnUiThread(()->{if(tts!=null)tts.speak(m,TextToSpeech.QUEUE_FLUSH,null,"nav");});}','')

import re
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\}\s*catch\(e\)\{\}","",s)
s=re.sub(r' @Override protected void onDestroy\(\)\{if\(tts!=null\)\{tts\.stop\(\);tts\.shutdown\(\);\}super\.onDestroy\(\);\}\n?','',s)

# Version label only; keep Version 16's stable navigation behavior.
s=s.replace('VERSION 16 • RUTTBIBLIOTEK','VERSION 18 • RUTTBIBLIOTEK')
s=s.replace('VERSION 16 • "+selectedDay.toUpperCase()','VERSION 18 • "+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 16','versionCode 18').replace('versionName "16.0"','versionName "18.0"')
b.write_text(t,encoding='utf-8')
