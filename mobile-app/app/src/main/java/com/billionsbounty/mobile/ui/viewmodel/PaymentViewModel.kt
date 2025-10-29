package com.billionsbounty.mobile.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.billionsbounty.mobile.data.repository.ApiRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PaymentState(
    val walletConnected: Boolean = false,
    val walletAddress: String? = null,
    val usdcBalance: Double = 0.0,
    val selectedAmount: Double? = null,
    val currentQuestionCost: Double = 10.0,
    val isProcessing: Boolean = false,
    val isMockMode: Boolean = false,
    val error: String? = null,
    val questionsGranted: Int = 0,
    val creditRemainder: Double = 0.0
)

@HiltViewModel
class PaymentViewModel @Inject constructor(
    private val apiRepository: ApiRepository
) : ViewModel() {
    
    private val _paymentState = MutableStateFlow(PaymentState())
    val paymentState: StateFlow<PaymentState> = _paymentState.asStateFlow()
    
    fun connectWallet(address: String) {
        _paymentState.value = _paymentState.value.copy(
            walletConnected = true,
            walletAddress = address
        )
    }
    
    fun updateUsdcBalance(balance: Double) {
        _paymentState.value = _paymentState.value.copy(usdcBalance = balance)
    }
    
    fun selectAmount(amount: Double) {
        val (questions, credit) = calculateQuestionsAndCredit(
            amount,
            _paymentState.value.currentQuestionCost
        )
        _paymentState.value = _paymentState.value.copy(
            selectedAmount = amount,
            questionsGranted = questions,
            creditRemainder = credit
        )
    }
    
    fun setCurrentQuestionCost(cost: Double) {
        _paymentState.value = _paymentState.value.copy(currentQuestionCost = cost)
    }
    
    fun calculateQuestionsAndCredit(amount: Double, costPerQuestion: Double): Pair<Int, Double> {
        val questions = (amount / costPerQuestion).toInt()
        val credit = amount % costPerQuestion
        return Pair(questions, credit)
    }
    
    fun processPayment(onSuccess: (Int, Double, Boolean) -> Unit, onError: (String) -> Unit) {
        val state = _paymentState.value
        
        if (!state.walletConnected) {
            onError("Wallet not connected")
            return
        }
        
        val amount = state.selectedAmount
        if (amount == null || amount <= 0) {
            onError("Please select a payment amount")
            return
        }
        
        if (state.usdcBalance < amount) {
            onError("Insufficient USDC balance")
            return
        }
        
        _paymentState.value = state.copy(isProcessing = true, error = null)
        
        viewModelScope.launch {
            val result = apiRepository.createPayment(
                amountUsd = amount,
                paymentMethod = "wallet",
                walletAddress = state.walletAddress
            )
            
            result.fold(
                onSuccess = { response ->
                    _paymentState.value = state.copy(
                        isProcessing = false
                    )
                    onSuccess(
                        state.questionsGranted,
                        state.creditRemainder,
                        state.isMockMode
                    )
                },
                onFailure = { exception ->
                    _paymentState.value = state.copy(
                        isProcessing = false,
                        error = exception.message
                    )
                    onError(exception.message ?: "Payment failed")
                }
            )
        }
    }
    
    fun clearError() {
        _paymentState.value = _paymentState.value.copy(error = null)
    }
    
    fun resetState() {
        _paymentState.value = PaymentState()
    }
}
