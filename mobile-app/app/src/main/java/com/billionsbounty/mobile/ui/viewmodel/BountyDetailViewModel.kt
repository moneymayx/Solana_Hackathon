package com.billionsbounty.mobile.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billionsbounty.mobile.data.api.*
import com.billionsbounty.mobile.data.preferences.WalletPreferences
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.wallet.WalletAdapter
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for BountyDetailScreen
 * Manages bounty details, user eligibility, teams, winning prompts, and chat
 */
@HiltViewModel
class BountyDetailViewModel @Inject constructor(
    private val repository: ApiRepository,
    private val walletAdapter: WalletAdapter,
    private val walletPreferences: WalletPreferences,
    private val nftRepository: com.billionsbounty.mobile.data.repository.NftRepository
) : ViewModel() {
    
    // Bounty data
    private val _bounty = MutableStateFlow<Bounty?>(null)
    val bounty: StateFlow<Bounty?> = _bounty.asStateFlow()
    
    private val _bountyStatus = MutableStateFlow<BountyStatusResponse?>(null)
    val bountyStatus: StateFlow<BountyStatusResponse?> = _bountyStatus.asStateFlow()
    
    // User eligibility & free questions
    private val _userEligibility = MutableStateFlow<UserEligibilityResponse?>(null)
    val userEligibility: StateFlow<UserEligibilityResponse?> = _userEligibility.asStateFlow()
    
    private val _freeQuestions = MutableStateFlow<FreeQuestionsResponse?>(null)
    val freeQuestions: StateFlow<FreeQuestionsResponse?> = _freeQuestions.asStateFlow()
    
    // Team data
    private val _userTeam = MutableStateFlow<UserTeam?>(null)
    val userTeam: StateFlow<UserTeam?> = _userTeam.asStateFlow()
    
    private val _allTeams = MutableStateFlow<List<Team>>(emptyList())
    val allTeams: StateFlow<List<Team>> = _allTeams.asStateFlow()
    
    // Winning prompts
    private val _winningPrompts = MutableStateFlow<List<WinningPrompt>>(emptyList())
    val winningPrompts: StateFlow<List<WinningPrompt>> = _winningPrompts.asStateFlow()
    
    // Chat messages
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    
    // UI state
    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isWalletConnected = MutableStateFlow(false)
    val isWalletConnected: StateFlow<Boolean> = _isWalletConnected.asStateFlow()
    
    private val _walletAddress = MutableStateFlow<String?>(null)
    val walletAddress: StateFlow<String?> = _walletAddress.asStateFlow()
    
    // Expose wallet adapter for UI components
    fun getWalletAdapter(): WalletAdapter = walletAdapter
    
    // Expose NFT repository for UI components
    fun getNftRepository(): com.billionsbounty.mobile.data.repository.NftRepository = nftRepository
    
    // Expose API repository for UI components
    fun getRepository(): ApiRepository = repository
    
    init {
        // Observe wallet state from adapter
        viewModelScope.launch {
            walletAdapter.walletAddress.collect { address ->
                _walletAddress.value = address
                _isWalletConnected.value = address != null
            }
        }
        
        // Try to restore wallet connection from preferences
        viewModelScope.launch {
            walletPreferences.walletAddress.collect { savedAddress ->
                if (savedAddress != null && walletAdapter.getPublicKey() == null) {
                    // Wallet was previously connected but adapter not initialized
                    // User will need to reconnect, but we can show they had a wallet
                    _walletAddress.value = savedAddress
                }
            }
        }
    }
    
    private val _showGlobalChat = MutableStateFlow(false)
    val showGlobalChat: StateFlow<Boolean> = _showGlobalChat.asStateFlow()
    
    // Current bounty ID
    private var currentBountyId: Int = 0
    
    /**
     * Load all bounty detail data
     */
    fun loadBountyDetails(bountyId: Int) {
        currentBountyId = bountyId
        _isLoading.value = true
        _error.value = null
        
        viewModelScope.launch {
            try {
                // Load bounty details
                loadBounty(bountyId)
                
                // Load bounty status
                loadBountyStatus(bountyId)
                
                // Load winning prompts
                loadWinningPrompts(bountyId)
                
                // Load user-specific data if wallet connected
                if (_isWalletConnected.value) {
                    loadUserEligibility()
                    loadUserTeam()
                }
                
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = "Failed to load bounty details: ${e.message}"
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Load bounty details
     */
    private suspend fun loadBounty(bountyId: Int) {
        try {
            val response = repository.getBountyDetails(bountyId)
            if (response.isSuccessful && response.body()?.success == true) {
                _bounty.value = response.body()?.bounty
            }
        } catch (e: Exception) {
            // Handle error silently or log
        }
    }
    
    /**
     * Load bounty status
     */
    private suspend fun loadBountyStatus(bountyId: Int) {
        try {
            val response = repository.getBountyStatus(bountyId)
            if (response.isSuccessful) {
                _bountyStatus.value = response.body()
            }
        } catch (e: Exception) {
            // Handle error silently or log
        }
    }
    
    /**
     * Load user eligibility
     */
    fun loadUserEligibility(userId: Int? = null, walletAddress: String? = null) {
        viewModelScope.launch {
            try {
                val response = repository.checkUserEligibility(
                    UserEligibilityRequest(userId, walletAddress)
                )
                if (response.isSuccessful) {
                    _userEligibility.value = response.body()
                }
            } catch (e: Exception) {
                // Handle error silently or log
            }
        }
    }
    
    /**
     * Load user's team
     */
    private suspend fun loadUserTeam(userId: Int = 1) {
        try {
            val response = repository.getUserTeam(userId)
            if (response.isSuccessful && response.body()?.success == true) {
                _userTeam.value = response.body()?.team
            }
        } catch (e: Exception) {
            // Handle error silently or log
        }
    }
    
    /**
     * Load all teams
     */
    fun loadAllTeams() {
        viewModelScope.launch {
            try {
                val response = repository.getAllTeams()
                if (response.isSuccessful && response.body()?.success == true) {
                    _allTeams.value = response.body()?.teams ?: emptyList()
                }
            } catch (e: Exception) {
                _error.value = "Failed to load teams: ${e.message}"
            }
        }
    }
    
    /**
     * Create a new team
     */
    fun createTeam(teamName: String, userId: Int = 1, onSuccess: (String) -> Unit) {
        viewModelScope.launch {
            try {
                val response = repository.createTeam(CreateTeamRequest(teamName, userId))
                if (response.isSuccessful && response.body()?.success == true) {
                    val teamId = response.body()?.team_id ?: ""
                    loadUserTeam(userId)
                    onSuccess(teamId)
                } else {
                    _error.value = "Failed to create team"
                }
            } catch (e: Exception) {
                _error.value = "Failed to create team: ${e.message}"
            }
        }
    }
    
    /**
     * Join a team
     */
    fun joinTeam(teamId: String, userId: Int = 1, onSuccess: () -> Unit) {
        viewModelScope.launch {
            try {
                val response = repository.joinTeam(JoinTeamRequest(teamId, userId))
                if (response.isSuccessful && response.body()?.success == true) {
                    loadUserTeam(userId)
                    onSuccess()
                } else {
                    _error.value = response.body()?.message ?: "Failed to join team"
                }
            } catch (e: Exception) {
                _error.value = "Failed to join team: ${e.message}"
            }
        }
    }
    
    /**
     * Load winning prompts
     */
    private suspend fun loadWinningPrompts(bountyId: Int) {
        try {
            val response = repository.getWinningPrompts(bountyId)
            if (response.isSuccessful && response.body()?.success == true) {
                _winningPrompts.value = response.body()?.prompts ?: emptyList()
            }
        } catch (e: Exception) {
            // Handle error silently or log
        }
    }
    
    /**
     * Send a chat message
     */
    fun sendMessage(message: String, userId: Int = 1) {
        if (message.isBlank()) return
        
        viewModelScope.launch {
            try {
                // Add user message to UI
                val userMessage = ChatMessage(
                    id = System.currentTimeMillis().toString(),
                    content = message,
                    isUser = true
                )
                _messages.value = _messages.value + userMessage
                
                // Send to API
                val response = repository.sendChatMessage(
                    ChatRequest(message = message, user_id = userId)
                )
                
                if (response.isSuccessful) {
                    val chatResponse = response.body()
                    if (chatResponse != null) {
                        // Add AI response to UI
                        val aiMessage = ChatMessage(
                            id = System.currentTimeMillis().toString(),
                            content = chatResponse.response,
                            isUser = false,
                            blacklisted = chatResponse.blacklisted,
                            isWinner = chatResponse.is_winner,
                            winnerPrize = chatResponse.winner_prize
                        )
                        _messages.value = _messages.value + aiMessage
                        
                        // If winner, refresh bounty status
                        if (chatResponse.is_winner) {
                            loadBountyStatus(currentBountyId)
                        }
                    }
                } else {
                    _error.value = "Failed to send message"
                }
            } catch (e: Exception) {
                _error.value = "Error: ${e.message}"
            }
        }
    }
    
    /**
     * Toggle between beat mode and watch mode
     */
    fun toggleChatMode() {
        _showGlobalChat.value = !_showGlobalChat.value
    }
    
    /**
     * Connect wallet - called after wallet adapter authorization
     */
    fun connectWallet(walletAddress: String, publicKey: String) {
        viewModelScope.launch {
            try {
                // Save to persistent storage
                walletPreferences.saveWalletConnection(walletAddress)
                
                // Register with backend
                val response = repository.connectWallet(
                    WalletConnectRequest(walletAddress, publicKey)
                )
                if (response.isSuccessful && response.body()?.success == true) {
                    _isWalletConnected.value = true
                    _walletAddress.value = walletAddress
                    
                    // Reload user-specific data
                    loadUserEligibility(walletAddress = walletAddress)
                    loadUserTeam(response.body()?.user_id ?: 1)
                }
            } catch (e: Exception) {
                _error.value = "Failed to connect wallet: ${e.message}"
            }
        }
    }
    
    /**
     * Disconnect wallet
     */
    fun disconnectWallet() {
        viewModelScope.launch {
            try {
                // Clear from persistent storage
                walletPreferences.clearWalletConnection()
                
                // Update state
                _isWalletConnected.value = false
                _walletAddress.value = null
                
                // Clear user-specific data
                _userEligibility.value = null
                _userTeam.value = null
            } catch (e: Exception) {
                _error.value = "Failed to disconnect wallet: ${e.message}"
            }
        }
    }
    
    /**
     * Clear error
     */
    fun clearError() {
        _error.value = null
    }
}


