package com.billionsbounty.mobile.utils

import android.content.Context
import com.billionsbounty.mobile.ui.components.ActivityStorage
import com.billionsbounty.mobile.ui.components.ActivityType
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Helper class for tracking activities across the app
 * Similar to frontend's addActivity() function
 */
object ActivityHelper {
    
    /**
     * Track a question activity
     * @param context Android context
     * @param bountyId The bounty ID
     * @param username User's display name
     * @param bountyName Optional bounty name
     * @param isFirstQuestion Whether this is the user's first question
     */
    fun trackQuestion(
        context: Context,
        bountyId: Int,
        username: String,
        bountyName: String? = null,
        isFirstQuestion: Boolean = false
    ) {
        if (username.isBlank()) return // Skip if no username set
        
        val activityType = if (isFirstQuestion) {
            ActivityType.FIRST_QUESTION
        } else {
            ActivityType.QUESTION
        }
        
        ActivityStorage.addActivity(
            context = context,
            bountyId = bountyId,
            username = username,
            activityType = activityType,
            bountyName = bountyName
        )
    }
    
    /**
     * Track NFT redemption activity
     */
    fun trackNftRedeem(
        context: Context,
        bountyId: Int,
        username: String
    ) {
        if (username.isBlank()) return
        
        ActivityStorage.addActivity(
            context = context,
            bountyId = bountyId,
            username = username,
            activityType = ActivityType.NFT_REDEEM
        )
    }
    
    /**
     * Track referral activity
     */
    fun trackReferral(
        context: Context,
        bountyId: Int,
        username: String
    ) {
        if (username.isBlank()) return
        
        ActivityStorage.addActivity(
            context = context,
            bountyId = bountyId,
            username = username,
            activityType = ActivityType.REFERRAL
        )
    }
    
    /**
     * Get username from user profile (async)
     * Returns null if username not set or if profile fetch fails
     */
    suspend fun getUsername(
        context: Context,
        walletAddress: String?,
        apiRepository: com.billionsbounty.mobile.data.repository.ApiRepository
    ): String? {
        if (walletAddress.isNullOrBlank()) return null
        
        return try {
            val response = apiRepository.getUserProfile(walletAddress)
            if (response.isSuccessful) {
                val profile = response.body()
                // Get display_name or username from UserProfileResponse
                profile?.let {
                    val displayName = it.display_name ?: it.username
                    // If display_name is not available, return null (user should set username)
                    displayName?.takeIf { name -> name.isNotBlank() }
                }
            } else {
                null
            }
        } catch (e: Exception) {
            android.util.Log.e("ActivityHelper", "Error fetching user profile", e)
            null
        }
    }
    
    /**
     * Check if user has asked a question before (to determine first question)
     */
    fun isFirstQuestion(
        context: Context,
        bountyId: Int,
        username: String
    ): Boolean {
        val activities = ActivityStorage.getActivities(context, bountyId)
        // Check if there are any previous question activities for this user
        return activities.none { activity ->
            activity.username == username && 
            (activity.message.contains("asked") || activity.message.contains("question"))
        }
    }
}

