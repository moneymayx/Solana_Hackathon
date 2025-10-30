package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.BorderStroke
import kotlinx.coroutines.launch
import androidx.compose.ui.text.style.TextAlign

data class StakingPosition(
    val position_id: Int,
    val staked_amount: Double,
    val lock_period_days: Int,
    val tier_allocation: Int,
    val unlocks_at: String,
    val claimed_rewards: Double,
    val projected_monthly_earnings: Double,
    val share_of_tier: Double,
    val days_remaining: Int,
    val status: String,
    val is_unlocked: Boolean
)

data class TierData(
    val total_staked: Double,
    val staker_count: Int,
    val tier_allocation: Int
)

data class PlatformRevenue(
    val monthly: Double,
    val staking_pool_percentage: Int,
    val staking_pool_monthly: Double,
    val buyback_percentage: Int,
    val buyback_monthly: Double
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StakingScreen(
    onBackClick: () -> Unit
) {
    var stakeAmount by remember { mutableStateOf("") }
    var selectedPeriod by remember { mutableStateOf(90) }
    var loading by remember { mutableStateOf(true) }
    var positions by remember { mutableStateOf<List<StakingPosition>>(emptyList()) }
    var platformRevenue by remember { mutableStateOf<PlatformRevenue?>(null) }
    var tierStats by remember { mutableStateOf<Map<String, TierData>>(emptyMap()) }
    var walletConnected by remember { mutableStateOf(false) }
    var currentBalance by remember { mutableStateOf(5000000.0) } // Mock balance
    
    val scope = rememberCoroutineScope()
    
    // Mock data loading (in production, fetch from API)
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(1000)
        platformRevenue = PlatformRevenue(
            monthly = 50000.0,
            staking_pool_percentage = 10,
            staking_pool_monthly = 5000.0,
            buyback_percentage = 10,
            buyback_monthly = 5000.0
        )
        tierStats = mapOf(
            "30_DAYS" to TierData(total_staked = 100000.0, staker_count = 25, tier_allocation = 20),
            "60_DAYS" to TierData(total_staked = 250000.0, staker_count = 50, tier_allocation = 30),
            "90_DAYS" to TierData(total_staked = 500000.0, staker_count = 100, tier_allocation = 50)
        )
        loading = false
    }
    
    Scaffold(
        topBar = {
            WebStyleHeader(
                onScrollToHome = onBackClick,
                onScrollToBounties = onBackClick,
                onScrollToHowItWorks = onBackClick,
                onScrollToFAQs = onBackClick,
                onNavigateToStaking = {} // Already on staking page
            )
        }
    ) { paddingValues ->
        if (loading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Header
                Text(
                    text = "Stake & Earn",
                    style = MaterialTheme.typography.headlineLarge,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF0F172A)
                )
                Text(
                    text = "Lock tokens to earn from ${platformRevenue?.staking_pool_percentage ?: 10}% of platform revenue",
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF64748B)
                )
                
                // Revenue Model Explanation
                RevenueModelCard(platformRevenue)
                
                // Staking Form
                StakingFormCard(
                    stakeAmount = stakeAmount,
                    onAmountChange = { stakeAmount = it },
                    selectedPeriod = selectedPeriod,
                    onPeriodChange = { selectedPeriod = it },
                    currentBalance = currentBalance,
                    platformRevenue = platformRevenue,
                    tierStats = tierStats,
                    walletConnected = walletConnected,
                    onStake = {
                        scope.launch {
                            // TODO: Call staking API
                            // For now, show success message
                        }
                    }
                )
                
                // Active Positions
                if (positions.isNotEmpty()) {
                    ActivePositionsCard(
                        positions = positions,
                        onUnstake = { positionId ->
                            // TODO: Call unstake API
                        },
                        onClaimRewards = {
                            // TODO: Call claim API
                        }
                    )
                }
                
                // Tier Statistics
                TierStatisticsCard(tierStats)
            }
        }
    }
}

@Composable
fun RevenueModelCard(platformRevenue: PlatformRevenue?) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "📊 Revenue-Based Staking Model",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF0F172A)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${platformRevenue?.staking_pool_percentage ?: 10}% of Revenue",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF2563EB)
                    )
                    Text(
                        text = "Goes to stakers monthly",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF64748B),
                        fontSize = 11.sp
                    )
                </Column>
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "Tiered Distribution",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF2563EB)
                    )
                    Text(
                        text = "Longer locks = bigger share",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF64748B),
                        fontSize = 11.sp
                    )
                </Column>
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "No Fixed APY",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.SemiBold,
                        color = Color(0xFF2563EB)
                    )
                    Text(
                        text = "Based on actual revenue",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF64748B),
                        fontSize = 11.sp
                    )
                </Column>
            }
            
            // Warning
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFFFEF3C7),
                shape = RoundedCornerShape(8.dp)
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text("⚠️", fontSize = 16.sp)
                    Text(
                        text = "Important: Rewards are based on actual platform revenue. Earnings will vary month-to-month based on platform performance. This is not a fixed APY product.",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF92400E),
                        fontSize = 11.sp
                    )
                }
            }
            
            // Revenue Breakdown
            if (platformRevenue != null) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFF8FAFC),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "📊 Revenue Allocation Breakdown",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF0F172A),
                            fontSize = 13.sp
                        )
                        
                        RevenueRow("Platform Revenue (Monthly):", "$${String.format("%,.2f", platformRevenue.monthly)}", Color(0xFF0F172A))
                        Divider(color = Color(0xFFE2E8F0), thickness = 1.dp)
                        RevenueRow("Staking Pool (${platformRevenue.staking_pool_percentage}%):", "$${String.format("%,.2f", platformRevenue.staking_pool_monthly)}", Color(0xFF059669))
                        RevenueRow("Buyback & Burn (${platformRevenue.buyback_percentage}%):", "$${String.format("%,.2f", platformRevenue.buyback_monthly)}", Color(0xFFEA580C))
                    }
                }
            }
        }
    }
}

@Composable
fun RevenueRow(label: String, value: String, valueColor: Color) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = Color(0xFF64748B),
            fontSize = 11.sp
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.SemiBold,
            color = valueColor,
            fontSize = 11.sp
        )
    }
}

@Composable
fun StakingFormCard(
    stakeAmount: String,
    onAmountChange: (String) -> Unit,
    selectedPeriod: Int,
    onPeriodChange: (Int) -> Unit,
    currentBalance: Double,
    platformRevenue: PlatformRevenue?,
    tierStats: Map<String, TierData>,
    walletConnected: Boolean,
    onStake: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Create Staking Position",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF0F172A)
            )
            
            // Lock Period Selection
            Text(
                text = "Lock Period",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF0F172A)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf(
                    Triple(30, 20, "Flexible"),
                    Triple(60, 30, "Balanced"),
                    Triple(90, 50, "Best Rewards")
                ).forEach { (days, allocation, label) ->
                    val isSelected = selectedPeriod == days
                    Surface(
                        modifier = Modifier.weight(1f),
                        onClick = { onPeriodChange(days) },
                        shape = RoundedCornerShape(8.dp),
                        color = if (isSelected) Color(0xFFDCEFFF) else Color(0xFFF8FAFC),
                        border = androidx.compose.foundation.BorderStroke(
                            2.dp,
                            if (isSelected) Color(0xFF2563EB) else Color(0xFFE2E8F0)
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = "$days Days",
                                fontWeight = FontWeight.Bold,
                                color = if (isSelected) Color(0xFF2563EB) else Color(0xFF0F172A),
                                fontSize = 16.sp
                            )
                            Text(
                                text = "$allocation% of pool",
                                fontSize = 12.sp,
                                color = if (isSelected) Color(0xFF2563EB) else Color(0xFF64748B)
                            )
                            Text(
                                text = label,
                                fontSize = 10.sp,
                                color = Color(0xFF64748B)
                            )
                        }
                    }
                }
            }
            
            // Amount Input
            Text(
                text = "Amount to Stake",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF0F172A)
            )
            
            OutlinedTextField(
                value = stakeAmount,
                onValueChange = onAmountChange,
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Enter amount") },
                trailingIcon = { Text("\$100Bs", fontSize = 14.sp, color = Color(0xFF64748B)) },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFF2563EB),
                    unfocusedBorderColor = Color(0xFFCBD5E1)
                )
            )
            
            if (currentBalance > 0) {
                Text(
                    text = "Available: ${String.format("%,.0f", currentBalance)} tokens",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF64748B),
                    fontSize = 12.sp
                )
            }
            
            // Estimated Rewards Preview
            val amount = stakeAmount.toDoubleOrNull() ?: 0.0
            if (amount > 0 && platformRevenue != null) {
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFDCEFFF),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "📈 Estimated Monthly Rewards",
                            fontWeight = FontWeight.SemiBold,
                            color = Color(0xFF1E40AF),
                            fontSize = 13.sp
                        )
                        Text(
                            text = "Based on current platform revenue ($${String.format("%,.2f", platformRevenue.monthly)}/month):",
                            fontSize = 11.sp,
                            color = Color(0xFF475569)
                        )
                        
                        val estimatedRewards = calculateEstimatedEarnings(amount, selectedPeriod, platformRevenue, tierStats)
                        Text(
                            text = "~$${String.format("%,.2f", estimatedRewards)}/month",
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF0F172A)
                        )
                        Text(
                            text = "* Estimates assume current tier size and revenue. Actual rewards vary based on platform performance and tier participation.",
                            fontSize = 9.sp,
                            color = Color(0xFF64748B)
                        )
                    }
                }
            }
            
            // Stake Button
            Button(
                onClick = onStake,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                enabled = walletConnected && amount > 0,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFBBF24),
                    disabledContainerColor = Color(0xFFE5E7EB)
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = if (walletConnected) "Stake for $selectedPeriod Days" else "👛 Connect Wallet First",
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp,
                    color = if (walletConnected) Color.White else Color(0xFF9CA3AF)
                )
            }
        }
    }
}

@Composable
fun ActivePositionsCard(
    positions: List<StakingPosition>,
    onUnstake: (Int) -> Unit,
    onClaimRewards: () -> Unit
) {
    // Claim Rewards Section
    val totalClaimable = positions.filter { it.status == "active" }.sumOf { it.projected_monthly_earnings }
    
    if (totalClaimable > 0) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "💰 Claimable Rewards",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "From all active positions",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF64748B),
                        fontSize = 12.sp
                    )
                    Text(
                        text = "~$${String.format("%,.2f", totalClaimable)} USDC",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF059669)
                    )
                }
                Button(
                    onClick = onClaimRewards,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF059669))
                ) {
                    Text("🎁 Claim")
                }
            }
        }
    }
    
    // Positions List
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Your Staking Positions",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            positions.forEach { position ->
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFFF8FAFC),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text(
                                    text = "${String.format("%,.0f", position.staked_amount)} \$100Bs",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp
                                )
                                Text(
                                    text = "${position.lock_period_days}-day lock • ${position.tier_allocation}% tier",
                                    fontSize = 12.sp,
                                    color = Color(0xFF64748B)
                                )
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text(
                                    text = "$${String.format("%,.2f", position.projected_monthly_earnings)}/mo",
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF059669)
                                )
                                Text(
                                    text = "${String.format("%.2f", position.share_of_tier)}% of tier",
                                    fontSize = 11.sp,
                                    color = Color(0xFF64748B)
                                )
                            }
                        }
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("Claimed: $${String.format("%,.2f", position.claimed_rewards)}", fontSize = 12.sp)
                            Text("Unlocks: ${position.unlocks_at}", fontSize = 12.sp)
                            Text(
                                if (position.is_unlocked) "🔓 Unlocked" else "🔒 ${position.days_remaining} days",
                                fontSize = 12.sp,
                                color = if (position.is_unlocked) Color(0xFF059669) else Color(0xFF64748B)
                            )
                        }
                        
                        if (position.is_unlocked && position.status == "active") {
                            Button(
                                onClick = { onUnstake(position.position_id) },
                                modifier = Modifier.fillMaxWidth(),
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2563EB))
                            ) {
                                Text("Unstake Tokens")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TierStatisticsCard(tierStats: Map<String, TierData>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Platform Staking Tiers",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                tierStats.forEach { (tierName, tierData) ->
                    Surface(
                        modifier = Modifier.weight(1f),
                        color = Color(0xFFF8FAFC),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = tierName.replace("_", " "),
                                fontSize = 11.sp,
                                color = Color(0xFF64748B)
                            )
                            Text(
                                text = String.format("%,.0f", tierData.total_staked),
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                color = Color(0xFF0F172A)
                            )
                            Text(
                                text = "${tierData.staker_count} stakers • ${tierData.tier_allocation}%",
                                fontSize = 10.sp,
                                color = Color(0xFF64748B)
                            )
                        }
                    }
                }
            }
        }
    }
}

fun calculateEstimatedEarnings(
    amount: Double,
    periodDays: Int,
    platformRevenue: PlatformRevenue,
    tierStats: Map<String, TierData>
): Double {
    if (amount <= 0) return 0.0
    
    val tierAllocation = when (periodDays) {
        30 -> 0.20
        60 -> 0.30
        90 -> 0.50
        else -> 0.50
    }
    
    val tierKey = "${periodDays}_DAYS"
    val tierTotalStaked = tierStats[tierKey]?.total_staked ?: amount
    
    val tierPool = platformRevenue.staking_pool_monthly * tierAllocation
    val userShare = amount / (tierTotalStaked + amount)
    
    return tierPool * userShare
}
