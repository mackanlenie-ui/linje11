package se.minaarbetspass;

import android.app.*;
import android.content.*;
import android.graphics.Rect;
import android.net.Uri;
import android.provider.MediaStore;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import java.io.File;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivityV112 extends MainActivityV111 {
    static final int PHOTO_CAMERA=1121,PHOTO_GALLERY=1122;
    static final String LENIE_OCT_SEED="__lenie_oct_2026_seed_v1";
    Uri pendingCameraUri;

    @Override void load(){
        super.load();
        seedLenieOctober2026();
    }

    void seedLenieOctober2026(){
        if(getPreferences(0).getBoolean(LENIE_OCT_SEED,false))return;
        int added=0;
        for(LenieOctober2026Seed.Entry e:LenieOctober2026Seed.entries()){
            Shift x=new Shift();x.owner=1;x.date=dateOf(2026,10,e.day);x.start=e.start;x.end=e.end;x.breakMin=0;x.done=false;x.kind="Ordinarie";
            x.note=(e.note.isEmpty()?"":e.note+" · ")+"Pappersschema oktober 2026 · rast ej angiven";
            if(hasLenieConflict(x))continue;
            shifts.add(x);added++;
        }
        if(added>0)save();
        getPreferences(0).edit().putBoolean(LENIE_OCT_SEED,true).apply();
    }

    long dateOf(int year,int month,int day){
        Calendar c=Calendar.getInstance();c.clear();c.set(year,month-1,day,0,0,0);return c.getTimeInMillis();
    }

    boolean exactLenieShift(Shift probe){
        for(Shift x:shifts)if(x.owner==1&&x.date==probe.date&&x.start.equals(probe.start)&&x.end.equals(probe.end))return true;
        return false;
    }

    boolean hasLenieConflict(Shift probe){
        for(Shift x:shifts)if(x.owner==1&&ScheduleInsights.overlaps(startAt(probe),endAt(probe),startAt(x),endAt(x)))return true;
        return false;
    }

    void importScheduleFromPhoto(){
        new AlertDialog.Builder(this).setTitle("Importera Lenies schema från foto")
            .setMessage("Appen försöker läsa datum och tider automatiskt. Handskrift kan feltolkas, så du får alltid granska passen innan de sparas.")
            .setItems(new String[]{"📷 Ta foto","🖼 Välj befintlig bild"},(d,w)->{if(w==0)takeSchedulePhoto();else chooseSchedulePhoto();})
            .setNegativeButton("Avbryt",null).show();
    }

    void takeSchedulePhoto(){
        try{
            Intent i=new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            if(i.resolveActivity(getPackageManager())==null){Toast.makeText(this,"Ingen kameraapp hittades",Toast.LENGTH_LONG).show();return;}
            File photo=File.createTempFile("lenie_schema_",".jpg",getCacheDir());
            pendingCameraUri=FileProvider.getUriForFile(this,getPackageName()+".fileprovider",photo);
            i.putExtra(MediaStore.EXTRA_OUTPUT,pendingCameraUri);
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            startActivityForResult(i,PHOTO_CAMERA);
        }catch(Exception e){Toast.makeText(this,"Kameran kunde inte startas",Toast.LENGTH_LONG).show();}
    }

    void chooseSchedulePhoto(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("image/*");startActivityForResult(i,PHOTO_GALLERY);
    }

    @Override protected void onActivityResult(int req,int result,Intent data){
        if(req==PHOTO_CAMERA||req==PHOTO_GALLERY){
            if(result==RESULT_OK){Uri uri=req==PHOTO_CAMERA?pendingCameraUri:(data==null?null:data.getData());if(uri!=null)scanSchedulePhoto(uri);}
            return;
        }
        super.onActivityResult(req,result,data);
    }

    void scanSchedulePhoto(Uri uri){
        final InputImage image;
        try{image=InputImage.fromFilePath(this,uri);}catch(Exception e){Toast.makeText(this,"Bilden kunde inte öppnas",Toast.LENGTH_LONG).show();return;}
        Toast.makeText(this,"Läser schemat…",Toast.LENGTH_SHORT).show();
        TextRecognizer recognizer=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        recognizer.process(image)
            .addOnSuccessListener(result->{recognizer.close();handleRecognizedSchedule(result);})
            .addOnFailureListener(error->{recognizer.close();new AlertDialog.Builder(this).setTitle("Kunde inte läsa bilden").setMessage("Prova ett rakare och ljusare foto där hela schemat syns.").setPositiveButton("OK",null).show();});
    }

    void handleRecognizedSchedule(Text result){
        ArrayList<PhotoScheduleParser.Token> tokens=new ArrayList<>();
        for(Text.TextBlock block:result.getTextBlocks())for(Text.Line line:block.getLines())for(Text.Element element:line.getElements()){
            Rect r=element.getBoundingBox();if(r!=null)tokens.add(new PhotoScheduleParser.Token(element.getText(),r.left,r.top,r.right,r.bottom));
        }
        Calendar now=Calendar.getInstance();
        PhotoScheduleParser.MonthYear my=PhotoScheduleParser.detectMonthYear(result.getText(),now.get(Calendar.YEAR),now.get(Calendar.MONTH)+1);
        if(my.detected)showPhotoReview(tokens,my.year,my.month);
        else askPhotoMonth(tokens,my.year,my.month);
    }

    void askPhotoMonth(ArrayList<PhotoScheduleParser.Token> tokens,int year,int month){
        DatePickerDialog picker=new DatePickerDialog(this,(v,y,m,d)->showPhotoReview(tokens,y,m+1),year,Math.max(0,Math.min(11,month-1)),1);
        picker.setTitle("Välj valfritt datum i schemats månad");picker.show();
    }

    void showPhotoReview(ArrayList<PhotoScheduleParser.Token> tokens,int year,int month){
        List<PhotoScheduleParser.Candidate> candidates=PhotoScheduleParser.parse(tokens,year,month);
        if(candidates.isEmpty()){
            new AlertDialog.Builder(this).setTitle("Inga säkra pass hittades")
                .setMessage("Appen hittade inget datum med exakt en tydlig start–slut-tid. Handskrift är svårare att läsa än tryckt text. Du kan prova ett bättre foto eller lägga in de otydliga passen manuellt.")
                .setPositiveButton("OK",null).show();return;
        }
        String[] labels=new String[candidates.size()];boolean[] checked=new boolean[candidates.size()];
        for(int i=0;i<candidates.size();i++){
            PhotoScheduleParser.Candidate c=candidates.get(i);Shift probe=photoShift(c,year,month);String status="";
            if(exactLenieShift(probe))status=" · finns redan";else if(hasLenieConflict(probe))status=" · överlappar befintligt";else checked[i]=true;
            labels[i]=cap(new SimpleDateFormat("EEE d MMM",new Locale("sv","SE")).format(new Date(probe.date)))+" · "+c.start+"–"+c.end+status;
        }
        new AlertDialog.Builder(this).setTitle("Granska tolkade pass")
            .setMessage("Tolkad månad: "+monthName(month)+" "+year+". Avmarkera allt som inte stämmer. Rader med flera möjliga tider har redan hoppats över. Rast sätts till 0 eftersom den inte står på schemat.")
            .setMultiChoiceItems(labels,checked,(d,w,isChecked)->checked[w]=isChecked)
            .setNegativeButton("Avbryt",null)
            .setPositiveButton("Importera valda",(d,w)->importPhotoCandidates(candidates,checked,year,month)).show();
    }

    Shift photoShift(PhotoScheduleParser.Candidate c,int year,int month){
        Shift x=new Shift();x.owner=1;x.date=dateOf(year,month,c.day);x.start=c.start;x.end=c.end;x.breakMin=0;x.done=false;x.kind="Ordinarie";x.note="Importerad från schemafoto · rast ej angiven";return x;
    }

    void importPhotoCandidates(List<PhotoScheduleParser.Candidate> candidates,boolean[] checked,int year,int month){
        int added=0,skipped=0;long first=0;
        for(int i=0;i<candidates.size();i++){
            if(i>=checked.length||!checked[i])continue;Shift x=photoShift(candidates.get(i),year,month);
            if(exactLenieShift(x)||hasLenieConflict(x)){skipped++;continue;}
            shifts.add(x);if(first==0)first=x.date;added++;
        }
        if(added>0){save();personView=1;getPreferences(0).edit().putInt("personView",1).apply();selectedDay=first;showCalendar();}
        Toast.makeText(this,added+" pass importerade"+(skipped>0?" · "+skipped+" hoppades över":""),Toast.LENGTH_LONG).show();
    }

    String monthName(int month){
        String[] names={"januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"};
        return month>=1&&month<=12?names[month-1]:"månad "+month;
    }
}
