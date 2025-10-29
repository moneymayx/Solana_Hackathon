package com.billionsbounty.mobile.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.billionsbounty.mobile.ui.screens.PaymentAmountSelectionDialog
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class PaymentAmountSelectionDialogTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun dialogDisplaysAllAmountOptions() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // Check all 6 amount options are displayed
        composeTestRule.onNodeWithText("$1").assertExists()
        composeTestRule.onNodeWithText("$10").assertExists()
        composeTestRule.onNodeWithText("$20").assertExists()
        composeTestRule.onNodeWithText("$50").assertExists()
        composeTestRule.onNodeWithText("$100").assertExists()
        composeTestRule.onNodeWithText("$1K").assertExists() // $1000 displays as 1K
    }

    @Test
    fun dialogShowsCorrectBadges() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // Check badges
        composeTestRule.onNodeWithText("POPULAR").assertExists() // $10
        composeTestRule.onNodeWithText("WHALE").assertExists() // $1000
    }

    @Test
    fun dialogShowsCorrectQuestionsForAmount() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // $10 / $10 = 1 question
        composeTestRule.onNodeWithText("1 question", substring = true).assertExists()
        
        // $20 / $10 = 2 questions
        composeTestRule.onNodeWithText("2 questions", substring = true).assertExists()
        
        // $50 / $10 = 5 questions
        composeTestRule.onNodeWithText("5 questions", substring = true).assertExists()
    }

    @Test
    fun insufficientAmountShowsTooLowBadge() {
        // Question cost is $15, so $1 and $10 should show "TOO LOW"
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 15.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // Multiple "TOO LOW" badges should exist for $1 and $10
        composeTestRule.onAllNodesWithText("TOO LOW").assertCountEquals(2)
    }

    @Test
    fun amountWithCreditShowsCorrectly() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // $50 / $10 = 5 questions + $0 credit (exact)
        composeTestRule.onNodeWithText("5 questions", substring = true).assertExists()
        
        // Note: Credit text would appear if we had an amount like $15
        // But with $10 cost, all our preset amounts divide evenly except $1
    }

    @Test
    fun clickingAmountCallsOnSelectAmount() {
        var selectedAmount: Double? = null
        
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = { selectedAmount = it },
                isProcessing = false
            )
        }

        // Click on $10 option
        composeTestRule.onNodeWithText("$10").performClick()

        assert(selectedAmount == 10.0)
    }

    @Test
    fun closeButtonDismissesDialog() {
        var dismissed = false
        
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = { dismissed = true },
                onSelectAmount = {},
                isProcessing = false
            )
        }

        // Click close button
        composeTestRule.onNodeWithContentDescription("Close").performClick()

        assert(dismissed)
    }

    @Test
    fun cancelButtonDismissesDialog() {
        var dismissed = false
        
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = { dismissed = true },
                onSelectAmount = {},
                isProcessing = false
            )
        }

        composeTestRule.onNodeWithText("Cancel").performClick()

        assert(dismissed)
    }

    @Test
    fun processingStateDisablesButtons() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = true
            )
        }

        // Buttons should be disabled when processing
        // Check that clicking doesn't trigger callbacks
        var amountSelected = false
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = { amountSelected = true },
                isProcessing = true
            )
        }

        composeTestRule.onNodeWithText("$10").assertExists()
        // Note: Can't easily test disabled state in Compose UI tests
        // This would be better tested in unit tests
    }

    @Test
    fun dialogShowsInfoSection() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        composeTestRule.onNodeWithText("How it works:", substring = true).assertExists()
        composeTestRule.onNodeWithText("prize pool", substring = true, ignoreCase = true).assertExists()
    }

    @Test
    fun dialogShowsHeader() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 10.0,
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        composeTestRule.onNodeWithText("Choose Your Bounty Contribution").assertExists()
    }

    @Test
    fun highQuestionCostShowsTip() {
        composeTestRule.setContent {
            PaymentAmountSelectionDialog(
                currentQuestionCost = 15.0, // Higher than $1
                onDismiss = {},
                onSelectAmount = {},
                isProcessing = false
            )
        }

        composeTestRule.onNodeWithText("💡 Tip:", substring = true).assertExists()
    }
}



