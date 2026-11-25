import java.util.Properties
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("org.jetbrains.kotlin.plugin.serialization")
}
val config = Properties().apply { rootProject.file("lookupsafe.properties").takeIf { it.exists() }?.inputStream()?.use { load(it) } }
fun setting(name: String, default: String = ""): String = System.getenv(name) ?: config.getProperty(name, default)
fun quoted(value: String) = "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "") + "\""
android {
    namespace = "app.lookupsafe"
    compileSdk = 35
    defaultConfig {
        applicationId = "app.lookupsafe"
        minSdk = 26
        targetSdk = 35
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        versionCode = 1
        versionName = "0.1.0"
        buildConfigField("String", "API_BASE_URL", quoted(setting("API_BASE_URL", "http://10.0.2.2:8787")))
        buildConfigField("String", "SUPABASE_URL", quoted(setting("SUPABASE_URL")))
        buildConfigField("String", "SUPABASE_PUBLISHABLE_KEY", quoted(setting("SUPABASE_PUBLISHABLE_KEY")))
    }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
    buildTypes { release { isMinifyEnabled = false } }
}
dependencies {
    implementation(platform("androidx.compose:compose-bom:2025.04.01"))
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-play-services:1.10.2")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.google.mlkit:text-recognition:16.0.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2025.04.01"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}

val validateReleaseConfig by tasks.registering {
    doLast {
        require(setting("API_BASE_URL").startsWith("https://")) { "Release builds require an HTTPS API_BASE_URL." }
        require(setting("SUPABASE_URL").startsWith("https://") && !setting("SUPABASE_URL").contains("YOUR_PROJECT")) { "Set the real SUPABASE_URL before building a release." }
        require(setting("SUPABASE_PUBLISHABLE_KEY").isNotBlank() && !setting("SUPABASE_PUBLISHABLE_KEY").startsWith("YOUR_")) { "Set the Supabase public key before building a release." }
    }
}
tasks.matching { it.name == "preReleaseBuild" }.configureEach { dependsOn(validateReleaseConfig) }
