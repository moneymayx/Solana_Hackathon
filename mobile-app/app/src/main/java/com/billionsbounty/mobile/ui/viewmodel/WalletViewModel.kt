package com.billionsbounty.mobile.ui.viewmodel

import androidx.activity.ComponentActivity
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billionsbounty.mobile.data.preferences.WalletPreferences
import com.billionsbounty.mobile.solana.SolanaClient
import com.billionsbounty.mobile.wallet.WalletAdapter
import com.billionsbounty.mobile.wallet.WalletConnectionState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for wallet connection and management
 * Handles authorization, balance checking, and persistence
 */
@HiltViewModel
class WalletViewModel @Inject constructor(
    private val walletAdapter: WalletAdapter,
    private val walletPreferences: WalletPreferences,
    private val solanaClient: SolanaClient
) : ViewModel() {
    
    val connectionState: StateFlow<WalletConnectionState> = walletAdapter.connectionState
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), WalletConnectionState.Disconnected)
    
    val walletAddress: StateFlow<String?> = walletAdapter.walletAddress
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
    
    private val _balance = MutableStateFlow<Double?>(null)
    val balance: StateFlow<Double?> = _balance.asStateFlow()
    
    private val _isLoadingBalance = MutableStateFlow(false)
    val isLoadingBalance: StateFlow<Boolean> = _isLoadingBalance.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    init {
        // Observe wallet address changes and fetch balance
        viewModelScope.launch {
            walletAddress.collect { address ->
                if (address != null) {
                    fetchBalance(address)
                } else {
                    _balance.value = null
                }
            }
        }
        
        // Try to restore previous wallet connection
        viewModelScope.launch {
            walletPreferences.walletAddress.collect { savedAddress ->
                if (savedAddress != null && walletAdapter.getPublicKey() == null) {
                    // Wallet was previously connected but not currently active
                    // User will need to reconnect
                }
            }
        }
    }
    
    /**
     * Connect wallet - launches wallet selector
     * @param activity Activity to launch wallet from
     */
    suspend fun connectWallet(activity: ComponentActivity): Result<String> {
        _error.value = null
        val result = walletAdapter.authorize(activity)
        
        result.onSuccess { address ->
            // Save to preferences
            walletPreferences.saveWalletConnection(address)
            fetchBalance(address)
        }
        
        result.onFailure { e ->
            _error.value = e.message ?: "Failed to connect wallet"
        }
        
        return result
    }
    
    /**
     * Disconnect wallet
     * @param activity Activity to disconnect from
     */
    suspend fun disconnectWallet(activity: ComponentActivity) {
        walletAdapter.disconnect(activity)
        walletPreferences.clearWalletConnection()
        _balance.value = null
        _error.value = null
    }
    
    /**
     * Fetch SOL balance for connected wallet
     */
    private fun fetchBalance(address: String) {
        viewModelScope.launch {
            _isLoadingBalance.value = true
            val result = solanaClient.getBalance(address)
            
            result.onSuccess { balance ->
                _balance.value = balance
            }
            
            result.onFailure { e ->
                _error.value = "Failed to fetch balance: ${e.message}"
            }
            
            _isLoadingBalance.value = false
        }
    }
    
    /**
     * Manually refresh balance
     */
    fun refreshBalance() {
        val address = walletAddress.value
        if (address != null) {
            fetchBalance(address)
        }
    }
    
    /**
     * Check if wallet is connected
     */
    fun isConnected(): Boolean {
        return walletAdapter.isConnected()
    }
    
    /**
     * Get the wallet adapter (for other components that need it)
     */
    fun getWalletAdapter(): WalletAdapter = walletAdapter
    
    /**
     * Clear error message
     */
    fun clearError() {
        _error.value = null
    }
    
    /**
     * Switch to devnet for testing
     */
    fun useDevnet(enabled: Boolean) {
        solanaClient.useDevnet(enabled)
        // Refresh balance after network switch
        refreshBalance()
    }
}
