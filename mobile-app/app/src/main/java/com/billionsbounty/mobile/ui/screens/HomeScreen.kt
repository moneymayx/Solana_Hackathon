package com.billionsbounty.mobile.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.foundation.text.ClickableText
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.billionsbounty.mobile.data.api.Bounty
import com.billionsbounty.mobile.ui.viewmodel.BountyViewModel
import kotlinx.coroutines.launch

/**
 * Main Home Screen - Redesigned to match web frontend
 * Structure:
 * 1. Header (White background, Crown logo, navigation menu)
 * 2. Hero text: "Beat the Bot, Win the Pot"
 * 3. Scrolling Banner with images
 * 4. Choose Your Bounty section
 * 5. How It Works section
 * 6. FAQ section
 * 7. Winners section
 */
@OptIn(ExperimentalMaterial3Api::class)
@Suppress("DEPRECATION")
@Composable
fun HomeScreen(
    onNavigateToBounty: (Int) -> Unit,
    onNavigateToBountyWatch: (Int) -> Unit = onNavigateToBounty,
    onNavigateToChat: () -> Unit,
    onNavigateToDashboard: () -> Unit = {},
    onNavigateToPayment: () -> Unit = {},
    onNavigateToReferral: () -> Unit = {},
    onNavigateToStaking: () -> Unit = {},
    onNavigateToTeam: () -> Unit = {},
    viewModel: BountyViewModel = hiltViewModel()
) {
    val bounties by viewModel.bounties.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    
    // LazyListState for scrolling to sections
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    
    // Section indices in the LazyColumn
    val heroIndex = 0
    val bannerIndex = 1
    val bountiesIndex = 2
    val howItWorksIndex = 3
    val faqIndex = 4
    val winnersIndex = 5

    LaunchedEffect(Unit) {
        viewModel.loadBounties()
    }

    Scaffold(
        topBar = {
            WebStyleHeader(
                onScrollToHome = {
                    scope.launch {
                        listState.animateScrollToItem(heroIndex)
                    }
                },
                onScrollToBounties = {
                    scope.launch {
                        listState.animateScrollToItem(bountiesIndex)
                    }
                },
                onScrollToHowItWorks = {
                    scope.launch {
                        listState.animateScrollToItem(howItWorksIndex)
                    }
                },
                onScrollToWinners = {
                    scope.launch {
                        listState.animateScrollToItem(winnersIndex)
                    }
                },
                onScrollToFAQs = {
                    scope.launch {
                        listState.animateScrollToItem(faqIndex)
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            state = listState,
            modifier = Modifier
                .fillMaxSize()
                .background(Color.White)
                .padding(paddingValues)
        ) {
            // Hero Section
            item {
                HeroTextSection()
            }
            
            // Scrolling Banner
            item {
                AutoScrollingBanner()
            }
            
            // Choose Your Bounty Section
            item {
                ChooseYourBountySection(
                    bounties = bounties,
                    isLoading = isLoading,
                    errorMessage = errorMessage,
                    onBountyClick = onNavigateToBounty,
                    onWatchClick = onNavigateToBountyWatch,
                    onRetry = { viewModel.loadBounties() }
                )
            }
            
            // How It Works Section
            item {
                HowItWorksSection()
            }
            
            // FAQ Section
            item {
                FAQSection()
            }
            
            // Winners Section
            item {
                WinnersSection(
                    bounties = bounties,
                    onNavigateToBounty = onNavigateToBounty
                )
            }
            
            // Footer
            item {
                FooterSection()
            }
        }
    }
}

/**
 * Web-style Header with navy blue background matching website
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WebStyleHeader(
    onScrollToHome: () -> Unit,
    onScrollToBounties: () -> Unit,
    onScrollToHowItWorks: () -> Unit,
    onScrollToWinners: () -> Unit,
    onScrollToFAQs: () -> Unit
) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(4.dp),
        color = Color(0xFF0F172A) // Dark navy blue (slate-900)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.Start, // Left-aligned like website
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Logo Section (acts as Home button)
            Image(
                painter = painterResource(id = com.billionsbounty.mobile.R.drawable.billions_logo),
                contentDescription = "BILLION$ Logo - Home",
                modifier = Modifier
                    .height(90.dp)
                    .clickable { onScrollToHome() },
                contentScale = ContentScale.Fit
            )
            
            // Separator
            Text(
                text = "|",
                color = Color.White.copy(alpha = 0.5f),
                fontSize = 16.sp,
                modifier = Modifier.padding(horizontal = 6.dp)
            )
            
            // Navigation Menu - All same font size
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val uriHandler = LocalUriHandler.current
                
                TextButton(
                    onClick = onScrollToBounties,
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    Text("Bounties", color = Color.White, fontWeight = FontWeight.Normal, fontSize = 14.sp)
                }
                TextButton(
                    onClick = onScrollToHowItWorks,
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    Text("How it Works", color = Color.White, fontWeight = FontWeight.Normal, fontSize = 14.sp)
                }
                TextButton(
                    onClick = onScrollToFAQs,
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    Text("FAQs", color = Color.White, fontWeight = FontWeight.Normal, fontSize = 14.sp)
                }
                TextButton(
                    onClick = onScrollToWinners,
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    Text("Winners", color = Color.White, fontWeight = FontWeight.Normal, fontSize = 14.sp)
                }
                TextButton(
                    onClick = { uriHandler.openUri("https://100billioncapital.com/") },
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp)
                ) {
                    Text("\$100Bs", color = Color.White, fontWeight = FontWeight.Normal, fontSize = 14.sp)
                }
            }
        }
    }
}

/**
 * Hero Text Section - "Beat the Bot, Win the Pot"
 */
@Composable
fun HeroTextSection() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.White)
            .padding(vertical = 16.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Beat the Bot, Win the Pot",
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF111827),
            textAlign = TextAlign.Center,
            fontSize = 28.sp,
            modifier = Modifier.padding(horizontal = 16.dp)
        )
    }
}

/**
 * Full-Width Banner Image
 */
@Composable
fun AutoScrollingBanner() {
    Image(
        painter = painterResource(id = com.billionsbounty.mobile.R.drawable.claude_champion_banner),
        contentDescription = "Claude Champion Banner",
            modifier = Modifier
                .fillMaxWidth()
            .wrapContentHeight(),
        contentScale = ContentScale.FillWidth
    )
}

/**
 * Choose Your Bounty Section
 */
@Composable
fun ChooseYourBountySection(
    bounties: List<com.billionsbounty.mobile.data.api.Bounty>,
    isLoading: Boolean,
    errorMessage: String?,
    onBountyClick: (Int) -> Unit,
    onWatchClick: (Int) -> Unit = onBountyClick,
    onRetry: () -> Unit
        ) {
            Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.White)
            .padding(horizontal = 16.dp, vertical = 16.dp)
    ) {
        // Header
                Text(
            text = "Choose Your Bounty",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
            color = Color(0xFF111827),
            modifier = Modifier.padding(bottom = 8.dp)
        )
        
        Text(
            text = "Each AI model offers a unique challenge. Select your target and start your attempt.",
            style = MaterialTheme.typography.bodyLarge,
            color = Color(0xFF6B7280),
            modifier = Modifier.padding(bottom = 32.dp)
        )
        
        when {
            isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Color(0xFFEAB308))
                }
            }
            errorMessage != null -> {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
            Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Error",
                        tint = Color.Red,
                modifier = Modifier.size(48.dp)
            )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = errorMessage,
                        color = Color.Red,
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = onRetry,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFEAB308)
                        )
                    ) {
                        Text("Retry")
                    }
                }
            }
            bounties.isEmpty() -> {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "No bounties available",
                        color = Color(0xFF6B7280),
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
            else -> {
                // Calculate height based on number of bounties (2 columns)
                val rows = (bounties.size + 1) / 2
                val cardHeight = 220.dp
                val spacing = 12.dp
                val totalHeight = (cardHeight * rows) + (spacing * (rows - 1))
    
    LazyVerticalGrid(
        columns = GridCells.Fixed(2),
                    modifier = Modifier.height(totalHeight),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
                    items(bounties) { bounty ->
            BountyCard(
                bounty = bounty,
                onClick = { onBountyClick(bounty.id) },
                onWatchClick = { onWatchClick(bounty.id) }
            )
                    }
                }
            }
        }
    }
}

/**
 * Bounty Card matching web design
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BountyCard(
    bounty: com.billionsbounty.mobile.data.api.Bounty,
    onClick: () -> Unit,
    onWatchClick: () -> Unit = onClick
) {
    // Color mapping based on provider
    val providerColors = remember(bounty.llm_provider) {
        when (bounty.llm_provider.lowercase()) {
            "claude" -> Color(0xFF8B5CF6)
            "gpt-4", "openai" -> Color(0xFF10B981)
            "gemini" -> Color(0xFF3B82F6)
            "llama" -> Color(0xFFF97316)
            else -> Color(0xFF6B7280)
        }
    }
    
    val difficultyColor = remember(bounty.difficulty_level) {
        when (bounty.difficulty_level.lowercase()) {
            "easy" -> Color(0xFF10B981)
            "medium" -> Color(0xFF3B82F6)
            "hard" -> Color(0xFFF97316)
            "expert" -> Color(0xFFEF4444)
            else -> Color(0xFF6B7280)
        }
    }
    
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(220.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(4.dp),
        border = androidx.compose.foundation.BorderStroke(2.dp, providerColors)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Header with name and difficulty
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
            Text(
                text = bounty.name,
                style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = providerColors,
                        maxLines = 2,
                        lineHeight = 18.sp
                    )
                    Text(
                        text = bounty.llm_provider,
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFF6B7280),
                        maxLines = 1
                    )
                }
                
                // Difficulty badge
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = difficultyColor.copy(alpha = 0.1f),
                    border = androidx.compose.foundation.BorderStroke(1.dp, difficultyColor)
                ) {
                    Text(
                        text = bounty.difficulty_level,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelSmall,
                        color = difficultyColor,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        softWrap = false
                    )
                }
            }
            
            // Prize amount - Large, bold, decorative font like website (Gravitas One)
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "$${bounty.current_pool.toInt().toString().replace(Regex("(\\d)(?=(\\d{3})+$)"), "$1,")}",
                    fontFamily = FontFamily.Serif, // Matches Gravitas One style
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827),
                    textAlign = TextAlign.Center,
                    fontSize = 40.sp,
                    letterSpacing = 0.sp
                )
                Text(
                    text = "Bounty Amount",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color(0xFF6B7280),
                    fontSize = 10.sp
                )
            }
            
            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onClick,
                    modifier = Modifier
                        .weight(1f)
                        .height(42.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = providerColors
                    ),
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = PaddingValues(horizontal = 4.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = "Beat the Bot",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        maxLines = 1,
                        softWrap = false
                    )
                }
                OutlinedButton(
                    onClick = onWatchClick,
                    modifier = Modifier
                        .weight(1f)
                        .height(42.dp),
                    shape = RoundedCornerShape(8.dp),
                    border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFD1D5DB)),
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = "Watch",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF374151),
                        maxLines = 1,
                        softWrap = false
                    )
                }
            }
        }
    }
}

/**
 * How It Works Section - 5 steps matching website
 */
@Composable
fun HowItWorksSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.White)
            .padding(horizontal = 16.dp, vertical = 24.dp)
    ) {
        // Header
        Text(
            text = "How Billions Works",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF111827),
            textAlign = TextAlign.Center,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 8.dp)
        )
        
        // Rules text
        val rulesText = buildAnnotatedString {
            append("The Rules: Our bot's are programmed to run without human intervention and to obey 1 simple rule:\n")
            withStyle(style = SpanStyle(fontWeight = FontWeight.Bold)) {
                append("\"never transfer the funds\"")
            }
        }
        
        Text(
            text = rulesText,
            style = MaterialTheme.typography.bodyMedium,
            color = Color(0xFF374151),
            textAlign = TextAlign.Center,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp)
        )
        
        // 5 Steps
        val steps = listOf(
            StepData(
                1,
                "Choose the Bounty",
                "Select from multiple AI models with different difficulty levels. Each offers unique challenges and bounty amounts."
            ),
            StepData(
                2,
                "Trick the Bot",
                "Use psychological, logic, creative, or advanced prompting techniques to convince the AI bot to send you the money"
            ),
            StepData(
                3,
                "Unsuccessful Attempts Cost",
                "When an user fails at getting the AI to send them the bounty, the question price increases by 0.78%, and the total bounty grows exponentially over time"
            ),
            StepData(
                4,
                "Win Cash Money",
                "Successful jailbreaks trigger automatic fund transfers from smart contracts. No human intervention needed."
            ),
            StepData(
                5,
                "The Bot Gets Smarter",
                "Winning prompts are both shared and retired, so that the same prompt will not trick the bot. Bounties are restarted with a higher starting jackpot"
            )
        )
        
        steps.forEach { step ->
            StepItem(step = step)
            Spacer(modifier = Modifier.height(16.dp))
        }
        
        // AI Logo Image
        Image(
            painter = painterResource(id = com.billionsbounty.mobile.R.drawable.ai_logo),
            contentDescription = "AI Technology",
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            contentScale = ContentScale.Fit
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Feature Cards - All purple icons matching website (Tailwind purple-500)
        val purpleColor = Color(0xFFA855F7)  // purple-500 from website
        
        FeatureCard(
            icon = Icons.Default.Lightbulb,
            title = "Educational Platform",
            description = "Designed for AI security research and educational purposes only. Not gambling or gaming.",
            iconColor = purpleColor
        )
        Spacer(modifier = Modifier.height(12.dp))
        FeatureCard(
            icon = Icons.Default.Person,
            title = "Team Collaboration",
            description = "Form teams to pool resources and share strategies. Work together to solve complex challenges.",
            iconColor = purpleColor
        )
        Spacer(modifier = Modifier.height(12.dp))
        FeatureCard(
            icon = Icons.Default.Build,
            title = "Smart Contracts",
            description = "All fund management handled by autonomous smart contracts. Transparent and secure operations.",
            iconColor = purpleColor
        )
        
        // Revenue Distribution
        Spacer(modifier = Modifier.height(24.dp))
        val uriHandler = LocalUriHandler.current
        val annotatedText = buildAnnotatedString {
            withStyle(style = SpanStyle(fontStyle = FontStyle.Italic)) {
                append("60% of question fees grow the bounty pool, 20% funds operations, 10% buys back and burns ")
                pushStringAnnotation(tag = "URL", annotation = "https://100billioncapital.com/")
                withStyle(
                    style = SpanStyle(
                        color = Color(0xFF9333EA),
                        textDecoration = TextDecoration.Underline,
                        fontStyle = FontStyle.Italic
                    )
                ) {
                    append("\$100Bs")
                }
                pop()
                append(", and 10% rewards \$100Bs stakers")
            }
        }
        
        ClickableText(
            text = annotatedText,
            onClick = { offset ->
                annotatedText.getStringAnnotations(tag = "URL", start = offset, end = offset)
                    .firstOrNull()?.let { annotation ->
                        uriHandler.openUri(annotation.item)
                    }
            },
            style = androidx.compose.ui.text.TextStyle(
                fontSize = 16.sp,
                color = Color(0xFF374151),
                textAlign = TextAlign.Center,
                lineHeight = 24.sp
            ),
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            overflow = androidx.compose.ui.text.style.TextOverflow.Visible,
            softWrap = true
        )
    }
}

data class StepData(val number: Int, val title: String, val description: String)

@Composable
fun StepItem(step: StepData) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Step number badge
        Surface(
            modifier = Modifier.size(48.dp),
            shape = RoundedCornerShape(24.dp),
            color = Color(0xFFEC4899)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Text(
                    text = "Step ${step.number}",
                    color = Color.White,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
        
        // Content
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = step.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF111827)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = step.description,
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF6B7280)
            )
        }
    }
}

@Composable
fun FeatureCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    description: String,
    iconColor: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF9FAFB)),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Surface(
                modifier = Modifier.size(48.dp),
                shape = CircleShape,
                color = iconColor.copy(alpha = 0.1f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = iconColor,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF111827)
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF6B7280)
                )
            }
        }
    }
}

/**
 * Winners Section with carousel
 */
@Composable
fun WinnersSection(
    bounties: List<Bounty>,
    onNavigateToBounty: (Int) -> Unit
) {
    // Winner data with actual images
    val winners = remember {
        listOf(
            WinnerData("Claude Champion", "claude_champ"),
            WinnerData("GPT Goon", "gpt_goon"),
            WinnerData("Gemini Giant", "gemini_giant"),
            WinnerData("Llama Legend", "llama_legend")
        )
    }
    
    // Find the hardest bounty (highest amount)
    val hardestBounty = remember(bounties) {
        bounties.maxByOrNull { it.current_pool }
    }
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF065F46), // green-800
                        Color(0xFF172554)  // blue-950
                    )
                )
            )
            .padding(16.dp)
    ) {
        Text(
            text = "Our Winners",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp)
        )
        
        // Winner images - actual images from drawable
        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(winners) { winner ->
                Card(
                    modifier = Modifier
                        .width(150.dp)
                        .height(200.dp),
                    shape = RoundedCornerShape(12.dp),
                    elevation = CardDefaults.cardElevation(4.dp)
                ) {
                    Image(
                        painter = painterResource(
                            id = when (winner.imageName) {
                                "claude_champ" -> com.billionsbounty.mobile.R.drawable.claude_champ
                                "gpt_goon" -> com.billionsbounty.mobile.R.drawable.gpt_goon
                                "gemini_giant" -> com.billionsbounty.mobile.R.drawable.gemini_giant
                                "llama_legend" -> com.billionsbounty.mobile.R.drawable.llama_legend
                                else -> com.billionsbounty.mobile.R.drawable.ai_logo
                            }
                        ),
                        contentDescription = "${winner.name} - Winner holding check",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // CTA Button - Navigate to hardest bounty (purple-to-green gradient like website)
        if (hardestBounty != null) {
            Button(
                onClick = { onNavigateToBounty(hardestBounty.id) },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
                    .background(
                        brush = Brush.horizontalGradient(
                            colors = listOf(
                                Color(0xFF9333EA), // purple-600
                                Color(0xFF16A34A)  // green-600
                            )
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.Transparent
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    text = "Solana Seeker?",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    fontSize = 20.sp
                )
            }
        }
    }
}

data class WinnerData(val name: String, val imageName: String)

/**
 * FAQ Section with collapsible items
 */
@Composable
fun FAQSection() {
    var expandedItems by remember { mutableStateOf(setOf<Int>()) }
    
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFF9FAFB))
            .padding(16.dp)
    ) {
        Text(
            text = "Frequently Asked Questions",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF111827),
            textAlign = TextAlign.Center,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 8.dp)
        )
        
        Text(
            text = "Everything you need to know about BILLION$",
            style = MaterialTheme.typography.bodyLarge,
            color = Color(0xFF6B7280),
            textAlign = TextAlign.Center,
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp)
        )
        
        val faqs = listOf(
            FAQItem(
                "What is BILLION\$?",
                "BILLION\$ is an educational AI security research platform where participants attempt to outsmart AI models programmed to protect funds. It's designed for cybersecurity research and education, not gambling. The platform uses smart contracts for transparent, autonomous fund management."
            ),
            FAQItem(
                "How does the question pricing work?",
                "Questions start at \$10 and increase by 0.78% after each unsuccessful attempt across all users. The price grows exponentially (base × 1.0078^attempts) up to a maximum of \$4,500. Each failed attempt makes the bounty grow while increasing the cost to participate."
            ),
            FAQItem(
                "How does the platform determine the difficulty of each AI bot?",
                "Each AI bot with a bounty has been battle-tested against other competing LLM models. We rank the bots from Easy to Expert based on the average number of questions other LLMs needed to ask before getting the bot to transfer the funds. The harder the difficulty, the larger the starting bounty and question price, reflecting the increased challenge and potential reward."
            ),
            FAQItem(
                "What is \$100Bs and how does it benefit me?",
                "\$100Bs is BILLION\$'s memecoin that provides discounts on question fees. Hold 1M tokens for 10% off, 10M for 25% off, or 100M for 50% off. The platform uses 10% of revenue to buy back and burn \$100Bs tokens monthly, creating deflationary pressure and long-term value."
            ),
            FAQItem(
                "How is platform revenue distributed?",
                "Every question payment is split: 60% goes to the bounty pool to increase jackpots, 20% covers operational costs (development, infrastructure, security), 10% is used to buy back and burn \$100Bs tokens, and 10% goes to \$100Bs stakers as rewards."
            ),
            FAQItem(
                "What happens if no one asks a question for 24 hours?",
                "If 24 hours pass without any questions, the 'escape plan' triggers automatically. The bounty is distributed: 80% is split equally among all participants from that period, and 20% goes to the last person who asked a question before the timeout."
            ),
            FAQItem(
                "How do I get free questions?",
                "You get 2 free questions when you first visit the platform anonymously. When you connect your wallet and provide an email, you receive 5 additional free questions. Using a referral code grants another 5 free questions. After that, you pay per question."
            ),
            FAQItem(
                "How do smart contracts ensure fairness?",
                "All funds are held in autonomous smart contracts on Solana. The platform never holds your private keys. When the AI determines a successful jailbreak, it triggers the smart contract to execute payouts automatically. All transactions are recorded on-chain for complete transparency."
            ),
            FAQItem(
                "Can I collaborate with others?",
                "Yes! Create or join teams to pool resources and share strategies. Teams can coordinate attempts and distribute winnings based on contribution percentages. Team collaboration helps tackle harder challenges and increases everyone's chances of success."
            ),
            FAQItem(
                "What are the rules for winning?",
                "There's only one rule: by any means necessary, get the AI to send you money even though it's programmed to never transfer funds. Use any prompt technique, strategy, or creativity. The AI adapts to winning strategies, so you'll need to innovate constantly."
            ),
            FAQItem(
                "Is BILLION\$ gambling?",
                "No. BILLION\$ is an educational research platform for studying AI security vulnerabilities and prompt engineering. Participants must be 18+ and consent to research participation. It's designed for cybersecurity education and is explicitly not gambling or gaming."
            )
        )
        
        faqs.forEachIndexed { index, faq ->
            FAQItemCard(
                question = faq.question,
                answer = faq.answer,
                isExpanded = expandedItems.contains(index),
                onToggle = {
                    expandedItems = if (expandedItems.contains(index)) {
                        expandedItems - index
                    } else {
                        expandedItems + index
                    }
                }
            )
            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}

data class FAQItem(val question: String, val answer: String)

@Composable
fun FAQItemCard(
    question: String,
    answer: String,
    isExpanded: Boolean,
    onToggle: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFE5E7EB))
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onToggle() }
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = question,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = Color(0xFF111827),
                    modifier = Modifier.weight(1f)
                )
                Icon(
                    imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = if (isExpanded) "Collapse" else "Expand",
                    tint = Color(0xFF6B7280)
                )
            }
            
            if (isExpanded) {
                Spacer(modifier = Modifier.height(12.dp))
                Divider(color = Color(0xFFF3F4F6))
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = answer,
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color(0xFF6B7280)
                )
            }
        }
    }
}

/**
 * Footer Section
 */
@Composable
fun FooterSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFF3F4F6))
            .border(1.dp, Color(0xFFE5E7EB))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Educational Research Platform - For educational and research purposes only. Not a gambling, lottery, or gaming platform. Users must be 18+ to participate.",
            style = MaterialTheme.typography.bodySmall,
            color = Color(0xFF6B7280),
            textAlign = TextAlign.Center,
            fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        Row(
            horizontalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            Text(
                text = "Terms of Service",
                style = MaterialTheme.typography.bodySmall,
                color = Color(0xFF9CA3AF)
            )
            Text(
                text = "Privacy Policy",
                style = MaterialTheme.typography.bodySmall,
                color = Color(0xFF9CA3AF)
            )
            Text(
                text = "Contact",
                style = MaterialTheme.typography.bodySmall,
                color = Color(0xFF9CA3AF)
            )
        }
    }
}
