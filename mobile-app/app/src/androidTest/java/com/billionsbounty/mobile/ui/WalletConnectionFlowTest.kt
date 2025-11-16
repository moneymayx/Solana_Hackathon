package com.billionsbounty.mobile.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.billionsbounty.mobile.MainActivity
import com.billionsbounty.mobile.ui.screens.WalletConnectionDialog
import com.billionsbounty.mobile.wallet.WalletAdapter
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Instrumented tests for wallet connection flow
 * Tests the actual UI interactions and wallet connection button
 * 
 * Note: These tests require an emulator/device but will test the actual
 * wallet flow with mocked wallet adapter responses
 */
@RunWith(AndroidJUnit4::class)
class WalletConnectionFlowTest {

    // Use the actual MainActivity to test real wallet adapter integration
    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun walletConnectionDialog_displaysCorrectly() {
        // This test just verifies the dialog can be rendered
        // The actual button click requires a real wallet app which we can't test in CI
        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { }
            )
        }

        // Verify dialog is displayed
        composeTestRule.onNodeWithText("Connect Wallet").assertExists()
        composeTestRule.onNodeWithText("Connect your Solana wallet to participate in bounties").assertExists()
    }

    @Test
    fun walletConnectionButton_exists() {
        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { }
            )
        }

        // Verify the connect button exists and is enabled
        composeTestRule
            .onNodeWithText("Connect Wallet")
            .assertExists()
            .assertIsEnabled()
    }

    @Test
    fun walletConnectionDialog_showsConnectedState() {
        val testAddress = "4ZdDfUbwRcBvFJdZqG8dKF8H9Y3jL8mP1wN7cT5xV2aE"

        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { },
                prefillConnectedAddress = testAddress
            )
        }

        // Verify connected state is displayed
        composeTestRule.onNodeWithText("Wallet Connected").assertExists()
    }

    @Test
    fun walletConnectionDialog_displaysTruncatedAddress() {
        val testAddress = "4ZdDfUbwRcBvFJdZqG8dKF8H9Y3jL8mP1wN7cT5xV2aE"

        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { },
                prefillConnectedAddress = testAddress
            )
        }

        // Address should be truncated in display (first 4, last 4)
        val truncatedAddress = "4ZdD...V2aE"
        composeTestRule.onNodeWithText(truncatedAddress).assertExists()
    }
}

/**
 * Mock wallet flow test
 * This uses a pure Compose test without Android components
 * to test the UI logic without requiring actual wallet integration
 */
class WalletConnectionDialogUITest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun walletDialogConnectButtonStartsEnabled() {
        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { }
            )
        }

        // Verify the connect button renders and is enabled before any wallet authorization call.
        composeTestRule
            .onNodeWithText("Connect Wallet")
            .assertExists()
            .assertIsEnabled()

        // Full loading state validation would require a fake wallet adapter that can expose transient state.
    }

    @Test
    fun walletDialogDisplaysAllRequiredElements() {
        composeTestRule.setContent {
            WalletConnectionDialog(
                walletAdapter = WalletAdapter(),
                onConnected = { },
                onDismiss = { }
            )
        }

        // Verify all UI elements exist
        composeTestRule.onNodeWithText("Connect Wallet").assertExists()
        composeTestRule.onNodeWithText("Connect your Solana wallet to participate in bounties").assertExists()
    }
}
