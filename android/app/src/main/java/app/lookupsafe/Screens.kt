@file:OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class, androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
package app.lookupsafe

import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle

@Composable fun LookupSafeApp(vm: AppViewModel) {
    val s by vm.state.collectAsStateWithLifecycle()
    val snackbar=remember { SnackbarHostState() }
    LaunchedEffect(s.message) { s.message?.let { snackbar.showSnackbar(it); vm.dismiss() } }
    BackHandler(enabled=s.signedIn && (s.selected!=null || s.tab!="Inicio")) {
        if(s.selected!=null) vm.select(null) else vm.tab("Inicio")
    }
    Scaffold(
        snackbarHost={ SnackbarHost(snackbar) },
        topBar={ if(s.signedIn) TopAppBar(title={ Text(if(s.selected!=null) "Análisis" else "lookupsafe",fontWeight=FontWeight.Bold) },
            navigationIcon={ if(s.selected!=null) IconButton(onClick={vm.select(null)}) { Icon(Icons.AutoMirrored.Outlined.ArrowBack,"Volver") } },
            actions={ if(s.selected==null) IconButton(onClick=vm::refresh,enabled=!s.busy) { Icon(Icons.Outlined.Refresh,"Actualizar") } }) },
        bottomBar={ if(s.signedIn && s.selected==null) NavigationBar {
            listOf("Inicio" to Icons.Outlined.Home,"Escanear" to Icons.Outlined.CameraAlt,"Historial" to Icons.Outlined.History,"Perfil" to Icons.Outlined.Person).forEach { (name,icon)->
                NavigationBarItem(selected=s.tab==name,onClick={vm.tab(name)},icon={Icon(icon,name)},label={Text(name)})
            }
        } }
    ) { insets->
        Column(Modifier.fillMaxSize().padding(insets)) {
            if(s.busy) LinearProgressIndicator(Modifier.fillMaxWidth())
            if(!s.signedIn) LoginScreen(vm,s.busy)
            else if(s.selected!=null) DetailScreen(s.selected!!,s.busy,vm)
            else when(s.tab) {
                "Inicio" -> HomeScreen(s,vm)
                "Escanear" -> ScanScreen(s,vm)
                "Historial" -> HistoryScreen(s,vm)
                else -> ProfileScreen(s,vm)
            }
        }
    }
}
@Composable private fun Page(content: @Composable ColumnScope.()->Unit) {
    Column(Modifier.fillMaxSize().imePadding().verticalScroll(rememberScrollState()).padding(22.dp),verticalArrangement=Arrangement.spacedBy(16.dp),content=content)
}
@Composable private fun LoginScreen(vm: AppViewModel,busy:Boolean) {
    var email by rememberSaveable { mutableStateOf("") }
    // Password deliberately stays in memory, never in saved-instance state.
    var password by remember { mutableStateOf("") }
    var signup by rememberSaveable { mutableStateOf(false) }
    Page {
        Spacer(Modifier.height(24.dp))
        Surface(color=MaterialTheme.colorScheme.primary,shape=RoundedCornerShape(22.dp)) {
            Icon(Icons.Outlined.VerifiedUser,null,Modifier.padding(20.dp).size(34.dp),tint=MaterialTheme.colorScheme.onPrimary)
        }
        Text("lookupsafe",fontSize=36.sp,fontWeight=FontWeight.ExtraBold)
        Text("Conoce tu etiqueta.\nDecide con información.",style=MaterialTheme.typography.headlineSmall)
        Text("Revisa etiquetas de alimentos, perfumes, desodorantes y productos de cuidado personal.",color=MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(12.dp))
        Text(if(signup) "Crea tu cuenta" else "Te damos la bienvenida",style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Bold)
        OutlinedTextField(email,{email=it},Modifier.fillMaxWidth(),label={Text("Correo electrónico")},singleLine=true,keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.Email),enabled=!busy)
        OutlinedTextField(password,{password=it},Modifier.fillMaxWidth(),label={Text("Contraseña")},singleLine=true,visualTransformation=PasswordVisualTransformation(),keyboardOptions=KeyboardOptions(keyboardType=KeyboardType.Password),enabled=!busy)
        if(signup) Text("Usa al menos 8 caracteres. Confirma tu correo antes de iniciar sesión.",style=MaterialTheme.typography.bodySmall)
        Button(onClick={vm.login(email,password,signup)},Modifier.fillMaxWidth().height(52.dp),enabled=!busy && email.contains('@') && password.length >= (if(signup) 8 else 1) && vm.configured) {
            Text(if(signup) "Crear cuenta" else "Entrar con correo")
        }
        TextButton(onClick={signup=!signup},Modifier.align(Alignment.CenterHorizontally),enabled=!busy) { Text(if(signup) "Ya tengo una cuenta" else "Crear una cuenta") }
        if(!vm.configured) Card { Text("Falta conectar Supabase. Completa android/lookupsafe.properties y vuelve a compilar la app.",Modifier.padding(16.dp)) }
        Text("Las fotos se procesan en tu dispositivo. Al analizar, se envía el texto revisado a tu cuenta. Puedes eliminar tus datos desde Perfil.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
@Composable private fun HomeScreen(s:AppState,vm:AppViewModel) {
    Page {
        Text(if(s.profile.displayName.isBlank()) "Tu próxima decisión,\nmejor informada." else "Hola, ${s.profile.displayName}",style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
        Text("Empieza por la lista de ingredientes.",color=MaterialTheme.colorScheme.onSurfaceVariant)
        Card(onClick={vm.tab("Escanear")},shape=RoundedCornerShape(24.dp)) {
            Column(Modifier.fillMaxWidth().background(Brush.linearGradient(listOf(Color(0xFF27A486),Color(0xFF146A55)))).padding(24.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
                Icon(Icons.Outlined.CameraAlt,null,Modifier.size(32.dp),tint=Color.White)
                Text("Revisar producto",color=Color.White,fontSize=23.sp,fontWeight=FontWeight.Bold)
                Text("Fotografía o importa una etiqueta",color=Color.White)
            }
        }
        Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(12.dp)) {
            Metric("${s.scans.size}${if(s.nextOffset!=null) "+" else ""}","Consultas cargadas",Modifier.weight(1f))
            Metric(s.profile.allergens.size.toString(),"Alertas de perfil",Modifier.weight(1f))
        }
        Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.SpaceBetween) {
            Text("Últimos escaneos",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
            TextButton(onClick={vm.tab("Historial")}) { Text("Ver todo") }
        }
        if(s.scans.isEmpty()) EmptyState("Tu historial empieza aquí", "Escanea una etiqueta y revisa el texto para guardar tu primera consulta.")
        s.scans.take(4).forEach { ScanRow(it) { vm.select(it) } }
        Text("Una coincidencia es una mención en la etiqueta, no una evaluación médica.",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
    }
}
@Composable private fun Metric(value:String,label:String,modifier:Modifier) {
    Card(modifier) { Column(Modifier.padding(18.dp)) { Text(value,style=MaterialTheme.typography.headlineMedium,color=MaterialTheme.colorScheme.primary,fontWeight=FontWeight.Bold); Text(label,style=MaterialTheme.typography.bodySmall) } }
}
@Composable private fun ScanScreen(s:AppState,vm:AppViewModel) {
    val context=LocalContext.current
    var cameraUri by rememberSaveable { mutableStateOf<String?>(null) }
    val camera=rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { ok-> if(ok) cameraUri?.let { vm.recognize(Uri.parse(it)) } }
    val gallery=rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri->uri?.let(vm::recognize) }
    Page {
        Text("Lee la etiqueta",style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
        Text("Alimentos, perfumes, desodorantes, cosméticos, champús y más.")
        Card(colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.secondaryContainer)) {
            Column(Modifier.fillMaxWidth().padding(28.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.spacedBy(16.dp)) {
                Icon(Icons.Outlined.DocumentScanner,null,Modifier.size(64.dp),tint=MaterialTheme.colorScheme.primary)
                Text("Texto claro · Buena luz · Sin reflejos",style=MaterialTheme.typography.bodySmall)
                Button(onClick={
                    try { val uri=ImageSharing.newPhoto(context); cameraUri=uri.toString(); camera.launch(uri) }
                    catch(_:Exception) { vm.error("No se pudo abrir la cámara. Importa una imagen o escribe el texto.") }
                },enabled=!s.busy) { Icon(Icons.Outlined.CameraAlt,null); Spacer(Modifier.width(8.dp)); Text("Tomar foto") }
                OutlinedButton(onClick={gallery.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))},enabled=!s.busy) { Text("Importar imagen") }
            }
        }
        OutlinedTextField(s.productName,vm::name,Modifier.fillMaxWidth(),label={Text("Nombre del producto")},singleLine=true,enabled=!s.busy)
        OutlinedTextField(s.labelText,vm::label,Modifier.fillMaxWidth(),label={Text("Ingredientes y advertencias")},minLines=6,maxLines=12,enabled=!s.busy,supportingText={Text("Revisa el texto reconocido antes de continuar. ${s.labelText.length}/12000")})
        Button(onClick=vm::analyze,Modifier.fillMaxWidth().height(52.dp),enabled=!s.busy && s.productName.isNotBlank() && s.labelText.trim().length>=2) { Text("Analizar y guardar") }
        Text("Solo se envía el texto que confirmes. La foto permanece en tu dispositivo.",style=MaterialTheme.typography.bodySmall)
    }
}
@Composable private fun HistoryScreen(s:AppState,vm:AppViewModel) {
    var query by rememberSaveable { mutableStateOf("") }
    var favorites by rememberSaveable { mutableStateOf(false) }
    val visible=s.scans.filter { it.productName.contains(query,true) && (!favorites || it.favorite) }
    Page {
        Text("Tus consultas",style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
        OutlinedTextField(query,{query=it},Modifier.fillMaxWidth(),label={Text("Buscar en consultas cargadas")},leadingIcon={Icon(Icons.Outlined.Search,null)},singleLine=true)
        FilterChip(selected=favorites,onClick={favorites=!favorites},label={Text("Solo favoritos")},leadingIcon={Icon(Icons.Outlined.BookmarkBorder,null)})
        if(visible.isEmpty()) EmptyState("Sin consultas para mostrar", "Escanea un producto o cambia los filtros.")
        visible.forEach { ScanRow(it) {vm.select(it)} }
        if(s.nextOffset!=null) OutlinedButton(onClick=vm::more,Modifier.fillMaxWidth(),enabled=!s.busy) {Text("Cargar más consultas")}
    }
}
@Composable private fun ScanRow(scan:Scan,onClick:()->Unit) {
    Card(onClick=onClick,Modifier.fillMaxWidth()) {
        Row(Modifier.padding(16.dp),verticalAlignment=Alignment.CenterVertically,horizontalArrangement=Arrangement.spacedBy(14.dp)) {
            Icon(if(scan.favorite) Icons.Outlined.Bookmark else Icons.Outlined.Inventory2,null,tint=MaterialTheme.colorScheme.primary)
            Column(Modifier.weight(1f)) {
                Text(scan.productName,fontWeight=FontWeight.SemiBold,maxLines=2,overflow=TextOverflow.Ellipsis)
                Text("${scan.createdAt.take(10)} · ${scan.analysis.ingredients.size} ingredientes",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)
                Text(if(scan.analysis.allergens.any {it.personal}) "Coincide con tu perfil" else "${scan.analysis.allergens.size} coincidencias",style=MaterialTheme.typography.labelSmall,color=MaterialTheme.colorScheme.primary)
            }
            Icon(Icons.Outlined.ChevronRight,"Abrir")
        }
    }
}
@Composable private fun DetailScreen(scan:Scan,busy:Boolean,vm:AppViewModel) {
    val context=LocalContext.current
    val uriHandler=LocalUriHandler.current
    var confirmDelete by remember { mutableStateOf(false) }
    var ingredient by remember { mutableStateOf<Ingredient?>(null) }
    Page {
        Text(scan.productName,style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
        Text("Consulta del ${scan.createdAt.take(10)}",style=MaterialTheme.typography.bodySmall)
        Card(colors=CardDefaults.cardColors(containerColor=if(scan.analysis.allergens.any {it.personal}) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.secondaryContainer)) {
            Column(Modifier.padding(20.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
                Icon(Icons.Outlined.Info,null)
                Text(scan.analysis.summary,fontWeight=FontWeight.Bold)
                Text("No se ha calculado una puntuación de seguridad.",style=MaterialTheme.typography.bodySmall)
            }
        }
        Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
            FilterChip(selected=scan.favorite,onClick={vm.favorite(scan)},enabled=!busy,label={Text(if(scan.favorite) "Guardado" else "Favorito")},leadingIcon={Icon(Icons.Outlined.BookmarkBorder,null)})
            AssistChip(onClick={try {ImageSharing.share(context,scan)} catch(_:Exception) {vm.error("No se pudo compartir la imagen.")}},label={Text("Compartir")},leadingIcon={Icon(Icons.Outlined.Share,null)})
        }
        Text("Ingredientes de interés",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
        if(scan.analysis.allergens.isEmpty()) Text("Sin coincidencias en el catálogo limitado. Esto no confirma ausencia de otros ingredientes de interés.")
        FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp)) {
            scan.analysis.allergens.forEach { a-> SuggestionChip(onClick={},label={Text(a.name+if(a.personal) " · Tu perfil" else "")}) }
        }
        Text("Ingredientes reconocidos",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
        scan.analysis.ingredients.forEach { item->
            Card(onClick={ingredient=item},Modifier.fillMaxWidth()) { Column(Modifier.padding(16.dp)) {Text(item.name,fontWeight=FontWeight.Medium);Text("Sin evaluación · Ver detalle",style=MaterialTheme.typography.bodySmall,color=MaterialTheme.colorScheme.onSurfaceVariant)} }
        }
        Text("Fuentes y alcance",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
        Text(scan.analysis.notice,style=MaterialTheme.typography.bodySmall)
        scan.analysis.sources.forEach { source-> TextButton(onClick={runCatching { uriHandler.openUri(source.url) }.onFailure {vm.error("No se pudo abrir el enlace.")}}) {Text(source.title)} }
        Text("Texto revisado",fontWeight=FontWeight.Bold)
        Text(scan.labelText,style=MaterialTheme.typography.bodySmall)
        OutlinedButton(onClick={confirmDelete=true},enabled=!busy) {Icon(Icons.Outlined.DeleteOutline,null);Text("Eliminar consulta")}
    }
    if(confirmDelete) AlertDialog(onDismissRequest={confirmDelete=false},title={Text("¿Eliminar esta consulta?")},text={Text("Se eliminará de tu historial de forma permanente.")},confirmButton={TextButton(onClick={confirmDelete=false;vm.delete(scan)}) {Text("Eliminar")}},dismissButton={TextButton(onClick={confirmDelete=false}) {Text("Cancelar")}})
    ingredient?.let { item-> AlertDialog(onDismissRequest={ingredient=null},title={Text(item.name)},text={Text("Este ingrediente se extrajo del texto que revisaste. No hay una evaluación específica de su seguridad en este catálogo. Consulta la etiqueta completa y las fuentes antes de decidir.")},confirmButton={TextButton(onClick={ingredient=null}) {Text("Entendido")}}) }
}
@Composable private fun ProfileScreen(s:AppState,vm:AppViewModel) {
    var name by remember(s.profile) { mutableStateOf(s.profile.displayName) }
    var allergens by remember(s.profile) { mutableStateOf(s.profile.allergens.toSet()) }
    var clear by remember { mutableStateOf(false) }
    Page {
        Text("Tu perfil",style=MaterialTheme.typography.headlineMedium,fontWeight=FontWeight.Bold)
        Text(s.email,color=MaterialTheme.colorScheme.onSurfaceVariant)
        OutlinedTextField(name,{name=it.take(80)},Modifier.fillMaxWidth(),label={Text("Tu nombre")},singleLine=true,enabled=!s.busy)
        Text("Ingredientes que quieres revisar",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
        Text("Las coincidencias se destacarán en tus próximos análisis. El catálogo es limitado y no evalúa la seguridad del producto.",style=MaterialTheme.typography.bodySmall)
        concernGroups.forEach { (category,items)->
            Text(category,style=MaterialTheme.typography.titleSmall,color=MaterialTheme.colorScheme.primary)
            FlowRow(horizontalArrangement=Arrangement.spacedBy(8.dp),verticalArrangement=Arrangement.spacedBy(4.dp)) {
                items.forEach { (id,label)-> FilterChip(selected=id in allergens,onClick={allergens=if(id in allergens) allergens-id else allergens+id},enabled=!s.busy,label={Text(label)}) }
            }
        }
        Button(onClick={vm.saveProfile(Profile(name,allergens.toList()))},Modifier.fillMaxWidth(),enabled=!s.busy) {Text("Guardar perfil")}
        HorizontalDivider()
        Text("Tus datos",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Bold)
        Text("Supabase gestiona tu acceso. Tu historial y preferencias se guardan en Cloudflare D1. Las fotos no se suben.",style=MaterialTheme.typography.bodySmall)
        OutlinedButton(onClick={clear=true},enabled=!s.busy) {Text("Eliminar historial y perfil")}
        TextButton(onClick=vm::logout,enabled=!s.busy) {Text("Cerrar sesión")}
        Text("lookupsafe · 0.1.0",style=MaterialTheme.typography.labelSmall)
    }
    if(clear) AlertDialog(onDismissRequest={clear=false},title={Text("¿Eliminar tus datos?")},text={Text("Se borrarán todas tus consultas y preferencias. Tu cuenta de Supabase permanece activa. Esta acción no se puede deshacer.")},confirmButton={TextButton(onClick={clear=false;vm.clearData()}) {Text("Eliminar datos")}},dismissButton={TextButton(onClick={clear=false}) {Text("Cancelar")}})
}
@Composable private fun EmptyState(title:String,description:String) {
    Card(Modifier.fillMaxWidth()) {Column(Modifier.padding(24.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {Icon(Icons.Outlined.Inventory2,null,tint=MaterialTheme.colorScheme.primary);Text(title,fontWeight=FontWeight.Bold);Text(description,style=MaterialTheme.typography.bodyMedium)}}
}
