package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.AttachMoney
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import kotlin.math.floor

/**
 * Payment Amount Selection Dialog
 * Matches web's PaymentAmountModal.tsx functionality
 */
@Composable
fun PaymentAmountSelectionDialog(
    currentQuestionCost: Double,
    onDismiss: () -> Unit,
    onSelectAmount: (Double) -> Unit,
    isProcessing: Boolean = false
) {
    val paymentAmounts = listOf(
        PaymentAmount(1.0, "STARTER"),
        PaymentAmount(10.0, "POPULAR"),
        PaymentAmount(20.0, "VALUE"),
        PaymentAmount(50.0, "POWER"),
        PaymentAmount(100.0, "PREMIUM"),
        PaymentAmount(1000.0, "WHALE")
    )

    Dialog(onDismissRequest = { if (!isProcessing) onDismiss() }) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .wrapContentHeight(),
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Choose Your Bounty Contribution",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f)
                    )
                    IconButton(onClick = { if (!isProcessing) onDismiss() }) {
                        Icon(Icons.Default.Close, contentDescription = "Close")
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Amount Grid
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    modifier = Modifier.heightIn(max = 400.dp)
                ) {
                    items(paymentAmounts) { paymentAmount ->
                        PaymentAmountCard(
                            amount = paymentAmount.amount,
                            badge = paymentAmount.badge,
                            currentQuestionCost = currentQuestionCost,
                            isProcessing = isProcessing,
                            onSelect = { onSelectAmount(paymentAmount.amount) }
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Info Section
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFDCEFFB),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "Info",
                            tint = Color(0xFF1E40AF),
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = "How it works:",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1E40AF)
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Each question costs $${"%.2f".format(currentQuestionCost)} (grows by 0.78% per entry). " +
                                      "Your payment goes toward the bounty prize pool (60%), operational costs (20%), " +
                                      "token buyback (10%), and staking rewards (10%).",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color(0xFF1E40AF),
                                lineHeight = 18.sp
                            )
                            if (currentQuestionCost > 1.0) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = "💡 Tip: Amounts below $${"%.2f".format(currentQuestionCost)} are insufficient for a question.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = Color(0xFF1E40AF),
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Cancel Button
                OutlinedButton(
                    onClick = { if (!isProcessing) onDismiss() },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isProcessing
                ) {
                    Text("Cancel")
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PaymentAmountCard(
    amount: Double,
    badge: String,
    currentQuestionCost: Double,
    isProcessing: Boolean,
    onSelect: () -> Unit
) {
    val questions = floor(amount / currentQuestionCost).toInt()
    val credit = amount % currentQuestionCost
    val isInsufficient = amount < currentQuestionCost
    
    val (containerColor, contentColor, badgeColor) = when {
        isInsufficient -> Triple(
            Color(0xFFFEE2E2),
            Color(0xFFDC2626),
            Color(0xFFDC2626)
        )
        badge == "POPULAR" -> Triple(
            Color(0xFFFEF3C7),
            Color(0xFFB45309),
            Color(0xFFEAB308)
        )
        badge == "WHALE" -> Triple(
            Color(0xFFF3E8FF),
            Color(0xFF7C3AED),
            Color(0xFF9333EA)
        )
        else -> Triple(
            Color(0xFFF3F4F6),
            Color(0xFF374151),
            Color(0xFF6B7280)
        )
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(120.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = containerColor),
        onClick = {
            if (!isInsufficient && !isProcessing) {
                onSelect()
            }
        },
        enabled = !isInsufficient && !isProcessing
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp)
        ) {
            // Badge
            if (!isInsufficient || isInsufficient) {
                Surface(
                    modifier = Modifier
                        .align(Alignment.TopEnd),
                    shape = RoundedCornerShape(4.dp),
                    color = if (isInsufficient) Color(0xFFDC2626) else badgeColor
                ) {
                    Text(
                        text = if (isInsufficient) "TOO LOW" else badge,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 9.sp
                    )
                }
            }

            // Content
            Column(
                modifier = Modifier.align(Alignment.CenterStart),
                verticalArrangement = Arrangement.Center
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.AttachMoney,
                        contentDescription = null,
                        tint = contentColor,
                        modifier = Modifier.size(24.dp)
                    )
                    Text(
                        text = if (amount >= 1000) "${(amount / 1000).toInt()}K" else amount.toInt().toString(),
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = contentColor
                    )
                }
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = when {
                        isInsufficient -> "Insufficient (need $${"%.2f".format(currentQuestionCost)})"
                        credit > 0 -> "$questions question${if (questions != 1) "s" else ""} + $${"%.2f".format(credit)} credit"
                        else -> "$questions question${if (questions != 1) "s" else ""}"
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = contentColor,
                    fontWeight = if (isInsufficient) FontWeight.Bold else FontWeight.Normal,
                    lineHeight = 14.sp
                )
            }
        }
    }
}

private data class PaymentAmount(
    val amount: Double,
    val badge: String
)

