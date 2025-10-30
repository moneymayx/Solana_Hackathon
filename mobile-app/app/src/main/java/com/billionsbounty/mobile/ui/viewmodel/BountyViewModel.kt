package com.billionsbounty.mobile.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billionsbounty.mobile.data.api.Bounty
import com.billionsbounty.mobile.data.api.BountiesResponse
import com.billionsbounty.mobile.data.api.LotteryStatusResponse
import com.billionsbounty.mobile.data.repository.ApiRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class BountyViewModel @Inject constructor(
    private val apiRepository: ApiRepository
) : ViewModel() {
    
    private val _bounties = MutableStateFlow<List<Bounty>>(emptyList())
    val bounties: StateFlow<List<Bounty>> = _bounties.asStateFlow()
    
    private val _lotteryStatus = MutableStateFlow<LotteryStatusResponse?>(null)
    val lotteryStatus: StateFlow<LotteryStatusResponse?> = _lotteryStatus.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    // Alias for error to match web naming convention
    val errorMessage: StateFlow<String?> = _error.asStateFlow()
    
    // Cache timestamp for bounties to prevent excessive API calls
    private var lastBountyFetchTime: Long = 0
    private val CACHE_DURATION_MS = 30000L // 30 seconds cache, matching web
    
    init {
        loadData()
    }
    
    private fun loadData() {
        loadBounties()
        loadLotteryStatus()
    }
    
    fun refresh() {
        // Force refresh bypasses cache
        loadBounties(forceRefresh = true)
        loadLotteryStatus()
    }
    
    // Make loadBounties public so it can be called from UI
    // Now includes caching to prevent excessive API calls
    fun loadBounties(forceRefresh: Boolean = false) {
        val currentTime = System.currentTimeMillis()
        
        // Skip fetch if cache is still valid and not forcing refresh
        if (!forceRefresh && 
            _bounties.value.isNotEmpty() && 
            (currentTime - lastBountyFetchTime) < CACHE_DURATION_MS) {
            return
        }
        
        _isLoading.value = true
        _error.value = null
        
        viewModelScope.launch {
            val result = apiRepository.getAllBounties()
            
            result.fold(
                onSuccess = { response ->
                    _bounties.value = response.bounties
                    _isLoading.value = false
                    lastBountyFetchTime = currentTime
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "Failed to load bounties"
                    _isLoading.value = false
                }
            )
        }
    }
    
    private fun loadLotteryStatus() {
        viewModelScope.launch {
            val result = apiRepository.getLotteryStatus()
            
            result.fold(
                onSuccess = { response ->
                    _lotteryStatus.value = response
                },
                onFailure = { exception ->
                    _error.value = exception.message ?: "Failed to load lottery status"
                }
            )
        }
    }
    
    fun clearError() {
        _error.value = null
    }
}
