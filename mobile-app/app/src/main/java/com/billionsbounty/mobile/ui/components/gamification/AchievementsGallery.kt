package com.billionsbounty.mobile.ui.components.gamification

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.billionsbounty.mobile.data.api.Achievement

@Composable
fun AchievementsGallery(
    achievements: List<Achievement>,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Achievements",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            
            if (achievements.isEmpty()) {
                Text(
                    text = "No achievements unlocked yet",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 16.dp),
                    textAlign = TextAlign.Center
                )
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Fixed(3),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                    modifier = Modifier.height((achievements.size / 3 + 1) * 100.dp)
                ) {
                    items(achievements) { achievement ->
                        AchievementItem(achievement = achievement)
                    }
                }
            }
        }
    }
}

@Composable
fun AchievementItem(
    achievement: Achievement
) {
    val rarityColor = when (achievement.rarity.lowercase()) {
        "legendary" -> Color(0xFFFFD700)
        "epic" -> Color(0xFF9C27B0)
        "rare" -> Color(0xFF2196F3)
        "uncommon" -> Color(0xFF4CAF50)
        else -> MaterialTheme.colorScheme.primary
    }
    
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        // Achievement icon/badge
        Surface(
            modifier = Modifier.size(64.dp),
            shape = CircleShape,
            color = rarityColor.copy(alpha = 0.2f),
            border = androidx.compose.foundation.BorderStroke(2.dp, rarityColor)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = achievement.icon,
                    fontSize = 32.sp
                )
            }
        }
        
        // Achievement name
        Text(
            text = achievement.name,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            maxLines = 2,
            modifier = Modifier.fillMaxWidth()
        )
        
        // Rarity badge
        Surface(
            shape = RoundedCornerShape(4.dp),
            color = rarityColor.copy(alpha = 0.1f)
        ) {
            Text(
                text = achievement.rarity.uppercase(),
                style = MaterialTheme.typography.labelSmall,
                color = rarityColor,
                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
            )
        }
    }
}

