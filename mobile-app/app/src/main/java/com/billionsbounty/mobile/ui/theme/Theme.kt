package com.billionsbounty.mobile.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// Web-matching color scheme: White/Gray/Yellow palette
private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFFFFFFF),        // White for header
    secondary = Color(0xFFEAB308),      // Yellow for accents
    tertiary = Color(0xFFF59E0B),       // Orange for highlights
    background = Color(0xFFFFFFFF),     // White background
    surface = Color(0xFFF3F4F6),        // Light gray surface
    onPrimary = Color(0xFF111827),      // Dark text on white
    onSecondary = Color(0xFF111827),    // Dark text on yellow
    onBackground = Color(0xFF111827),   // Dark text on background
    onSurface = Color(0xFF374151)       // Gray text
)

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFFFFFFFF),        // White for header
    secondary = Color(0xFFEAB308),      // Yellow for accents (#EAB308)
    tertiary = Color(0xFFF59E0B),       // Orange for highlights
    background = Color(0xFFFFFFFF),     // White background
    surface = Color(0xFFF3F4F6),        // Light gray surface
    onPrimary = Color(0xFF111827),      // Dark text on white (#111827)
    onSecondary = Color(0xFF111827),    // Dark text on yellow
    onBackground = Color(0xFF111827),   // Dark text on background
    onSurface = Color(0xFF374151),      // Gray text (#374151)
    outline = Color(0xFFE5E7EB)         // Border gray
)

@Composable
fun BillionsBountyTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            // Set status bar to dark navy blue to match header
            window.statusBarColor = Color(0xFF0F172A).toArgb()
            // Use light icons on dark status bar
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
