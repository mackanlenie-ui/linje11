package se.minaarbetspass;

import android.content.Context;
import android.content.SharedPreferences;
import java.util.*;

final class AppPrefs {
    static final String NAME="mina_arbetspass_data";
    private static final String MIGRATED="__stable_prefs_migrated_v1";
    private AppPrefs(){}

    static synchronized SharedPreferences get(Context context){
        Context app=context.getApplicationContext()==null?context:context.getApplicationContext();
        SharedPreferences target=app.getSharedPreferences(NAME,Context.MODE_PRIVATE);
        if(!target.getBoolean(MIGRATED,false))migrate(app,target);
        return target;
    }

    private static void migrate(Context context,SharedPreferences target){
        HashSet<String> present=new HashSet<>(target.getAll().keySet());
        SharedPreferences.Editor edit=target.edit();
        for(String name:StorageMigrationPolicy.legacyNames(context.getPackageName())){
            if(NAME.equals(name))continue;
            SharedPreferences source=context.getSharedPreferences(name,Context.MODE_PRIVATE);
            for(Map.Entry<String,?> entry:source.getAll().entrySet()){
                String key=entry.getKey();
                if(MIGRATED.equals(key)||present.contains(key))continue;
                if(put(edit,key,entry.getValue()))present.add(key);
            }
        }
        edit.putBoolean(MIGRATED,true).commit();
    }

    @SuppressWarnings("unchecked")
    private static boolean put(SharedPreferences.Editor edit,String key,Object value){
        if(value instanceof String)edit.putString(key,(String)value);
        else if(value instanceof Integer)edit.putInt(key,(Integer)value);
        else if(value instanceof Long)edit.putLong(key,(Long)value);
        else if(value instanceof Float)edit.putFloat(key,(Float)value);
        else if(value instanceof Boolean)edit.putBoolean(key,(Boolean)value);
        else if(value instanceof Set)edit.putStringSet(key,new HashSet<>((Set<String>)value));
        else return false;
        return true;
    }
}
