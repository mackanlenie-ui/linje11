from pathlib import Path

# Version 49 builds on V48: route simulation/test mode, off-route detection with
# automatic rerouting, and a preloaded local navigation plan for offline use.
exec(Path('scripts/version48.py').read_text(encoding='utf-8'))

main = Path('app/src/main/java/se/linje11/gps/MainActivity.java')
s = main.read_text(encoding='utf-8')

# Small floating test-mode button so the normal driving controls stay unchanged.
controls_anchor = "<div class='controls'>"
test_button = "<button id='testBtn' onclick='toggleTest()' style='position:absolute;z-index:9999;right:10px;bottom:112px;background:white;border:0;border-radius:12px;padding:8px 11px;font-size:13px;font-weight:bold;box-shadow:0 2px 8px #0004;color:#17365d'>🧪 Test</button>"
if test_button not in s:
    if controls_anchor not in s:
        raise SystemExit('v49 controls anchor not found')
    s = s.replace(controls_anchor, test_button + controls_anchor, 1)

# Extra state used for a full-route offline plan, route deviation detection and simulation.
state_old = "nextTurn=null,lastGoodTurn=null,nearHits=0"
state_new = "nextTurn=null,lastGoodTurn=null,preloadPlan=null,preloadPts=[],offHits=0,rerouteNotice=0,simTimer=null,simIndex=0,nearHits=0"
if state_old not in s:
    raise SystemExit('v49 state point not found')
s = s.replace(state_old, state_new, 1)

# Helpers are inserted before the existing nearestActive function. The plan is
# built from OSRM geometry + maneuver locations and persisted in localStorage.
anchor = 'function nearestActive(p){'
if anchor not in s:
    raise SystemExit('v49 helper anchor not found')
helpers = r'''function planKey(){return routeKey+'_offline_plan_v49';}function savePlan(){try{if(preloadPlan)localStorage.setItem(planKey(),JSON.stringify(preloadPlan));}catch(e){}}function loadPlan(){try{var x=localStorage.getItem(planKey());if(x){preloadPlan=JSON.parse(x);preloadPts=preloadPlan.pts||[];}}catch(e){preloadPlan=null;preloadPts=[];}}function nearestIdx(a,p){if(!a||!a.length||!p)return-1;var bi=0,bd=1e20,step=Math.max(1,Math.floor(a.length/450));for(var i=0;i<a.length;i+=step){var d=km(p,a[i])*1000;if(d<bd){bd=d;bi=i;}}for(var j=Math.max(0,bi-step-3);j<=Math.min(a.length-1,bi+step+3);j++){var q=km(p,a[j])*1000;if(q<bd){bd=q;bi=j;}}return bi;}function buildPlan(rr){try{if(!rr||!rr.geometry||!rr.geometry.coordinates)return;var pp=rr.geometry.coordinates.map(function(x){return[x[1],x[0]];}),tt=[],ss=(rr.legs&&rr.legs[0]&&rr.legs[0].steps)||[];ss.forEach(function(q){var type=((q.maneuver&&q.maneuver.type)||'').toLowerCase(),mod=((q.maneuver&&q.maneuver.modifier)||'').toLowerCase();if(type==='depart'||type==='arrive')return;var loc=q.maneuver&&q.maneuver.location;if(!loc||loc.length<2)return;var isRound=type.indexOf('roundabout')>=0||type.indexOf('rotary')>=0,real=isRound||mod.indexOf('left')>=0||mod.indexOf('right')>=0;if(!real)return;var ix=nearestIdx(pp,[loc[1],loc[0]]),icon='⬆️',txt='Fortsätt rakt fram';if(isRound){icon='🔄';txt='Kör in i rondellen';}else if(mod.indexOf('left')>=0){icon=mod.indexOf('slight')>=0?'↖️':'⬅️';txt=mod.indexOf('slight')>=0?'Håll svagt vänster':'Sväng vänster';}else if(mod.indexOf('right')>=0){icon=mod.indexOf('slight')>=0?'↗️':'➡️';txt=mod.indexOf('slight')>=0?'Håll svagt höger':'Sväng höger';}tt.push({i:ix,icon:icon,text:txt,roundabout:isRound,exit:(q.maneuver&&q.maneuver.exit)||null,name:q.name||'',key:'plan49|'+ix+'|'+type+'|'+mod});});preloadPlan={pts:pp,turns:tt,ts:Date.now()};preloadPts=pp;savePlan();}catch(e){}}function distAlong(a,i,j){if(!a||i<0||j<=i)return 0;var d=0;for(var x=i+1;x<=j&&x<a.length;x++)d+=km(a[x-1],a[x])*1000;return d;}function plannedTurn(){try{if(!preloadPlan||!preloadPts.length||!lastGps)return null;var ci=nearestIdx(preloadPts,lastGps),turns=preloadPlan.turns||[];for(var k=0;k<turns.length;k++){var t=turns[k];if(t.i>ci+2){var d=distAlong(preloadPts,ci,t.i);if(d<15)continue;return{icon:t.icon,text:t.text+(t.name?' mot '+t.name:''),d:d,key:t.key,roundabout:!!t.roundabout,exit:t.exit,offline:true};}}return null;}catch(e){return null;}}async function preloadRouteData(){loadPlan();if(!navigator.onLine)return;try{var w=routeWaypoints();if(!w||w.length<2)return;var coords=w.map(function(x){return x[1]+','+x[0];}).join(';');var u='https://router.project-osrm.org/route/v1/driving/'+coords+'?overview=full&geometries=geojson&steps=true';var r=await fetch(u),d=await r.json();if(d.routes&&d.routes.length){buildPlan(d.routes[0]);var rs=document.getElementById('routeStatus');if(rs)rs.textContent=(stops.length===0?'📍 Destination: SLUT':'📍 Rutt')+' • 💾 Offlineplan klar ✓';}}catch(e){}}function distanceFromPlan(){if(!lastGps||!preloadPts.length)return null;var i=nearestIdx(preloadPts,lastGps);return i<0?null:km(lastGps,preloadPts[i])*1000;}function checkOffRoute(){if(!lastGps||!preloadPts.length)return;var d=distanceFromPlan();if(d!=null&&d>80&&lastAccuracy<=45)offHits++;else offHits=Math.max(0,offHits-1);if(offHits>=2){var rs=document.getElementById('routeStatus');if(rs)rs.textContent='⚠️ Utanför rutten • räknar om…';if(navigator.onLine&&Date.now()-rerouteNotice>5000){rerouteNotice=Date.now();updateRoad(true);}}}function simPosition(p){if(!p)return;lastGps=[p[0],p[1]];lastAccuracy=5;if(!gps)gps=L.marker(lastGps,{icon:L.divIcon({className:'',html:'<div class="gpsDot"></div>',iconSize:[32,32],iconAnchor:[16,16]})}).addTo(map);else gps.setLatLng(lastGps);document.getElementById('gpsStatus').textContent='🧪 TESTLÄGE • simulerad GPS';if(follow)map.setView(lastGps,16);arrived();nextTurn=plannedTurn()||offlineTurn();checkOffRoute();info();}function toggleTest(){var b=document.getElementById('testBtn');if(simTimer){clearInterval(simTimer);simTimer=null;if(b)b.textContent='🧪 Test';document.getElementById('gpsStatus').textContent='Testläge stoppat';return;}var a=(preloadPts&&preloadPts.length>10)?preloadPts:pts;if(!a||a.length<2)return;simIndex=0;if(b)b.textContent='⏹ Stoppa test';simTimer=setInterval(function(){if(simIndex>=a.length){clearInterval(simTimer);simTimer=null;if(b)b.textContent='🧪 Test';return;}simPosition(a[simIndex]);simIndex+=Math.max(1,Math.floor(a.length/180));},350);}'''
s = s.replace(anchor, helpers + anchor, 1)

# Every successful live route response refreshes the local plan for the active leg.
old_online = 'nextTurn=turnText(rr);if(nextTurn)lastGoodTurn=nextTurn;if(rr.geometry'
new_online = 'nextTurn=turnText(rr);if(nextTurn)lastGoodTurn=nextTurn;if(rr.geometry)buildPlan(rr);if(rr.geometry'
if old_online not in s:
    raise SystemExit('v49 online plan point not found')
s = s.replace(old_online, new_online, 1)

# Prefer the preloaded precise maneuver plan offline, then conservative geometry fallback.
old_offline = "var localTurn=offlineTurn();if(lastGoodTurn&&lastGoodTurn.roundabout){"
new_offline = "var localTurn=plannedTurn()||offlineTurn();if(lastGoodTurn&&lastGoodTurn.roundabout){"
if old_offline not in s:
    raise SystemExit('v49 offline fallback point not found')
s = s.replace(old_offline, new_offline, 1)

# Preload the whole route when navigation opens.
watch = 'navigator.geolocation.watchPosition(function(pos){'
if watch not in s:
    raise SystemExit('v49 watcher point not found')
s = s.replace(watch, 'preloadRouteData();'+watch, 1)

# Run deviation check after each accepted real GPS fix.
watch_tail = 'arrived();if(!nextTurn)nextTurn=offlineTurn();info();updateRoad(false);}'
watch_tail_new = 'arrived();if(!nextTurn)nextTurn=plannedTurn()||offlineTurn();checkOffRoute();info();updateRoad(false);}'
if watch_tail in s:
    s = s.replace(watch_tail, watch_tail_new, 1)
else:
    # V48/V47 can have extra statements around the watcher; add the check at a
    # stable updateRoad call if the exact compact form changed.
    s = s.replace('arrived();if(!nextTurn)nextTurn=offlineTurn();info();updateRoad(false);', 'arrived();if(!nextTurn)nextTurn=plannedTurn()||offlineTurn();checkOffRoute();info();updateRoad(false);', 1)

# When connectivity returns, refresh both the current leg and the full-route plan.
s = s.replace("updateRoad(true);});if(!navigator.onLine)", "preloadRouteData();updateRoad(true);});if(!navigator.onLine)", 1)

s = s.replace('VERSION 48 • ADAPTIV NAVIGATION', 'VERSION 49 • TEST + OMDIRIGERING')
for n in range(1, 49):
    s = s.replace(f'VERSION {n} • "+selectedDay.toUpperCase()', 'VERSION 49 • "+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\"+selectedDay.toUpperCase()', 'VERSION 49 • \\"+selectedDay.toUpperCase()')
    s = s.replace(f'VERSION {n} • \\\"+selectedDay.toUpperCase()', 'VERSION 49 • \\\"+selectedDay.toUpperCase()')

main.write_text(s, encoding='utf-8')

b = Path('app/build.gradle')
t = b.read_text(encoding='utf-8').replace('versionCode 48', 'versionCode 49').replace('versionName "48.0"', 'versionName "49.0"')
b.write_text(t, encoding='utf-8')

print('Version 49 applied: simulation, off-route rerouting and preloaded offline navigation plan')
