package com.billionsbounty.mobile.ui.screens

import android.os.Build
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.billionsbounty.mobile.BuildConfig
import com.billionsbounty.mobile.wallet.MockWalletAdapter
import com.billionsbounty.mobile.wallet.WalletAdapter
import com.billionsbounty.mobile.wallet.WalletConnectionState
import kotlinx.coroutines.launch

/**
 * Real Wallet Connection Dialog
 * Uses Solana Mobile Wallet Adapter to connect to Phantom, Solflare, etc.
 */
@Composable
fun WalletConnectionDialog(
    walletAdapter: WalletAdapter,
    onDismiss: () -> Unit,
    onConnected: (String) -> Unit,
    prefillConnectedAddress: String? = null
) {
    val context = LocalContext.current
    val activity = context as? ComponentActivity
    val coroutineScope = rememberCoroutineScope()
    val mockWalletAdapter = remember { MockWalletAdapter() }
    val canUseMockWallet = remember { BuildConfig.DEBUG && isRunningOnEmulator() }
    
    var isConnecting by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    // Prefill is used strictly for previews/tests so we can verify connected UI without hitting the real adapter.
    var connectedAddress by remember { mutableStateOf<String?>(prefillConnectedAddress) }
    
    fun startAuthorization(authorizer: suspend (ComponentActivity) -> Result<String>) {
        val currentActivity = activity
        if (currentActivity == null) {
            error = "Cannot connect wallet from this context"
            return
        }
        
        isConnecting = true
        error = null
        
        coroutineScope.launch {
            val result = authorizer(currentActivity)
            isConnecting = false
            
            result.fold(
                onSuccess = { address ->
                    connectedAddress = address
                    // Give users a short success moment before closing.
                    kotlinx.coroutines.delay(1500)
                    onConnected(address)
                    onDismiss()
                },
                onFailure = { throwable ->
                    error = throwable.message ?: "Failed to connect wallet"
                }
            )
        }
    }
    
    // Keep the dialog open during the connection flow so users don't have to re-open it
    // Prevent dismissal on back press or outside tap while connecting
    Dialog(
        onDismissRequest = {
            if (!isConnecting && connectedAddress == null) onDismiss()
        },
        properties = DialogProperties(
            dismissOnBackPress = !isConnecting,
            dismissOnClickOutside = !isConnecting
        )
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.White
            )
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Header Icon
                Icon(
                    imageVector = if (connectedAddress != null) Icons.Default.CheckCircle
                                  else if (error != null) Icons.Default.Error
                                  else Icons.Default.AccountBalanceWallet,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp),
                    tint = if (connectedAddress != null) Color(0xFF16A34A)
                           else if (error != null) Color(0xFFDC2626)
                           else Color(0xFF8B5CF6)
                )
                
                // Title
                Text(
                    text = if (connectedAddress != null) "Wallet Connected!"
                           else "Connect Wallet",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827)
                )
                
                // Description or Address
                if (connectedAddress != null) {
                    Text(
                        text = "Successfully connected to:",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280)
                    )
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFF3F4F6)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = connectedAddress!!.take(8) + "..." + connectedAddress!!.takeLast(8),
                            fontSize = 12.sp,
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            color = Color(0xFF374151),
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                } else {
                    Text(
                        text = "Connect your Solana wallet to participate in bounties and earn rewards.",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280),
                        textAlign = TextAlign.Center
                    )
                }
                
                // Error Message
                if (error != null) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFFEE2E2)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = error!!,
                            fontSize = 12.sp,
                            color = Color(0xFFDC2626),
                            modifier = Modifier.padding(12.dp)
                        )
                    }
                }
                
                Divider(modifier = Modifier.padding(vertical = 8.dp))
                
                // Action Buttons
                if (connectedAddress == null) {
                    // Connect Button
                    Button(
                        onClick = {
                            startAuthorization { componentActivity ->
                                walletAdapter.authorize(componentActivity)
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp),
                        // Disable while connecting so the user cannot accidentally dismiss or double-trigger
                        enabled = !isConnecting,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF8B5CF6)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        if (isConnecting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Connecting...", fontSize = 14.sp)
                        } else {
                            Text("Connect Wallet", fontSize = 14.sp, fontWeight = FontWeight.Medium)
                        }
                    }
                    
                    if (canUseMockWallet) {
                        // Provide a debug-only escape hatch so emulator testing can exercise post-wallet flows.
                        TextButton(
                            onClick = {
                                startAuthorization { componentActivity ->
                                    mockWalletAdapter.authorize(componentActivity)
                                }
                            },
                            enabled = !isConnecting
                        ) {
                            Text("Simulate Wallet (Emulator)", fontSize = 12.sp)
                        }
                        Text(
                            text = "Debug helper: generates a temporary wallet address so you can test flows without a mobile wallet.",
                            fontSize = 10.sp,
                            color = Color(0xFF6B7280),
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(horizontal = 16.dp)
                        )
                    }
                    
                    // Help Text
                    Text(
                        text = "This will open your Solana wallet app (Phantom, Solflare, etc.)",
                        fontSize = 11.sp,
                        color = Color(0xFF9CA3AF),
                        textAlign = TextAlign.Center,
                        modifier = Modifier.padding(horizontal = 16.dp)
                    )
                }
                
                // Close/Done Button
                OutlinedButton(
                    onClick = {
                        if (!isConnecting) onDismiss()
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFD1D5DB)),
                    shape = RoundedCornerShape(8.dp),
                    enabled = !isConnecting
                ) {
                    Text(
                        if (connectedAddress != null) "Done" else "Cancel",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF374151)
                    )
                }
            }
        }
    }
}

private fun isRunningOnEmulator(): Boolean {
    val fingerprint = Build.FINGERPRINT.lowercase()
    val model = Build.MODEL.lowercase()
    val brand = Build.BRAND.lowercase()
    val product = Build.PRODUCT.lowercase()
    
    // Consolidated heuristics recommended by Android docs for detecting emulators during debug builds.
    return fingerprint.contains("generic") ||
        fingerprint.contains("unknown") ||
        model.contains("sdk") ||
        model.contains("emulator") ||
        brand.startsWith("generic") ||
        product.contains("sdk_gphone") ||
        product.contains("emulator")
}

/**
 * Simplified "Coming Soon" dialog for when wallet adapter isn't available
 */
@Composable
fun WalletComingSoonDialog(onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                imageVector = Icons.Default.AccountBalanceWallet,
                contentDescription = null,
                tint = Color(0xFF8B5CF6),
                modifier = Modifier.size(48.dp)
            )
        },
        title = {
            Text(
                text = "Wallet Integration",
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = "Solana wallet connection is ready!",
                    fontSize = 14.sp,
                    color = Color(0xFF374151)
                )
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFDCFCE7)
                    ),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text(
                        text = "Install Phantom or Solflare wallet from the Play Store, then try connecting again.",
                        fontSize = 12.sp,
                        color = Color(0xFF166534),
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = onDismiss,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF8B5CF6)
                )
            ) {
                Text("Got it")
            }
        }
    )
}
