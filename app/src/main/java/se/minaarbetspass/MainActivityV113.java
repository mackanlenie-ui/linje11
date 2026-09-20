package se.minaarbetspass;

import android.app.*;
import android.content.*;
import android.graphics.*;
import android.net.Uri;
import android.os.Build;
import android.provider.MediaStore;
import android.view.*;
import android.widget.*;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import java.util.*;
import java.text.SimpleDateFormat;

public class MainActivityV113 extends MainActivityV112 {
    static final String LAST_PHOTO_IMPORT="__last_photo_import_signatures_v1";
    static final int UNCERTAIN=0xffffb74d;

    @Override boolean exactLenieShift(Shift probe){
        String wanted=PhotoImportDraft.signature(probe.date,probe.start,probe.end);
        for(Shift x:shifts)if(x.owner==1&&PhotoImportDraft.signature(x.date,x.start,x.end).equals(wanted))return true;
        return false;
    }

    @Override void scanSchedulePhoto(Uri uri){
        final InputImage original;
        try{original=InputImage.fromFilePath(this,uri);}catch(Exception e){Toast.makeText(this,"Bilden kunde inte öppnas",Toast.LENGTH_LONG).show();return;}
        Toast.makeText(this,"Förbättrar och läser schemat…",Toast.LENGTH_SHORT).show();
        TextRecognizer recognizer=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        recognizer.process(original).addOnSuccessListener(first->
            new Thread(()->{
                Bitmap enhanced=null;
                try{enhanced=loadEnhancedBitmap(uri);}catch(Exception ignored){}
                final Bitmap ready=enhanced;
                runOnUiThread(()->{
                    if(ready==null){recognizer.close();reviewBestRecognition(first,null);return;}
                    recognizer.process(InputImage.fromBitmap(ready,0))
                        .addOnSuccessListener(second->{reviewBestRecognition(first,second);ready.recycle();recognizer.close();})
                        .addOnFailureListener(err->{ready.recycle();recognizer.close();reviewBestRecognition(first,null);});
                });
            }).start()
        ).addOnFailureListener(error->{recognizer.close();new AlertDialog.Builder(this).setTitle("Kunde inte läsa bilden").setMessage("Prova ett rakare och ljusare foto där hela schemat syns.").setPositiveButton("OK",null).show();});
    }

    Bitmap loadEnhancedBitmap(Uri uri)throws Exception{
        Bitmap source;
        if(Build.VERSION.SDK_INT>=28){
            ImageDecoder.Source s=ImageDecoder.createSource(getContentResolver(),uri);
            source=ImageDecoder.decodeBitmap(s,(decoder,info,src)->{
                decoder.setAllocator(ImageDecoder.ALLOCATOR_SOFTWARE);
                android.util.Size z=info.getSize();int w=z.getWidth(),h=z.getHeight(),max=Math.max(w,h);
                if(max>2200){float scale=2200f/max;decoder.setTargetSize(Math.max(1,Math.round(w*scale)),Math.max(1,Math.round(h*scale)));}
            });
        }else{
            source=MediaStore.Images.Media.getBitmap(getContentResolver(),uri);
            int max=Math.max(source.getWidth(),source.getHeight());
            if(max>2200){float scale=2200f/max;Bitmap smaller=Bitmap.createScaledBitmap(source,Math.max(1,Math.round(source.getWidth()*scale)),Math.max(1,Math.round(source.getHeight()*scale)),true);if(smaller!=source)source.recycle();source=smaller;}
        }
        Bitmap out=Bitmap.createBitmap(source.getWidth(),source.getHeight(),Bitmap.Config.ARGB_8888);
        int width=source.getWidth(),height=source.getHeight();int[] row=new int[width];
        for(int y=0;y<height;y++){source.getPixels(row,0,width,0,y,width,1);for(int x=0;x<width;x++)row[x]=PhotoImageMath.enhanceArgb(row[x]);out.setPixels(row,0,width,0,y,width,1);}
        if(source!=out)source.recycle();return out;
    }

    ArrayList<PhotoScheduleParser.Token> tokensFrom(Text result){
        ArrayList<PhotoScheduleParser.Token> tokens=new ArrayList<>();
        if(result==null)return tokens;
        for(Text.TextBlock block:result.getTextBlocks())for(Text.Line line:block.getLines())for(Text.Element element:line.getElements()){
            Rect r=element.getBoundingBox();if(r!=null)tokens.add(new PhotoScheduleParser.Token(element.getText(),r.left,r.top,r.right,r.bottom));
        }
        return tokens;
    }

    int recognitionScore(Text result){
        ArrayList<PhotoScheduleParser.Token> tokens=tokensFrom(result);int score=0;
        for(PhotoScheduleParser.Candidate c:PhotoScheduleParser.parseForReview(tokens,2026,1))score+=c.uncertain?1:3;
        return score;
    }

    void reviewBestRecognition(Text first,Text second){
        Text best=second!=null&&recognitionScore(second)>recognitionScore(first)?second:first;
        ArrayList<PhotoScheduleParser.Token> tokens=tokensFrom(best);
        Calendar now=Calendar.getInstance();
        PhotoScheduleParser.MonthYear my=PhotoScheduleParser.detectMonthYear(best==null?"":best.getText(),now.get(Calendar.YEAR),now.get(Calendar.MONTH)+1);
        if(!my.detected&&best!=first&&first!=null){
            PhotoScheduleParser.MonthYear original=PhotoScheduleParser.detectMonthYear(first.getText(),my.year,my.month);
            if(original.detected)my=original;
        }
        if(my.detected)showPhotoReview(tokens,my.year,my.month);else askPhotoMonth(tokens,my.year,my.month);
    }

    @Override void showPhotoReview(ArrayList<PhotoScheduleParser.Token> tokens,int year,int month){
        List<PhotoScheduleParser.Candidate> candidates=PhotoScheduleParser.parseForReview(tokens,year,month);
        if(candidates.isEmpty()){
            new AlertDialog.Builder(this).setTitle("Inga pass hittades").setMessage("Appen kunde inte hitta schemarader med tydliga datum. Prova ett rakare, närmare och ljusare foto.").setPositiveButton("OK",null).show();return;
        }
        ArrayList<PhotoImportDraft> drafts=new ArrayList<>();for(PhotoScheduleParser.Candidate c:candidates)drafts.add(new PhotoImportDraft(c));

        LinearLayout list=new LinearLayout(this);list.setOrientation(LinearLayout.VERTICAL);list.setPadding(dp(8),dp(8),dp(8),dp(8));
        TextView help=text("Kontrollera varje rad. ⚠ Osäkra rader sparas inte förrän du har tryckt Redigera och fyllt i en giltig tid.",13,MUTED,false);
        list.addView(help,mp(-1,-2,0,0,0,8));

        for(PhotoImportDraft draft:drafts)list.addView(reviewDraftRow(draft,year,month),mp(-1,-2,0,5,0,5));
        ScrollView scroll=new ScrollView(this);scroll.addView(list);scroll.setFillViewport(true);

        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Granska schemafoto · "+monthName(month)+" "+year)
            .setView(scroll).setNegativeButton("Avbryt",null).setPositiveButton("Importera valda",null).create();
        dialog.setOnShowListener(x->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            int selected=0;for(PhotoImportDraft d:drafts)if(d.selected&&d.canImport())selected++;
            if(selected==0){Toast.makeText(this,"Välj minst ett giltigt pass",Toast.LENGTH_SHORT).show();return;}
            dialog.dismiss();importPhotoDrafts(drafts,year,month);
        }));
        dialog.show();
    }

    View reviewDraftRow(PhotoImportDraft draft,int year,int month){
        LinearLayout box=card();
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);
        CheckBox check=new CheckBox(this);TextView label=text("",15,TEXT,true);Button edit=styledButton();edit.setText("Redigera");
        top.addView(check,new LinearLayout.LayoutParams(dp(48),dp(48)));
        top.addView(label,new LinearLayout.LayoutParams(0,-2,1));
        top.addView(edit,new LinearLayout.LayoutParams(dp(96),dp(48)));
        box.addView(top);
        Runnable refresh=()->refreshDraftRow(draft,year,month,check,label);
        check.setOnCheckedChangeListener((b,on)->{if(b.isEnabled())draft.selected=on;});
        edit.setOnClickListener(v->editPhotoDraft(draft,year,month,refresh));
        refresh.run();return box;
    }

    void refreshDraftRow(PhotoImportDraft draft,int year,int month,CheckBox check,TextView label){
        check.setOnCheckedChangeListener(null);
        if(!draft.canImport()){
            draft.selected=false;check.setChecked(false);check.setEnabled(false);
            label.setText("⚠ "+draft.day+" "+monthName(month)+" · osäker tid");label.setTextColor(UNCERTAIN);
        }else{
            Shift probe=draftShift(draft,year,month);
            String suffix="";boolean blocked=false;
            if(exactLenieShift(probe)){suffix=" · finns redan";blocked=true;}
            else if(hasLenieConflict(probe)){suffix=" · överlappar befintligt";blocked=true;}
            if(blocked)draft.selected=false;
            check.setEnabled(!blocked);check.setChecked(draft.selected&&!blocked);
            label.setText((draft.uncertain?"⚠ ":"")+draft.day+" "+monthName(month)+" · "+draft.start+"–"+draft.end+suffix);
            label.setTextColor(draft.uncertain?UNCERTAIN:(blocked?MUTED:LENIE));
        }
        check.setOnCheckedChangeListener((b,on)->{if(b.isEnabled())draft.selected=on;});
    }

    void editPhotoDraft(PhotoImportDraft draft,int year,int month,Runnable refresh){
        LinearLayout form=new LinearLayout(this);form.setOrientation(LinearLayout.VERTICAL);form.setPadding(dp(20),dp(4),dp(20),0);
        EditText day=input(String.valueOf(draft.day),"Dag");day.setSingleLine(true);day.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        EditText start=input(draft.start,"Start, t.ex. 07:30");start.setSingleLine(true);
        EditText end=input(draft.end,"Slut, t.ex. 16:00");end.setSingleLine(true);
        form.addView(label("Dag i "+monthName(month)+" "+year));form.addView(day);form.addView(label("Starttid"));form.addView(start);form.addView(label("Sluttid"));form.addView(end);
        AlertDialog d=new AlertDialog.Builder(this).setTitle("Redigera tolkat pass").setView(form).setNegativeButton("Avbryt",null).setPositiveButton("Spara",null).create();
        d.setOnShowListener(x->d.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            int n;try{n=Integer.parseInt(day.getText().toString().trim());}catch(Exception e){day.setError("Ange dag");return;}
            Calendar c=Calendar.getInstance();c.clear();c.set(year,month-1,1);int max=c.getActualMaximum(Calendar.DAY_OF_MONTH);
            if(n<1||n>max){day.setError("Dagen finns inte i månaden");return;}
            if(!draft.applyEdit(n,start.getText().toString(),end.getText().toString())){end.setError("Kontrollera start- och sluttid");return;}
            refresh.run();d.dismiss();
        }));d.show();
    }

    Shift draftShift(PhotoImportDraft draft,int year,int month){
        Shift x=new Shift();x.owner=1;x.date=dateOf(year,month,draft.day);x.start=PhotoImportDraft.normalizeTime(draft.start);x.end=PhotoImportDraft.normalizeTime(draft.end);
        x.breakMin=0;x.done=false;x.kind="Ordinarie";x.note="Importerad från schemafoto · rast ej angiven";return x;
    }

    void importPhotoDrafts(List<PhotoImportDraft> drafts,int year,int month){
        int added=0,skipped=0;long first=0;HashSet<String> imported=new HashSet<>();
        for(PhotoImportDraft d:drafts){
            if(!d.selected||!d.canImport())continue;Shift x=draftShift(d,year,month);
            String sig=PhotoImportDraft.signature(x.date,x.start,x.end);
            if(imported.contains(sig)||exactLenieShift(x)||hasLenieConflict(x)){skipped++;continue;}
            shifts.add(x);imported.add(sig);if(first==0)first=x.date;added++;
        }
        if(added>0){
            save();getPreferences(0).edit().putStringSet(LAST_PHOTO_IMPORT,new HashSet<>(imported)).apply();
            personView=1;getPreferences(0).edit().putInt("personView",1).apply();selectedDay=first;showCalendar();
        }
        Toast.makeText(this,added+" pass importerade"+(skipped>0?" · "+skipped+" dubbletter/överlapp hoppades över":""),Toast.LENGTH_LONG).show();
    }

    void undoLatestPhotoImport(){
        Set<String> stored=getPreferences(0).getStringSet(LAST_PHOTO_IMPORT,Collections.emptySet());
        if(stored==null||stored.isEmpty()){new AlertDialog.Builder(this).setTitle("Ångra fotoimport").setMessage("Det finns ingen sparad fotoimport att ångra.").setPositiveButton("OK",null).show();return;}
        final HashSet<String> targets=new HashSet<>(stored);
        new AlertDialog.Builder(this).setTitle("Ångra senaste fotoimport?").setMessage("Endast passen som lades till vid den senaste fotoimporten tas bort. Övriga pass påverkas inte.")
            .setNegativeButton("Avbryt",null).setPositiveButton("Ångra",(d,w)->{
                int removed=0;HashSet<String> remaining=new HashSet<>(targets);
                Iterator<Shift> it=shifts.iterator();
                while(it.hasNext()&&!remaining.isEmpty()){
                    Shift x=it.next();if(x.owner!=1)continue;String sig=PhotoImportDraft.signature(x.date,x.start,x.end);
                    if(remaining.remove(sig)){it.remove();removed++;}
                }
                if(removed>0)save();getPreferences(0).edit().remove(LAST_PHOTO_IMPORT).apply();refresh();
                Toast.makeText(this,removed+" importerade pass borttagna",Toast.LENGTH_LONG).show();
            }).show();
    }
}
