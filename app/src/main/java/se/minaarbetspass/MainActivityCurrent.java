package se.minaarbetspass;

import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.PopupMenu;

public class MainActivityCurrent extends MainActivityV112 {
    @Override public SharedPreferences getPreferences(int mode){return AppPrefs.get(this);}

    @Override void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);
        p.getMenu().add("Importera schema från foto");
        p.getMenu().add("Säkerhetskopiera");
        p.getMenu().add("Återställ säkerhetskopia");
        p.getMenu().add("Passmallar");
        p.getMenu().add("Påminnelser");
        p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{
            String s=i.getTitle().toString();
            if(s.equals("Importera schema från foto"))importScheduleFromPhoto();
            else if(s.startsWith("Säker"))exportData();
            else if(s.startsWith("Åter"))importData();
            else if(s.equals("Passmallar"))chooseTemplate();
            else if(s.equals("Påminnelser"))reminderSettings();
            else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.12\n\nLenies tydligt läsbara oktoberpass från pappersschemat läggs in automatiskt utan att skriva över befintliga pass.\n\nNy fotoimport kan ta eller välja en schemabild, tolka tydliga datum/tider och visar alltid en granskningslista innan något sparas. Handskrift kan feltolkas, så kontrollera alltid resultatet.\n\nAppen använder samma permanenta signering som tidigare versioner och kan installeras som en vanlig uppdatering.").setPositiveButton("OK",null).show();
            return true;
        });
        p.show();
    }
}
