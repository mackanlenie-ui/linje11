package se.gpsrutt.inspelare;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.location.*;
import android.os.*;

import java.util.List;
import java.util.Locale;

public class TrackingService extends Service implements LocationListener {
    public static final String ACTION_UPDATE = "se.gpsrutt.inspelare.UPDATE";
    public static final String ACTION_STOP = "se.gpsrutt.inspelare.STOP";
    private static final String CHANNEL = "tracking";
    private static final int NOTIF = 42;

    private static final float MOVING_SPEED = 2.5f;
    private static final float STOP_SPEED = 1.0f;
    private static final long STOP_TIME = 12000L;
    private static final float DUPLICATE_RADIUS = 30f;

    private LocationManager lm;
    private boolean hasMoved = false;
    private long slowSince = 0L;
    private Location lastRoutePoint;
    private Location lastStop;

    @Override public void onCreate() {
        super.onCreate();
        createChannel();

        Intent open = new Intent(this, MainActivity.class);
        PendingIntent pi = PendingIntent.getActivity(this, 0, open,
                PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT);

        Notification n = new Notification.Builder(this, CHANNEL)
                .setContentTitle("GPS Ruttinspelare")
                .setContentText("Spelar in körning, stopp och adresser")
                .setSmallIcon(android.R.drawable.ic_menu_mylocation)
                .setOngoing(true)
                .setContentIntent(pi)
                .build();

        startForeground(NOTIF, n);
        startGps();
    }

    private void createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel c = new NotificationChannel(CHANNEL, "GPS-inspelning",
                    NotificationManager.IMPORTANCE_LOW);
            getSystemService(NotificationManager.class).createNotificationChannel(c);
        }
    }

    private void startGps() {
        lm = (LocationManager)getSystemService(LOCATION_SERVICE);
        if (lm == null) return;
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            stopSelf();
            return;
        }
        lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 1f, this);
    }

    @Override public void onLocationChanged(Location loc) {
        float speed = loc.hasSpeed() ? loc.getSpeed() : 0f;

        if (lastRoutePoint == null || lastRoutePoint.distanceTo(loc) >= 5f) {
            TripStore.addRoutePoint(this, loc.getLatitude(), loc.getLongitude(),
                    speed, loc.hasAccuracy() ? loc.getAccuracy() : -1f);
            lastRoutePoint = new Location(loc);
        }

        if (speed >= MOVING_SPEED) {
            hasMoved = true;
            slowSince = 0L;
        } else if (hasMoved && speed <= STOP_SPEED) {
            if (slowSince == 0L) slowSince = System.currentTimeMillis();

            if (System.currentTimeMillis() - slowSince >= STOP_TIME) {
                boolean duplicate = lastStop != null && lastStop.distanceTo(loc) < DUPLICATE_RADIUS;
                if (!duplicate) {
                    final Location saved = new Location(loc);
                    lastStop = new Location(loc);
                    geocodeAndSaveStop(saved);
                }
                hasMoved = false;
                slowSince = 0L;
            }
        } else if (speed > STOP_SPEED) {
            slowSince = 0L;
        }

        Intent i = new Intent(ACTION_UPDATE);
        i.putExtra("lat", loc.getLatitude());
        i.putExtra("lon", loc.getLongitude());
        i.putExtra("speed", speed);
        i.putExtra("accuracy", loc.hasAccuracy() ? loc.getAccuracy() : -1f);
        sendBroadcast(i);
    }

    private void geocodeAndSaveStop(Location loc) {
        final double lat = loc.getLatitude();
        final double lon = loc.getLongitude();
        final float acc = loc.hasAccuracy() ? loc.getAccuracy() : -1f;

        if (!Geocoder.isPresent()) {
            saveStopAndBroadcast(lat, lon, acc, coordFallback(lat, lon));
            return;
        }

        Geocoder geocoder = new Geocoder(this, new Locale("sv", "SE"));

        if (Build.VERSION.SDK_INT >= 33) {
            geocoder.getFromLocation(lat, lon, 1, new Geocoder.GeocodeListener() {
                @Override public void onGeocode(List<Address> addresses) {
                    String address = formatAddress(addresses, lat, lon);
                    saveStopAndBroadcast(lat, lon, acc, address);
                }

                @Override public void onError(String errorMessage) {
                    saveStopAndBroadcast(lat, lon, acc, coordFallback(lat, lon));
                }
            });
        } else {
            new Thread(() -> {
                String address = coordFallback(lat, lon);
                try {
                    List<Address> addresses = geocoder.getFromLocation(lat, lon, 1);
                    address = formatAddress(addresses, lat, lon);
                } catch (Exception ignored) {}
                saveStopAndBroadcast(lat, lon, acc, address);
            }).start();
        }
    }

    private String formatAddress(List<Address> addresses, double lat, double lon) {
        if (addresses == null || addresses.isEmpty()) return coordFallback(lat, lon);
        Address a = addresses.get(0);

        String road = a.getThoroughfare();
        String number = a.getSubThoroughfare();
        String locality = a.getLocality();
        String subLocality = a.getSubLocality();

        StringBuilder s = new StringBuilder();
        if (road != null && !road.trim().isEmpty()) {
            s.append(road.trim());
            if (number != null && !number.trim().isEmpty()) s.append(" ").append(number.trim());
        } else if (a.getFeatureName() != null && !a.getFeatureName().trim().isEmpty()) {
            s.append(a.getFeatureName().trim());
        }

        String place = locality;
        if ((place == null || place.trim().isEmpty()) && subLocality != null) place = subLocality;

        if (place != null && !place.trim().isEmpty()) {
            if (s.length() > 0 && !s.toString().contains(place.trim())) s.append(", ");
            if (!s.toString().contains(place.trim())) s.append(place.trim());
        }

        if (s.length() == 0) {
            String line = a.getAddressLine(0);
            if (line != null && !line.trim().isEmpty()) s.append(line.trim());
        }

        return s.length() == 0 ? coordFallback(lat, lon) : s.toString();
    }

    private String coordFallback(double lat, double lon) {
        return String.format(Locale.US, "%.6f, %.6f", lat, lon);
    }

    private void saveStopAndBroadcast(double lat, double lon, float acc, String address) {
        TripStore.addStop(this, lat, lon, acc, address);
        Intent i = new Intent(ACTION_STOP);
        i.putExtra("address", address);
        sendBroadcast(i);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override public void onDestroy() {
        if (lm != null) {
            try { lm.removeUpdates(this); } catch (Exception ignored) {}
        }
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }
    @Override public void onProviderEnabled(String provider) {}
    @Override public void onProviderDisabled(String provider) {}
    @Override public void onStatusChanged(String provider, int status, Bundle extras) {}
}
