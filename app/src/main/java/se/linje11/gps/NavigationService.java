package se.linje11.gps;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.location.*;
import android.os.*;
import androidx.core.app.ActivityCompat;

public class NavigationService extends Service implements LocationListener {
    public static final String ACTION_LOCATION = "se.linje11.gps.BG_LOCATION";
    private static final String CHANNEL_ID = "rutt_gps_navigation";
    private static final int NOTIFICATION_ID = 5401;
    private LocationManager locationManager;

    @Override public void onCreate() {
        super.onCreate();
        createChannel();
        startForeground(NOTIFICATION_ID, buildNotification("GPS aktiv • navigation körs i bakgrunden"));
        startLocationUpdates();
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        startLocationUpdates();
        return START_STICKY;
    }

    private void createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel c = new NotificationChannel(CHANNEL_ID, "Rutt GPS navigation", NotificationManager.IMPORTANCE_LOW);
            c.setDescription("Håller GPS och navigation aktiva under körning");
            c.setShowBadge(false);
            ((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(c);
        }
    }

    private Notification buildNotification(String text) {
        Intent open = new Intent(this, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O ? new Notification.Builder(this, CHANNEL_ID) : new Notification.Builder(this);
        return b.setContentTitle("Rutt GPS • Körnavigation")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.ic_menu_mylocation)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setContentIntent(pi)
                .build();
    }

    private void startLocationUpdates() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
                ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) return;
        if (locationManager == null) locationManager = (LocationManager)getSystemService(LOCATION_SERVICE);
        try { locationManager.removeUpdates(this); } catch (Exception ignored) {}
        try {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER))
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 1f, this, Looper.getMainLooper());
        } catch (Exception ignored) {}
        try {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER))
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2500L, 3f, this, Looper.getMainLooper());
        } catch (Exception ignored) {}
    }

    @Override public void onLocationChanged(Location loc) {
        getSharedPreferences("nav_bg", MODE_PRIVATE).edit()
                .putFloat("lat", (float)loc.getLatitude())
                .putFloat("lon", (float)loc.getLongitude())
                .putFloat("acc", loc.hasAccuracy()?loc.getAccuracy():999f)
                .putFloat("speed", loc.hasSpeed()?loc.getSpeed():0f)
                .putFloat("bearing", loc.hasBearing()?loc.getBearing():-1f)
                .putLong("time", System.currentTimeMillis()).apply();
        Intent i = new Intent(ACTION_LOCATION);
        i.setPackage(getPackageName());
        i.putExtra("lat", loc.getLatitude());
        i.putExtra("lon", loc.getLongitude());
        i.putExtra("acc", loc.hasAccuracy()?loc.getAccuracy():999f);
        i.putExtra("speed", loc.hasSpeed()?loc.getSpeed():0f);
        i.putExtra("bearing", loc.hasBearing()?loc.getBearing():-1f);
        sendBroadcast(i);
    }

    @Override public void onProviderEnabled(String provider) {}
    @Override public void onProviderDisabled(String provider) {}
    @SuppressWarnings("deprecation") @Override public void onStatusChanged(String provider, int status, Bundle extras) {}

    @Override public void onDestroy() {
        if (locationManager != null) try { locationManager.removeUpdates(this); } catch (Exception ignored) {}
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}
