package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.billionsbounty.mobile.data.repository.NftRepository
import com.billionsbounty.mobile.wallet.WalletAdapter
import kotlinx.coroutines.launch

/**
 * Dialog for NFT verification
 * Allows users to verify NFT ownership to receive 5 free questions
 */
@Composable
fun NftVerificationDialog(
    walletAdapter: WalletAdapter?,
    nftRepository: NftRepository,
    onDismiss: () -> Unit,
    onVerificationSuccess: () -> Unit
) {
    var loading by remember { mutableStateOf(false) }
    var checking by remember { mutableStateOf(true) }
    var ownsNft by remember { mutableStateOf(false) }
    var alreadyVerified by remember { mutableStateOf(false) }
    var questionsRemaining by remember { mutableStateOf(0) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var successMessage by remember { mutableStateOf<String?>(null) }
    
    val coroutineScope = rememberCoroutineScope()
    val walletAddress = walletAdapter?.getPublicKey()

    // Check ownership on dialog open
    LaunchedEffect(walletAddress) {
        if (walletAddress != null) {
            checking = true
            errorMessage = null
            
            // Check if already verified
            nftRepository.getNftStatus(walletAddress)
                .onSuccess { status ->
                    if (status.verified) {
                        alreadyVerified = true
                        questionsRemaining = status.questions_remaining
                        checking = false
                        return@LaunchedEffect
                    }
                }
                .onFailure { error ->
                    errorMessage = "Failed to check verification status: ${error.message}"
                }
            
            // Check if owns NFT (backend will handle mock mode)
            nftRepository.checkNftOwnership(walletAddress)
                .onSuccess { response ->
                    ownsNft = response.has_nft
                    checking = false
                }
                .onFailure { error ->
                    errorMessage = "Failed to check NFT ownership: ${error.message}"
                    checking = false
                }
        } else {
            errorMessage = "Please connect your wallet first"
            checking = false
        }
    }

    // Verify NFT ownership
    fun verifyNft() {
        if (walletAddress == null) {
            errorMessage = "Wallet not connected"
            return
        }

        coroutineScope.launch {
            loading = true
            errorMessage = null
            
            try {
                // In a real implementation, we would:
                // 1. Create a transaction for NFT verification
                // 2. Sign it with the wallet
                // 3. Send to the smart contract
                // For now, we'll simulate with a placeholder signature
                
                val signature = "simulated_signature_${System.currentTimeMillis()}"
                
                nftRepository.verifyNftOwnership(walletAddress, signature)
                    .onSuccess { result ->
                        if (result.success && result.verified) {
                            successMessage = result.message ?: "You've been granted ${result.questions_granted} free questions!"
                            kotlinx.coroutines.delay(1000)
                            onVerificationSuccess()
                            kotlinx.coroutines.delay(500)
                            onDismiss()
                        } else {
                            errorMessage = result.message ?: "Verification failed"
                        }
                    }
                    .onFailure { error ->
                        errorMessage = "Verification failed: ${error.message}"
                    }
            } catch (e: Exception) {
                errorMessage = "Error: ${e.message}"
            } finally {
                loading = false
            }
        }
    }

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .wrapContentHeight(),
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Solana Seekers",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close")
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Content
                when {
                    checking -> {
                        // Checking status
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                CircularProgressIndicator()
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    text = "Checking NFT ownership...",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Color.Gray
                                )
                            }
                        }
                    }
                    
                    alreadyVerified -> {
                        // Already verified
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                imageVector = Icons.Default.CheckCircle,
                                contentDescription = "Verified",
                                modifier = Modifier.size(64.dp),
                                tint = Color(0xFF10B981)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "Already Verified!",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "You've already verified your NFT ownership.",
                                style = MaterialTheme.typography.bodyMedium,
                                textAlign = TextAlign.Center,
                                color = Color.Gray
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Questions remaining: $questionsRemaining",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color(0xFF8B5CF6),
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                    
                    successMessage != null -> {
                        // Success state
                        Column(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "🎉",
                                style = MaterialTheme.typography.displayLarge
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "Verification Successful!",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "You've been granted 5 free questions!",
                                style = MaterialTheme.typography.bodyMedium,
                                textAlign = TextAlign.Center,
                                color = Color.Gray
                            )
                        }
                    }
                    
                    else -> {
                        // Main verification UI
                        Column(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            // How it works
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                color = Color(0xFFF3E8FF),
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Column(
                                    modifier = Modifier.padding(12.dp)
                                ) {
                                    Text(
                                        text = "How it works:",
                                        style = MaterialTheme.typography.titleSmall,
                                        fontWeight = FontWeight.Bold,
                                        color = Color(0xFF7C3AED)
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "1. We check if you own the required NFT\n" +
                                               "2. You sign a transaction to verify ownership\n" +
                                               "3. Receive 5 free questions instantly",
                                        style = MaterialTheme.typography.bodySmall,
                                        color = Color(0xFF7C3AED)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            // NFT ownership status
                            if (walletAddress == null) {
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = Color(0xFFFEE2E2),
                                    shape = RoundedCornerShape(8.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Error,
                                            contentDescription = "Error",
                                            tint = Color(0xFFDC2626)
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "Please connect your wallet to verify NFT ownership.",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = Color(0xFFDC2626)
                                        )
                                    }
                                }
                            } else if (!ownsNft) {
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = Color(0xFFFEE2E2),
                                    shape = RoundedCornerShape(8.dp)
                                ) {
                                    Column(
                                        modifier = Modifier.padding(12.dp)
                                    ) {
                                        Text(
                                            text = "NFT Not Found",
                                            style = MaterialTheme.typography.titleSmall,
                                            fontWeight = FontWeight.Bold,
                                            color = Color(0xFFDC2626)
                                        )
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "You don't own the required NFT to verify.",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = Color(0xFFDC2626)
                                        )
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "Required: ${NftRepository.AUTHORIZED_NFT_MINT.take(8)}...${NftRepository.AUTHORIZED_NFT_MINT.takeLast(8)}",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = Color(0xFFDC2626),
                                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                                        )
                                    }
                                }
                            } else {
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = Color(0xFFD1FAE5),
                                    shape = RoundedCornerShape(8.dp)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(12.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.CheckCircle,
                                            contentDescription = "Success",
                                            tint = Color(0xFF059669)
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(
                                            text = "✓ NFT Found: You own the required NFT! Click verify to get 5 free questions.",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = Color(0xFF059669)
                                        )
                                    }
                                }
                            }

                            // Error message
                            if (errorMessage != null) {
                                Spacer(modifier = Modifier.height(12.dp))
                                Surface(
                                    modifier = Modifier.fillMaxWidth(),
                                    color = Color(0xFFFEE2E2),
                                    shape = RoundedCornerShape(8.dp)
                                ) {
                                    Text(
                                        text = errorMessage!!,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = Color(0xFFDC2626),
                                        modifier = Modifier.padding(12.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            // Action buttons
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                OutlinedButton(
                                    onClick = onDismiss,
                                    modifier = Modifier.weight(1f),
                                    enabled = !loading
                                ) {
                                    Text("Cancel")
                                }
                                
                                Button(
                                    onClick = { verifyNft() },
                                    modifier = Modifier.weight(1f),
                                    enabled = walletAddress != null && ownsNft && !loading,
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = Color(0xFF8B5CF6)
                                    )
                                ) {
                                    if (loading) {
                                        CircularProgressIndicator(
                                            modifier = Modifier.size(16.dp),
                                            color = Color.White,
                                            strokeWidth = 2.dp
                                        )
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text("Verifying...")
                                    } else {
                                        Text("Verify Genesis NFT")
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


