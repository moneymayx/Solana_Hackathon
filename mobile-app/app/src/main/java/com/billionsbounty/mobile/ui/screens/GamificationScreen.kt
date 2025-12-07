package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.ui.components.gamification.*
import com.billionsbounty.mobile.data.api.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GamificationScreen(
    walletAddress: String?,
    apiRepository: ApiRepository,
    onBackClick: () -> Unit
) {
    val scope = rememberCoroutineScope()
    
    // State
    var streakData by remember { mutableStateOf<StreakResponse?>(null) }
    var pointsData by remember { mutableStateOf<UserPointsResponse?>(null) }
    var challenges by remember { mutableStateOf<List<UserChallenge>>(emptyList()) }
    var achievements by remember { mutableStateOf<List<Achievement>>(emptyList()) }
    var powerUps by remember { mutableStateOf<List<PowerUp>>(emptyList()) }
    var milestones by remember { mutableStateOf<List<Milestone>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }
    
    // Selected milestone for celebration
    var selectedMilestone by remember { mutableStateOf<Milestone?>(null) }
    
    // Load data
    LaunchedEffect(walletAddress) {
        if (walletAddress != null) {
            isLoading = true
            error = null
            
            try {
                // Load all gamification data in parallel
                val streakResult = apiRepository.getUserStreak(walletAddress)
                val pointsResult = apiRepository.getUserPoints(walletAddress)
                val challengesResult = apiRepository.getUserChallenges(walletAddress)
                val achievementsResult = apiRepository.getUserAchievements(walletAddress)
                val powerUpsResult = apiRepository.getUserPowerUps(walletAddress)
                val milestonesResult = apiRepository.getUserMilestones(walletAddress)
                
                streakResult.onSuccess { streakData = it }
                pointsResult.onSuccess { pointsData = it }
                challengesResult.onSuccess { challenges = it.challenges }
                achievementsResult.onSuccess { achievements = it.achievements }
                powerUpsResult.onSuccess { powerUps = it.power_ups }
                milestonesResult.onSuccess { 
                    milestones = it.milestones
                    // Show first unshown milestone
                    it.milestones.firstOrNull { !it.celebration_shown }?.let { milestone ->
                        selectedMilestone = milestone
                    }
                }
                
                isLoading = false
            } catch (e: Exception) {
                error = e.message ?: "Failed to load gamification data"
                isLoading = false
            }
        } else {
            error = "Wallet address not available"
            isLoading = false
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Gamification") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        when {
            isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            error != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "Error: $error",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = onBackClick) {
                        Text("Go Back")
                    }
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Quick Stats
                    item {
                        QuickStatsCard(pointsData = pointsData)
                    }
                    
                    // Streak Display
                    item {
                        StreakDisplay(streakData = streakData)
                    }
                    
                    // Challenges
                    item {
                        ChallengesList(
                            challenges = challenges,
                            onChallengeClick = { challengeId ->
                                // Handle challenge click
                            }
                        )
                    }
                    
                    // Achievements
                    item {
                        AchievementsGallery(achievements = achievements)
                    }
                    
                    // Power-Ups
                    item {
                        PowerUpsInventory(
                            powerUps = powerUps,
                            onActivate = { powerUpId ->
                                scope.launch {
                                    apiRepository.activatePowerUp(powerUpId).onSuccess {
                                        // Refresh power-ups
                                        apiRepository.getUserPowerUps(walletAddress ?: "")
                                            .onSuccess { powerUps = it.power_ups }
                                    }
                                }
                            }
                        )
                    }
                }
            }
        }
        
        // Milestone Celebration Dialog
        MilestoneCelebration(
            milestone = selectedMilestone,
            onDismiss = {
                selectedMilestone?.let { milestone ->
                    scope.launch {
                        apiRepository.markMilestoneShown(milestone.id).onSuccess {
                            selectedMilestone = null
                            // Refresh milestones
                            apiRepository.getUserMilestones(walletAddress ?: "")
                                .onSuccess { milestones = it.milestones }
                        }
                    }
                } ?: run {
                    selectedMilestone = null
                }
            }
        )
    }
}

