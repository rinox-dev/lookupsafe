package app.lookupsafe

import kotlinx.serialization.Serializable
import kotlinx.serialization.SerialName

@Serializable data class Session(
    @SerialName("access_token") val accessToken: String,
    @SerialName("refresh_token") val refreshToken: String,
    @SerialName("expires_in") val expiresIn: Long = 3600,
    val user: AuthUser = AuthUser(),
    val expiresAt: Long = 0
)
@Serializable data class AuthUser(val id: String = "", val email: String = "")
@Serializable data class Profile(val displayName: String = "", val allergens: List<String> = emptyList())
@Serializable data class Ingredient(val name: String, val status: String = "unreviewed")
@Serializable data class Allergen(val id: String, val name: String, val personal: Boolean)
@Serializable data class Source(val title: String, val url: String)
@Serializable data class Analysis(
    val version: Int, val status: String, val ingredients: List<Ingredient>,
    val allergens: List<Allergen>, val score: Int? = null,
    val summary: String, val notice: String, val sources: List<Source>
)
@Serializable data class Scan(
    val id: String, val productName: String, val labelText: String,
    val analysis: Analysis, val favorite: Boolean, val createdAt: String
)
@Serializable data class ScanPage(val items: List<Scan>, val nextOffset: Int? = null)
val allergenOptions = linkedMapOf("milk" to "Leche", "egg" to "Huevo", "peanut" to "Maní", "tree_nut" to "Frutos de cáscara", "soy" to "Soya", "wheat" to "Trigo", "fish" to "Pescado", "shellfish" to "Crustáceos", "sesame" to "Sésamo")
val concernGroups = linkedMapOf(
    "Alérgenos alimentarios" to allergenOptions,
    "Fragancias" to linkedMapOf("fragrance" to "Fragancia/perfume", "linalool" to "Linalool", "limonene" to "Limoneno", "citronellol" to "Citronelol", "geraniol" to "Geraniol", "eugenol" to "Eugenol", "cinnamal" to "Cinamal", "coumarin" to "Cumarina", "benzyl_alcohol" to "Alcohol bencílico", "benzyl_salicylate" to "Salicilato de bencilo", "phthalates" to "Ftalatos"),
    "Conservantes" to linkedMapOf("methylisothiazolinone" to "Metilisotiazolinona", "methylchloroisothiazolinone" to "Metilcloroisotiazolinona", "formaldehyde" to "Formaldehído", "parabens" to "Parabenos"),
    "Desodorantes y antitranspirantes" to linkedMapOf("aluminum_compounds" to "Compuestos de aluminio", "baking_soda" to "Bicarbonato de sodio")
)
val concernOptions = concernGroups.values.fold(linkedMapOf<String,String>()) { all, group -> all.apply { putAll(group) } }
