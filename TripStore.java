package se.gpsrutt.inspelare;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;

public class TripStore {
    private static final String PREF = "trip_store";
    private static final String ROUTE = "route";
    private static final String STOPS = "stops";

    public static synchronized void clear(Context c) {
        c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit()
                .putString(ROUTE, "[]")
                .putString(STOPS, "[]")
                .apply();
    }

    public static synchronized void addRoutePoint(Context c, double lat, double lon, float speed, float accuracy) {
        try {
            SharedPreferences p = c.getSharedPreferences(PREF, Context.MODE_PRIVATE);
            JSONArray a = new JSONArray(p.getString(ROUTE, "[]"));
            JSONObject o = new JSONObject();
            o.put("lat", lat);
            o.put("lon", lon);
            o.put("time", System.currentTimeMillis());
            o.put("speed", speed);
            o.put("accuracy", accuracy);
            a.put(o);
            p.edit().putString(ROUTE, a.toString()).apply();
        } catch (Exception ignored) {}
    }

    public static synchronized void addStop(Context c, double lat, double lon, float accuracy, String address) {
        try {
            SharedPreferences p = c.getSharedPreferences(PREF, Context.MODE_PRIVATE);
            JSONArray a = new JSONArray(p.getString(STOPS, "[]"));
            JSONObject o = new JSONObject();
            o.put("number", a.length() + 1);
            o.put("lat", lat);
            o.put("lon", lon);
            o.put("time", System.currentTimeMillis());
            o.put("accuracy", accuracy);
            o.put("address", address == null ? "" : address);
            a.put(o);
            p.edit().putString(STOPS, a.toString()).apply();
        } catch (Exception ignored) {}
    }

    public static synchronized JSONArray route(Context c) {
        try {
            return new JSONArray(c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString(ROUTE, "[]"));
        } catch (Exception e) {
            return new JSONArray();
        }
    }

    public static synchronized JSONArray stops(Context c) {
        try {
            return new JSONArray(c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString(STOPS, "[]"));
        } catch (Exception e) {
            return new JSONArray();
        }
    }
}
