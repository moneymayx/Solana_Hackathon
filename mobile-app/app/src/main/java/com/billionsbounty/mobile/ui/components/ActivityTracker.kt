package com.billionsbounty.mobile.ui.components

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.ui.draw.alpha
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.billionsbounty.mobile.BuildConfig
import kotlinx.coroutines.delay
import java.util.UUID

/**
 * Activity data model matching frontend ActivityTracker
 */
data class Activity(
    val id: String,
    val username: String,
    val message: String,
    val timestamp: Long,
    val bountyId: Int
)

/**
 * Activity type enum matching frontend addActivity function
 */
enum class ActivityType {
    QUESTION,
    NFT_REDEEM,
    REFERRAL,
    FIRST_QUESTION
}

/**
 * Activity Tracker Component
 * 
 * Displays rotating activity feed showing user actions (questions, NFT redemptions, referrals)
 * Similar to frontend ActivityTracker.tsx but uses SharedPreferences instead of localStorage
 * 
 * @param bountyId The bounty ID to filter activities by
 * @param enabled Whether activity tracker is enabled (can be controlled by feature flag)
 */
@Composable
fun ActivityTracker(
    bountyId: Int,
    enabled: Boolean = true
) {
    val context = LocalContext.current
    val activities = rememberActivities(bountyId, context, enabled)
    
    if (!enabled || activities.isEmpty()) {
        return
    }
    
    val currentIndex = remember { mutableStateOf(0) }
    
    // Auto-cycle through activities every 4 seconds (matching frontend)
    LaunchedEffect(activities.size) {
        while (activities.isNotEmpty()) {
            delay(4000) // 4 seconds per activity (matching frontend ACTIVITY_CYCLE_DURATION)
            currentIndex.value = (currentIndex.value + 1) % activities.size
        }
    }
    
    // Refresh activities every 3 seconds to pick up new ones
    LaunchedEffect(bountyId) {
        while (enabled) {
            delay(3000)
            // Activities will auto-refresh via rememberActivities
        }
    }
    
    val currentActivity = activities.getOrNull(currentIndex.value)
    
    currentActivity?.let { activity ->
        ActivityCard(activity = activity)
    }
}

/**
 * Remember and manage activities from SharedPreferences
 */
@Composable
fun rememberActivities(
    bountyId: Int,
    context: Context,
    enabled: Boolean
): List<Activity> {
    var activities by remember { mutableStateOf<List<Activity>>(emptyList()) }
    
    LaunchedEffect(bountyId, enabled) {
        if (!enabled) {
            activities = emptyList()
            return@LaunchedEffect
        }
        
        // Load activities
        val loaded = ActivityStorage.getActivities(context, bountyId)
        activities = loaded
        
        // Refresh every 3 seconds to pick up new activities
        while (enabled) {
            delay(3000)
            val refreshed = ActivityStorage.getActivities(context, bountyId)
            if (refreshed != activities) {
                activities = refreshed
            }
        }
    }
    
    return activities
}

/**
 * Activity card composable
 */
@Composable
fun ActivityCard(activity: Activity) {
    val animatedAlpha by animateFloatAsState(
        targetValue = 1f,
        animationSpec = tween(durationMillis = 500),
        label = "activityAlpha"
    )
    
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 12.dp)
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .alpha(animatedAlpha),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
            ),
            shape = RoundedCornerShape(12.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Pulsing indicator dot
                val infiniteTransition = rememberInfiniteTransition(label = "pulse")
                val pulseAlpha by infiniteTransition.animateFloat(
                    initialValue = 0.5f,
                    targetValue = 1f,
                    animationSpec = infiniteRepeatable(
                        animation = tween(1000, easing = FastOutSlowInEasing),
                        repeatMode = RepeatMode.Reverse
                    ),
                    label = "pulse"
                )
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .alpha(pulseAlpha)
                        .background(MaterialTheme.colorScheme.primary)
                )
                
                // Username (bold)
                Text(
                    text = activity.username,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                
                // Message
                Text(
                    text = activity.message,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
                )
            }
        }
    }
}

/**
 * Activity Storage (Android equivalent of localStorage)
 * Uses SharedPreferences to persist activities
 */
object ActivityStorage {
    private const val PREFS_NAME = "bounty_activities"
    private const val KEY_ACTIVITIES = "activities"
    private const val ACTIVITY_MAX_AGE = 24 * 60 * 60 * 1000L // 24 hours in milliseconds
    private const val MAX_ACTIVITIES = 100 // Keep only last 100 activities
    
    /**
     * Get activities filtered by bounty ID and last 24 hours
     */
    fun getActivities(context: Context, bountyId: Int): List<Activity> {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val activitiesJson = prefs.getString(KEY_ACTIVITIES, null) ?: return emptyList()
        
        try {
            val allActivities = parseActivitiesJson(activitiesJson)
            val now = System.currentTimeMillis()
            
            // Filter: same bounty_id and within last 24 hours
            return allActivities.filter { activity ->
                activity.bountyId == bountyId &&
                (now - activity.timestamp) < ACTIVITY_MAX_AGE
            }
        } catch (e: Exception) {
            android.util.Log.e("ActivityStorage", "Error reading activities", e)
            return emptyList()
        }
    }
    
    /**
     * Add a new activity
     */
    fun addActivity(
        context: Context,
        bountyId: Int,
        username: String,
        activityType: ActivityType,
        bountyName: String? = null
    ) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        
        val messages = mapOf(
            ActivityType.QUESTION to "just asked ${bountyName ?: "a question"}",
            ActivityType.NFT_REDEEM to "redeemed their NFT",
            ActivityType.REFERRAL to "referred a new friend",
            ActivityType.FIRST_QUESTION to "just asked their first question"
        )
        
        val activity = Activity(
            id = "${System.currentTimeMillis()}-${UUID.randomUUID()}",
            username = username,
            message = messages[activityType] ?: "",
            timestamp = System.currentTimeMillis(),
            bountyId = bountyId
        )
        
        try {
            // Get existing activities
            val existingJson = prefs.getString(KEY_ACTIVITIES, null)
            val allActivities = if (existingJson != null) {
                parseActivitiesJson(existingJson)
            } else {
                mutableListOf()
            }
            
            // Add new activity at the beginning
            allActivities.add(0, activity)
            
            // Keep only last MAX_ACTIVITIES
            val trimmed = if (allActivities.size > MAX_ACTIVITIES) {
                allActivities.take(MAX_ACTIVITIES)
            } else {
                allActivities
            }
            
            // Save back to SharedPreferences
            val jsonString = activitiesToJson(trimmed)
            prefs.edit()
                .putString(KEY_ACTIVITIES, jsonString)
                .apply()
        } catch (e: Exception) {
            android.util.Log.e("ActivityStorage", "Error saving activity", e)
        }
    }

    /**
     * Developer helper to seed demo activities without touching production builds.
     * Uses curated entries to keep devnet sessions lively when real traffic is absent.
     */
    fun seedDevActivities(
        context: Context,
        bountyId: Int,
        bountyName: String? = null
    ) {
        if (!BuildConfig.ENABLE_ACTIVITY_DEV_SEED) return

        try {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val existingJson = prefs.getString(KEY_ACTIVITIES, null)
            val existingActivities = if (existingJson != null) {
                parseActivitiesJson(existingJson)
            } else {
                mutableListOf()
            }

            val now = System.currentTimeMillis()
            val seedTemplates = listOf(
                DevSeedTemplate(
                    username = "solana-hacker",
                    message = "just asked ${bountyName ?: "a question"}",
                    offsetMs = 30_000L
                ),
                DevSeedTemplate(
                    username = "nft-whale",
                    message = "redeemed their NFT",
                    offsetMs = 90_000L
                ),
                DevSeedTemplate(
                    username = "referral-pro",
                    message = "referred a new friend",
                    offsetMs = 150_000L
                ),
                DevSeedTemplate(
                    username = "newcomer",
                    message = "just asked their first question",
                    offsetMs = 210_000L
                )
            )

            val seededActivities = seedTemplates.mapIndexed { index, template ->
                Activity(
                    id = "${now}-${index}-${UUID.randomUUID()}",
                    username = template.username,
                    message = template.message,
                    timestamp = now - template.offsetMs,
                    bountyId = bountyId
                )
            }

            val combined = (seededActivities + existingActivities).take(MAX_ACTIVITIES)
            val jsonString = activitiesToJson(combined)

            prefs.edit()
                .putString(KEY_ACTIVITIES, jsonString)
                .apply()
        } catch (e: Exception) {
            android.util.Log.e("ActivityStorage", "Error seeding dev activities", e)
        }
    }
    
    /**
     * Parse JSON string to list of activities
     */
    private fun parseActivitiesJson(json: String): MutableList<Activity> {
        // Simple JSON parsing (for production, consider using a proper JSON library)
        val activities = mutableListOf<Activity>()
        
        // Remove outer brackets
        val content = json.trim().removePrefix("[").removeSuffix("]")
        if (content.isBlank()) return activities
        
        // Split by objects
        val objects = content.split("},").map { it.trim() }
        
        objects.forEach { obj ->
            try {
                val cleanObj = obj.removePrefix("{").removeSuffix("}").trim()
                val fields = cleanObj.split(",").associate { pair ->
                    val (key, value) = pair.split(":", limit = 2)
                    key.trim().removeSurrounding("\"") to value.trim().removeSurrounding("\"")
                }
                
                activities.add(
                    Activity(
                        id = fields["id"] ?: UUID.randomUUID().toString(),
                        username = fields["username"] ?: "",
                        message = fields["message"] ?: "",
                        timestamp = fields["timestamp"]?.toLongOrNull() ?: System.currentTimeMillis(),
                        bountyId = fields["bountyId"]?.toIntOrNull() ?: 0
                    )
                )
            } catch (e: Exception) {
                android.util.Log.w("ActivityStorage", "Error parsing activity: $obj", e)
            }
        }
        
        return activities
    }
    
    /**
     * Convert activities list to JSON string
     */
    private fun activitiesToJson(activities: List<Activity>): String {
        val jsonObjects = activities.map { activity ->
            """
            {
                "id": "${activity.id}",
                "username": "${activity.username.replace("\"", "\\\"")}",
                "message": "${activity.message.replace("\"", "\\\"")}",
                "timestamp": ${activity.timestamp},
                "bountyId": ${activity.bountyId}
            }
            """.trimIndent()
        }
        return "[${jsonObjects.joinToString(",")}]"
    }
    
    /**
     * Clear all activities (useful for testing or reset)
     */
    fun clearActivities(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().remove(KEY_ACTIVITIES).apply()
    }

    private data class DevSeedTemplate(
        val username: String,
        val message: String,
        val offsetMs: Long
    )
}

