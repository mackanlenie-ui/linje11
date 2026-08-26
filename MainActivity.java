package se.linje11.gps;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private static final String[] OUTBOUND = new String[] {
            "Södra Åbyggeby, Gävle",
            "Norra Åbyggeby, Gävle",
            "Forsby, Gävle",
            "Strömsbro skola, Gävle",
            "Rådhuset, Gävle"
    };

    private static final String[] INBOUND = new String[] {
            "Rådhuset, Gävle",
            "Strömsbro skola, Gävle",
            "Forsby, Gävle",
            "Norra Åbyggeby, Gävle",
            "Södra Åbyggeby, Gävle"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button outbound = findViewById(R.id.btnOutbound);
        Button inbound = findViewById(R.id.btnInbound);

        outbound.setOnClickListener(v -> openRoute(OUTBOUND));
        inbound.setOnClickListener(v -> openRoute(INBOUND));
    }

    private void openRoute(String[] stops) {
        if (stops.length < 2) return;

        String origin = Uri.encode(stops[0]);
        String destination = Uri.encode(stops[stops.length - 1]);

        StringBuilder waypoints = new StringBuilder();
        for (int i = 1; i < stops.length - 1; i++) {
            if (waypoints.length() > 0) waypoints.append("%7C");
            waypoints.append(Uri.encode(stops[i]));
        }

        String url = "https://www.google.com/maps/dir/?api=1"
                + "&origin=" + origin
                + "&destination=" + destination
                + "&waypoints=" + waypoints
                + "&travelmode=driving";

        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
        intent.setPackage("com.google.android.apps.maps");

        try {
            startActivity(intent);
        } catch (Exception e) {
            Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            try {
                startActivity(browserIntent);
            } catch (Exception ex) {
                Toast.makeText(this, "Kunde inte öppna kartan.", Toast.LENGTH_LONG).show();
            }
        }
    }
}
