package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.billionsbounty.mobile.ui.viewmodel.PaymentViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentScreen(
    viewModel: PaymentViewModel,
    currentQuestionCost: Double = 10.0,
    onBackClick: () -> Unit,
    onPaymentSuccess: () -> Unit
) {
    val state by viewModel.paymentState.collectAsState()
    var showAmountSelection by remember { mutableStateOf(false) }
    
    // Update the current question cost in ViewModel
    LaunchedEffect(currentQuestionCost) {
        viewModel.setCurrentQuestionCost(currentQuestionCost)
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Complete Payment") },
                navigationIcon = {
                    TextButton(onClick = onBackClick) {
                        Text("Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Step 1: Wallet Connection
            if (!state.walletConnected) {
                WalletConnectionStep(
                    onConnect = { address ->
                        viewModel.connectWallet(address)
                    }
                )
            } else {
                // Step 2: Amount Selection
                if (state.selectedAmount == null) {
                    AmountSelectionPrompt(
                        onSelectAmount = { showAmountSelection = true }
                    )
                } else {
                    // Step 3: Payment Confirmation
                    PaymentConfirmationStep(
                        viewModel = viewModel,
                        onSuccess = { questions, credit, isMock ->
                            onPaymentSuccess()
                        },
                        onError = { error ->
                            // Error is already set in ViewModel
                        },
                        onChangeAmount = { showAmountSelection = true }
                    )
                }
            }
            
            // Error Display
            state.error?.let { error ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = "Error",
                            tint = MaterialTheme.colorScheme.error
                        )
                        Text(
                            text = error,
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }
        }
    }
    
    // Payment Amount Selection Dialog
    if (showAmountSelection) {
        PaymentAmountSelectionDialog(
            currentQuestionCost = state.currentQuestionCost,
            onDismiss = { showAmountSelection = false },
            onSelectAmount = { amount ->
                viewModel.selectAmount(amount)
                showAmountSelection = false
            },
            isProcessing = state.isProcessing
        )
    }
}

@Composable
fun WalletConnectionStep(onConnect: (String) -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "🔗 Connect Wallet",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            
            Text(
                text = "Connect your Solana wallet to make a payment",
                style = MaterialTheme.typography.bodyLarge
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Mock wallet connection - would use WalletViewModel in real implementation
            Button(
                onClick = { onConnect("YourWalletAddress123...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text("Connect Phantom Wallet")
            }
            
            OutlinedButton(
                onClick = { onConnect("YourWalletAddress123...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text("Connect Solflare Wallet")
            }
        }
    }
}

@Composable
fun AmountSelectionPrompt(onSelectAmount: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "💰 Select Payment Amount",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            
            Text(
                text = "Choose how much you'd like to contribute to the bounty prize pool",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Button(
                onClick = onSelectAmount,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
            ) {
                Text("Try Your Luck")
            }
        }
    }
}

@Composable
fun PaymentConfirmationStep(
    viewModel: PaymentViewModel,
    onSuccess: (Int, Double, Boolean) -> Unit,
    onError: (String) -> Unit,
    onChangeAmount: () -> Unit
) {
    val state by viewModel.paymentState.collectAsState()
    
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "💳 Payment Summary",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            
            Divider()
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Payment Amount:")
                Text(
                    text = "$${String.format("%.2f", state.selectedAmount ?: 0.0)}",
                    fontWeight = FontWeight.Bold
                )
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Questions Granted:")
                Text(
                    text = "${state.questionsGranted}",
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            if (state.creditRemainder > 0) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text("Credit Balance:")
                    Text(
                        text = "$${String.format("%.2f", state.creditRemainder)}",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF10B981)
                    )
                }
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Wallet:")
                Text(
                    text = state.walletAddress?.take(8) ?: "",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Your USDC Balance:")
                Text(
                    text = "${String.format("%.2f", state.usdcBalance)} USDC",
                    color = if (state.usdcBalance >= (state.selectedAmount ?: 0.0)) Color.Green else Color.Red
                )
            }
            
            Divider()
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Total:",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "$${String.format("%.2f", state.selectedAmount ?: 0.0)}",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Button(
                onClick = {
                    viewModel.processPayment(
                        onSuccess = onSuccess,
                        onError = onError
                    )
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                enabled = !state.isProcessing && state.usdcBalance >= (state.selectedAmount ?: 0.0)
            ) {
                if (state.isProcessing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White
                    )
                } else {
                    Text("Confirm Payment")
                }
            }
            
            OutlinedButton(
                onClick = onChangeAmount,
                modifier = Modifier.fillMaxWidth(),
                enabled = !state.isProcessing
            ) {
                Text("Change Amount")
            }
        }
    }
}
