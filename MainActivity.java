package se.gpsrutt.inspelare;

import android.Manifest;
import android.app.Activity;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.*;
import android.os.*;
import android.view.*;
import android.webkit.*;
import android.widget.*;

import org.json.JSONArray;
import org.json.JSONObject;

public class MainActivity extends Activity {
    private static final int REQ_LOCATION = 1001;
    private static final int REQ_NOTIFY = 1002;

    private TextView status;
    private TextView gps;
    private TextView stopCount;

    private final BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override public void onReceive(Context c, Intent i) {
            if (TrackingService.ACTION_UPDATE.equals(i.getAction())) {
                double lat = i.getDoubleExtra("lat", 0);
                double lon = i.getDoubleExtra("lon", 0);
                float speed = i.getFloatExtra("speed", 0);
                float acc = i.getFloatExtra("accuracy", -1);
                gps.setText(String.format(java.util.Locale.getDefault(),
                        "GPS: %.6f, %.6f\nHastighet: %.1f km/h • Noggrannhet: %.0f m",
                        lat, lon, speed * 3.6f, acc));
                status.setText("● Inspelning aktiv");
                status.setTextColor(Color.rgb(20, 120, 60));
            } else if (TrackingService.ACTION_STOP.equals(i.getAction())) {
                refreshCounts();
                String address = i.getStringExtra("address");
                if (address == null || address.trim().isEmpty()) address = "okänd adress";
                Toast.makeText(MainActivity.this, "📍 Stopp markerat: " + address, Toast.LENGTH_LONG).show();
            }
        }
    };

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        buildUi();
        requestPermissionsIfNeeded();
    }

    private void buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(24, 28, 24, 32);

        TextView title = text("GPS Ruttinspelare", 28, true);
        title.setGravity(Gravity.CENTER_HORIZONTAL);
        root.addView(title);

        TextView sub = text("Ingen förinlagd rutt. Appen skapar rutten medan du kör.", 15, false);
        sub.setGravity(Gravity.CENTER_HORIZONTAL);
        sub.setPadding(0, 6, 0, 22);
        root.addView(sub);

        status = text("Inspelning inte startad", 18, true);
        root.addView(status);

        gps = text("GPS: väntar…", 15, false);
        gps.setPadding(0, 8, 0, 16);
        root.addView(gps);

        stopCount = text("", 16, true);
        stopCount.setPadding(0, 0, 0, 16);
        root.addView(stopCount);

        Button start = button("▶ Starta ny körning");
        start.setOnClickListener(v -> {
            TripStore.clear(this);
            startTracking();
            refreshCounts();
        });
        root.addView(start);

        Button stop = button("■ Avsluta körning");
        stop.setOnClickListener(v -> {
            stopService(new Intent(this, TrackingService.class));
            status.setText("Körningen avslutad");
            status.setTextColor(Color.DKGRAY);
            refreshCounts();
        });
        root.addView(stop);

        Button map = button("🗺 Visa inspelad rutt + stopp");
        map.setOnClickListener(v -> showMap());
        root.addView(map);

        Button manual = button("📍 Lägg till stopp manuellt");
        manual.setOnClickListener(v -> Toast.makeText(this,
                "Manuell stoppknapp kan läggas till i nästa version.", Toast.LENGTH_SHORT).show());
        root.addView(manual);

        TextView info = text(
                "Automatik: rutten sparas löpande från GPS. Ett stopp markeras efter att du har kört och sedan varit nästan stilla i cirka 12 sekunder. Appen försöker automatiskt hämta gatunamn/adress för varje stopp. Stopp nära föregående stopp filtreras bort.",
                13, false);
        info.setPadding(4, 14, 4, 0);
        root.addView(info);

        ScrollView scroll = new ScrollView(this);
        scroll.addView(root);
        setContentView(scroll);
        refreshCounts();
    }

    private void refreshCounts() {
        JSONArray r = TripStore.route(this);
        JSONArray s = TripStore.stops(this);
        stopCount.setText("Ruttpunkter: " + r.length() + "   •   Stopp: " + s.length());
    }

    private void requestPermissionsIfNeeded() {
        if (Build.VERSION.SDK_INT >= 23 &&
                checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
            }, REQ_LOCATION);
        }
        if (Build.VERSION.SDK_INT >= 33 &&
                checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIFY);
        }
    }

    private void startTracking() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            requestPermissionsIfNeeded();
            return;
        }
        Intent s = new Intent(this, TrackingService.class);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(s);
        else startService(s);
        status.setText("● Inspelning startar…");
        status.setTextColor(Color.rgb(20, 120, 60));
    }

    private void showMap() {
        JSONArray route = TripStore.route(this);
        JSONArray stops = TripStore.stops(this);

        if (route.length() < 2) {
            Toast.makeText(this, "För få GPS-punkter ännu.", Toast.LENGTH_SHORT).show();
            return;
        }

        WebView web = new WebView(this);
        WebSettings st = web.getSettings();
        st.setJavaScriptEnabled(true);
        st.setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient());

        StringBuilder routeJs = new StringBuilder("[");
        for (int i = 0; i < route.length(); i++) {
            try {
                JSONObject o = route.getJSONObject(i);
                if (i > 0) routeJs.append(",");
                routeJs.append("[").append(o.getDouble("lat")).append(",").append(o.getDouble("lon")).append("]");
            } catch (Exception ignored) {}
        }
        routeJs.append("]");

        StringBuilder stopsJs = new StringBuilder("[");
        for (int i = 0; i < stops.length(); i++) {
            try {
                JSONObject o = stops.getJSONObject(i);
                if (i > 0) stopsJs.append(",");
                String addr = o.optString("address", "");
                addr = addr.replace("\\", "\\\\").replace("'", "\\'");
                stopsJs.append("{lat:").append(o.getDouble("lat"))
                        .append(",lon:").append(o.getDouble("lon"))
                        .append(",n:").append(o.getInt("number"))
                        .append(",address:'").append(addr).append("'}");
            } catch (Exception ignored) {}
        }
        stopsJs.append("]");

        String html = "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>" +
                "<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>" +
                "<style>html,body,#map{height:100%;margin:0}.stop{background:#fff;border:3px solid #d32f2f;border-radius:50%;width:32px;height:32px;line-height:26px;text-align:center;font-weight:bold}</style>" +
                "</head><body><div id='map'></div><script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script><script>" +
                "const route=" + routeJs + ";const stops=" + stopsJs + ";" +
                "const map=L.map('map');" +
                "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}).addTo(map);" +
                "const line=L.polyline(route,{weight:6}).addTo(map);map.fitBounds(line.getBounds(),{padding:[30,30]});" +
                "stops.forEach(s=>L.marker([s.lat,s.lon],{icon:L.divIcon({className:'',html:'<div class=\"stop\">'+s.n+'</div>',iconSize:[36,36],iconAnchor:[18,18]})}).addTo(map).bindPopup('<b>Stopp '+s.n+'</b><br>'+s.address));" +
                "</script></body></html>";

        web.loadDataWithBaseURL("https://gpsrutt.local/", html, "text/html", "UTF-8", null);
        setContentView(web);
    }

    @Override public void onBackPressed() {
        buildUi();
    }

    private Button button(String s) {
        Button b = new Button(this);
        b.setText(s);
        b.setAllCaps(false);
        b.setTextSize(16);
        return b;
    }

    private TextView text(String s, int sp, boolean bold) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(sp);
        if (bold) t.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return t;
    }

    @Override protected void onResume() {
        super.onResume();
        IntentFilter f = new IntentFilter();
        f.addAction(TrackingService.ACTION_UPDATE);
        f.addAction(TrackingService.ACTION_STOP);
        if (Build.VERSION.SDK_INT >= 33) registerReceiver(receiver, f, RECEIVER_NOT_EXPORTED);
        else registerReceiver(receiver, f);
    }

    @Override protected void onPause() {
        try { unregisterReceiver(receiver); } catch (Exception ignored) {}
        super.onPause();
    }
}
