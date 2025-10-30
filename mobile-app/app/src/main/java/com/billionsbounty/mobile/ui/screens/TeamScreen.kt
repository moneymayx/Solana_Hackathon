package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// Data classes matching web API
data class Team(
    val id: Int,
    val name: String,
    val description: String,
    val leader_id: Int,
    val max_members: Int,
    val total_pool: Double,
    val total_attempts: Int,
    val member_count: Int,
    val created_at: String,
    val invite_code: String? = null
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TeamScreen(
    onBackClick: () -> Unit
) {
    var teams by remember { mutableStateOf<List<Team>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }
    var showCreateDialog by remember { mutableStateOf(false) }
    var showJoinDialog by remember { mutableStateOf(false) }
    var inviteCode by remember { mutableStateOf("") }
    var userId by remember { mutableStateOf(1) } // Mock user ID
    
    val scope = rememberCoroutineScope()
    
    // Fetch teams from API
    fun fetchTeams() {
        scope.launch {
            try {
                loading = true
                
                // Simulate API call - In production, call: GET http://localhost:8000/api/teams/browse?limit=50
                delay(1000)
                
                // Mock data
                teams = listOf(
                    Team(
                        id = 1,
                        name = "Elite Jailbreakers",
                        description = "Top-tier prompt engineers working together",
                        leader_id = 1,
                        max_members = 5,
                        total_pool = 250.50,
                        total_attempts = 120,
                        member_count = 5,
                        created_at = "2024-10-25T10:00:00Z",
                        invite_code = "ELITE123"
                    ),
                    Team(
                        id = 2,
                        name = "AI Hackers United",
                        description = "Collaborative research on AI safety",
                        leader_id = 2,
                        max_members = 10,
                        total_pool = 500.00,
                        total_attempts = 250,
                        member_count = 8,
                        created_at = "2024-10-24T15:30:00Z",
                        invite_code = "AIHACK99"
                    ),
                    Team(
                        id = 3,
                        name = "Prompt Masters",
                        description = "Learning and sharing the best prompting techniques",
                        leader_id = 3,
                        max_members = 5,
                        total_pool = 175.25,
                        total_attempts = 85,
                        member_count = 3,
                        created_at = "2024-10-26T08:00:00Z",
                        invite_code = "PROMPT42"
                    ),
                    Team(
                        id = 4,
                        name = "Bounty Hunters",
                        description = "Focused on maximizing bounty rewards",
                        leader_id = 4,
                        max_members = 7,
                        total_pool = 350.75,
                        total_attempts = 180,
                        member_count = 6,
                        created_at = "2024-10-23T12:00:00Z",
                        invite_code = "BOUNTY77"
                    ),
                    Team(
                        id = 5,
                        name = "Research Collective",
                        description = "Academic approach to AI jailbreaking",
                        leader_id = 5,
                        max_members = 8,
                        total_pool = 425.00,
                        total_attempts = 220,
                        member_count = 7,
                        created_at = "2024-10-22T09:30:00Z",
                        invite_code = "RESEARCH1"
                    )
                )
                
                loading = false
            } catch (e: Exception) {
                loading = false
                // Handle error
            }
        }
    }
    
    // Load teams on first composition
    LaunchedEffect(Unit) {
        fetchTeams()
    }
    
    Scaffold(
        topBar = {
            WebStyleHeader(
                onScrollToHome = onBackClick,
                onScrollToBounties = onBackClick,
                onScrollToHowItWorks = onBackClick,
                onScrollToFAQs = onBackClick,
                onNavigateToStaking = {}
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Teams",
                            style = MaterialTheme.typography.headlineLarge,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF0F172A)
                        )
                        Text(
                            text = "Collaborate and share resources",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFF64748B)
                        )
                    }
                    
                    Button(
                        onClick = { showCreateDialog = true },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981))
                    ) {
                        Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Create")
                    }
                }
            }
            
            // Join by Invite Code
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(4.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "Join Team by Invite Code",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedTextField(
                                value = inviteCode,
                                onValueChange = { inviteCode = it.uppercase() },
                                modifier = Modifier.weight(1f),
                                placeholder = { Text("ABC12XYZ", fontSize = 14.sp) },
                                singleLine = true,
                                textStyle = androidx.compose.ui.text.TextStyle(
                                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                                )
                            )
                            Button(
                                onClick = {
                                    // TODO: Call API to join by code
                                    // POST http://localhost:8000/api/teams/join/by-code
                                    showJoinDialog = true
                                },
                                enabled = inviteCode.isNotEmpty()
                            ) {
                                Text("Join")
                            }
                        }
                    }
                }
            }
            
            // Stats Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFDCEFF)),
                    elevation = CardDefaults.cardElevation(4.dp),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceAround
                    ) {
                        StatColumn("Active Teams", teams.size.toString())
                        StatColumn("Total Members", teams.sumOf { it.member_count }.toString())
                        StatColumn("Total Pool", "$${String.format("%,.0f", teams.sumOf { it.total_pool })}")
                    }
                }
            }
            
            // Teams List Header
            item {
                Text(
                    text = "Browse Teams",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Loading State
            if (loading) {
                items(3) {
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF1F5F9))
                    ) {
                        // Shimmer effect placeholder
                    }
                }
            } else {
                // Teams List
                items(teams) { team ->
                    TeamCard(
                        team = team,
                        onJoinClick = {
                            // TODO: Call join API
                            // POST http://localhost:8000/api/teams/{teamId}/join
                        },
                        onViewClick = {
                            // TODO: Navigate to team detail
                        }
                    )
                }
            }
            
            // Empty State
            if (!loading && teams.isEmpty()) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF8FAFC))
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(32.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("👥", fontSize = 48.sp)
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "No teams found",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                "Create the first team!",
                                style = MaterialTheme.typography.bodyMedium,
                                color = Color(0xFF64748B)
                            )
                        }
                    }
                }
            }
        }
    }
    
    // Create Team Dialog
    if (showCreateDialog) {
        CreateTeamDialog(
            onDismiss = { showCreateDialog = false },
            onConfirm = { teamName, teamDescription ->
                scope.launch {
                    // TODO: Call API to create team
                    // POST http://localhost:8000/api/teams/create
                    // { leader_id, name, description, max_members, is_public }
                    showCreateDialog = false
                    fetchTeams()
                }
            }
        )
    }
}

@Composable
fun TeamCard(
    team: Team,
    onJoinClick: () -> Unit,
    onViewClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(4.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = team.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF0F172A)
                    )
                    if (team.description.isNotEmpty()) {
                        Text(
                            text = team.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFF64748B),
                            fontSize = 12.sp
                        )
                    }
                }
                
                // Invite Code Badge
                if (!team.invite_code.isNullOrEmpty()) {
                    Surface(
                        color = Color(0xFFDCEFF),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            team.invite_code,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            fontSize = 10.sp,
                            fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                            color = Color(0xFF1E40AF),
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
            
            // Stats
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                TeamStat(Icons.Default.People, "${team.member_count}/${team.max_members}")
                TeamStat(Icons.Default.AttachMoney, "$${String.format("%.2f", team.total_pool)}")
                TeamStat(Icons.Default.TrendingUp, "${team.total_attempts}")
            }
            
            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onViewClick,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("View Details")
                }
                
                val canJoin = team.member_count < team.max_members
                Button(
                    onClick = onJoinClick,
                    modifier = Modifier.weight(1f),
                    enabled = canJoin,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF3B82F6),
                        disabledContainerColor = Color(0xFFE5E7EB)
                    )
                ) {
                    if (canJoin) {
                        Icon(Icons.Default.PersonAdd, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Join")
                    } else {
                        Text("Full", fontSize = 12.sp)
                    }
                }
            }
        }
    }
}

@Composable
fun TeamStat(icon: androidx.compose.ui.graphics.vector.ImageVector, value: String) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(14.dp),
            tint = Color(0xFF64748B)
        )
        Text(
            text = value,
            fontSize = 12.sp,
            color = Color(0xFF64748B),
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun StatColumn(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF2563EB)
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = Color(0xFF64748B)
        )
    }
}

@Composable
fun CreateTeamDialog(
    onDismiss: () -> Unit,
    onConfirm: (name: String, description: String) -> Unit
) {
    var teamName by remember { mutableStateOf("") }
    var teamDescription by remember { mutableStateOf("") }
    
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text("Create New Team", fontWeight = FontWeight.Bold)
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedTextField(
                    value = teamName,
                    onValueChange = { teamName = it },
                    label = { Text("Team Name *") },
                    placeholder = { Text("e.g., Elite Jailbreakers") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                OutlinedTextField(
                    value = teamDescription,
                    onValueChange = { teamDescription = it },
                    label = { Text("Description (Optional)") },
                    placeholder = { Text("What's your team about?") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3,
                    maxLines = 5
                )
                
                Text(
                    "You'll receive an invite code to share with members.",
                    fontSize = 11.sp,
                    color = Color(0xFF64748B)
                )
            }
        },
        confirmButton = {
            Button(
                onClick = { onConfirm(teamName, teamDescription) },
                enabled = teamName.isNotBlank(),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF10B981))
            ) {
                Text("Create Team")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancel")
            }
        }
    )
}
