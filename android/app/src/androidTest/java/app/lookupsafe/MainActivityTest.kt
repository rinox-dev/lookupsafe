package app.lookupsafe

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MainActivityTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun loginScreenLoadsAndSignupCanBeOpenedAndClosed() {
        compose.onNodeWithText("lookupsafe").assertIsDisplayed()
        compose.onNodeWithText("Revisa etiquetas de alimentos, perfumes, desodorantes y productos de cuidado personal.").assertIsDisplayed()
        compose.onNodeWithText("Falta conectar Supabase. Completa android/lookupsafe.properties y vuelve a compilar la app.").assertIsDisplayed()
        compose.onNodeWithText("Entrar con correo").assertIsDisplayed()

        compose.onNodeWithText("Crear una cuenta").performClick()
        compose.onNodeWithText("Crea tu cuenta").assertIsDisplayed()
        compose.onNodeWithText("Ya tengo una cuenta").performClick()
        compose.onNodeWithText("Te damos la bienvenida").assertIsDisplayed()
    }
}
