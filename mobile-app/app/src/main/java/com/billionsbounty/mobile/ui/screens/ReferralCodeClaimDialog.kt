package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CardGiftcard
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.billionsbounty.mobile.data.repository.ApiRepository
import kotlinx.coroutines.launch

/**
 * Dialog for claiming referral code
 * User enters email to link wallet and receive free questions
 */
@Composable
fun ReferralCodeClaimDialog(
    referralCode: String,
    walletAddress: String,
    repository: ApiRepository,
    onClaimed: (receiverQuestions: Int, referrerQuestions: Int) -> Unit,
    onDismiss: () -> Unit
) {
    var email by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var success by remember { mutableStateOf(false) }
    var receiverQuestions by remember { mutableStateOf(0) }
    var referrerQuestions by remember { mutableStateOf(0) }
    val coroutineScope = rememberCoroutineScope()
    
    Dialog(onDismissRequest = onDismiss) {
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
                    imageVector = if (success) Icons.Default.Check else Icons.Default.CardGiftcard,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = if (success) Color(0xFF16A34A) else Color(0xFF10B981)
                )
                
                // Title
                Text(
                    text = if (success) "🎉 Success!" else "Claim Free Questions",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827)
                )
                
                if (success) {
                    // Success Message
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFDCFCE7)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                text = "You now have $receiverQuestions free questions!",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF166534),
                                textAlign = TextAlign.Center
                            )
                            Text(
                                text = "The person who referred you also got $referrerQuestions questions!",
                                fontSize = 14.sp,
                                color = Color(0xFF166534),
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                    
                    Button(
                        onClick = {
                            onClaimed(receiverQuestions, referrerQuestions)
                            onDismiss()
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF16A34A)
                        )
                    ) {
                        Text("Start Using Free Questions")
                    }
                } else {
                    // Description
                    Text(
                        text = "Enter your email to claim your free questions!",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280),
                        textAlign = TextAlign.Center
                    )
                    
                    // Referral Code Display
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFF3F4F6)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "Referral Code",
                                fontSize = 12.sp,
                                color = Color(0xFF6B7280)
                            )
                            Text(
                                text = referralCode,
                                fontSize = 20.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF10B981),
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                            )
                        }
                    }
                    
                    // Benefits
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFFEF3C7)
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = "You'll get:",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF92400E)
                            )
                            Text(
                                text = "✓ 5 free questions to test AI models",
                                fontSize = 12.sp,
                                color = Color(0xFF92400E)
                            )
                            Text(
                                text = "✓ Your referrer will also get 5 questions",
                                fontSize = 12.sp,
                                color = Color(0xFF92400E)
                            )
                        }
                    }
                    
                    // Email Input
                    OutlinedTextField(
                        value = email,
                        onValueChange = { email = it },
                        label = { Text("Email Address") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = !isLoading,
                        isError = error != null,
                        supportingText = if (error != null) {
                            { Text(error!!, color = Color(0xFFDC2626)) }
                        } else null
                    )
                    
                    // Claim Button
                    Button(
                        onClick = {
                            if (email.isBlank()) {
                                error = "Please enter your email address"
                                return@Button
                            }
                            
                            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                                error = "Please enter a valid email address"
                                return@Button
                            }
                            
                            isLoading = true
                            error = null
                            
                            coroutineScope.launch {
                                val response = repository.useReferralCode(
                                    walletAddress = walletAddress,
                                    referralCode = referralCode,
                                    email = email
                                )
                                
                                isLoading = false
                                
                                if (response.isSuccessful) {
                                    val data = response.body()
                                    if (data?.success == true) {
                                        success = true
                                        receiverQuestions = data.receiver_questions
                                        referrerQuestions = data.referrer_questions
                                    } else {
                                        error = data?.detail ?: data?.error ?: "Failed to claim referral code"
                                    }
                                } else {
                                    error = "Failed to claim referral code. Please try again."
                                }
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(48.dp),
                        enabled = !isLoading,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF10B981)
                        )
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Claiming...")
                        } else {
                            Text("Claim 5 Free Questions")
                        }
                    }
                    
                    // Cancel Button
                    TextButton(
                        onClick = onDismiss,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Maybe Later", color = Color(0xFF6B7280))
                    }
                }
            }
        }
    }
}



