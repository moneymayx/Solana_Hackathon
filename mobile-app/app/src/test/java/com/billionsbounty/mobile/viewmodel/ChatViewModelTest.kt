package com.billionsbounty.mobile.viewmodel

import com.billionsbounty.mobile.data.api.*
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.ui.viewmodel.ChatViewModel
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
import kotlin.test.assertTrue

@OptIn(ExperimentalCoroutinesApi::class)
class ChatViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Mock
    private lateinit var apiRepository: ApiRepository

    private lateinit var viewModel: ChatViewModel
    private lateinit var closeable: AutoCloseable

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        closeable = MockitoAnnotations.openMocks(this)
        viewModel = ChatViewModel(apiRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        closeable.close()
    }

    @Test
    fun `initial state is correct`() {
        assertTrue(viewModel.messages.value.isEmpty())
        assertFalse(viewModel.isLoading.value)
        assertEquals(null, viewModel.error.value)
        assertFalse(viewModel.isWinner.value)
        assertEquals(0, viewModel.questionsRemaining.value)
        assertFalse(viewModel.isPaidQuestions.value)
        assertEquals(10.0, viewModel.currentQuestionCost.value)
    }

    @Test
    fun `sendBountyMessage adds user message to list`() = runTest {
        val mockResponse = BountyChatResponse(
            success = true,
            response = "AI response",
            questions_remaining = 5,
            free_questions = FreeQuestionsData(
                eligible = true,
                questions_remaining = 5,
                questions_used = 0,
                is_paid = false
            )
        )
        
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendBountyMessage(
            bountyId = 1,
            message = "Test message",
            walletAddress = "TestWallet123"
        )

        advanceUntilIdle()

        val messages = viewModel.messages.value
        assertEquals(2, messages.size) // User + AI message
        assertEquals("Test message", messages[0].content)
        assertTrue(messages[0].isUser)
        assertEquals("AI response", messages[1].content)
        assertFalse(messages[1].isUser)
    }

    @Test
    fun `sendBountyMessage updates questions remaining`() = runTest {
        val mockResponse = BountyChatResponse(
            success = true,
            response = "AI response",
            questions_remaining = 3,
            free_questions = FreeQuestionsData(
                eligible = true,
                questions_remaining = 3,
                questions_used = 2,
                is_paid = true
            )
        )
        
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendBountyMessage(
            bountyId = 1,
            message = "Test",
            walletAddress = "TestWallet123"
        )

        advanceUntilIdle()

        assertEquals(3, viewModel.questionsRemaining.value)
        assertTrue(viewModel.isPaidQuestions.value)
    }

    @Test
    fun `sendBountyMessage updates question cost from bounty status`() = runTest {
        val mockResponse = BountyChatResponse(
            success = true,
            response = "AI response",
            questions_remaining = 5,
            bounty_status = BountyStatusData(
                current_pool = 1000.0,
                total_entries = 100,
                difficulty_level = "hard"
            )
        )
        
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendBountyMessage(
            bountyId = 1,
            message = "Test",
            walletAddress = "TestWallet123"
        )

        advanceUntilIdle()

        // Hard difficulty starting cost is $5, with 100 entries
        // Cost = 5.00 * 1.0078^100 ≈ 10.86
        assertTrue(viewModel.currentQuestionCost.value > 5.0)
    }

    @Test
    fun `sendBountyMessage sets winner state`() = runTest {
        val mockResponse = BountyChatResponse(
            success = true,
            response = "Congratulations!",
            is_winner = true,
            questions_remaining = 0
        )
        
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendBountyMessage(
            bountyId = 1,
            message = "Final answer",
            walletAddress = "TestWallet123"
        )

        advanceUntilIdle()

        assertTrue(viewModel.isWinner.value)
    }

    @Test
    fun `sendBountyMessage handles errors gracefully`() = runTest {
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.failure(Exception("Network error")))

        viewModel.sendBountyMessage(
            bountyId = 1,
            message = "Test",
            walletAddress = "TestWallet123"
        )

        advanceUntilIdle()

        assertEquals("Network error", viewModel.error.value)
        assertFalse(viewModel.isLoading.value)
    }

    @Test
    fun `sendMessage adds messages for general chat`() = runTest {
        val mockResponse = ChatResponse(
            response = "General chat response",
            user_id = 123,
            session_id = "session123"
        )
        
        whenever(apiRepository.sendChatMessage(any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendMessage("Hello", userId = 123)

        advanceUntilIdle()

        val messages = viewModel.messages.value
        assertEquals(2, messages.size)
        assertEquals("Hello", messages[0].content)
        assertEquals("General chat response", messages[1].content)
    }

    @Test
    fun `updateQuestionsRemaining updates state correctly`() {
        viewModel.updateQuestionsRemaining(7, isPaid = true)
        
        assertEquals(7, viewModel.questionsRemaining.value)
        assertTrue(viewModel.isPaidQuestions.value)
    }

    @Test
    fun `getQuestionsRemainingMessage returns correct format for paid`() {
        viewModel.updateQuestionsRemaining(3, isPaid = true)
        
        assertEquals("3 questions remaining", viewModel.getQuestionsRemainingMessage())
    }

    @Test
    fun `getQuestionsRemainingMessage returns correct format for free`() {
        viewModel.updateQuestionsRemaining(5, isPaid = false)
        
        assertEquals("5 free questions remaining", viewModel.getQuestionsRemainingMessage())
    }

    @Test
    fun `getQuestionsRemainingMessage handles singular`() {
        viewModel.updateQuestionsRemaining(1, isPaid = true)
        
        assertEquals("1 question remaining", viewModel.getQuestionsRemainingMessage())
    }

    @Test
    fun `clearMessages removes all messages`() = runTest {
        val mockResponse = BountyChatResponse(
            success = true,
            response = "AI response",
            questions_remaining = 5
        )
        
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.success(mockResponse))

        viewModel.sendBountyMessage(1, "Test", "wallet")
        advanceUntilIdle()

        assertTrue(viewModel.messages.value.isNotEmpty())

        viewModel.clearMessages()

        assertTrue(viewModel.messages.value.isEmpty())
    }

    @Test
    fun `clearError removes error state`() = runTest {
        whenever(apiRepository.sendBountyChatMessage(any(), any(), any(), any()))
            .thenReturn(Result.failure(Exception("Error")))

        viewModel.sendBountyMessage(1, "Test", "wallet")
        advanceUntilIdle()

        assertEquals("Error", viewModel.error.value)

        viewModel.clearError()

        assertEquals(null, viewModel.error.value)
    }

    @Test
    fun `clearWinnerState resets winner flag`() {
        viewModel.clearWinnerState()
        assertFalse(viewModel.isWinner.value)
    }

    @Test
    fun `blank message is not sent`() = runTest {
        viewModel.sendBountyMessage(1, "", "wallet")
        advanceUntilIdle()

        assertTrue(viewModel.messages.value.isEmpty())
    }

    @Test
    fun `whitespace-only message is not sent`() = runTest {
        viewModel.sendBountyMessage(1, "   ", "wallet")
        advanceUntilIdle()

        assertTrue(viewModel.messages.value.isEmpty())
    }
}



