package com.billionsbounty.mobile.navigation

import androidx.compose.runtime.*
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.billionsbounty.mobile.ui.screens.BountyDetailScreen
import com.billionsbounty.mobile.ui.screens.HomeScreen
import com.billionsbounty.mobile.ui.screens.PaymentScreen
import com.billionsbounty.mobile.ui.screens.DashboardScreen
import com.billionsbounty.mobile.ui.screens.ReferralScreen
import com.billionsbounty.mobile.ui.screens.StakingScreen
import com.billionsbounty.mobile.ui.screens.TeamScreen
import com.billionsbounty.mobile.ui.screens.GamificationScreen
import com.billionsbounty.mobile.di.ApiRepositoryEntryPoint
import dagger.hilt.android.EntryPointAccessors
import androidx.compose.ui.platform.LocalContext
import com.billionsbounty.mobile.ui.viewmodel.BountyViewModel
import com.billionsbounty.mobile.ui.viewmodel.ChatViewModel
import com.billionsbounty.mobile.ui.viewmodel.PaymentViewModel

sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Dashboard : Screen("dashboard")
    object Chat : Screen("chat/{bountyId}?watchMode={watchMode}") {
        fun createRoute(bountyId: Int, watchMode: Boolean = false) = "chat/$bountyId?watchMode=$watchMode"
    }
    object Payment : Screen("payment")
    object Referral : Screen("referral")
    object Staking : Screen("staking")
    object Team : Screen("team")
    object Gamification : Screen("gamification")
}

@Composable
fun NavGraph(
    navController: NavHostController = rememberNavController(),
    startDestination: String = Screen.Home.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToBounty = { bountyId ->
                    navController.navigate(Screen.Chat.createRoute(bountyId, watchMode = false))
                },
                onNavigateToBountyWatch = { bountyId ->
                    navController.navigate(Screen.Chat.createRoute(bountyId, watchMode = true))
                },
                onNavigateToChat = {
                    navController.navigate(Screen.Chat.createRoute(1))
                },
                onNavigateToDashboard = {
                    navController.navigate(Screen.Dashboard.route)
                },
                onNavigateToPayment = {
                    navController.navigate(Screen.Payment.route)
                },
                onNavigateToReferral = {
                    navController.navigate(Screen.Referral.route)
                },
                onNavigateToStaking = {
                    navController.navigate(Screen.Staking.route)
                },
                onNavigateToTeam = {
                    navController.navigate(Screen.Team.route)
                },
                onNavigateToGamification = {
                    navController.navigate(Screen.Gamification.route)
                }
            )
        }
        
        composable(Screen.Dashboard.route) {
            val viewModel: BountyViewModel = hiltViewModel()
            DashboardScreen(
                viewModel = viewModel,
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Chat.route) { backStackEntry ->
            val bountyId = backStackEntry.arguments?.getString("bountyId")?.toIntOrNull() ?: 1
            val watchMode = backStackEntry.arguments?.getString("watchMode")?.toBooleanStrictOrNull() ?: false
            BountyDetailScreen(
                bountyId = bountyId,
                startInWatchMode = watchMode,
                onBackClick = {
                    navController.popBackStack()
                },
                onNavigateToWallet = {
                    // Navigate to wallet connection screen
                }
            )
        }
        
        composable(Screen.Payment.route) {
            val viewModel: PaymentViewModel = hiltViewModel()
            PaymentScreen(
                viewModel = viewModel,
                onBackClick = {
                    navController.popBackStack()
                },
                onPaymentSuccess = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Referral.route) {
            ReferralScreen(
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Staking.route) {
            StakingScreen(
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Team.route) {
            TeamScreen(
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Gamification.route) {
            val context = LocalContext.current
            val apiRepository = EntryPointAccessors.fromApplication(
                context.applicationContext,
                ApiRepositoryEntryPoint::class.java
            ).apiRepository()
            
            // Get wallet address from wallet adapter or preferences
            // For now, using a placeholder - you may need to get this from WalletViewModel
            val walletAddress: String? = null // TODO: Get from WalletViewModel or preferences
            
            GamificationScreen(
                walletAddress = walletAddress,
                apiRepository = apiRepository,
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }
    }
}
