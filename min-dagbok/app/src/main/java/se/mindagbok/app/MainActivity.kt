package se.mindagbok.app

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val Bg = Color(0xFF101116)
private val Panel = Color(0xFF1B1D26)
private val Accent = Color(0xFFB9A0FF)
private val Ink = Color(0xFFF3F0FA)
private val Muted = Color(0xFFA6A2B3)
private val gson = Gson()
data class Entry(val id: Long = System.currentTimeMillis(), val title: String, val body: String, val mood: String, val date: Long = System.currentTimeMillis(), val favorite: Boolean = false)

private class Vault(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(context, "mindagbok_vault", MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(), EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV, EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
    fun get(key: String, default: String = "") = prefs.getString(key, default) ?: default
    fun put(key: String, value: String) { prefs.edit().putString(key, value).apply() }
}
class MainActivity : ComponentActivity() { override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { DiaryApp() } } }

@Composable fun DiaryApp() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val vault = remember { Vault(context) }
    var unlocked by remember { mutableStateOf(vault.get("pin").isBlank()) }
    var pinSetup by remember { mutableStateOf(vault.get("pin").isBlank()) }
    var pinInput by remember { mutableStateOf("") }
    var entries by remember { mutableStateOf(runCatching { gson.fromJson<List<Entry>>(vault.get("entries", "[]"), object : TypeToken<List<Entry>>() {}.type) ?: emptyList() }.getOrDefault(emptyList())) }
    var query by remember { mutableStateOf("") }
    var favoriteOnly by remember { mutableStateOf(false) }
    var editing by remember { mutableStateOf<Entry?>(null) }
    var editor by remember { mutableStateOf(false) }
    var title by remember { mutableStateOf("") }
    var body by remember { mutableStateOf("") }
    var mood by remember { mutableStateOf("🙂") }
    fun save(list: List<Entry>) { entries = list.sortedByDescending { it.date }; vault.put("entries", gson.toJson(entries)) }
    fun edit(e: Entry? = null) { editing=e; title=e?.title ?: ""; body=e?.body ?: ""; mood=e?.mood ?: "🙂"; editor=true }
    fun biometric() {
        if (BiometricManager.from(context).canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL) != BiometricManager.BIOMETRIC_SUCCESS) return
        val prompt = BiometricPrompt(context as ComponentActivity, ContextCompat.getMainExecutor(context), object: BiometricPrompt.AuthenticationCallback() { override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) { unlocked=true } })
        prompt.authenticate(BiometricPrompt.PromptInfo.Builder().setTitle("Lås upp Min Dagbok").setSubtitle("Bekräfta att det är du").setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL).build())
    }
    MaterialTheme(colorScheme=darkColorScheme(background=Bg, surface=Panel, primary=Accent, onBackground=Ink, onSurface=Ink)) {
        Surface(Modifier.fillMaxSize(), color=Bg) {
            if (!unlocked) Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement=Arrangement.Center, horizontalAlignment=Alignment.CenterHorizontally) {
                Icon(Icons.Default.AutoStories, null, tint=Accent, modifier=Modifier.size(58.dp)); Spacer(Modifier.height(16.dp)); Text("Min Dagbok", fontSize=30.sp, fontWeight=FontWeight.Bold); Text(if(pinSetup) "Skapa en PIN-kod" else "Din dagbok är låst", color=Muted); Spacer(Modifier.height(20.dp))
                OutlinedTextField(pinInput, { pinInput=it.filter(Char::isDigit).take(8) }, label={Text(if(pinSetup) "Ny PIN-kod (4–8 siffror)" else "PIN-kod")}, visualTransformation=PasswordVisualTransformation(), singleLine=true)
                Spacer(Modifier.height(12.dp)); Button(onClick={ if(pinSetup && pinInput.length>=4){vault.put("pin",pinInput);pinSetup=false;unlocked=true;pinInput=""} else if(pinInput==vault.get("pin")){unlocked=true;pinInput=""} }, enabled=pinInput.length>=4, modifier=Modifier.fillMaxWidth()){Text(if(pinSetup)"Skapa lås" else "Lås upp")}
                if(!pinSetup) TextButton(onClick={biometric()}) { Icon(Icons.Default.Fingerprint,null); Spacer(Modifier.width(8.dp)); Text("Använd fingeravtryck") }
                Text("Inläggen sparas krypterat på enheten.", color=Muted, fontSize=12.sp)
            } else if(editor) Column(Modifier.fillMaxSize().padding(18.dp)) {
                Row(verticalAlignment=Alignment.CenterVertically){ IconButton(onClick={editor=false}){Icon(Icons.Default.ArrowBack,"Tillbaka")}; Text(if(editing==null)"Nytt inlägg" else "Redigera inlägg", fontSize=22.sp,fontWeight=FontWeight.Bold); Spacer(Modifier.weight(1f)); TextButton(onClick={ if(title.isNotBlank()||body.isNotBlank()){val e=Entry(id=editing?.id?:System.currentTimeMillis(),title=title.ifBlank{"Min dag"},body=body,mood=mood,date=editing?.date?:System.currentTimeMillis(),favorite=editing?.favorite?:false);save(listOf(e)+entries.filterNot{it.id==e.id})};editor=false }){Text("Spara")} }
                Text(SimpleDateFormat("EEEE d MMMM yyyy",Locale("sv","SE")).format(Date()), color=Muted); Spacer(Modifier.height(12.dp))
                OutlinedTextField(title,{title=it},label={Text("Rubrik")},modifier=Modifier.fillMaxWidth(),singleLine=true); Spacer(Modifier.height(12.dp)); Text("Hur känns dagen?",color=Muted)
                Row(horizontalArrangement=Arrangement.spacedBy(6.dp)){listOf("😞","😕","😐","🙂","😄","😌","😤").forEach{m->Text(m,modifier=Modifier.background(if(mood==m)Accent.copy(alpha=.25f) else Panel,RoundedCornerShape(12.dp)).clickable{mood=m}.padding(9.dp),fontSize=23.sp)}}
                Spacer(Modifier.height(12.dp)); OutlinedTextField(body,{body=it},label={Text("Skriv om din dag…")},modifier=Modifier.fillMaxWidth().weight(1f),minLines=8); Text("Kom ihåg att spara inlägget.",color=Muted,fontSize=12.sp)
            } else Column(Modifier.fillMaxSize().padding(horizontal=18.dp)) {
                Spacer(Modifier.height(20.dp)); Row(verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(48.dp).background(Panel,RoundedCornerShape(16.dp)),contentAlignment=Alignment.Center){Icon(Icons.Default.AutoStories,null,tint=Accent,modifier=Modifier.size(28.dp))}; Spacer(Modifier.width(12.dp)); Column(Modifier.weight(1f)){Text("Min Dagbok",fontSize=25.sp,fontWeight=FontWeight.Bold);Text(SimpleDateFormat("EEEE d MMMM",Locale("sv","SE")).format(Date()).replaceFirstChar{it.uppercase()},color=Muted)};IconButton(onClick={unlocked=false}){Icon(Icons.Default.Lock,"Lås dagboken",tint=Accent)}}
                Spacer(Modifier.height(16.dp)); Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){Stat("Inlägg",entries.size.toString(),Modifier.weight(1f));Stat("Favoriter",entries.count{it.favorite}.toString(),Modifier.weight(1f));Stat("Dagar",entries.map{SimpleDateFormat("yyyyMMdd",Locale.US).format(Date(it.date))}.distinct().size.toString(),Modifier.weight(1f))}
                Spacer(Modifier.height(14.dp)); OutlinedTextField(query,{query=it},modifier=Modifier.fillMaxWidth(),placeholder={Text("Sök i dagboken…")},leadingIcon={Icon(Icons.Default.Search,null)},singleLine=true)
                Row{FilterChip(selected=!favoriteOnly,onClick={favoriteOnly=false},label={Text("Alla")});Spacer(Modifier.width(8.dp));FilterChip(selected=favoriteOnly,onClick={favoriteOnly=true},label={Text("★ Favoriter")})}
                val filtered=entries.filter{(!favoriteOnly||it.favorite)&&(query.isBlank()||it.title.contains(query,true)||it.body.contains(query,true))}
                if(filtered.isEmpty()) Column(Modifier.fillMaxWidth().weight(1f),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Icon(Icons.Default.MenuBook,null,tint=Accent,modifier=Modifier.size(54.dp));Text(if(query.isBlank())"Din berättelse börjar här" else "Inga träffar",fontSize=20.sp,fontWeight=FontWeight.SemiBold);Text("Skriv några rader när det passar.",color=Muted);Spacer(Modifier.height(10.dp));Button(onClick={edit()}){Icon(Icons.Default.Add,null);Text(" Nytt inlägg")}}
                else LazyColumn(Modifier.weight(1f),contentPadding=PaddingValues(vertical=8.dp),verticalArrangement=Arrangement.spacedBy(10.dp)){items(filtered,key={it.id}){e->Card(colors=CardDefaults.cardColors(containerColor=Panel),shape=RoundedCornerShape(20.dp),modifier=Modifier.fillMaxWidth().clickable{edit(e)}){Column(Modifier.padding(14.dp)){Row(verticalAlignment=Alignment.CenterVertically){Text(e.mood,fontSize=23.sp);Spacer(Modifier.width(8.dp));Column(Modifier.weight(1f)){Text(e.title,fontWeight=FontWeight.Bold,fontSize=17.sp);Text(SimpleDateFormat("d MMM yyyy · HH:mm",Locale("sv","SE")).format(Date(e.date)),color=Muted,fontSize=12.sp)};IconButton(onClick={save(entries.map{if(it.id==e.id)it.copy(favorite=!it.favorite)else it})}){Icon(if(e.favorite)Icons.Default.Star else Icons.Default.StarBorder,"Favorit",tint=if(e.favorite)Accent else Muted)};IconButton(onClick={save(entries.filterNot{it.id==e.id})}){Icon(Icons.Default.DeleteOutline,"Radera",tint=Muted)}};if(e.body.isNotBlank()){Spacer(Modifier.height(6.dp));Text(e.body,color=Ink,maxLines=4)}}}}}
                Row(Modifier.fillMaxWidth().padding(vertical=10.dp),horizontalArrangement=Arrangement.spacedBy(8.dp)){OutlinedButton(onClick={val intent=android.content.Intent(android.content.Intent.ACTION_SEND).apply{type="application/json";putExtra(android.content.Intent.EXTRA_SUBJECT,"Säkerhetskopia – Min Dagbok");putExtra(android.content.Intent.EXTRA_TEXT,gson.toJson(entries))};context.startActivity(android.content.Intent.createChooser(intent,"Exportera dagboken"))},modifier=Modifier.weight(1f)){Icon(Icons.Default.FileUpload,null);Text(" Exportera")};Button(onClick={edit()},modifier=Modifier.weight(1f)){Icon(Icons.Default.Add,null);Text(" Nytt inlägg")}}
            }
        }
    }
}
@Composable private fun Stat(label:String,value:String,modifier:Modifier=Modifier){Card(modifier,colors=CardDefaults.cardColors(containerColor=Panel),shape=RoundedCornerShape(16.dp)){Column(Modifier.padding(12.dp)){Text(value,fontSize=22.sp,fontWeight=FontWeight.Bold,color=Accent);Text(label,fontSize=12.sp,color=Muted)}}}
