package app.lookupsafe

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext

data class AppState(
    val signedIn: Boolean = false, val busy: Boolean = false, val message: String? = null,
    val tab: String = "Inicio", val profile: Profile = Profile(), val email: String = "",
    val scans: List<Scan> = emptyList(), val nextOffset: Int? = null, val selected: Scan? = null,
    val productName: String = "", val labelText: String = ""
)
class AppViewModel(application: Application): AndroidViewModel(application) {
    private val repo = Repository(application)
    private val mutable = MutableStateFlow(AppState())
    val state = mutable.asStateFlow()
    val configured get() = repo.configured
    init { if(repo.hasSession) run { mutable.update { it.copy(signedIn=true,email=repo.email) }; reload() } }
    private fun run(block: suspend () -> Unit) {
        if(mutable.value.busy) return
        mutable.update { it.copy(busy=true,message=null) }
        viewModelScope.launch {
            try { block() }
            catch(e: CancellationException) { throw e }
            catch(e: Exception) { mutable.update {
                val message=e.message ?: "No se pudo completar. Revisa tu conexión."
                if(repo.hasSession) it.copy(message=message,signedIn=true) else AppState(message=message)
            } }
            finally { mutable.update { it.copy(busy=false) } }
        }
    }
    private suspend fun reload() {
        val profile=repo.profile(); val scans=repo.scans()
        mutable.update { it.copy(profile=profile,scans=scans.items,nextOffset=scans.nextOffset,email=repo.email) }
    }
    fun login(email: String, password: String, signup: Boolean) = run {
        if(repo.login(email,password,signup)) {
            mutable.update { it.copy(signedIn=true,email=repo.email) }; reload()
        } else mutable.update { it.copy(message="Revisa tu correo para confirmar tu cuenta. Luego inicia sesión.") }
    }
    fun logout() = run {
        try { repo.logout() } finally { mutable.value=AppState(message="Sesión cerrada en este dispositivo.") }
    }
    fun refresh() = run { reload() }
    fun more() = run {
        val offset=mutable.value.nextOffset ?: return@run
        val page=repo.scans(offset)
        mutable.update { it.copy(scans=(it.scans+page.items).distinctBy { s->s.id },nextOffset=page.nextOffset) }
    }
    fun tab(value: String) { mutable.update { it.copy(tab=value,selected=null) } }
    fun select(scan: Scan?) { mutable.update { it.copy(selected=scan) } }
    fun name(value: String) { mutable.update { it.copy(productName=value.take(120)) } }
    fun label(value: String) { mutable.update { it.copy(labelText=value.take(12000)) } }
    fun dismiss() { mutable.update { it.copy(message=null) } }
    fun error(message: String) { mutable.update { it.copy(message=message) } }
    fun recognize(uri: Uri) = run {
        val recognizer=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
        try {
            val image=withContext(Dispatchers.IO) { InputImage.fromFilePath(getApplication(),uri) }
            val text=recognizer.process(image).await().text
            mutable.update { it.copy(labelText=text.take(12000),message=if(text.isBlank()) "No se detectó texto. Prueba otra foto o escribe la etiqueta." else "Revisa y corrige el texto antes de analizar.") }
        } finally { recognizer.close() }
    }
    fun analyze() = run {
        val s=mutable.value
        require(s.productName.isNotBlank() && s.labelText.trim().length>=2) { "Escribe el nombre y los ingredientes." }
        val result=repo.analyze(s.productName,s.labelText)
        mutable.update { it.copy(scans=listOf(result)+it.scans,selected=result,productName="",labelText="") }
    }
    fun favorite(scan: Scan) = run {
        val result=repo.favorite(scan)
        mutable.update { it.copy(selected=result,scans=it.scans.map { s->if(s.id==result.id) result else s }) }
    }
    fun delete(scan: Scan) = run {
        repo.delete(scan); mutable.update { it.copy(selected=null) }; reload()
    }
    fun saveProfile(profile: Profile) = run {
        val saved=repo.saveProfile(profile)
        mutable.update { it.copy(profile=saved,message="Perfil guardado. Se aplicará a tus próximos análisis.") }
    }
    fun clearData() = run { repo.clearData(); reload(); mutable.update { it.copy(selected=null,message="Historial y perfil eliminados. Tu cuenta de acceso permanece activa.") } }
}
