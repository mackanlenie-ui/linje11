package se.filmprop.finance;

import android.app.Activity;
import android.app.AlertDialog;
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
import android.widget.Toast;

public class MainActivity extends Activity {
    private final int BLUE = Color.rgb(35, 49, 111);
    private final int BLUE_DARK = Color.rgb(26, 36, 86);
    private final int ACCENT = Color.rgb(107, 92, 246);
    private final int BG = Color.rgb(246, 247, 251);
    private final int WHITE = Color.WHITE;
    private final int INK = Color.rgb(28, 31, 42);
    private final int MUTED = Color.rgb(105, 110, 128);
    private final int LINE = Color.rgb(229, 231, 238);
    private final int SOFT = Color.rgb(237, 239, 248);

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BLUE_DARK);
        getWindow().setNavigationBarColor(WHITE);

        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setBackgroundColor(BG);

        page.addView(topBar(), new LinearLayout.LayoutParams(-1, dp(104)));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(18), dp(18), dp(18), dp(28));
        scroll.addView(content);

        content.addView(title("Översikt", 28));
        content.addView(space(18));
        content.addView(sectionTitle("Genvägar"));
        content.addView(shortcuts());
        content.addView(space(22));
        content.addView(sectionTitle("Betala och överföra"));
        content.addView(paymentCard());
        content.addView(space(22));
        content.addView(sectionTitle("Konton och kort"));
        content.addView(accountSummary());
        content.addView(space(12));
        content.addView(accountCard());
        content.addView(space(26));

        LinearLayout footer = new LinearLayout(this);
        footer.setGravity(Gravity.CENTER);
        footer.addView(text("Tryggt. Enkelt. Nordia.", 12, MUTED, false));
        content.addView(footer);

        page.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        page.addView(bottomNav(), new LinearLayout.LayoutParams(-1, dp(74)));
        setContentView(page);
    }

    private View topBar() {
        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(18), dp(10), dp(16), 0);
        bar.setBackgroundColor(BLUE_DARK);

        TextView menu = text("☰", 24, WHITE, false);
        menu.setGravity(Gravity.CENTER);
        bar.addView(menu, new LinearLayout.LayoutParams(dp(42), dp(52)));

        LinearLayout brand = new LinearLayout(this);
        brand.setOrientation(LinearLayout.VERTICAL);
        brand.setPadding(dp(8), 0, 0, 0);
        brand.addView(text("Nordia", 27, WHITE, true));
        brand.addView(text("Din digitala vardagsbank", 12, Color.rgb(213, 218, 245), false));
        bar.addView(brand, new LinearLayout.LayoutParams(0, -2, 1));

        TextView profile = text("N", 17, BLUE_DARK, true);
        profile.setGravity(Gravity.CENTER);
        profile.setBackground(circle(Color.rgb(225, 228, 250)));
        bar.addView(profile, new LinearLayout.LayoutParams(dp(44), dp(44)));
        return bar;
    }

    private View shortcuts() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER);
        row.addView(shortcut("↔", "Betala och\növerföra"), weightMargins(0, 5));
        row.addView(shortcut("⇄", "Överföring\neget konto"), weightMargins(5, 5));
        row.addView(shortcut("⚙", "Inställningar"), weightMargins(5, 5));
        row.addView(shortcut("⌕", "Sök"), weightMargins(5, 0));
        return row;
    }

    private View shortcut(String icon, String label) {
        LinearLayout wrap = new LinearLayout(this);
        wrap.setOrientation(LinearLayout.VERTICAL);
        wrap.setGravity(Gravity.TOP | Gravity.CENTER_HORIZONTAL);
        wrap.setPadding(dp(4), dp(4), dp(4), 0);

        TextView i = text(icon, 22, BLUE, true);
        i.setGravity(Gravity.CENTER);
        i.setBackground(circle(SOFT));
        wrap.addView(i, new LinearLayout.LayoutParams(dp(54), dp(54)));

        TextView l = text(label, 11, INK, true);
        l.setGravity(Gravity.CENTER);
        l.setPadding(0, dp(7), 0, 0);
        wrap.addView(l, new LinearLayout.LayoutParams(-1, dp(42)));

        wrap.setOnClickListener(v -> Toast.makeText(this, "Funktionen är inte aktiv i den här versionen", Toast.LENGTH_SHORT).show());
        return wrap;
    }

    private View paymentCard() {
        LinearLayout card = card(WHITE);
        LinearLayout status = horizontal();

        TextView icon = text("✓", 18, ACCENT, true);
        icon.setGravity(Gravity.CENTER);
        icon.setBackground(circle(Color.rgb(236, 233, 255)));
        status.addView(icon, new LinearLayout.LayoutParams(dp(42), dp(42)));

        LinearLayout info = new LinearLayout(this);
        info.setOrientation(LinearLayout.VERTICAL);
        info.setPadding(dp(12), 0, 0, 0);
        info.addView(text("Du har inga betalningar.", 15, INK, true));
        info.addView(text("Allt är klart just nu", 12, MUTED, false));
        status.addView(info, new LinearLayout.LayoutParams(0, -2, 1));
        card.addView(status);

        card.addView(divider(16));

        LinearLayout action = horizontal();
        action.addView(text("Betala och överföra", 15, BLUE, true), new LinearLayout.LayoutParams(0, -2, 1));
        TextView arrow = text("›", 28, BLUE, false);
        arrow.setGravity(Gravity.CENTER);
        action.addView(arrow, new LinearLayout.LayoutParams(dp(32), dp(40)));
        action.setOnClickListener(v -> Toast.makeText(this, "Funktionen är inte aktiv", Toast.LENGTH_SHORT).show());
        card.addView(action);
        return card;
    }

    private View accountSummary() {
        LinearLayout card = card(WHITE);
        LinearLayout row = horizontal();

        LinearLayout left = new LinearLayout(this);
        left.setOrientation(LinearLayout.VERTICAL);
        left.addView(text("Tillgängligt belopp på konton", 13, MUTED, false));
        left.addView(space(3));
        left.addView(text("1 konto", 12, MUTED, false));
        row.addView(left, new LinearLayout.LayoutParams(0, -2, 1));

        TextView amount = text("40,65", 22, INK, true);
        amount.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        row.addView(amount, new LinearLayout.LayoutParams(dp(125), dp(48)));
        card.addView(row);
        return card;
    }

    private View accountCard() {
        LinearLayout card = card(WHITE);
        LinearLayout top = horizontal();

        LinearLayout name = new LinearLayout(this);
        name.setOrientation(LinearLayout.VERTICAL);
        name.addView(text("PERSONKONTO", 14, INK, true));
        name.addView(text("3015 03 19088", 12, MUTED, false));
        top.addView(name, new LinearLayout.LayoutParams(0, -2, 1));

        TextView amount = text("40,65", 19, INK, true);
        amount.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        top.addView(amount, new LinearLayout.LayoutParams(dp(100), dp(48)));
        card.addView(top);

        card.addView(divider(13));

        LinearLayout bottom = horizontal();
        bottom.addView(text("Tillgängligt belopp", 12, MUTED, false), new LinearLayout.LayoutParams(0, -2, 1));
        TextView open = text("›", 26, BLUE, false);
        open.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
        bottom.addView(open, new LinearLayout.LayoutParams(dp(36), dp(38)));
        card.addView(bottom);
        return card;
    }

    private View bottomNav() {
        LinearLayout nav = new LinearLayout(this);
        nav.setOrientation(LinearLayout.HORIZONTAL);
        nav.setGravity(Gravity.CENTER);
        nav.setPadding(dp(4), dp(4), dp(4), dp(6));
        nav.setBackgroundColor(WHITE);
        nav.addView(navItem("⌂", "Översikt", true, false), weight());
        nav.addView(navItem("◔", "Få koll", false, false), weight());
        nav.addView(navItem("◇", "Spara", false, false), weight());
        nav.addView(navItem("▦", "Tjänster", false, false), weight());
        nav.addView(navItem("?", "Hjälp", false, true), weight());
        return nav;
    }

    private View navItem(String icon, String label, boolean active, boolean help) {
        LinearLayout item = new LinearLayout(this);
        item.setOrientation(LinearLayout.VERTICAL);
        item.setGravity(Gravity.CENTER);
        int color = active ? BLUE : MUTED;
        item.addView(text(icon, 20, color, true));
        TextView l = text(label, 10, color, active);
        l.setPadding(0, dp(3), 0, 0);
        item.addView(l);

        if (help) {
            item.setOnClickListener(v -> new AlertDialog.Builder(this)
                    .setTitle("Om Nordia")
                    .setMessage("Nordia är en helt fiktiv bankapp skapad som rekvisita för filmproduktion. Den är inte ansluten till någon bank, saknar internetbehörighet och kan inte genomföra bankärenden.")
                    .setPositiveButton("OK", null)
                    .show());
        } else if (!active) {
            item.setOnClickListener(v -> Toast.makeText(this, "Funktionen är inte aktiv", Toast.LENGTH_SHORT).show());
        }
        return item;
    }

    private LinearLayout card(int color) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(17), dp(16), dp(17), dp(16));
        card.setBackground(round(color, 18));
        card.setElevation(dp(1));
        return card;
    }

    private LinearLayout horizontal() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        return row;
    }

    private TextView title(String s, int size) { return text(s, size, INK, true); }

    private TextView sectionTitle(String s) {
        TextView v = text(s, 18, INK, true);
        v.setPadding(0, 0, 0, dp(10));
        return v;
    }

    private TextView text(String s, float size, int color, boolean bold) {
        TextView v = new TextView(this);
        v.setText(s);
        v.setTextSize(size);
        v.setTextColor(color);
        v.setIncludeFontPadding(false);
        if (bold) v.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return v;
    }

    private View divider(int padding) {
        LinearLayout box = new LinearLayout(this);
        box.setPadding(0, dp(padding), 0, dp(padding));
        View line = new View(this);
        line.setBackgroundColor(LINE);
        box.addView(line, new LinearLayout.LayoutParams(-1, dp(1)));
        return box;
    }

    private View space(int h) {
        Space s = new Space(this);
        s.setLayoutParams(new LinearLayout.LayoutParams(1, dp(h)));
        return s;
    }

    private LinearLayout.LayoutParams weight() { return new LinearLayout.LayoutParams(0, -1, 1); }

    private LinearLayout.LayoutParams weightMargins(int left, int right) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(0, -2, 1);
        p.leftMargin = dp(left);
        p.rightMargin = dp(right);
        return p;
    }

    private GradientDrawable round(int color, int radius) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(color);
        g.setCornerRadius(dp(radius));
        return g;
    }

    private GradientDrawable circle(int color) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(color);
        g.setShape(GradientDrawable.OVAL);
        return g;
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }
}
