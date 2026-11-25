package app.lookupsafe

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity: ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val dark=isSystemInDarkTheme()
            val scheme=if(dark) darkColorScheme(
                primary=Color(0xFF63D5B5),onPrimary=Color(0xFF00382B),primaryContainer=Color(0xFF0F2A24),onPrimaryContainer=Color(0xFF7FE0C5),
                secondary=Color(0xFF7FE0C5),secondaryContainer=Color(0xFF0F2A24),onSecondaryContainer=Color(0xFFB0F0DC),
                background=Color(0xFF0B0F14),surface=Color(0xFF151C26),surfaceContainer=Color(0xFF151C26),
                surfaceContainerLow=Color(0xFF151C26),surfaceContainerHighest=Color(0xFF1A212C),surfaceVariant=Color(0xFF222C38))
                else lightColorScheme(
                    primary=Color(0xFF1F8A70),onPrimary=Color.White,primaryContainer=Color(0xFFE6F4EF),onPrimaryContainer=Color(0xFF146A55),
                    secondary=Color(0xFF146A55),secondaryContainer=Color(0xFFE6F4EF),onSecondaryContainer=Color(0xFF146A55),
                    background=Color(0xFFF5F7FA),surface=Color.White,surfaceContainer=Color.White,
                    surfaceContainerLow=Color.White,surfaceContainerHighest=Color(0xFFE8EEF3),surfaceVariant=Color(0xFFE8EEF3))
            MaterialTheme(colorScheme=scheme) { LookupSafeApp(viewModel()) }
        }
    }
}
