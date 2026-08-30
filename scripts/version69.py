from pathlib import Path

exec(Path('scripts/version68.py').read_text(encoding='utf-8'))

main=Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s=main.read_text(encoding='utf-8')

# V69 driving improvements: automatic driving zoom, course-up rotation,
# richer turn instructions and automatic return to GPS follow mode.
css=r'''#map{transition:transform .35s ease;transform-origin:50% 62%}body.freeLook #map{transform:none!important}'''
if '</style>' not in s: raise SystemExit('v69 style end not found')
s=s.replace('</style>',css+'</style>',1)

# Inject generic navigation helpers before the first closing script. They attach to
# the existing Leaflet map without changing the proven route/stops logic.
js=r'''
<script>
(function(){
 var follow=true,lastTouch=0,lastHeading=null,lastLL=null;
 function dist(a,b){var R=6371000,p=Math.PI/180,d1=(b.lat-a.lat)*p,d2=(b.lng-a.lng)*p,x=Math.sin(d1/2)**2+Math.cos(a.lat*p)*Math.cos(b.lat*p)*Math.sin(d2/2)**2;return 2*R*Math.asin(Math.sqrt(x));}
 function bearing(a,b){var p=Math.PI/180,y=Math.sin((b.lng-a.lng)*p)*Math.cos(b.lat*p),x=Math.cos(a.lat*p)*Math.sin(b.lat*p)-Math.sin(a.lat*p)*Math.cos(b.lat*p)*Math.cos((b.lng-a.lng)*p);return (Math.atan2(y,x)/p+360)%360;}
 function setCourse(h){if(!isFinite(h))return;lastHeading=h;var el=document.getElementById('map');if(el&&!document.body.classList.contains('freeLook'))el.style.transform='rotate('+(-h)+'deg) scale(1.13)';}
 function resume(){follow=true;document.body.classList.remove('freeLook');if(lastLL&&window.map){map.setView(lastLL,17,{animate:true});if(lastHeading!=null)setCourse(lastHeading);}}
 ['touchstart','mousedown','wheel'].forEach(function(ev){document.addEventListener(ev,function(e){if(e.target&&e.target.closest&&e.target.closest('#map')){follow=false;lastTouch=Date.now();document.body.classList.add('freeLook');setTimeout(function(){if(Date.now()-lastTouch>=7500)resume();},7800);}}, {passive:true});});
 if(window.map){map.on('dragstart zoomstart',function(){follow=false;lastTouch=Date.now();document.body.classList.add('freeLook');setTimeout(function(){if(Date.now()-lastTouch>=7500)resume();},7800);});}
 if(navigator.geolocation){navigator.geolocation.watchPosition(function(p){var ll=L.latLng(p.coords.latitude,p.coords.longitude);var speed=p.coords.speed||0,h=p.coords.heading;if((h==null||!isFinite(h))&&lastLL&&dist(lastLL,ll)>3)h=bearing(lastLL,ll);lastLL=ll;if(follow&&window.map){var z=speed>16?16:speed>5?17:18;map.setView(ll,z,{animate:true});if(h!=null&&isFinite(h))setCourse(h);}},function(){},{enableHighAccuracy:true,maximumAge:500,timeout:10000});}
 window.ruttGpsResumeFollow=resume;
})();
</script>'''
if '</body>' in s:s=s.replace('</body>',js+'</body>',1)

# Improve common maneuver wording while keeping existing turn engine intact.
s=s.replace("'FÖLJ VÄGEN'","'FÖLJ VÄGEN FRAMÅT'")
s=s.replace('"FÖLJ VÄGEN"','"FÖLJ VÄGEN FRAMÅT"')
s=s.replace('VERSION 68 • MINDRE NAVIGERINGSRUTA','VERSION 69 • SMART KÖRNAVIGERING')
for n in range(1,69):
    s=s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()','VERSION 69 • "+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()','VERSION 69 • \\"+selectedDay.toUpperCase()')
    s=s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()','VERSION 69 • \\\"+selectedDay.toUpperCase()')
main.write_text(s,encoding='utf-8')

b=Path('app/build.gradle')
t=b.read_text(encoding='utf-8').replace('versionCode 68','versionCode 69').replace('versionName "68.0"','versionName "69.0"')
b.write_text(t,encoding='utf-8')
print('Version 69 applied: auto zoom, course-up rotation, improved guidance, auto GPS follow return')
