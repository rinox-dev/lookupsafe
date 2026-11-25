package app.lookupsafe

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.json.*
import kotlinx.serialization.encodeToString
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

class ApiException(val code: Int, message: String): Exception(message)
class Repository(context: Context) {
    private val json = Json { ignoreUnknownKeys = true }
    private val client = OkHttpClient.Builder().callTimeout(25, TimeUnit.SECONDS).build()
    private val store = SessionStore(context)
    private val authMutex = Mutex()
    private var session: Session? = store.read()?.let { runCatching { json.decodeFromString<Session>(it) }.getOrNull() }
    val configured get() = BuildConfig.SUPABASE_URL.startsWith("https://") && BuildConfig.SUPABASE_PUBLISHABLE_KEY.isNotBlank() && !BuildConfig.SUPABASE_URL.contains("YOUR_PROJECT") && !BuildConfig.SUPABASE_PUBLISHABLE_KEY.startsWith("YOUR_")
    val email get() = session?.user?.email.orEmpty()
    val hasSession get() = session != null
    private suspend fun request(url: String, method: String = "GET", payload: String? = null, token: String? = null, auth: Boolean = false): String = withContext(Dispatchers.IO) {
        val builder = Request.Builder().url(url).header("Accept", "application/json")
        if(auth) builder.header("apikey", BuildConfig.SUPABASE_PUBLISHABLE_KEY)
        token?.let { builder.header("Authorization", "Bearer $it") }
        builder.method(method, payload?.toRequestBody("application/json".toMediaType()))
        client.newCall(builder.build()).execute().use { response ->
            val text = response.body?.string().orEmpty()
            if(!response.isSuccessful) {
                val error = runCatching { json.parseToJsonElement(text).jsonObject }.getOrNull()
                val message = listOf("msg","error_description","message","error").firstNotNullOfOrNull { error?.get(it)?.jsonPrimitive?.contentOrNull }
                throw ApiException(response.code, message ?: "No se pudo completar la solicitud (${response.code}).")
            }
            text
        }
    }
    private suspend fun auth(path: String, payload: JsonObject, token: String? = null) = request("${BuildConfig.SUPABASE_URL.trimEnd('/')}/auth/v1/$path", "POST", payload.toString(), token, true)
    private fun keep(raw: String) {
        val incoming = json.decodeFromString<Session>(raw)
        val next = incoming.copy(expiresAt = System.currentTimeMillis() / 1000 + incoming.expiresIn)
        store.save(json.encodeToString(next))
        session = next
    }
    suspend fun login(email: String, password: String, signup: Boolean): Boolean = authMutex.withLock {
        check(configured) { "Configura Supabase en android/lookupsafe.properties y vuelve a compilar." }
        val raw = auth(if(signup) "signup" else "token?grant_type=password", buildJsonObject { put("email",email.trim()); put("password",password) })
        val token = json.parseToJsonElement(raw).jsonObject["access_token"]?.jsonPrimitive?.contentOrNull
        if(token.isNullOrBlank()) false else { keep(raw); true }
    }
    private suspend fun accessToken(force: Boolean = false): String = authMutex.withLock {
        val current = session ?: throw ApiException(401,"Inicia sesión para continuar.")
        if(force || current.expiresAt <= System.currentTimeMillis()/1000 + 60) {
            try { keep(auth("token?grant_type=refresh_token",buildJsonObject { put("refresh_token",current.refreshToken) })) }
            catch(e: ApiException) { if(e.code in listOf(400,401,403)) { session=null; store.clear() }; throw e }
        }
        session!!.accessToken
    }
    suspend fun logout() {
        val token = session?.accessToken
        try { if(token != null) auth("logout?scope=local",buildJsonObject {},token) }
        finally { authMutex.withLock { session=null; store.clear() } }
    }
    private suspend fun api(path: String, method: String = "GET", payload: String? = null): String {
        val token = accessToken()
        try { return request("${BuildConfig.API_BASE_URL.trimEnd('/')}/v1/$path",method,payload,token) }
        catch(e: ApiException) {
            if(e.code != 401) throw e
            return request("${BuildConfig.API_BASE_URL.trimEnd('/')}/v1/$path",method,payload,accessToken(true))
        }
    }
    suspend fun profile(): Profile = json.decodeFromString(api("profile"))
    suspend fun saveProfile(value: Profile): Profile = json.decodeFromString(api("profile","PUT",json.encodeToString(value)))
    suspend fun scans(offset: Int = 0): ScanPage = json.decodeFromString(api("scans?limit=30&offset=$offset"))
    suspend fun analyze(name: String, label: String): Scan = json.decodeFromString(api("scans","POST",buildJsonObject { put("productName",name.trim()); put("labelText",label.trim()) }.toString()))
    suspend fun favorite(scan: Scan): Scan = json.decodeFromString(api("scans/${scan.id}","PATCH",buildJsonObject { put("favorite",!scan.favorite) }.toString()))
    suspend fun delete(scan: Scan) { api("scans/${scan.id}","DELETE") }
    suspend fun clearData() { api("data","DELETE") }
}
