package se.linje11.gps;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.database.Cursor;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class MainActivity extends AppCompatActivity {
    private static final int IMPORT_ROUTE = 100;
    private final String[] days = {"Måndag","Tisdag","Onsdag","Torsdag","Fredag"};
    private LinearLayout routeList;
    private Spinner daySpinner;
    private String selectedDay = "Måndag";

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b); setContentView(R.layout.activity_main);
        getWindow().addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        daySpinner=findViewById(R.id.daySpinner); routeList=findViewById(R.id.routeList);
        ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,days);
        daySpinner.setAdapter(a);
        daySpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            public void onItemSelected(AdapterView<?> p,View v,int pos,long id){selectedDay=days[pos]; refresh();}
            public void onNothingSelected(AdapterView<?> p){}
        });
        findViewById(R.id.btnImport).setOnClickListener(v->chooseFile());
        refresh();
    }

    private void chooseFile(){
        Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT); i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/json"); startActivityForResult(i,IMPORT_ROUTE);
    }

    @Override protected void onActivityResult(int r,int c,Intent data){
        super.onActivityResult(r,c,data); if(r!=IMPORT_ROUTE||c!=RESULT_OK||data==null||data.getData()==null)return;
        try{
            Uri uri=data.getData(); String json=read(uri); JSONObject root=new JSONObject(json);
            if(!"gps-ruttinspelare".equals(root.optString("format"))){Toast.makeText(this,"Filen är inte en GPS Ruttinspelare-rutt",Toast.LENGTH_LONG).show();return;}
            String name=fileName(uri); if(name.endsWith(".json"))name=name.substring(0,name.length()-5);
            JSONArray routes=load(selectedDay); JSONObject item=new JSONObject();
            item.put("name",name); item.put("route",root); routes.put(item); save(selectedDay,routes); refresh();
            Toast.makeText(this,"Importerad till "+selectedDay,Toast.LENGTH_SHORT).show();
        }catch(Exception e){Toast.makeText(this,"Import misslyckades: "+e.getMessage(),Toast.LENGTH_LONG).show();}
    }

    private void refresh(){
        if(routeList==null)return; routeList.removeAllViews(); JSONArray routes=load(selectedDay);
        if(routes.length()==0){TextView t=new TextView(this);t.setText("Inga rutter för "+selectedDay+" ännu.");t.setTextSize(17);t.setPadding(8,24,8,24);routeList.addView(t);return;}
        for(int i=0;i<routes.length();i++) try{
            JSONObject item=routes.getJSONObject(i); JSONObject route=item.getJSONObject("route"); int stops=route.optJSONArray("stops")!=null?route.optJSONArray("stops").length():0;
            LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.VERTICAL);row.setPadding(0,8,0,12);
            Button open=new Button(this);open.setAllCaps(false);open.setText(item.optString("name","Rutt "+(i+1))+"  •  "+stops+" stopp"); final int idx=i;
            open.setOnClickListener(v->openRoute(idx)); row.addView(open);
            Button del=new Button(this);del.setAllCaps(false);del.setText("Ta bort");del.setOnClickListener(v->deleteRoute(idx));row.addView(del);routeList.addView(row);
        }catch(Exception ignored){}
    }

    private void openRoute(int index){
        try{
            JSONObject route=load(selectedDay).getJSONObject(index).getJSONObject("route"); JSONArray stops=route.getJSONArray("stops");
            if(stops.length()<2){Toast.makeText(this,"Rutten behöver minst två stopp",Toast.LENGTH_LONG).show();return;}
            JSONObject first=stops.getJSONObject(0), last=stops.getJSONObject(stops.length()-1);
            StringBuilder url=new StringBuilder("https://www.google.com/maps/dir/?api=1&origin=").append(first.getDouble("lat")).append(",").append(first.getDouble("lon"));
            url.append("&destination=").append(last.getDouble("lat")).append(",").append(last.getDouble("lon"));
            if(stops.length()>2){url.append("&waypoints=");for(int i=1;i<stops.length()-1;i++){if(i>1)url.append("%7C");JSONObject s=stops.getJSONObject(i);url.append(s.getDouble("lat")).append(",").append(s.getDouble("lon"));}}
            url.append("&travelmode=driving"); Intent intent=new Intent(Intent.ACTION_VIEW,Uri.parse(url.toString())); intent.setPackage("com.google.android.apps.maps");
            try{startActivity(intent);}catch(Exception e){startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url.toString())));}
        }catch(Exception e){Toast.makeText(this,"Kunde inte öppna rutten",Toast.LENGTH_LONG).show();}
    }

    private void deleteRoute(int index){try{JSONArray old=load(selectedDay), n=new JSONArray();for(int i=0;i<old.length();i++)if(i!=index)n.put(old.get(i));save(selectedDay,n);refresh();}catch(Exception ignored){}}
    private JSONArray load(String day){try{return new JSONArray(getPreferences(MODE_PRIVATE).getString("routes_"+day,"[]"));}catch(Exception e){return new JSONArray();}}
    private void save(String day,JSONArray a){getPreferences(MODE_PRIVATE).edit().putString("routes_"+day,a.toString()).apply();}
    private String read(Uri u)throws Exception{InputStream in=getContentResolver().openInputStream(u);ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))>0)out.write(b,0,n);in.close();return new String(out.toByteArray(),StandardCharsets.UTF_8);}
    private String fileName(Uri u){String name="Importerad rutt";Cursor c=getContentResolver().query(u,null,null,null,null);if(c!=null){if(c.moveToFirst()){int x=c.getColumnIndex(OpenableColumns.DISPLAY_NAME);if(x>=0)name=c.getString(x);}c.close();}return name;}
}
