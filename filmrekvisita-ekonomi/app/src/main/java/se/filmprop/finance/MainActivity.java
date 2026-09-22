package se.filmprop.finance;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Space;
import android.widget.TextView;

public class MainActivity extends Activity {
    int navy = Color.rgb(23,19,75), ink = Color.rgb(34,34,43), muted = Color.rgb(103,104,116);
    int bg = Color.rgb(246,246,250), white = Color.WHITE, lavender = Color.rgb(234,232,255);

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().setStatusBarColor(navy);
        getWindow().setNavigationBarColor(white);

        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setBackgroundColor(bg);

        LinearLayout top = new LinearLayout(this);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setPadding(dp(18),dp(10),dp(14),0);
        top.setBackgroundColor(navy);
        TextView brand = t("FILMREKVISITA",18,white,true);
        TextView badge = t("DEMO",12,navy,true);
        badge.setGravity(Gravity.CENTER);
        badge.setPadding(dp(14),dp(7),dp(14),dp(7));
        badge.setBackground(round(Color.rgb(205,201,255),20));
        top.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        top.addView(badge);
        page.addView(top,new LinearLayout.LayoutParams(-1,dp(72)));

        ScrollView scroll = new ScrollView(this);
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setPadding(dp(18),dp(20),dp(18),dp(28));
        scroll.addView(c);
        page.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));

        c.addView(t("Hej, Alex & Robin",26,ink,true));
        c.addView(sp(5));
        c.addView(t("Fiktiv ekonomiöversikt för filminspelning",14,muted,false));
        c.addView(sp(18));

        LinearLayout account = card(navy);
        account.addView(t("Gemensamt konto",15,Color.rgb(214,211,242),true));
        account.addView(sp(10));
        account.addView(t("82 450,75 kr",32,white,true));
        account.addView(sp(10));
        account.addView(t("DEMO • konto •••• 4182",12,Color.rgb(194,190,229),false));
        c.addView(account);

        c.addView(section("Senaste händelser"));
        LinearLayout list = card(white);
        list.addView(row("Matbutik","Idag","− 428,50 kr"));
        list.addView(line());
        list.addView(row("Inkomst","20 sep","+ 32 840,00 kr"));
        list.addView(line());
        list.addView(row("Boende","18 sep","− 9 850,00 kr"));
        list.addView(line());
        list.addView(row("Bio & middag","17 sep","− 746,00 kr"));
        c.addView(list);

        c.addView(section("Kommande"));
        LinearLayout upcoming = card(white);
        upcoming.addView(row("Mobilabonnemang","24 sep","− 399,00 kr"));
        upcoming.addView(line());
        upcoming.addView(row("El","27 sep","− 684,00 kr"));
        c.addView(upcoming);

        c.addView(sp(22));
        TextView note = t("FILMREKVISITA • Alla namn, saldon och händelser är fiktiva. Appen saknar internetbehörighet och kan inte ansluta till någon bank eller genomföra några transaktioner.",11,muted,false);
        note.setPadding(dp(12),dp(12),dp(12),dp(12));
        note.setBackground(round(Color.rgb(237,237,244),14));
        c.addView(note);

        setContentView(page);
    }

    View row(String a,String b,String amount) {
        LinearLayout r = new LinearLayout(this);
        r.setGravity(Gravity.CENTER_VERTICAL);
        r.setPadding(0,dp(12),0,dp(12));
        TextView icon = t("•",24,navy,true);
        icon.setGravity(Gravity.CENTER);
        icon.setBackground(round(lavender,24));
        r.addView(icon,new LinearLayout.LayoutParams(dp(42),dp(42)));
        LinearLayout text = new LinearLayout(this);
        text.setOrientation(LinearLayout.VERTICAL);
        text.setPadding(dp(12),0,0,0);
        text.addView(t(a,15,ink,true));
        text.addView(t(b,12,muted,false));
        r.addView(text,new LinearLayout.LayoutParams(0,-2,1));
        TextView money = t(amount,14,ink,true);
        money.setGravity(Gravity.RIGHT);
        r.addView(money,new LinearLayout.LayoutParams(dp(132),-2));
        return r;
    }

    TextView section(String s) {
        TextView v=t(s,18,ink,true); v.setPadding(0,dp(24),0,dp(10)); return v;
    }
    LinearLayout card(int color) {
        LinearLayout v=new LinearLayout(this); v.setOrientation(LinearLayout.VERTICAL);
        v.setPadding(dp(18),dp(18),dp(18),dp(18)); v.setBackground(round(color,22)); return v;
    }
    TextView t(String s,float size,int color,boolean bold) {
        TextView v=new TextView(this); v.setText(s); v.setTextSize(size); v.setTextColor(color);
        if(bold) v.setTypeface(Typeface.DEFAULT,Typeface.BOLD); return v;
    }
    View sp(int h) { Space s=new Space(this); s.setLayoutParams(new LinearLayout.LayoutParams(1,dp(h))); return s; }
    View line() { View v=new View(this); v.setBackgroundColor(Color.rgb(226,226,234)); v.setLayoutParams(new LinearLayout.LayoutParams(-1,dp(1))); return v; }
    GradientDrawable round(int color,int radius) { GradientDrawable g=new GradientDrawable(); g.setColor(color); g.setCornerRadius(dp(radius)); return g; }
    int dp(int v) { return Math.round(v*getResources().getDisplayMetrics().density); }
}
