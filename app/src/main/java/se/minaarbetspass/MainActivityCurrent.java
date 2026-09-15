package se.minaarbetspass;

import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.PopupMenu;

public class MainActivityCurrent extends MainActivityV111 {
    @Override public SharedPreferences getPreferences(int mode){return AppPrefs.get(this);}

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
            else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.11\n\nNy stabil datalagring med automatisk migrering, bläddring mellan veckor, kopiera vecka och gemensamt lediga kvällar.\n\nAppen använder samma permanenta signering som 1.9.1 och 1.10, så den kan installeras som en vanlig uppdatering.").setPositiveButton("OK",null).show();
            return true;
        });
        p.show();
    }
}
