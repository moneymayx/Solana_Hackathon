package com.billionsbounty.mobile.viewmodel

import com.billionsbounty.mobile.data.api.PaymentResponse
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.ui.viewmodel.PaymentViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

@OptIn(ExperimentalCoroutinesApi::class)
class PaymentViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Mock
    private lateinit var apiRepository: ApiRepository

    private lateinit var viewModel: PaymentViewModel
    private lateinit var closeable: AutoCloseable

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        closeable = MockitoAnnotations.openMocks(this)
        viewModel = PaymentViewModel(apiRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        closeable.close()
    }

    @Test
    fun `initial state is correct`() {
        val state = viewModel.paymentState.value
        
        assertFalse(state.walletConnected)
        assertNull(state.walletAddress)
        assertNull(state.selectedAmount)
        assertEquals(10.0, state.currentQuestionCost)
        assertFalse(state.isProcessing)
        assertFalse(state.isMockMode)
        assertEquals(0, state.questionsGranted)
        assertEquals(0.0, state.creditRemainder)
    }

    @Test
    fun `connectWallet updates state correctly`() {
        val testAddress = "TestWallet123"
        
        viewModel.connectWallet(testAddress)
        
        val state = viewModel.paymentState.value
        assertTrue(state.walletConnected)
        assertEquals(testAddress, state.walletAddress)
    }

    @Test
    fun `selectAmount calculates questions and credit correctly`() {
        // Test $10 payment with $10 question cost = 1 question, $0 credit
        viewModel.selectAmount(10.0)
        
        var state = viewModel.paymentState.value
        assertEquals(10.0, state.selectedAmount)
        assertEquals(1, state.questionsGranted)
        assertEquals(0.0, state.creditRemainder)

        // Test $25 payment with $10 question cost = 2 questions, $5 credit
        viewModel.selectAmount(25.0)
        
        state = viewModel.paymentState.value
        assertEquals(25.0, state.selectedAmount)
        assertEquals(2, state.questionsGranted)
        assertEquals(5.0, state.creditRemainder)

        // Test $7.50 payment with $10 question cost = 0 questions, $7.50 credit
        viewModel.selectAmount(7.5)
        
        state = viewModel.paymentState.value
        assertEquals(7.5, state.selectedAmount)
        assertEquals(0, state.questionsGranted)
        assertEquals(7.5, state.creditRemainder)
    }

    @Test
    fun `calculateQuestionsAndCredit returns correct values`() {
        // $10 / $10 = 1 question, $0 credit
        val (q1, c1) = viewModel.calculateQuestionsAndCredit(10.0, 10.0)
        assertEquals(1, q1)
        assertEquals(0.0, c1)

        // $15 / $10 = 1 question, $5 credit
        val (q2, c2) = viewModel.calculateQuestionsAndCredit(15.0, 10.0)
        assertEquals(1, q2)
        assertEquals(5.0, c2)

        // $100 / $10 = 10 questions, $0 credit
        val (q3, c3) = viewModel.calculateQuestionsAndCredit(100.0, 10.0)
        assertEquals(10, q3)
        assertEquals(0.0, c3)

        // $1 / $10 = 0 questions, $1 credit
        val (q4, c4) = viewModel.calculateQuestionsAndCredit(1.0, 10.0)
        assertEquals(0, q4)
        assertEquals(1.0, c4)
    }

    @Test
    fun `setCurrentQuestionCost updates state`() {
        viewModel.setCurrentQuestionCost(15.5)
        
        val state = viewModel.paymentState.value
        assertEquals(15.5, state.currentQuestionCost)
    }

    @Test
    fun `processPayment fails without wallet connection`() = runTest {
        var errorMessage: String? = null
        
        viewModel.processPayment(
            onSuccess = { _, _, _ -> },
            onError = { errorMessage = it }
        )

        advanceUntilIdle()
        assertEquals("Wallet not connected", errorMessage)
    }

    @Test
    fun `processPayment fails without selected amount`() = runTest {
        viewModel.connectWallet("TestWallet123")
        var errorMessage: String? = null
        
        viewModel.processPayment(
            onSuccess = { _, _, _ -> },
            onError = { errorMessage = it }
        )

        advanceUntilIdle()
        assertEquals("Please select a payment amount", errorMessage)
    }

    @Test
    fun `processPayment fails with insufficient balance`() = runTest {
        viewModel.connectWallet("TestWallet123")
        viewModel.selectAmount(100.0)
        viewModel.updateUsdcBalance(50.0)
        var errorMessage: String? = null
        
        viewModel.processPayment(
            onSuccess = { _, _, _ -> },
            onError = { errorMessage = it }
        )

        advanceUntilIdle()
        assertEquals("Insufficient USDC balance", errorMessage)
    }

    @Test
    fun `processPayment succeeds with valid state`() = runTest {
        // Setup
        viewModel.connectWallet("TestWallet123")
        viewModel.selectAmount(10.0)
        viewModel.updateUsdcBalance(100.0)
        
        val mockResponse = PaymentResponse(
            success = true,
            transaction_id = "tx123",
            status = "pending"
        )
        
        whenever(apiRepository.createPayment(any(), any(), any()))
            .thenReturn(Result.success(mockResponse))
        
        var successCalled = false
        var returnedQuestions = 0
        var returnedCredit = 0.0
        var returnedMockMode = false
        
        viewModel.processPayment(
            onSuccess = { questions, credit, isMock ->
                successCalled = true
                returnedQuestions = questions
                returnedCredit = credit
                returnedMockMode = isMock
            },
            onError = { }
        )

        advanceUntilIdle()
        assertTrue(successCalled)
        assertEquals(1, returnedQuestions)
        assertEquals(0.0, returnedCredit)
    }

    @Test
    fun `clearError removes error message`() {
        // Trigger an error first
        viewModel.processPayment(
            onSuccess = { _, _, _ -> },
            onError = { }
        )
        
        // Clear the error
        viewModel.clearError()
        
        val state = viewModel.paymentState.value
        assertNull(state.error)
    }

    @Test
    fun `resetState returns to initial values`() {
        // Modify state
        viewModel.connectWallet("TestWallet123")
        viewModel.selectAmount(50.0)
        viewModel.updateUsdcBalance(100.0)
        
        // Reset
        viewModel.resetState()
        
        // Verify initial state
        val state = viewModel.paymentState.value
        assertFalse(state.walletConnected)
        assertNull(state.walletAddress)
        assertNull(state.selectedAmount)
        assertEquals(10.0, state.currentQuestionCost)
    }
}

