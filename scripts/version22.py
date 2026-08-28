from pathlib import Path
import re

# Rebase on the last on-device stable navigation build.
exec(Path('scripts/version16.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Remove TextToSpeech completely while preserving Version 16 map/GPS/routing.
s=s.replace('import android.speech.tts.TextToSpeech;\n','')
s=s.replace('import java.util.Locale;\n','')
s=s.replace(' private TextToSpeech tts;','')
s=s.replace(' private TextToSpeech tts;\n','')

# Remove TTS initialization from onCreate if present.
s=re.sub(r'tts=new TextToSpeech\(this,.*?\);','',s)

# Remove speakMessage from the Android JS bridge but keep chooseRoute.
s=re.sub(r'@JavascriptInterface public void speakMessage\(String m\)\{.*?\}\},"Android"\);', '},"Android");', s, count=1)

# Remove all JavaScript voice calls safely.
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\s*\}\s*catch\(e\)\{\}","",s)
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\}\s*catch\(e\)\{\}","",s)

# Remove TTS shutdown override if present.
s=re.sub(r' @Override protected void onDestroy\(\)\{if\(tts!=null\)\{tts\.stop\(\);tts\.shutdown\(\);\}super\.onDestroy\(\);\}\n?','',s)

# Version label only. No Version 17-21 startup changes are carried forward.
s=s.replace('VERSION 16 • RUTTBIBLIOTEK','VERSION 22 • RUTTBIBLIOTEK')
s=s.replace('VERSION 16 • \"+selectedDay.toUpperCase()','VERSION 22 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 16','versionCode 22').replace('versionName \"16.0\"','versionName \"22.0\"')
b.write_text(t,encoding='utf-8')
