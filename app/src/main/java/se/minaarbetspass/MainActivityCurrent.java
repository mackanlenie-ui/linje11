package se.minaarbetspass;

import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.PopupMenu;

public class MainActivityCurrent extends MainActivityV114 {
    @Override public SharedPreferences getPreferences(int mode){return AppPrefs.get(this);}

    @Override void showMenu(View anchor){
        PopupMenu p=new PopupMenu(this,anchor);
        p.getMenu().add("Importera schema från foto");
        p.getMenu().add("Återkommande pass");
        p.getMenu().add("Exportera till kalender");
        p.getMenu().add("Ångra senaste fotoimport");
        p.getMenu().add("Säkerhetskopiera");
        p.getMenu().add("Återställ säkerhetskopia");
        p.getMenu().add("Passmallar");
        p.getMenu().add("Påminnelser");
        p.getMenu().add("Om appen");
        p.setOnMenuItemClickListener(i->{
            String s=i.getTitle().toString();
            if(s.equals("Importera schema från foto"))importScheduleFromPhoto();
            else if(s.equals("Återkommande pass"))createRecurringShift();
            else if(s.equals("Exportera till kalender"))exportCalendarDialog();
            else if(s.equals("Ångra senaste fotoimport"))undoLatestPhotoImport();
            else if(s.startsWith("Säker"))exportData();
            else if(s.startsWith("Åter"))importData();
            else if(s.equals("Passmallar"))chooseTemplate();
            else if(s.equals("Påminnelser"))reminderSettings();
            else new AlertDialog.Builder(this).setTitle("Mina arbetspass").setMessage("Version 1.14\n\nNy hemskärmswidget visar ditt nästa pass, Lenies nästa pass och nästa gemensamma lediga dag.\n\nÅterkommande pass kan läggas in varje vecka eller varannan vecka. Kalenderexport skapar en .ics-fil för Samsung Calendar, Google Calendar eller annan kalenderapp.\n\nVår kalender visar tydligt om bara du jobbar, bara Lenie jobbar, båda jobbar eller båda är lediga.").setPositiveButton("OK",null).show();
            return true;
        });
        p.show();
    }
}
