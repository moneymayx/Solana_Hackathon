package com.billionsbounty.mobile.ui.viewmodel

import androidx.activity.ComponentActivity
import com.billionsbounty.mobile.data.preferences.WalletPreferences
import com.billionsbounty.mobile.solana.SolanaClient
import com.billionsbounty.mobile.wallet.WalletAdapter
import com.billionsbounty.mobile.wallet.WalletConnectionState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

/**
 * Unit tests for WalletViewModel
 * Tests wallet connection, balance fetching, network switching, and persistence
 */
@OptIn(ExperimentalCoroutinesApi::class)
class WalletViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Mock
    private lateinit var walletAdapter: WalletAdapter

    @Mock
    private lateinit var walletPreferences: WalletPreferences

    @Mock
    private lateinit var solanaClient: SolanaClient

    @Mock
    private lateinit var activity: ComponentActivity

    private lateinit var viewModel: WalletViewModel
    private lateinit var closeable: AutoCloseable

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        closeable = MockitoAnnotations.openMocks(this)

        // Setup default mocks
        whenever(walletAdapter.connectionState).thenReturn(flowOf(WalletConnectionState.Disconnected))
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(null))
        whenever(walletPreferences.walletAddress).thenReturn(flowOf(null))
        
        // Create ViewModel
        viewModel = WalletViewModel(walletAdapter, walletPreferences, solanaClient)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
        closeable.close()
    }

    // ==============================================================================
    // WALLET CONNECTION TESTS
    // ==============================================================================

    @Test
    fun `initial state is disconnected`() = runTest {
        val connectionState = viewModel.connectionState.value
        
        assertEquals(WalletConnectionState.Disconnected, connectionState)
        assertNull(viewModel.walletAddress.value)
        assertNull(viewModel.balance.value)
        assertFalse(viewModel.isLoadingBalance.value)
        assertNull(viewModel.error.value)
    }

    @Test
    fun `connectWallet successfully connects`() = runTest {
        val testAddress = "TestWalletAddress12345"
        
        // Mock successful authorization
        whenever(walletAdapter.authorize(activity)).thenReturn(Result.success(testAddress))
        doNothing().whenever(walletPreferences).saveWalletConnection(any())
        
        // Update adapter state to simulate connection
        whenever(walletAdapter.connectionState).thenReturn(flowOf(WalletConnectionState.Connected))
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        
        val result = viewModel.connectWallet(activity)
        
        assertTrue(result.isSuccess)
        assertEquals(testAddress, result.getOrNull())
        verify(walletAdapter).authorize(activity)
        verify(walletPreferences).saveWalletConnection(testAddress)
    }

    @Test
    fun `connectWallet handles failure gracefully`() = runTest {
        val errorMessage = "User rejected connection"
        
        // Mock failed authorization
        whenever(walletAdapter.authorize(activity)).thenReturn(Result.failure(Exception(errorMessage)))
        
        val result = viewModel.connectWallet(activity)
        
        assertTrue(result.isFailure)
        assertEquals(errorMessage, result.exceptionOrNull()?.message)
        verify(walletAdapter).authorize(activity)
        verify(walletPreferences, never()).saveWalletConnection(any())
    }

    @Test
    fun `disconnectWallet clears state`() = runTest {
        // Setup initial connection state
        whenever(walletAdapter.walletAddress).thenReturn(flowOf("TestWallet123"))
        whenever(walletAdapter.connectionState).thenReturn(flowOf(WalletConnectionState.Connected))
        doNothing().whenever(walletAdapter).disconnect(activity)
        doNothing().whenever(walletPreferences).clearWalletConnection()
        
        viewModel.disconnectWallet(activity)
        
        verify(walletAdapter).disconnect(activity)
        verify(walletPreferences).clearWalletConnection()
    }

    // ==============================================================================
    // BALANCE FETCHING TESTS
    // ==============================================================================

    @Test
    fun `balance is fetched on wallet connection`() = runTest {
        val testAddress = "TestWalletAddress12345"
        val testBalance = 5.5
        
        // Mock adapter state changes
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.success(testBalance))
        
        // Wait for collect to run
        testDispatcher.scheduler.advanceUntilIdle()
        
        assertEquals(testBalance, viewModel.balance.value)
        verify(solanaClient).getBalance(testAddress)
    }

    @Test
    fun `balance fetch error is handled`() = runTest {
        val testAddress = "TestWalletAddress12345"
        val errorMessage = "Network error"
        
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.failure(Exception(errorMessage)))
        
        testDispatcher.scheduler.advanceUntilIdle()
        
        assertEquals(errorMessage, viewModel.error.value)
        verify(solanaClient).getBalance(testAddress)
    }

    @Test
    fun `refreshBalance fetches current balance`() = runTest {
        val testAddress = "TestWalletAddress12345"
        val testBalance = 10.0
        
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.success(testBalance))
        
        viewModel.refreshBalance()
        testDispatcher.scheduler.advanceUntilIdle()
        
        assertEquals(testBalance, viewModel.balance.value)
        verify(solanaClient, atLeastOnce()).getBalance(testAddress)
    }

    @Test
    fun `refreshBalance does nothing when not connected`() = runTest {
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(null))
        
        viewModel.refreshBalance()
        testDispatcher.scheduler.advanceUntilIdle()
        
        verify(solanaClient, never()).getBalance(any())
    }

    // ==============================================================================
    // NETWORK SWITCHING TESTS
    // ==============================================================================

    @Test
    fun `useDevnet switches network`() = runTest {
        doNothing().whenever(solanaClient).useDevnet(true)
        
        viewModel.useDevnet(true)
        
        verify(solanaClient).useDevnet(true)
    }

    @Test
    fun `switching to devnet refreshes balance`() = runTest {
        val testAddress = "TestWalletAddress12345"
        
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        doNothing().whenever(solanaClient).useDevnet(true)
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.success(1.0))
        
        viewModel.useDevnet(true)
        testDispatcher.scheduler.advanceUntilIdle()
        
        verify(solanaClient).useDevnet(true)
        verify(solanaClient).getBalance(testAddress)
    }

    // ==============================================================================
    // UTILITY METHOD TESTS
    // ==============================================================================

    @Test
    fun `isConnected returns true when connected`() = runTest {
        whenever(walletAdapter.isConnected()).thenReturn(true)
        
        assertTrue(viewModel.isConnected())
    }

    @Test
    fun `isConnected returns false when disconnected`() = runTest {
        whenever(walletAdapter.isConnected()).thenReturn(false)
        
        assertFalse(viewModel.isConnected())
    }

    @Test
    fun `getWalletAdapter returns the adapter`() = runTest {
        val adapter = viewModel.getWalletAdapter()
        
        assertNotNull(adapter)
        assertEquals(walletAdapter, adapter)
    }

    @Test
    fun `clearError removes error`() = runTest {
        // Set an error first
        val testAddress = "TestWalletAddress12345"
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(
            Result.failure(Exception("Network error"))
        )
        
        testDispatcher.scheduler.advanceUntilIdle()
        assertNotNull(viewModel.error.value)
        
        // Clear error
        viewModel.clearError()
        
        assertNull(viewModel.error.value)
    }

    // ==============================================================================
    // INTEGRATION FLOW TESTS
    // ==============================================================================

    @Test
    fun `full connection flow works correctly`() = runTest {
        val testAddress = "TestWalletAddress12345"
        val testBalance = 15.5
        
        // Step 1: Connect wallet
        whenever(walletAdapter.authorize(activity)).thenReturn(Result.success(testAddress))
        doNothing().whenever(walletPreferences).saveWalletConnection(any())
        
        val connectResult = viewModel.connectWallet(activity)
        assertTrue(connectResult.isSuccess)
        assertEquals(testAddress, connectResult.getOrNull())
        
        // Step 2: Balance should be fetched
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.success(testBalance))
        
        testDispatcher.scheduler.advanceUntilIdle()
        
        assertEquals(testBalance, viewModel.balance.value)
        
        // Verify all interactions
        verify(walletAdapter).authorize(activity)
        verify(walletPreferences).saveWalletConnection(testAddress)
        verify(solanaClient).getBalance(testAddress)
    }

    @Test
    fun `disconnect clears balance and preference`() = runTest {
        val testAddress = "TestWalletAddress12345"
        
        // Setup connected state
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(testAddress))
        whenever(solanaClient.getBalance(testAddress)).thenReturn(Result.success(10.0))
        
        testDispatcher.scheduler.advanceUntilIdle()
        assertNotNull(viewModel.balance.value)
        
        // Disconnect
        doNothing().whenever(walletAdapter).disconnect(activity)
        doNothing().whenever(walletPreferences).clearWalletConnection()
        whenever(walletAdapter.walletAddress).thenReturn(flowOf(null))
        
        viewModel.disconnectWallet(activity)
        testDispatcher.scheduler.advanceUntilIdle()
        
        assertNull(viewModel.balance.value)
        verify(walletAdapter).disconnect(activity)
        verify(walletPreferences).clearWalletConnection()
    }
}
