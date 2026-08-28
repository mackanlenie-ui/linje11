from pathlib import Path
import re

# Rebase on the last on-device stable navigation build.
exec(Path('scripts/version16.py').read_text(encoding='utf-8'))
p=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=p.read_text(encoding='utf-8')

# Keep the proven Version 16 Java/WebView/GPS structure exactly as-is.
# Only silence voice guidance by removing JavaScript calls to speakMessage.
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\s*\}\s*catch\(e\)\{\}","",s)
s=re.sub(r"try\{Android\.speakMessage\([^;]*?\);?\}\s*catch\(e\)\{\}","",s)

# Version label only. No Version 17-21 startup changes are carried forward.
s=s.replace('VERSION 16 • RUTTBIBLIOTEK','VERSION 22 • RUTTBIBLIOTEK')
s=s.replace('VERSION 16 • \"+selectedDay.toUpperCase()','VERSION 22 • \"+selectedDay.toUpperCase()')
p.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 16','versionCode 22').replace('versionName \"16.0\"','versionName \"22.0\"')
b.write_text(t,encoding='utf-8')
