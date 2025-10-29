package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
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
import androidx.hilt.navigation.compose.hiltViewModel
import com.billionsbounty.mobile.data.api.*
import com.billionsbounty.mobile.ui.viewmodel.BountyDetailViewModel
import com.billionsbounty.mobile.ui.viewmodel.ChatMessage
import com.billionsbounty.mobile.wallet.WalletAdapter
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import kotlin.math.pow

/**
 * Helper function to get starting bounty based on difficulty
 */
private fun getStartingBounty(difficulty: String): Int {
    return when (difficulty.lowercase()) {
        "easy" -> 500
        "medium" -> 2500
        "hard" -> 5000
        "expert" -> 10000
        else -> 500
    }
}

/**
 * Helper function to get starting question cost based on difficulty
 */
private fun getStartingQuestionCost(difficulty: String): Double {
    return when (difficulty.lowercase()) {
        "easy" -> 0.50
        "medium" -> 2.50
        "hard" -> 5.00
        "expert" -> 10.00
        else -> 0.50
    }
}

/**
 * Helper function to calculate current question cost
 */
private fun getCurrentQuestionCost(startingCost: Double, totalEntries: Int): Double {
    return startingCost * 1.0078.pow(totalEntries)
}

/**
 * Comprehensive Bounty Detail Screen matching web functionality
 * Includes: Header, Stats, Chat Interface, Teams, Winning Prompts, Payment/Referral Flows
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BountyDetailScreen(
    bountyId: Int,
    startInWatchMode: Boolean = false,
    onBackClick: () -> Unit,
    onNavigateToWallet: () -> Unit = {},
    viewModel: BountyDetailViewModel = hiltViewModel()
) {
    // Collect state from ViewModel
    val bounty by viewModel.bounty.collectAsState()
    val bountyStatus by viewModel.bountyStatus.collectAsState()
    val userEligibility by viewModel.userEligibility.collectAsState()
    val userTeam by viewModel.userTeam.collectAsState()
    val winningPrompts by viewModel.winningPrompts.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()
    val isWalletConnected by viewModel.isWalletConnected.collectAsState()
    val showGlobalChat by viewModel.showGlobalChat.collectAsState()
    
    var showPaymentFlow by remember { mutableStateOf(false) }
    var showReferralFlow by remember { mutableStateOf(false) }
    var showNftFlow by remember { mutableStateOf(false) }
    var showTeamDialog by remember { mutableStateOf(false) }
    var showCreateTeamDialog by remember { mutableStateOf(false) }
    var showWalletDialog by remember { mutableStateOf(false) }
    var showRulesDialog by remember { mutableStateOf(false) }
    
    // For smooth scrolling to chat section
    val listState = rememberLazyListState()
    val coroutineScope = rememberCoroutineScope()
    
    // Chat section index (adjust based on actual position in LazyColumn)
    // Header(0) + Wallet Banner(1) + Free Questions(2) + Stats(3) + Toggle(4) + Chat(5)
    val chatSectionIndex = 5
    
    // Load initial data
    LaunchedEffect(bountyId) {
        viewModel.loadBountyDetails(bountyId)
    }
    
    // Handle startInWatchMode - enable global chat and scroll to it
    LaunchedEffect(startInWatchMode) {
        if (startInWatchMode && !showGlobalChat) {
            viewModel.toggleChatMode() // Enable watch mode
            // Wait a bit for UI to render, then scroll
            kotlinx.coroutines.delay(300)
            listState.animateScrollToItem(chatSectionIndex)
        }
    }
    
    if (isLoading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
        return
    }
    
    LazyColumn(
        state = listState,
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
    ) {
        // Header Section
        item {
            BountyHeader(
                bounty = bounty,
                onBackClick = onBackClick,
                isWalletConnected = isWalletConnected,
                onWalletClick = { showWalletDialog = true }
            )
        }
        
        // Wallet Connection Banner
        if (!isWalletConnected) {
            item {
                WalletConnectionBanner(
                    onConnectClick = { showWalletDialog = true }
                )
            }
        }
        
        // Free Questions Counter (if eligible)
        if (userEligibility?.eligible == true && userEligibility?.questions_remaining ?: 0 > 0) {
            item {
                FreeQuestionsCounter(
                    remaining = userEligibility?.questions_remaining ?: 0,
                    used = userEligibility?.questions_used ?: 0
                )
            }
        }
        
        // Bounty Stats Section
        item {
            BountyStatsSection(
                bounty = bounty,
                bountyStatus = bountyStatus
            )
        }
        
        // Beat the Bot / Watch Toggle
        item {
            ActionToggleSection(
                showGlobalChat = showGlobalChat,
                onToggle = { 
                    viewModel.toggleChatMode()
                    // Scroll to chat section when switching to Watch mode
                    coroutineScope.launch {
                        listState.animateScrollToItem(chatSectionIndex)
                    }
                },
                onViewRules = { showRulesDialog = true }
            )
        }
        
        // Chat Interface Section
        item {
            ChatInterfaceSection(
                bountyId = bountyId,
                bountyName = bounty?.name ?: "",
                bounty = bounty,
                bountyStatus = bountyStatus,
                isWatching = showGlobalChat,
                isWalletConnected = isWalletConnected,
                userEligibility = userEligibility,
                viewModel = viewModel,
                onShowPayment = { showPaymentFlow = true },
                onShowReferral = { showReferralFlow = true },
                onShowNft = { showNftFlow = true }
            )
        }
        
        // Team Collaboration Section
        item {
            TeamCollaborationSection(
                userTeam = userTeam,
                onCreateTeam = { showCreateTeamDialog = true },
                onJoinTeam = { 
                    viewModel.loadAllTeams()
                    showTeamDialog = true 
                }
            )
        }
        
        // Winning Prompts Section
        item {
            WinningPromptsSection(
                prompts = winningPrompts
            )
        }
    }
    
    // Payment Flow Dialog
    if (showPaymentFlow) {
        PaymentFlowDialog(
            bountyId = bountyId,
            walletAdapter = viewModel.getWalletAdapter(),
            onDismiss = { showPaymentFlow = false },
            onPaymentSuccess = { 
                showPaymentFlow = false
                viewModel.loadUserEligibility()
            }
        )
    }
    
    // NFT Verification Dialog
    if (showNftFlow) {
        NftVerificationDialog(
            walletAdapter = viewModel.getWalletAdapter(),
            nftRepository = viewModel.getNftRepository(),
            onDismiss = { showNftFlow = false },
            onVerificationSuccess = { 
                showNftFlow = false
                viewModel.loadUserEligibility()
            }
        )
    }
    
    // Referral Flow Dialog
    if (showReferralFlow) {
        ReferralFlowDialog(
            onDismiss = { showReferralFlow = false },
            onReferralSuccess = {
                showReferralFlow = false
                viewModel.loadUserEligibility()
            }
        )
    }
    
    // Team Browse Dialog
    if (showTeamDialog) {
        val allTeams by viewModel.allTeams.collectAsState()
        TeamBrowseDialog(
            teams = allTeams,
            onDismiss = { showTeamDialog = false },
            onJoinTeam = { teamId ->
                viewModel.joinTeam(teamId) {
                    showTeamDialog = false
                }
            }
        )
    }
    
    // Create Team Dialog
    if (showCreateTeamDialog) {
        BountyCreateTeamDialog(
            onDismiss = { showCreateTeamDialog = false },
            onCreateTeam = { teamName ->
                viewModel.createTeam(teamName) {
                    showCreateTeamDialog = false
                }
            }
        )
    }
    
    // Wallet Connection Dialog
    if (showWalletDialog) {
        WalletConnectionDialog(
            walletAdapter = viewModel.getWalletAdapter(),
            onDismiss = { showWalletDialog = false },
            onConnected = { address ->
                // Wallet connected successfully
                viewModel.connectWallet(
                    walletAddress = address,
                    publicKey = address // In real usage, these might be different
                )
            }
        )
    }
    
    // Rules Dialog
    if (showRulesDialog) {
        RulesDialog(
            onDismiss = { showRulesDialog = false }
        )
    }
}

/**
 * Bounty Header with back button, name, description, prize pool, and wallet button
 */
@Composable
fun BountyHeader(
    bounty: Bounty?,
    onBackClick: () -> Unit,
    isWalletConnected: Boolean = false,
    onWalletClick: () -> Unit = {}
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF1E293B), // slate-800
                        Color(0xFF0F172A)  // slate-900
                    )
                )
            )
            .padding(16.dp)
    ) {
        Column {
            // Back button and title row
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                IconButton(
                    onClick = onBackClick,
                    modifier = Modifier.size(40.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back",
                        tint = Color.White
                    )
                }
                
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = bounty?.name ?: "Loading...",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                    Text(
                        text = bounty?.description ?: "",
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color(0xFFCBD5E1) // slate-300
                    )
                }
                
                // Prize pool
                Column(
                    horizontalAlignment = Alignment.End
                ) {
                    Text(
                        text = "$${bounty?.current_pool?.toInt()?.toString()?.replace(Regex("(\\d)(?=(\\d{3})+$)"), "$1,") ?: "0"}",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFBBF24) // yellow-400
                    )
                    Text(
                        text = "Prize Pool",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFFCBD5E1)
                    )
                }
                
                // Wallet Button
                IconButton(
                    onClick = onWalletClick,
                    modifier = Modifier.size(40.dp)
                ) {
                    Icon(
                        imageVector = if (isWalletConnected) Icons.Default.AccountBalanceWallet else Icons.Default.AccountBalanceWallet,
                        contentDescription = if (isWalletConnected) "Wallet Connected" else "Connect Wallet",
                        tint = if (isWalletConnected) Color(0xFF10B981) else Color.White // green if connected, white if not
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            // Difficulty badge
            bounty?.let {
                DifficultyBadge(difficulty = it.difficulty_level)
            }
        }
    }
}

/**
 * Difficulty badge with color coding
 */
@Composable
fun DifficultyBadge(difficulty: String) {
    val (bgColor, textColor, icon) = when (difficulty.lowercase()) {
        "expert" -> Triple(Color(0xFFFEE2E2), Color(0xFFDC2626), Icons.Default.Star) // red
        "hard" -> Triple(Color(0xFFFFEDD5), Color(0xFFEA580C), Icons.Default.Warning) // orange
        "medium" -> Triple(Color(0xFFDBEAFE), Color(0xFF2563EB), Icons.Default.Info) // blue
        "easy" -> Triple(Color(0xFFD1FAE5), Color(0xFF059669), Icons.Default.CheckCircle) // green
        else -> Triple(Color(0xFFF1F5F9), Color(0xFF64748B), Icons.Default.Info)
    }
    
    Surface(
        shape = RoundedCornerShape(20.dp),
        color = bgColor,
        border = androidx.compose.foundation.BorderStroke(1.dp, textColor.copy(alpha = 0.3f))
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = textColor,
                modifier = Modifier.size(16.dp)
            )
            Text(
                text = difficulty.capitalize(),
                color = textColor,
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

/**
 * Wallet connection banner
 */
@Composable
fun WalletConnectionBanner(onConnectClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFFEF3C7) // yellow-100
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    imageVector = Icons.Default.AccountBalanceWallet,
                    contentDescription = null,
                    tint = Color(0xFFD97706), // yellow-600
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = "Connect wallet to participate",
                    fontSize = 14.sp,
                    color = Color(0xFF92400E), // yellow-800
                    fontWeight = FontWeight.Medium
                )
            }
            
            Button(
                onClick = onConnectClick,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFD97706)
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text("Connect", fontSize = 13.sp)
            }
        }
    }
}

/**
 * Free questions counter
 */
@Composable
fun FreeQuestionsCounter(
    remaining: Int,
    used: Int
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFDCFCE7) // green-100
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = CircleShape,
                color = Color(0xFF16A34A), // green-600
                modifier = Modifier.size(48.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Default.CardGiftcard,
                        contentDescription = null,
                        tint = Color.White,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = "Free Research Attempts",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF15803D) // green-700
                )
                Text(
                    text = "$remaining remaining • $used used",
                    fontSize = 12.sp,
                    color = Color(0xFF166534) // green-800
                )
            }
        }
    }
}

/**
 * Bounty stats section
 */
@Composable
fun BountyStatsSection(
    bounty: Bounty?,
    bountyStatus: BountyStatusResponse?
) {
    val difficulty = bounty?.difficulty_level ?: "easy"
    val totalEntries = bounty?.total_entries ?: 0
    val startingBounty = getStartingBounty(difficulty)
    val startingQuestionCost = getStartingQuestionCost(difficulty)
    val currentQuestionCost = getCurrentQuestionCost(startingQuestionCost, totalEntries)
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Bounty Stats",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF111827)
            )
            
            // Total Entries (first)
            StatRow(label = "Total Entries", value = "$totalEntries")
            
            // Starting Bounty (second)
            StatRow(label = "Starting Bounty", value = "$$startingBounty")
            
            // Starting Question Cost (third)
            StatRow(label = "Starting Question Cost", value = "$${String.format("%.2f", startingQuestionCost)}")
            
            // Current Bounty
            StatRow(
                label = "Current Bounty",
                value = "$${bounty?.current_pool?.toInt() ?: 0}",
                valueColor = Color(0xFF059669),
                isBold = true
            )
            
            // Current Question Cost
            StatRow(
                label = "Current Question Cost",
                value = "$${String.format("%.2f", currentQuestionCost)}",
                valueColor = Color(0xFF059669),
                isBold = true
            )
            
            // Status
            StatRow(
                label = "Status",
                value = if (bounty?.is_active == true) "Active" else "Inactive",
                valueColor = if (bounty?.is_active == true) Color(0xFF059669) else Color(0xFF6B7280),
                showBadge = true
            )
        }
    }
}

@Composable
fun StatRow(
    label: String,
    value: String,
    valueColor: Color = Color(0xFF111827),
    isBold: Boolean = false,
    showBadge: Boolean = false
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            fontSize = 14.sp,
            color = Color(0xFF6B7280)
        )
        
        if (showBadge) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = valueColor.copy(alpha = 0.1f)
            ) {
                Text(
                    text = value,
                    fontSize = 12.sp,
                    color = valueColor,
                    fontWeight = if (isBold) FontWeight.Bold else FontWeight.Normal,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        } else {
            Text(
                text = value,
                fontSize = 14.sp,
                color = valueColor,
                fontWeight = if (isBold) FontWeight.Bold else FontWeight.Normal
            )
        }
    }
}

/**
 * Action toggle section (Beat the Bot / Watch)
 */
@Composable
fun ActionToggleSection(
    showGlobalChat: Boolean,
    onToggle: () -> Unit,
    onViewRules: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Actions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF111827)
            )
            
            Button(
                onClick = onToggle,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (!showGlobalChat) 
                        Color(0xFFF59E0B) // yellow-500
                    else 
                        Color(0xFFF3F4F6) // gray-100
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = if (showGlobalChat) "Beat the Bot" else "Watch the Madness",
                    fontWeight = FontWeight.Medium,
                    color = if (!showGlobalChat) Color.White else Color(0xFF374151)
                )
            }
            
            OutlinedButton(
                onClick = onViewRules,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFD1D5DB)),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = "View Rules",
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF374151)
                )
            }
        }
    }
}

/**
 * Chat interface with messages and input
 */
@Composable
fun ChatInterfaceSection(
    bountyId: Int,
    bountyName: String,
    bounty: Bounty?,
    bountyStatus: BountyStatusResponse?,
    isWatching: Boolean,
    isWalletConnected: Boolean,
    userEligibility: UserEligibilityResponse?,
    viewModel: BountyDetailViewModel,
    onShowPayment: () -> Unit,
    onShowReferral: () -> Unit,
    onShowNft: () -> Unit
) {
    val messages by viewModel.messages.collectAsState()
    var messageText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()
    
    // Auto-scroll to bottom when new messages arrive
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }
    
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .height(500.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Header
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = Color(0xFFF8FAFC),
                shadowElevation = 1.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = if (isWatching) "Watch Mode" else "Beat the Bot",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                    Surface(
                        shape = RoundedCornerShape(12.dp),
                        color = if (isWatching) Color(0xFFDBEAFE) else Color(0xFFFEF3C7)
                    ) {
                        Text(
                            text = if (isWatching) "Watching" else "Active",
                            fontSize = 12.sp,
                            color = if (isWatching) Color(0xFF1E40AF) else Color(0xFF92400E),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
            }
            
            // Messages
            LazyColumn(
                state = listState,
                modifier = Modifier.weight(1f),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                if (messages.isEmpty()) {
                    item {
                        Box(
                            modifier = Modifier.fillMaxWidth(),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = if (isWatching) 
                                    "Watching global chat..." 
                                else 
                                    "Start chatting with the AI to attempt the jailbreak!",
                                color = Color(0xFF64748B),
                                style = MaterialTheme.typography.bodyMedium,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
                
                items(messages) { message ->
                    ChatMessageBubble(message = message)
                }
            }
            
            // Input section (only if not watching)
            if (!isWatching) {
                Divider(color = Color(0xFFE2E8F0))
                
                if (!isWalletConnected) {
                    // Show wallet connection prompt
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Connect wallet to participate",
                            color = Color(0xFF6B7280),
                            fontSize = 14.sp
                        )
                    }
                } else if (userEligibility?.eligible == false) {
                    // Show payment/referral options
                    // Calculate current question cost
                    val difficulty = bounty?.difficulty_level ?: "easy"
                    val totalEntries = bounty?.total_entries ?: 0
                    val startingCost = getStartingQuestionCost(difficulty)
                    val currentCost = getCurrentQuestionCost(startingCost, totalEntries)
                    
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        // Payment button
                        Button(
                            onClick = onShowPayment,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF8B5CF6)
                            )
                        ) {
                            Text("Pay $${String.format("%.2f", currentCost)}", fontSize = 14.sp)
                        }
                        
                        // NFT & Referral buttons
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Button(
                                onClick = onShowNft,
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color(0xFF7C3AED)
                                )
                            ) {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text("Verify NFT", fontSize = 12.sp)
                                    Text("5 Free Qs", fontSize = 10.sp)
                                }
                            }
                            Button(
                                onClick = onShowReferral,
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = Color(0xFF16A34A)
                                )
                            ) {
                                Column(
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text("Referral", fontSize = 12.sp)
                                    Text("5 Free Qs", fontSize = 10.sp)
                                }
                            }
                        }
                    }
                } else {
                    // Show message input
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        OutlinedTextField(
                            value = messageText,
                            onValueChange = { messageText = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text("Type your message...", fontSize = 14.sp) },
                            singleLine = true
                        )
                        
                        FloatingActionButton(
                            onClick = {
                                if (messageText.isNotBlank()) {
                                    viewModel.sendMessage(messageText)
                                    messageText = ""
                                }
                            },
                            modifier = Modifier.size(48.dp),
                            containerColor = Color(0xFF8B5CF6)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Send,
                                contentDescription = "Send",
                                tint = Color.White,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Chat message bubble
 */
@Composable
fun ChatMessageBubble(message: ChatMessage) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        Card(
            modifier = Modifier.widthIn(max = 280.dp),
            colors = CardDefaults.cardColors(
                containerColor = if (message.isUser) 
                    Color(0xFF8B5CF6) 
                else 
                    Color(0xFFF1F5F9)
            ),
            shape = RoundedCornerShape(
                topStart = 12.dp,
                topEnd = 12.dp,
                bottomStart = if (message.isUser) 12.dp else 4.dp,
                bottomEnd = if (message.isUser) 4.dp else 12.dp
            )
        ) {
            Column(
                modifier = Modifier.padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = message.content,
                    color = if (message.isUser) Color.White else Color(0xFF1E293B),
                    fontSize = 14.sp
                )
                
                if (message.blacklisted) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = null,
                            tint = Color(0xFFDC2626),
                            modifier = Modifier.size(14.dp)
                        )
                        Text(
                            text = "Blacklisted phrase detected",
                            fontSize = 11.sp,
                            color = Color(0xFFDC2626)
                        )
                    }
                }
                
                if (message.isWinner) {
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.EmojiEvents,
                            contentDescription = null,
                            tint = Color(0xFFFBBF24),
                            modifier = Modifier.size(14.dp)
                        )
                        Text(
                            text = "Winner!",
                            fontSize = 11.sp,
                            color = Color(0xFFFBBF24),
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
    }
}

/**
 * Team collaboration section
 */
@Composable
fun TeamCollaborationSection(
    userTeam: UserTeam?,
    onCreateTeam: () -> Unit,
    onJoinTeam: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.People,
                    contentDescription = null,
                    tint = Color(0xFF6B7280),
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = "Team Collaboration",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827)
                )
            }
            
            if (userTeam != null) {
                // User is in a team
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFDCFCE7) // green-100
                    ),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFF86EFAC)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .background(Color(0xFF16A34A), CircleShape)
                            )
                            Text(
                                text = "Team Member",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF15803D)
                            )
                        }
                        Text(
                            text = userTeam.team_name,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF15803D)
                        )
                        Text(
                            text = "Pool: $${userTeam.total_pool}",
                            fontSize = 12.sp,
                            color = Color(0xFF166534)
                        )
                    }
                }
                
                OutlinedButton(
                    onClick = { /* Manage team */ },
                    modifier = Modifier.fillMaxWidth(),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFD1D5DB)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Text("Manage Team", fontSize = 13.sp, color = Color(0xFF374151))
                }
            } else {
                // User not in a team
                Text(
                    text = "Join a team to pool resources and share strategies for this bounty.",
                    fontSize = 14.sp,
                    color = Color(0xFF6B7280)
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = onJoinTeam,
                        modifier = Modifier
                            .weight(1f)
                            .height(44.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF2563EB) // blue-600
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.PersonAdd,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Join Team", fontSize = 13.sp)
                    }
                    
                    Button(
                        onClick = onCreateTeam,
                        modifier = Modifier
                            .weight(1f)
                            .height(44.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF16A34A) // green-600
                        ),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Create Team", fontSize = 13.sp)
                    }
                }
            }
        }
    }
}

/**
 * Winning prompts section
 */
@Composable
fun WinningPromptsSection(
    prompts: List<WinningPrompt>
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.EmojiEvents,
                    contentDescription = null,
                    tint = Color(0xFFF59E0B),
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = "Winning Prompts (Unusable)",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827)
                )
            }
            
            if (prompts.isEmpty()) {
                Text(
                    text = "Prompts that successfully jailbroke the bot will appear here once a winner is declared.",
                    fontSize = 13.sp,
                    color = Color(0xFF64748B),
                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                )
                
                // Example prompt
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFF8FAFC)
                    ),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0)),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Surface(
                            shape = CircleShape,
                            color = Color(0xFF8B5CF6),
                            modifier = Modifier.size(32.dp)
                        ) {
                            Box(contentAlignment = Alignment.Center) {
                                Text(
                                    text = "1",
                                    color = Color.White,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        
                        Column(
                            modifier = Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Text(
                                text = "Example Winning Prompt",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color(0xFF111827)
                            )
                            Text(
                                text = "This is an example of what a successful jailbreak prompt looks like. Each prompt that successfully convinced the AI to transfer funds will be displayed here for reference.",
                                fontSize = 12.sp,
                                color = Color(0xFF64748B),
                                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                            )
                        }
                    }
                }
            } else {
                // Display actual winning prompts
                prompts.forEachIndexed { index, prompt ->
                    WinningPromptCard(prompt = prompt, index = index + 1)
                }
            }
        }
    }
}

@Composable
fun WinningPromptCard(prompt: WinningPrompt, index: Int) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFFEF3C7) // yellow-100
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFFBBF24)),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = Color(0xFFF59E0B),
                modifier = Modifier.size(32.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = "$index",
                        color = Color.White,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "Winner: ${prompt.winner_name}",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color(0xFF78350F)
                )
                Text(
                    text = prompt.prompt,
                    fontSize = 12.sp,
                    color = Color(0xFF92400E)
                )
            }
        }
    }
}

// Placeholder dialogs (to be implemented)
@Composable
fun PaymentFlowDialog(
    bountyId: Int,
    walletAdapter: WalletAdapter?,
    onDismiss: () -> Unit,
    onPaymentSuccess: () -> Unit
) {
    var step by remember { mutableStateOf("userInfo") } // userInfo or payment
    var username by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var usernameError by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    val coroutineScope = rememberCoroutineScope()
    
    // Get wallet address
    val walletAddress = walletAdapter?.walletAddress?.collectAsState()?.value
    
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
                if (step == "userInfo") {
                    // User Info Step
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = "User Info",
                        tint = Color(0xFF8B5CF6),
                        modifier = Modifier.size(48.dp)
                    )
                    
                    Text(
                        text = "Enter Your Information",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                    
                    Text(
                        text = "Please provide your username and email to continue",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280),
                        textAlign = TextAlign.Center
                    )
                    
                    // Username Input
                    OutlinedTextField(
                        value = username,
                        onValueChange = { 
                            username = it
                            usernameError = null
                        },
                        label = { Text("Username *") },
                        placeholder = { Text("Min 3 characters") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = !isLoading,
                        isError = usernameError != null,
                        supportingText = if (usernameError != null) {
                            { Text(usernameError!!, color = Color(0xFFDC2626)) }
                        } else null
                    )
                    
                    // Email Input
                    OutlinedTextField(
                        value = email,
                        onValueChange = { email = it },
                        label = { Text("Email (optional)") },
                        placeholder = { Text("your@email.com") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = !isLoading
                    )
                    
                    // Continue Button
                    Button(
                        onClick = {
                            // Validate username
                            if (username.length < 3) {
                                usernameError = "Username must be at least 3 characters"
                                return@Button
                            }
                            
                            if (walletAddress == null) {
                                usernameError = "Please connect your wallet first"
                                return@Button
                            }
                            
                            isLoading = true
                            usernameError = null
                            
                            // Save username and email to database via API
                            coroutineScope.launch {
                                try {
                                    val client = okhttp3.OkHttpClient()
                                    val json = org.json.JSONObject().apply {
                                        put("wallet_address", walletAddress)
                                        put("username", username)
                                        if (email.isNotBlank()) {
                                            put("email", email)
                                        }
                                    }
                                    
                                    val requestBody = okhttp3.RequestBody.create(
                                        "application/json".toMediaType(),
                                        json.toString()
                                    )
                                    
                                    val request = okhttp3.Request.Builder()
                                        .url("http://10.0.2.2:8000/api/user/update-profile") // 10.0.2.2 for Android emulator
                                        .post(requestBody)
                                        .build()
                                    
                                    val response = client.newCall(request).execute()
                                    
                                    if (response.isSuccessful) {
                                        step = "payment"
                                    } else {
                                        val errorBody = response.body?.string()
                                        val errorJson = org.json.JSONObject(errorBody ?: "{}")
                                        usernameError = errorJson.optString("detail", "Failed to save information")
                                    }
                                } catch (e: Exception) {
                                    usernameError = "Network error: ${e.message}"
                                } finally {
                                    isLoading = false
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !isLoading && username.isNotBlank() && username.length >= 3,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF8B5CF6)
                        )
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Saving...")
                        } else {
                            Icon(
                                imageVector = Icons.Default.ArrowForward,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Continue to Payment")
                        }
                    }
                    
                    // Cancel Button
                    TextButton(
                        onClick = onDismiss,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Cancel")
                    }
                } else {
                    // Payment Options Step
                    Icon(
                        imageVector = Icons.Default.Payment,
                        contentDescription = "Payment",
                        tint = Color(0xFF8B5CF6),
                        modifier = Modifier.size(48.dp)
                    )
                    
                    Text(
                        text = "Choose Payment Method",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                    
                    Text(
                        text = "Select how you'd like to pay for questions",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280),
                        textAlign = TextAlign.Center
                    )
                    
                    // Payment Options
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // USDC Wallet Payment
                        Button(
                            onClick = {
                                // TODO: Implement USDC wallet payment
                                onPaymentSuccess()
                                onDismiss()
                            },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF8B5CF6)
                            )
                        ) {
                            Icon(
                                imageVector = Icons.Default.AccountBalanceWallet,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Pay with USDC Wallet")
                        }
                        
                        // Apple Pay / PayPal - REMOVED (MoonPay service denied)
                        // Button(
                        //     onClick = {
                        //         // TODO: Implement fiat payment
                        //         onPaymentSuccess()
                        //         onDismiss()
                        //     },
                        //     modifier = Modifier.fillMaxWidth(),
                        //     colors = ButtonDefaults.buttonColors(
                        //         containerColor = Color(0xFF10B981)
                        //     )
                        // ) {
                        //     Icon(
                        //         imageVector = Icons.Default.Payment,
                        //         contentDescription = null,
                        //         modifier = Modifier.size(20.dp)
                        //     )
                        //     Spacer(modifier = Modifier.width(8.dp))
                        //     Text("Pay with Apple Pay / PayPal")
                        // }
                    }
                    
                    // Back Button
                    TextButton(
                        onClick = { step = "userInfo" },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Back")
                    }
                }
            }
        }
    }
}

@Composable
fun ReferralFlowDialog(
    onDismiss: () -> Unit,
    onReferralSuccess: () -> Unit
) {
    var username by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var referralCode by remember { mutableStateOf<String?>(null) }
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
                if (referralCode != null) {
                    // Success State - Show Referral Code
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = "Success",
                        tint = Color(0xFF16A34A),
                        modifier = Modifier.size(48.dp)
                    )
                    
                    Text(
                        text = "Your Referral Code",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                    
                    Text(
                        text = "Share this code with friends to get 5 free questions for each person who uses it!",
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
                        Text(
                            text = referralCode!!,
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF16A34A),
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                    
                    // Done Button
                    Button(
                        onClick = {
                            onReferralSuccess()
                            onDismiss()
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF16A34A)
                        )
                    ) {
                        Text("Done")
                    }
                } else {
                    // Form State - Collect Username and Email
                    Icon(
                        imageVector = Icons.Default.CardGiftcard,
                        contentDescription = "Referral",
                        tint = Color(0xFF16A34A),
                        modifier = Modifier.size(48.dp)
                    )
                    
                    Text(
                        text = "Get Your Referral Code",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF111827)
                    )
                    
                    Text(
                        text = "Enter your username and email to get a referral code",
                        fontSize = 14.sp,
                        color = Color(0xFF6B7280),
                        textAlign = TextAlign.Center
                    )
                    
                    // Username Input
                    OutlinedTextField(
                        value = username,
                        onValueChange = { username = it },
                        label = { Text("Username") },
                        placeholder = { Text("Min 3 characters") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = !isLoading,
                        isError = error != null && username.isNotBlank() && username.length < 3
                    )
                    
                    // Email Input
                    OutlinedTextField(
                        value = email,
                        onValueChange = { email = it },
                        label = { Text("Email Address") },
                        placeholder = { Text("your@email.com") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        enabled = !isLoading,
                        isError = error != null && email.isNotBlank() && (!email.contains("@") || !email.contains(".com"))
                    )
                    
                    // Error Message
                    if (error != null) {
                        Text(
                            text = error!!,
                            color = Color(0xFFDC2626),
                            fontSize = 12.sp,
                            textAlign = TextAlign.Center
                        )
                    }
                    
                    // Submit Button
                    Button(
                        onClick = {
                            // Validate username
                            if (username.length < 3) {
                                error = "Username must be at least 3 characters"
                                return@Button
                            }
                            
                            // Validate email
                            if (!email.contains("@") || !email.contains(".com")) {
                                error = "Email must contain @ and .com"
                                return@Button
                            }
                            
                            isLoading = true
                            error = null
                            
                            // TODO: Replace with actual API call
                            coroutineScope.launch {
                                kotlinx.coroutines.delay(1500)
                                // Simulate success - generate code from username
                                referralCode = username.uppercase() + kotlin.random.Random.nextInt(1000, 9999)
                                isLoading = false
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !isLoading && username.isNotBlank() && email.isNotBlank(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF16A34A)
                        )
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("Get Referral Code")
                        }
                    }
                    
                    // Cancel Button
                    TextButton(
                        onClick = onDismiss,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Cancel")
                    }
                }
            }
        }
    }
}

@Composable
fun TeamBrowseDialog(
    teams: List<Team>,
    onDismiss: () -> Unit,
    onJoinTeam: (String) -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { 
            Text(
                text = "Join a Team",
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            if (teams.isEmpty()) {
                Text(
                    text = "No teams available. Create one instead!",
                    color = Color(0xFF6B7280)
                )
            } else {
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.height(300.dp)
                ) {
                    items(teams) { team ->
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = Color(0xFFF8FAFC)
                            ),
                            border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE2E8F0))
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = team.name,
                                        fontWeight = FontWeight.Medium,
                                        fontSize = 14.sp
                                    )
                                    Text(
                                        text = "${team.member_count} members • ${team.total_attempts} attempts",
                                        fontSize = 12.sp,
                                        color = Color(0xFF6B7280)
                                    )
                                }
                                Button(
                                    onClick = { onJoinTeam(team.id) },
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = Color(0xFF2563EB)
                                    ),
                                    modifier = Modifier.height(36.dp)
                                ) {
                                    Text("Join", fontSize = 12.sp)
                                }
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}

@Composable
fun BountyCreateTeamDialog(
    onDismiss: () -> Unit,
    onCreateTeam: (String) -> Unit
) {
    var teamName by remember { mutableStateOf("") }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { 
            Text(
                text = "Create New Team",
                fontWeight = FontWeight.Bold
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "Enter a name for your team:",
                    fontSize = 14.sp,
                    color = Color(0xFF6B7280)
                )
                OutlinedTextField(
                    value = teamName,
                    onValueChange = { teamName = it },
                    placeholder = { Text("Team name", fontSize = 14.sp) },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { 
                    if (teamName.isNotBlank()) {
                        onCreateTeam(teamName)
                    }
                },
                enabled = teamName.isNotBlank(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF16A34A)
                )
            ) {
                Text("Create")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}

