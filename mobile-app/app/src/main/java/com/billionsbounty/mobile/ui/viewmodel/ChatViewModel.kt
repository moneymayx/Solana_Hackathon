package com.billionsbounty.mobile.ui.viewmodel

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.utils.ActivityHelper
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ChatMessage(
    val id: String,
    val content: String,
    val isUser: Boolean,
    val isWinner: Boolean = false,
    val blacklisted: Boolean = false,
    val winnerPrize: Double? = null
)

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val apiRepository: ApiRepository
) : ViewModel() {
    
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    
    private val _isWinner = MutableStateFlow(false)
    val isWinner: StateFlow<Boolean> = _isWinner.asStateFlow()
    
    private val _questionsRemaining = MutableStateFlow(0)
    val questionsRemaining: StateFlow<Int> = _questionsRemaining.asStateFlow()
    
    private val _isPaidQuestions = MutableStateFlow(false)
    val isPaidQuestions: StateFlow<Boolean> = _isPaidQuestions.asStateFlow()
    
    private val _currentQuestionCost = MutableStateFlow(10.0)
    val currentQuestionCost: StateFlow<Double> = _currentQuestionCost.asStateFlow()
    
    private var sessionId: String? = null
    private var currentBountyId: Int? = null
    private var firstQuestionTracker = mutableMapOf<Pair<Int, String>, Boolean>() // Track first questions per (bountyId, username)
    
    /**
     * Send a message to a specific bounty's chat
     */
    fun sendBountyMessage(
        bountyId: Int,
        message: String,
        walletAddress: String? = null,
        context: Context? = null,
        bountyName: String? = null
    ) {
        if (message.isBlank()) return
        
        currentBountyId = bountyId
        
        // Add user message to UI
        addMessage(
            ChatMessage(
                id = "${System.currentTimeMillis()}-user",
                content = message,
                isUser = true
            )
        )
        
        _isLoading.value = true
        _error.value = null
        
        viewModelScope.launch {
            val result = apiRepository.sendBountyChatMessage(
                bountyId = bountyId,
                message = message,
                walletAddress = walletAddress,
                sessionId = sessionId
            )
            
            if (result.isSuccess) {
                val response = result.getOrThrow()
                
                // Add AI response to UI
                addMessage(
                    ChatMessage(
                        id = "${System.currentTimeMillis()}-ai",
                        content = response.response,
                        isUser = false,
                        isWinner = response.is_winner
                    )
                )
                
                // Update questions remaining from response
                _questionsRemaining.value = response.questions_remaining
                
                // Update paid/free questions flag
                response.free_questions?.let { freeQuestions ->
                    _isPaidQuestions.value = freeQuestions.is_paid
                }
                
                // Update current question cost if bounty status available
                response.bounty_status?.let { bountyStatus ->
                    // Calculate current cost based on difficulty and entries
                    val startingCost = getStartingQuestionCost(bountyStatus.difficulty_level ?: "easy")
                    val currentCost = startingCost * Math.pow(1.0078, bountyStatus.total_entries.toDouble())
                    _currentQuestionCost.value = currentCost
                }
                
                // Show winner celebration if applicable
                if (response.is_winner) {
                    _isWinner.value = true
                    
                    // Track jailbreak success for gamification (10x multiplier)
                    walletAddress?.let { address ->
                        viewModelScope.launch {
                            apiRepository.recordActivity(address).onFailure { e ->
                                android.util.Log.e("ChatViewModel", "Failed to record jailbreak activity", e)
                            }
                        }
                    }
                }
                
                // Track question activity for backend streak/points system
                walletAddress?.let { address ->
                    viewModelScope.launch {
                        apiRepository.recordActivity(address).onFailure { e ->
                            android.util.Log.e("ChatViewModel", "Failed to record question activity", e)
                        }
                    }
                }
                
                // Track activity for UI display (localStorage equivalent)
                context?.let { ctx ->
                    walletAddress?.let { address ->
                        viewModelScope.launch {
                            val username = ActivityHelper.getUsername(ctx, address, apiRepository)
                            username?.let { name ->
                                val isFirst = ActivityHelper.isFirstQuestion(ctx, bountyId, name)
                                ActivityHelper.trackQuestion(
                                    context = ctx,
                                    bountyId = bountyId,
                                    username = name,
                                    bountyName = bountyName,
                                    isFirstQuestion = isFirst
                                )
                            }
                        }
                    }
                }
                
                _isLoading.value = false
            } else {
                val exception = result.exceptionOrNull() ?: Exception("Unknown error")
                _error.value = exception.message ?: "Failed to send message"
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Send a message using the old general chat endpoint
     */
    fun sendMessage(message: String, userId: Int? = null) {
        if (message.isBlank()) return
        
        // Add user message to UI
        addMessage(
            ChatMessage(
                id = "${System.currentTimeMillis()}-user",
                content = message,
                isUser = true
            )
        )
        
        _isLoading.value = true
        _error.value = null
        
        viewModelScope.launch {
            val result = apiRepository.sendChatMessage(
                message = message,
                userId = userId,
                sessionId = sessionId
            )
            
            if (result.isSuccess) {
                val response = result.getOrThrow()
                
                // Update session ID if provided
                sessionId = response.session_id
                
                // Add AI response to UI
                addMessage(
                    ChatMessage(
                        id = "${System.currentTimeMillis()}-ai",
                        content = response.response,
                        isUser = false,
                        isWinner = response.is_winner,
                        blacklisted = response.blacklisted,
                        winnerPrize = response.winner_prize
                    )
                )
                
                // Show winner celebration if applicable
                if (response.is_winner) {
                    _isWinner.value = true
                }
                
                _isLoading.value = false
            } else {
                val exception = result.exceptionOrNull() ?: Exception("Unknown error")
                _error.value = exception.message ?: "Failed to send message"
                _isLoading.value = false
            }
        }
    }
    
    /**
     * Get starting question cost based on difficulty
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
     * Update questions remaining from external source
     */
    fun updateQuestionsRemaining(remaining: Int, isPaid: Boolean = false) {
        _questionsRemaining.value = remaining
        _isPaidQuestions.value = isPaid
    }
    
    /**
     * Get formatted message for questions remaining
     */
    fun getQuestionsRemainingMessage(): String {
        val count = _questionsRemaining.value
        return if (_isPaidQuestions.value) {
            "$count question${if (count != 1) "s" else ""} remaining"
        } else {
            "$count free question${if (count != 1) "s" else ""} remaining"
        }
    }
    
    private fun addMessage(message: ChatMessage) {
        _messages.value = _messages.value + message
    }
    
    fun clearMessages() {
        _messages.value = emptyList()
        sessionId = null
    }
    
    fun clearError() {
        _error.value = null
    }
    
    fun clearWinnerState() {
        _isWinner.value = false
    }
}
