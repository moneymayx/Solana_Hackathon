package com.billionsbounty.mobile.ui.components

import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onAllNodesWithText
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
    fun activityTrackerDoesNotRenderWhenNoActivities() {
        // Given - no activities in storage
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        ActivityStorage.clearActivities(context)

        // When
        composeTestRule.setContent {
            ActivityTracker(bountyId = 1, enabled = true)
        }

        // Then - verify no activity text is rendered
        composeTestRule.onAllNodesWithText("just asked Test Bounty").assertCountEquals(0)
    }

    @Test
    fun activityTrackerDisplaysActivityWhenAvailable() {
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
        composeTestRule.onNodeWithText("TestUser").assertIsDisplayed()
        composeTestRule.onNodeWithText("just asked Test Bounty").assertIsDisplayed()
    }

    @Test
    fun activityTrackerDoesNotRenderWhenDisabled() {
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
        composeTestRule.onAllNodesWithText("TestUser").assertCountEquals(0)
    }

    @Test
    fun activityTrackerFiltersByBountyId() {
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
        composeTestRule.onNodeWithText("User1").assertIsDisplayed()
        composeTestRule.onAllNodesWithText("User2").assertCountEquals(0)
    }
}

