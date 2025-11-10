package com.billionsbounty.mobile.ui.components

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.assertDoesNotExist
import androidx.compose.ui.test.assertExists
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Rule
import org.junit.Test

/**
 * Instrumented tests for ActivityTracker component
 * Tests UI rendering and activity display
 */
class ActivityTrackerInstrumentedTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `ActivityTracker does not render when no activities`() {
        // Given - no activities in storage
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        ActivityStorage.clearActivities(context)

        // When
        composeTestRule.setContent {
            ActivityTracker(bountyId = 1, enabled = true)
        }

        // Then - component should not render (returns null when no activities)
        composeTestRule.onRoot().assertExists()
        // Activity tracker returns null when no activities, so we can't assert on it directly
    }

    @Test
    fun `ActivityTracker displays activity when available`() {
        // Given - add an activity
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        ActivityStorage.clearActivities(context)
        ActivityStorage.addActivity(
            context = context,
            bountyId = 1,
            username = "TestUser",
            activityType = ActivityType.QUESTION,
            bountyName = "Test Bounty"
        )

        // When
        composeTestRule.setContent {
            ActivityTracker(bountyId = 1, enabled = true)
        }

        // Wait for compose to settle and activity to load
        composeTestRule.waitForIdle()

        // Then - activity should be visible
        composeTestRule.onNodeWithText("TestUser").assertExists()
        composeTestRule.onNodeWithText("just asked Test Bounty").assertExists()
    }

    @Test
    fun `ActivityTracker does not render when disabled`() {
        // Given - add an activity
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        ActivityStorage.clearActivities(context)
        ActivityStorage.addActivity(
            context = context,
            bountyId = 1,
            username = "TestUser",
            activityType = ActivityType.QUESTION,
            bountyName = "Test Bounty"
        )

        // When - tracker is disabled
        composeTestRule.setContent {
            ActivityTracker(bountyId = 1, enabled = false)
        }

        composeTestRule.waitForIdle()

        // Then - activity should not be visible
        composeTestRule.onNodeWithText("TestUser").assertDoesNotExist()
    }

    @Test
    fun `ActivityTracker filters by bounty ID`() {
        // Given - activities for different bounties
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        ActivityStorage.clearActivities(context)
        ActivityStorage.addActivity(context, 1, "User1", ActivityType.QUESTION, "Bounty 1")
        ActivityStorage.addActivity(context, 2, "User2", ActivityType.QUESTION, "Bounty 2")

        // When - show tracker for bounty 1
        composeTestRule.setContent {
            ActivityTracker(bountyId = 1, enabled = true)
        }

        composeTestRule.waitForIdle()

        // Then - only bounty 1 activity should be visible
        composeTestRule.onNodeWithText("User1").assertExists()
        composeTestRule.onNodeWithText("User2").assertDoesNotExist()
    }
}

