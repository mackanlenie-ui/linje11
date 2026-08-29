from pathlib import Path

# Version 43 builds on Version 42 and only adds a little more top spacing
# above the route chooser's "Byt dag" button.
exec(Path('scripts/version42.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

old = 'private void showRouteChooser(){LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(10),dp(10),dp(10));Button back=cleanButton("← Byt dag",48);'
new = 'private void showRouteChooser(){LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(10),dp(22),dp(10),dp(10));Button back=cleanButton("← Byt dag",48);'
if old not in s:
    raise SystemExit('v43 route chooser top padding point not found')
s = s.replace(old, new, 1)

s = s.replace('VERSION 42 • TRYGGARE NAVIGATION', 'VERSION 43 • TRYGGARE NAVIGATION')
s = s.replace('VERSION 42 • "+selectedDay.toUpperCase()', 'VERSION 43 • "+selectedDay.toUpperCase()')
main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 42', 'versionCode 43').replace('versionName "42.0"', 'versionName "43.0"')
b.write_text(t, encoding='utf-8')

print('Version 43 applied: Byt dag moved slightly down from notification/status bar')
