package com.billionsbounty.mobile.ui.components.gamification

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.billionsbounty.mobile.data.api.PowerUp
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Composable
fun PowerUpsInventory(
    powerUps: List<PowerUp>,
    modifier: Modifier = Modifier,
    onActivate: (Int) -> Unit = {}
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
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Power-Ups",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                
                Icon(
                    imageVector = Icons.Default.Bolt,
                    contentDescription = "Power-Ups",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            if (powerUps.isEmpty()) {
                Text(
                    text = "No power-ups available",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    modifier = Modifier.padding(vertical = 16.dp)
                )
            } else {
                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(powerUps) { powerUp ->
                        PowerUpItem(
                            powerUp = powerUp,
                            onActivate = { onActivate(powerUp.id) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun PowerUpItem(
    powerUp: PowerUp,
    onActivate: () -> Unit
) {
    val isActive = powerUp.is_active
    val isUsed = powerUp.is_used
    val canActivate = !isActive && !isUsed
    
    Card(
        onClick = if (canActivate) onActivate else {},
        modifier = Modifier.width(140.dp),
        colors = CardDefaults.cardColors(
            containerColor = when {
                isActive -> MaterialTheme.colorScheme.primaryContainer
                isUsed -> MaterialTheme.colorScheme.surfaceVariant
                else -> MaterialTheme.colorScheme.surface
            }
        ),
        shape = RoundedCornerShape(12.dp),
        enabled = canActivate
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            // Power-up icon
            Icon(
                imageVector = Icons.Default.Bolt,
                contentDescription = powerUp.name,
                tint = if (isActive) {
                    Color(0xFFFF6B35)
                } else {
                    MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                },
                modifier = Modifier.size(32.dp)
            )
            
            // Power-up name
            Text(
                text = powerUp.name,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                maxLines = 2
            )
            
            // Multiplier
            Text(
                text = "${powerUp.multiplier}x",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.primary
            )
            
            // Duration
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Timer,
                    contentDescription = "Duration",
                    modifier = Modifier.size(12.dp),
                    tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
                Text(
                    text = "${powerUp.duration_minutes}m",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            
            // Status
            when {
                isActive -> {
                    powerUp.expires_at?.let { expiresAt ->
                        Text(
                            text = "Active until ${formatTime(expiresAt)}",
                            style = MaterialTheme.typography.labelSmall,
                            color = Color(0xFF4CAF50)
                        )
                    }
                }
                isUsed -> {
                    Text(
                        text = "Used",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                    )
                }
                else -> {
                    Button(
                        onClick = onActivate,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.primary
                        )
                    ) {
                        Text("Activate")
                    }
                }
            }
        }
    }
}

private fun formatTime(timeString: String): String {
    return try {
        val formatter = DateTimeFormatter.ISO_DATE_TIME
        val dateTime = LocalDateTime.parse(timeString, formatter)
        "${dateTime.hour}:${dateTime.minute.toString().padStart(2, '0')}"
    } catch (e: Exception) {
        timeString
    }
}

