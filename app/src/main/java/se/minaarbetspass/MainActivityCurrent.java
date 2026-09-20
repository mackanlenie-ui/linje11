package se.minaarbetspass;

import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.PopupMenu;

public class MainActivityCurrent extends MainActivityV113 {
    @Override public SharedPreferences getPreferences(int mode){return AppPrefs.get(this);}

    @Override void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);
        p.getMenu().add("Importera schema från foto");
        p.getMenu().add("Ångra senaste fotoimport");
        p.getMenu().add("Säkerhetskopiera");
        p.getMenu().add("Återställ säkerhetskopia");
        p.getMenu().add("Passmallar");
        p.getMenu().add("Påminnelser");
        p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{
            String s=i.getTitle().toString();
            if(s.equals("Importera schema från foto"))importScheduleFromPhoto();
            else if(s.equals("Ångra senaste fotoimport"))undoLatestPhotoImport();
            else if(s.startsWith("Säker"))exportData();
            else if(s.startsWith("Åter"))importData();
            else if(s.equals("Passmallar"))chooseTemplate();
            else if(s.equals("Påminnelser"))reminderSettings();
            else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.13\n\nFotoimporten gör nu en extra kontrastförbättrad avläsning och väljer den tolkning som hittar flest användbara schemarader.\n\nOsäkra rader visas tydligt utan gissad tid, varje rad kan redigeras före sparning och dubbletter jämförs med normaliserade datum/tider.\n\nSenaste fotoimporten kan ångras utan att andra pass tas bort.").setPositiveButton("OK",null).show();
            return true;
        });
        p.show();
    }
}
