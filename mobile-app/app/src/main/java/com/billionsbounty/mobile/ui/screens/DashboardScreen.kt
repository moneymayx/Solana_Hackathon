package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.platform.LocalUriHandler
import com.billionsbounty.mobile.ui.viewmodel.BountyViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import androidx.compose.ui.text.font.FontFamily

// Data classes for API responses
data class DashboardOverview(
    val lottery_status: LotteryStatus,
    val platform_stats: PlatformStats,
    val recent_activity: RecentActivity,
    val system_health: SystemHealth,
    val last_updated: String
)

data class LotteryStatus(
    val current_jackpot_usdc: Double,
    val total_entries: Int,
    val is_active: Boolean,
    val fund_verified: Boolean
)

data class PlatformStats(
    val total_users: Int,
    val total_questions: Int,
    val total_attempts: Int,
    val total_successes: Int,
    val success_rate: Double
)

data class RecentActivity(
    val new_users_24h: Int,
    val questions_24h: Int,
    val attempts_24h: Int
)

data class SystemHealth(
    val ai_agent_active: Boolean,
    val smart_contract_connected: Boolean,
    val database_connected: Boolean,
    val rate_limiter_active: Boolean,
    val sybil_detection_active: Boolean
)

data class FundVerification(
    val lottery_funds: LotteryFunds,
    val treasury_funds: TreasuryFunds,
    val verification_links: VerificationLinks,
    val last_updated: String
)

data class LotteryFunds(
    val current_jackpot_usdc: Double,
    val jackpot_balance_usdc: Double,
    val fund_verified: Boolean,
    val lottery_pda: String,
    val program_id: String
)

data class TreasuryFunds(
    val balance_sol: Double,
    val balance_usd: Double
)

data class VerificationLinks(
    val solana_explorer: String,
    val program_id: String
)

data class SecurityStatus(
    val rate_limiting: RateLimiting,
    val sybil_detection: SybilDetection,
    val ai_security: AISecurity,
    val overall_security_score: String,
    val last_updated: String
)

data class RateLimiting(
    val active: Boolean,
    val requests_per_minute: Int,
    val requests_per_hour: Int,
    val cooldown_seconds: Int
)

data class SybilDetection(
    val active: Boolean,
    val detection_methods: List<String>,
    val blacklisted_phrases: String
)

data class AISecurity(
    val personality_system: String,
    val manipulation_detection: String,
    val blacklisting_system: String,
    val success_rate_target: String,
    val learning_enabled: Boolean
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: BountyViewModel,
    onBackClick: () -> Unit
) {
    var selectedTab by remember { mutableStateOf(0) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    
    // Mock data for now - In production, fetch from API
    var overviewData by remember { mutableStateOf<DashboardOverview?>(null) }
    var fundData by remember { mutableStateOf<FundVerification?>(null) }
    var securityData by remember { mutableStateOf<SecurityStatus?>(null) }
    
    val scope = rememberCoroutineScope()
    
    // Fetch dashboard data
    LaunchedEffect(Unit) {
        scope.launch {
            try {
                loading = true
                error = null
                
                // Simulate API calls - In production, call actual backend
                delay(1000)
                
                // Mock data
                overviewData = DashboardOverview(
                    lottery_status = LotteryStatus(
                        current_jackpot_usdc = 10500.0,
                        total_entries = 1234,
                        is_active = true,
                        fund_verified = true
                    ),
                    platform_stats = PlatformStats(
                        total_users = 10234,
                        total_questions = 45000,
                        total_attempts = 45678,
                        total_successes = 45,
                        success_rate = 0.098
                    ),
                    recent_activity = RecentActivity(
                        new_users_24h = 123,
                        questions_24h = 567,
                        attempts_24h = 890
                    ),
                    system_health = SystemHealth(
                        ai_agent_active = true,
                        smart_contract_connected = true,
                        database_connected = true,
                        rate_limiter_active = true,
                        sybil_detection_active = true
                    ),
                    last_updated = "2024-10-30T12:00:00Z"
                )
                
                fundData = FundVerification(
                    lottery_funds = LotteryFunds(
                        current_jackpot_usdc = 10500.0,
                        jackpot_balance_usdc = 10500.0,
                        fund_verified = true,
                        lottery_pda = "BountyLottery111111111111111111111111111",
                        program_id = "Program111111111111111111111111111111111"
                    ),
                    treasury_funds = TreasuryFunds(
                        balance_sol = 45.5678,
                        balance_usd = 6834.50
                    ),
                    verification_links = VerificationLinks(
                        solana_explorer = "https://explorer.solana.com/address/BountyLottery111111111111111111111111111?cluster=devnet",
                        program_id = "https://explorer.solana.com/address/Program111111111111111111111111111111111?cluster=devnet"
                    ),
                    last_updated = "2024-10-30T12:00:00Z"
                )
                
                securityData = SecurityStatus(
                    rate_limiting = RateLimiting(
                        active = true,
                        requests_per_minute = 60,
                        requests_per_hour = 100,
                        cooldown_seconds = 300
                    ),
                    sybil_detection = SybilDetection(
                        active = true,
                        detection_methods = listOf(
                            "Wallet Analysis",
                            "IP Tracking",
                            "Behavior Patterns",
                            "Device Fingerprinting"
                        ),
                        blacklisted_phrases = "200+ phrases detected and blocked"
                    ),
                    ai_security = AISecurity(
                        personality_system = "Multi-personality resistant guard",
                        manipulation_detection = "Real-time pattern analysis",
                        blacklisting_system = "Dynamic phrase detection",
                        success_rate_target = "< 0.1%",
                        learning_enabled = true
                    ),
                    overall_security_score = "High",
                    last_updated = "2024-10-30T12:00:00Z"
                )
                
                loading = false
            } catch (e: Exception) {
                error = "Failed to load dashboard data"
                loading = false
            }
        }
    }
    
    Scaffold(
        topBar = {
            WebStyleHeader(
                onScrollToHome = onBackClick,
                onScrollToBounties = onBackClick,
                onScrollToHowItWorks = onBackClick,
                onScrollToFAQs = onBackClick,
                onNavigateToStaking = {}
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
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Loading dashboard...", color = Color(0xFF64748B))
                }
            }
        } else if (error != null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("⚠️", fontSize = 48.sp)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        "Dashboard Error",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Text(error!!, color = Color(0xFF64748B), textAlign = TextAlign.Center)
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { /* Retry */ }) {
                        Text("Retry")
                    }
                }
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                // Header
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFF1F2937),
                    shadowElevation = 4.dp
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Public Dashboard",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                        Text(
                            text = "Real-time system status and fund verification",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFFD1D5DB)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Last updated: ${overviewData?.last_updated?.take(19) ?: "Unknown"}",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFF9CA3AF),
                            fontFamily = FontFamily.Monospace
                        )
                    }
                }
                
                // Tab Row
                TabRow(
                    selectedTabIndex = selectedTab,
                    containerColor = Color(0xFF1F2937),
                    contentColor = Color.White
                ) {
                    Tab(
                        selected = selectedTab == 0,
                        onClick = { selectedTab = 0 },
                        text = { 
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("📊 ", fontSize = 16.sp)
                                Text("Overview") 
                            }
                        }
                    )
                    Tab(
                        selected = selectedTab == 1,
                        onClick = { selectedTab = 1 },
                        text = { 
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("💰 ", fontSize = 16.sp)
                                Text("Funds") 
                            }
                        }
                    )
                    Tab(
                        selected = selectedTab == 2,
                        onClick = { selectedTab = 2 },
                        text = { 
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("🔒 ", fontSize = 16.sp)
                                Text("Security") 
                            }
                        }
                    )
                }
                
                // Tab Content
                when (selectedTab) {
                    0 -> OverviewTab(overviewData)
                    1 -> FundsTab(fundData)
                    2 -> SecurityTab(securityData)
                }
            }
        }
    }
}

@Composable
fun OverviewTab(data: DashboardOverview?) {
    if (data == null) return
    
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Key Metrics
        item {
            Text(
                "Key Metrics",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                MetricCard(
                    title = "Current Jackpot",
                    value = "$${String.format("%,.2f", data.lottery_status.current_jackpot_usdc)}",
                    icon = "💰",
                    subtitle = if (data.lottery_status.fund_verified) "Verified" else "Unverified",
                    subtitleColor = if (data.lottery_status.fund_verified) Color(0xFF10B981) else Color(0xFFEF4444),
                    modifier = Modifier.weight(1f)
                )
                MetricCard(
                    title = "Total Users",
                    value = String.format("%,d", data.platform_stats.total_users),
                    icon = "👥",
                    subtitle = "+${data.recent_activity.new_users_24h} today",
                    subtitleColor = Color(0xFF10B981),
                    modifier = Modifier.weight(1f)
                )
            }
        }
        
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                MetricCard(
                    title = "Attempts",
                    value = String.format("%,d", data.platform_stats.total_attempts),
                    icon = "🔬",
                    subtitle = "+${data.recent_activity.attempts_24h} today",
                    subtitleColor = Color(0xFF3B82F6),
                    modifier = Modifier.weight(1f)
                )
                MetricCard(
                    title = "Success Rate",
                    value = String.format("%.3f%%", data.platform_stats.success_rate),
                    icon = "🎯",
                    subtitle = "${data.platform_stats.total_successes} successes",
                    subtitleColor = Color(0xFFA855F7),
                    modifier = Modifier.weight(1f)
                )
            }
        }
        
        // System Health
        item {
            Text(
                "System Health",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }
        
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    SystemHealthItem("AI Agent", data.system_health.ai_agent_active)
                    SystemHealthItem("Smart Contract", data.system_health.smart_contract_connected)
                    SystemHealthItem("Database", data.system_health.database_connected)
                    SystemHealthItem("Rate Limiter", data.system_health.rate_limiter_active)
                    SystemHealthItem("Sybil Detection", data.system_health.sybil_detection_active)
                }
            }
        }
    }
}

@Composable
fun FundsTab(data: FundVerification?) {
    if (data == null) return
    
    val uriHandler = LocalUriHandler.current
    
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                "Fund Verification",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
        }
        
        // Lottery Funds
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Lottery Funds (USDC)",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    InfoRow("Current Jackpot", "$${String.format("%,.2f", data.lottery_funds.current_jackpot_usdc)}")
                    InfoRow("Actual Balance", "$${String.format("%,.2f", data.lottery_funds.jackpot_balance_usdc)}")
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Verification:", fontSize = 14.sp, color = Color(0xFF64748B))
                        Text(
                            if (data.lottery_funds.fund_verified) "✅ Verified" else "❌ Unverified",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = if (data.lottery_funds.fund_verified) Color(0xFF10B981) else Color(0xFFEF4444)
                        )
                    }
                }
            }
        }
        
        // Treasury Funds
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Treasury Funds (SOL)",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    InfoRow("SOL Balance", "${String.format("%.4f", data.treasury_funds.balance_sol)} SOL")
                    InfoRow("USD Value", "$${String.format("%,.2f", data.treasury_funds.balance_usd)}")
                }
            }
        }
        
        // Verification Links
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "On-Chain Verification",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    Text(
                        "Lottery PDA Address:",
                        fontSize = 12.sp,
                        color = Color(0xFF64748B)
                    )
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        color = Color(0xFFF1F5F9),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            data.lottery_funds.lottery_pda,
                            modifier = Modifier.padding(12.dp),
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                    
                    Button(
                        onClick = { uriHandler.openUri(data.verification_links.solana_explorer) },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3B82F6))
                    ) {
                        Text("🔗 View on Solana Explorer")
                    }
                }
            }
        }
    }
}

@Composable
fun SecurityTab(data: SecurityStatus?) {
    if (data == null) return
    
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFDCFCE7)),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            "Security Status",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            "All systems operational",
                            fontSize = 12.sp,
                            color = Color(0xFF059669)
                        )
                    }
                    Surface(
                        color = Color(0xFF10B981),
                        shape = RoundedCornerShape(20.dp)
                    ) {
                        Text(
                            data.overall_security_score,
                            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
        
        // Rate Limiting
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Rate Limiting",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                            Text("${data.rate_limiting.requests_per_minute}", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color(0xFF3B82F6))
                            Text("Req/Min", fontSize = 11.sp, color = Color(0xFF64748B))
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                            Text("${data.rate_limiting.requests_per_hour}", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color(0xFF3B82F6))
                            Text("Req/Hour", fontSize = 11.sp, color = Color(0xFF64748B))
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                            Text("${data.rate_limiting.cooldown_seconds}s", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Color(0xFF3B82F6))
                            Text("Cooldown", fontSize = 11.sp, color = Color(0xFF64748B))
                        }
                    }
                }
            }
        }
        
        // Sybil Detection
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Sybil Detection",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    data.sybil_detection.detection_methods.forEach { method ->
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("✓", color = Color(0xFF10B981), modifier = Modifier.width(24.dp))
                            Text(method, fontSize = 13.sp)
                        }
                    }
                    
                    Text(
                        data.sybil_detection.blacklisted_phrases,
                        fontSize = 11.sp,
                        color = Color(0xFF64748B)
                    )
                }
            }
        }
        
        // AI Security
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "AI Security System",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold
                    )
                    
                    InfoRow("Personality System", data.ai_security.personality_system)
                    InfoRow("Manipulation Detection", data.ai_security.manipulation_detection)
                    InfoRow("Blacklisting System", data.ai_security.blacklisting_system)
                    InfoRow("Success Rate Target", data.ai_security.success_rate_target)
                }
            }
        }
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    icon: String,
    subtitle: String,
    subtitleColor: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(title, fontSize = 12.sp, color = Color(0xFF64748B))
                    Text(value, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0F172A))
                }
                Text(icon, fontSize = 24.sp)
            }
            Text(subtitle, fontSize = 11.sp, color = subtitleColor, fontWeight = FontWeight.Medium)
        }
    }
}

@Composable
fun SystemHealthItem(name: String, status: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                if (status) "✅" else "❌",
                fontSize = 20.sp,
                modifier = Modifier.width(32.dp)
            )
            Text(name, fontSize = 14.sp, fontWeight = FontWeight.Medium)
        }
        Text(
            if (status) "Active" else "Inactive",
            fontSize = 13.sp,
            color = if (status) Color(0xFF10B981) else Color(0xFFEF4444),
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, fontSize = 14.sp, color = Color(0xFF64748B))
        Text(value, fontSize = 14.sp, fontWeight = FontWeight.Medium, fontFamily = FontFamily.Monospace)
    }
}
