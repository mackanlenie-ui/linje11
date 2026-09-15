package se.minaarbetspass;

import android.app.AlertDialog;
import android.view.View;
import android.widget.PopupMenu;

public class MainActivityCurrent extends MainActivityV19 {
    @Override void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);
        p.getMenu().add("Säkerhetskopiera");
        p.getMenu().add("Återställ säkerhetskopia");
        p.getMenu().add("Passmallar");
        p.getMenu().add("Påminnelser");
        p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{
            String s=i.getTitle().toString();
            if(s.startsWith("Säker"))exportData();
            else if(s.startsWith("Åter"))importData();
            else if(s.equals("Passmallar"))chooseTemplate();
            else if(s.equals("Påminnelser"))reminderSettings();
            else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.9.1\n\nNy veckoplan och förbättrad idag-/nästa-pass-översikt för både mina pass och Lenies schema.\n\nFrån och med den här versionen används en permanent signeringsnyckel så kommande versioner kan installeras som vanliga uppdateringar.\n\nDina uppgifter sparas endast lokalt i telefonen. Lenies schema får inga arbetspåminnelser.").setPositiveButton("OK",null).show();
            return true;
        });
        p.show();
    }
}
