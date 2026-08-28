from pathlib import Path
exec(Path('scripts/version17.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Version 18: remove voice navigation/TTS entirely. Keep all visual driving
# guidance, routing, automatic arrival and progress features from Version 17.
s=s.replace('import android.speech.tts.TextToSpeech;\n','')
s=s.replace('import java.util.Locale;\n','')
s=s.replace(' private TextToSpeech tts;','')

# Remove TTS initialization if present.
s=s.replace('tts=new TextToSpeech(this,x->{if(x==TextToSpeech.SUCCESS)tts.setLanguage(new Locale("sv","SE"));});','')

# Keep only the route chooser bridge; remove speakMessage from the JS bridge.
s=s.replace('@JavascriptInterface public void speakMessage(String m){runOnUiThread(()->{if(tts!=null)tts.speak(m,TextToSpeech.QUEUE_FLUSH,null,"nav");});}','')

# Strip all JavaScript calls to Android.speakMessage while leaving navigation logic intact.
import re
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\}\s*catch\(e\)\{\}","",s)
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\s*\}\s*catch\(e\)\{\}","",s)

# Remove TTS shutdown lifecycle method if present.
s=re.sub(r' @Override protected void onDestroy\(\)\{if\(tts!=null\)\{tts\.stop\(\);tts\.shutdown\(\);\}super\.onDestroy\(\);\}\n?','',s)

s=s.replace('VERSION 17 • RUTTBIBLIOTEK','VERSION 18 • RUTTBIBLIOTEK').replace('VERSION 17 • \"+selectedDay.toUpperCase()','VERSION 18 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 17','versionCode 18').replace('versionName \"17.0\"','versionName \"18.0\"')
b.write_text(t,encoding='utf-8')
