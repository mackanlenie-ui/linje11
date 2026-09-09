package se.steffy.facebookfirefox;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        openFacebookDesktop();
    }

    private void openFacebookDesktop() {
        Uri desktopFacebook = Uri.parse("https://www.facebook.com/home.php?m2w");
        Intent intent = new Intent(Intent.ACTION_VIEW, desktopFacebook);
        intent.setPackage("org.mozilla.firefox");
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            startActivity(intent);
        } catch (ActivityNotFoundException e) {
            intent.setPackage(null);
            try {
                startActivity(intent);
            } catch (ActivityNotFoundException ignored) {
                Toast.makeText(this, "Firefox eller annan webbläsare saknas", Toast.LENGTH_LONG).show();
            }
        }
        finish();
    }
}
