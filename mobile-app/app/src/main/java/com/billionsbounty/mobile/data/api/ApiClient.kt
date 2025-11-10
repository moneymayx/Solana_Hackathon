package com.billionsbounty.mobile.data.api

import retrofit2.Response
import retrofit2.http.*

/**
 * API interface for communicating with the FastAPI backend
 * Maps to all endpoints in apps/backend/main.py
 */
interface ApiClient {
    
    // Chat endpoints
    @POST("/api/chat")
    suspend fun sendChatMessage(
        @Body request: ChatRequest
    ): Response<ChatResponse>
    
    @GET("/api/conversation/history")
    suspend fun getConversationHistory(
        @Query("user_id") userId: Int? = null
    ): Response<ConversationHistoryResponse>
    
    // Lottery/Bounty endpoints
    @GET("/api/lottery/status")
    suspend fun getLotteryStatus(): Response<LotteryStatusResponse>
    
    @GET("/api/bounties")
    suspend fun getAllBounties(): Response<BountiesResponse>
    
    @GET("/api/bounty/{id}")
    suspend fun getBountyDetails(@Path("id") id: Int): Response<BountyDetailsResponse>
    
    @POST("/api/lottery/select-winner")
    suspend fun selectWinner(): Response<SelectWinnerResponse>
    
    // Dashboard endpoints
    @GET("/api/dashboard/overview")
    suspend fun getDashboardOverview(): Response<DashboardOverviewResponse>
    
    @GET("/api/dashboard/fund-verification")
    suspend fun getFundVerification(): Response<FundVerificationResponse>
    
    @GET("/api/dashboard/security-status")
    suspend fun getSecurityStatus(): Response<SecurityStatusResponse>
    
    // Wallet endpoints
    @POST("/api/wallet/connect")
    suspend fun connectWallet(@Body request: WalletConnectRequest): Response<WalletConnectResponse>
    
    // Payment endpoints
    @POST("/api/payment/create")
    suspend fun createPayment(@Body request: PaymentRequest): Response<PaymentResponse>
    
    @POST("/api/payment/verify")
    suspend fun verifyPayment(@Body request: TransactionVerifyRequest): Response<TransactionVerifyResponse>
    
    // Referral endpoints
    @POST("/api/referral/generate")
    suspend fun generateReferralCode(@Body request: GenerateReferralRequest): Response<ReferralResponse>
    
    @GET("/api/referral/{code}")
    suspend fun checkReferralCode(@Path("code") code: String): Response<ReferralCheckResponse>
    
    @GET("/api/referral/stats/{userId}")
    suspend fun getReferralStats(@Path("userId") userId: Int): Response<ReferralStatsResponse>
    
    @POST("/api/referral/use-code")
    suspend fun useReferralCode(@Body request: UseReferralCodeRequest): Response<UseReferralCodeResponse>
    
    @POST("/api/referral/process")
    suspend fun processReferral(@Body request: ProcessReferralRequest): Response<ProcessReferralResponse>
    
    @POST("/api/referral/use-free-question")
    suspend fun useFreeQuestion(@Body request: UseFreeQuestionRequest): Response<UseFreeQuestionResponse>
    
    // User Profile endpoints
    @GET("/api/user/profile/{walletAddress}")
    suspend fun getUserProfile(@Path("walletAddress") walletAddress: String): Response<UserProfileResponse>
    
    @POST("/api/user/set-profile")
    suspend fun setUserProfile(@Body request: SetProfileRequest): Response<SetProfileResponse>
    
    @POST("/api/user/link-email")
    suspend fun linkEmailToWallet(@Body request: LinkEmailRequest): Response<LinkEmailResponse>
    
    // Staking endpoints
    @GET("/api/staking/status")
    suspend fun getStakingStatus(): Response<StakingStatusResponse>
    
    @POST("/api/staking/stake")
    suspend fun stakeTokens(@Body request: StakeRequest): Response<StakeResponse>
    
    @POST("/api/staking/unstake")
    suspend fun unstakeTokens(@Body request: UnstakeRequest): Response<UnstakeResponse>
    
    // Team endpoints
    @GET("/api/teams")
    suspend fun getAllTeams(): Response<TeamsResponse>
    
    @POST("/api/teams/create")
    suspend fun createTeam(@Body request: CreateTeamRequest): Response<CreateTeamResponse>
    
    @GET("/api/teams/{teamId}")
    suspend fun getTeamDetails(@Path("teamId") teamId: String): Response<TeamDetailsResponse>
    
    // Token endpoints
    @GET("/api/token/status")
    suspend fun getTokenStatus(): Response<TokenStatusResponse>
    
    @GET("/api/token/economics")
    suspend fun getTokenEconomics(): Response<TokenEconomicsResponse>
    
    // Stats
    @GET("/api/stats")
    suspend fun getPlatformStats(): Response<PlatformStatsResponse>
    
    // User Eligibility & Free Questions
    @POST("/api/user/eligibility")
    suspend fun checkUserEligibility(@Body request: UserEligibilityRequest): Response<UserEligibilityResponse>
    
    @GET("/api/referral/free-questions/{userId}")
    suspend fun getFreeQuestions(@Path("userId") userId: Int): Response<FreeQuestionsResponse>
    
    // Bounty Status
    @GET("/api/bounty/{id}/status")
    suspend fun getBountyStatus(@Path("id") bountyId: Int): Response<BountyStatusResponse>
    
    // Winning Prompts
    @GET("/api/bounty/{id}/winning-prompts")
    suspend fun getWinningPrompts(@Path("id") bountyId: Int): Response<WinningPromptsResponse>
    
    // Team operations
    @GET("/api/user/{userId}/team")
    suspend fun getUserTeam(@Path("userId") userId: Int): Response<UserTeamResponse>
    
    @POST("/api/teams/join")
    suspend fun joinTeam(@Body request: JoinTeamRequest): Response<JoinTeamResponse>
    
    // Bounty Messages
    @GET("/api/bounty/{bountyId}/messages/public")
    suspend fun getBountyMessages(
        @Path("bountyId") bountyId: Int,
        @Query("limit") limit: Int = 50
    ): Response<BountyMessagesResponse>
    
    // Bounty-specific chat endpoint
    @POST("/api/bounty/{bountyId}/chat")
    suspend fun sendBountyChatMessage(
        @Path("bountyId") bountyId: Int,
        @Body request: BountyChatRequest
    ): Response<BountyChatResponse>
    
    // Free questions eligibility check
    @GET("/api/free-questions/{walletAddress}")
    suspend fun checkFreeQuestions(
        @Path("walletAddress") walletAddress: String
    ): Response<FreeQuestionsCheckResponse>
    
    // NFT endpoints
    @GET("/api/nft/status/{walletAddress}")
    suspend fun getNftStatus(
        @Path("walletAddress") walletAddress: String
    ): Response<NftStatusResponse>
    
    @POST("/api/nft/verify")
    suspend fun verifyNft(
        @Body request: NftVerifyRequest
    ): Response<NftVerifyResponse>
    
    // ==============================================================================
    // V2 SMART CONTRACT ENDPOINTS (ACTIVE - Production)
    // ==============================================================================
    // V2 endpoints for smart contract-based payments
    // All fund routing happens on-chain via V2 smart contracts
    // Backend only provides API endpoints - no fund routing in backend code
    // See ARCHITECTURE.md for system architecture
    
    /**
     * Get V2 bounty status
     * @param bountyId The bounty ID (typically 1)
     */
    @GET("/api/v2/bounty/{bounty_id}/status")
    suspend fun getV2BountyStatus(@Path("bounty_id") bountyId: Int): Response<V2BountyStatusResponse>
    
    /**
     * Process V2 entry payment
     * Note: This endpoint requires client-side transaction signing
     * The backend provides configuration, but the transaction is signed by the user
     */
    @POST("/api/v2/payment/process")
    suspend fun processV2Payment(@Body request: V2ProcessPaymentRequest): Response<V2ProcessPaymentResponse>
    
    /**
     * Get V2 contract configuration (public info only)
     * Returns program ID, USDC mint, wallet addresses, etc.
     */
    @GET("/api/v2/config")
    suspend fun getV2Config(): Response<V2ConfigResponse>
}

/**
 * Data classes for requests and responses
 */

// Chat
data class ChatRequest(
    val message: String,
    val user_id: Int? = null,
    val session_id: String? = null,
    val wallet_address: String? = null,
    val ip_address: String? = null
)

data class ChatResponse(
    val response: String,
    val user_id: Int,
    val session_id: String,
    val is_winner: Boolean = false,
    val blacklisted: Boolean = false,
    val winner_prize: Double? = null
)

data class ConversationHistoryResponse(
    val conversations: List<ConversationMessage>
)

data class ConversationMessage(
    val id: String,
    val user_message: String,
    val ai_response: String,
    val timestamp: String,
    val is_winner: Boolean = false
)

// Lottery/Bounty
data class LotteryStatusResponse(
    val success: Boolean,
    val program_id: String,
    val current_jackpot: Double,
    val total_entries: Int,
    val is_active: Boolean,
    val research_fund_floor: Double,
    val research_fee: Double
)

data class BountiesResponse(
    val success: Boolean,
    val bounties: List<Bounty>
)

data class Bounty(
    val id: Int,
    val name: String,
    val description: String = "",
    val llm_provider: String,
    val current_pool: Double,
    val starting_pool: Double = 0.0,
    val total_entries: Int,
    val win_rate: Double,
    val difficulty_level: String,
    val is_active: Boolean,
    val created_at: String = "",
    val updated_at: String = ""
)

data class BountyDetailsResponse(
    val success: Boolean,
    val bounty: Bounty
)

data class SelectWinnerResponse(
    val success: Boolean,
    val winner: String?,
    val prize: Double?
)

// Dashboard
data class DashboardOverviewResponse(
    val success: Boolean,
    val data: DashboardData
)

data class DashboardData(
    val lottery_status: LotteryStatusResponse,
    val platform_stats: PlatformStats,
    val recent_activity: RecentActivity
)

data class PlatformStats(
    val total_users: Int,
    val total_questions: Int,
    val total_attempts: Int,
    val total_successes: Int
)

data class RecentActivity(
    val new_users_24h: Int,
    val questions_24h: Int,
    val attempts_24h: Int
)

data class FundVerificationResponse(
    val success: Boolean,
    val data: FundVerificationData? = null,
    val error: String? = null
)

data class FundVerificationData(
    val lottery_funds: LotteryFundsData,
    val jackpot_wallet: JackpotWalletData,
    val staking_wallet: StakingWalletData? = null,
    val v2_wallets: V2WalletsData? = null,
    val fund_activity: FundActivityData,
    val verification_links: VerificationLinksData,
    val last_updated: String
)

data class LotteryFundsData(
    val current_jackpot_usdc: Double,
    val jackpot_balance_usdc: Double,
    val fund_verified: Boolean,
    val balance_gap_usdc: Double,
    val surplus_usdc: Double,
    val lottery_pda: String,
    val program_id: String,
    val jackpot_token_account: String,
    val last_prize_pool_update: String? = null
)

data class JackpotWalletData(
    val address: String,
    val token_account: String,
    val mint: String? = null,
    val balance_usdc: Double,
    val balance_sol: Double? = null,
    val verification_status: String,
    val last_balance_check: String
)

data class StakingWalletData(
    val address: String,
    val balance_sol: Double? = null,
    val balance_usd: Double? = null,
    val last_balance_check: String
)

data class V2WalletsData(
    val bounty_pool: V2WalletInfo? = null,
    val operational: V2WalletInfo? = null,
    val buyback: V2WalletInfo? = null,
    val staking: V2WalletInfo? = null
)

data class V2WalletInfo(
    val address: String,
    val label: String
)

data class FundActivityData(
    val total_completed_usdc: Double,
    val total_pending_usdc: Double,
    val total_failed_usdc: Double,
    val pending_count: Int,
    val failed_count: Int,
    val total_entries_recorded: Int,
    val last_deposit_at: String? = null
)

data class VerificationLinksData(
    val solana_explorer: String? = null,
    val program_id: String? = null,
    val jackpot_token_account: String? = null,
    val jackpot_wallet: String? = null,
    val staking_wallet: String? = null,
    val bounty_pool_wallet: String? = null,
    val operational_wallet: String? = null,
    val buyback_wallet: String? = null,
    val bounty_pda: String? = null
)

data class SecurityStatusResponse(
    val success: Boolean,
    val data: SecurityData
)

data class SecurityData(
    val rate_limiting: RateLimitStatus,
    val sybil_detection: SybilDetectionStatus,
    val ai_security: AISecurityStatus
)

data class RateLimitStatus(
    val active: Boolean,
    val requests_per_minute: Int
)

data class SybilDetectionStatus(
    val active: Boolean,
    val detection_methods: List<String>
)

data class AISecurityStatus(
    val personality_system: String,
    val manipulation_detection: String
)

// Wallet
data class WalletConnectRequest(
    val wallet_address: String,
    val public_key: String
)

data class WalletConnectResponse(
    val success: Boolean,
    val user_id: Int
)

// Payment
data class PaymentRequest(
    val amount_usd: Double,
    val payment_method: String,
    val wallet_address: String? = null
)

data class PaymentResponse(
    val success: Boolean,
    val transaction_id: String?,
    val status: String
)

data class TransactionVerifyRequest(
    val tx_signature: String,
    val wallet_address: String,
    val payment_method: String = "wallet",
    val amount_usd: Double? = null
)

data class TransactionVerifyResponse(
    val success: Boolean,
    val verified: Boolean,
    val amount: Double,
    val questions_granted: Int = 0,
    val credit_remainder: Double = 0.0,
    val is_mock: Boolean = false,
    val is_paid: Boolean = false,
    val message: String? = null
)

// Referral
data class GenerateReferralRequest(
    val user_id: Int
)

data class ReferralResponse(
    val success: Boolean,
    val referral_code: String
)

data class ReferralCheckResponse(
    val valid: Boolean,
    val referrer_id: Int?
)

data class ReferralStatsResponse(
    val total_referrals: Int,
    val successful_referrals: Int,
    val total_rewards: Double
)

// Staking
data class StakingStatusResponse(
    val success: Boolean,
    val total_staked: Double,
    val apr: Double
)

data class StakeRequest(
    val amount: Double,
    val user_id: Int
)

data class StakeResponse(
    val success: Boolean,
    val staked_amount: Double
)

data class UnstakeRequest(
    val amount: Double,
    val user_id: Int
)

data class UnstakeResponse(
    val success: Boolean,
    val unstaked_amount: Double
)

// Teams
data class TeamsResponse(
    val success: Boolean,
    val teams: List<Team>
)

data class Team(
    val id: String,
    val name: String,
    val member_count: Int,
    val total_attempts: Int
)

data class CreateTeamRequest(
    val name: String,
    val user_id: Int
)

data class CreateTeamResponse(
    val success: Boolean,
    val team_id: String
)

data class TeamDetailsResponse(
    val success: Boolean,
    val team: TeamDetails
)

data class TeamDetails(
    val id: String,
    val name: String,
    val members: List<TeamMember>,
    val total_attempts: Int
)

data class TeamMember(
    val user_id: Int,
    val wallet_address: String
)

// Token
data class TokenStatusResponse(
    val success: Boolean,
    val total_supply: Double,
    val price_usd: Double
)

data class TokenEconomicsResponse(
    val success: Boolean,
    val distribution: TokenDistribution
)

data class TokenDistribution(
    val community: Double,
    val staking: Double,
    val operations: Double
)

// Stats
data class PlatformStatsResponse(
    val bounty_status: Map<String, Any>,
    val rate_limits: Map<String, Int>,
    val bounty_structure: Map<String, Double>
)

// User Eligibility & Free Questions
data class UserEligibilityRequest(
    val user_id: Int?,
    val wallet_address: String?
)

data class UserEligibilityResponse(
    val eligible: Boolean,
    val type: String, // 'free_questions', 'payment_required', 'referral_signup'
    val message: String,
    val questions_remaining: Int,
    val questions_used: Int,
    val source: String? = null,
    val referral_code: String? = null,
    val email: String? = null
)

data class FreeQuestionsResponse(
    val user_id: Int,
    val free_questions_available: Int,
    val free_questions_used: Int,
    val source: String
)

// Bounty Status (Enhanced)
data class BountyStatusResponse(
    val id: Int,
    val current_pool: Double,
    val total_entries: Int,
    val win_rate: Double,
    val time_until_rollover: String? = null
)

// Winning Prompts
data class WinningPromptsResponse(
    val success: Boolean,
    val prompts: List<WinningPrompt>
)

data class WinningPrompt(
    val id: Int,
    val prompt: String,
    val winner_name: String,
    val timestamp: String,
    val bounty_id: Int
)

// Team (Enhanced)
data class UserTeamResponse(
    val success: Boolean,
    val team: UserTeam?
)

data class UserTeam(
    val team_id: String,
    val team_name: String,
    val total_pool: Double,
    val member_count: Int,
    val bounty_id: Int? = null
)

data class JoinTeamRequest(
    val team_id: String,
    val user_id: Int
)

data class JoinTeamResponse(
    val success: Boolean,
    val message: String
)

// Referral - Use Code
data class UseReferralCodeRequest(
    val wallet_address: String,
    val referral_code: String,
    val email: String
)

data class UseReferralCodeResponse(
    val success: Boolean,
    val receiver_questions: Int,
    val referrer_questions: Int,
    val message: String? = null,
    val detail: String? = null,
    val error: String? = null
)

// Referral - Process
data class ProcessReferralRequest(
    val referee_user_id: Int,
    val referral_code: String,
    val wallet_address: String
)

data class ProcessReferralResponse(
    val success: Boolean,
    val message: String? = null
)

// Referral - Use Free Question
data class UseFreeQuestionRequest(
    val user_id: Int
)

data class UseFreeQuestionResponse(
    val success: Boolean,
    val remaining: Int,
    val message: String? = null
)

// User Profile
data class UserProfileResponse(
    val success: Boolean,
    val user_id: Int,
    val wallet_address: String,
    val email: String? = null,
    val referral_code: String? = null,
    val free_questions_available: Int = 0,
    val created_at: String? = null,
    val display_name: String? = null, // Username/display name for activity tracker
    val username: String? = null // Alias for display_name
)

// Set User Profile (username and optional email)
data class SetProfileRequest(
    val wallet_address: String,
    val username: String,
    val email: String? = null
)

data class SetProfileResponse(
    val success: Boolean,
    val message: String,
    val username: String? = null,
    val email: String? = null
)

// Link Email to Wallet
data class LinkEmailRequest(
    val wallet_address: String,
    val email: String
)

data class LinkEmailResponse(
    val success: Boolean,
    val message: String
)

// Bounty Messages
data class BountyMessagesResponse(
    val success: Boolean,
    val messages: List<BountyMessage>,
    val total: Int,
    val bounty_id: Int
)

data class BountyMessage(
    val id: Int,
    val user_id: Int?,
    val message_type: String,  // 'user' or 'assistant'
    val content: String,
    val timestamp: String?,
    val cost: Double?
)

// Bounty-specific Chat
data class BountyChatRequest(
    val message: String,
    val wallet_address: String? = null,
    val session_id: String? = null
)

data class BountyChatResponse(
    val success: Boolean,
    val response: String,
    val user_id: Int? = null,
    val questions_remaining: Int = 0,
    val questions_used: Int = 0,
    val is_winner: Boolean = false,
    val free_questions: FreeQuestionsData? = null,
    val bounty_status: BountyStatusData? = null
)

data class FreeQuestionsData(
    val eligible: Boolean,
    val questions_remaining: Int,
    val questions_used: Int,
    val source: String? = null,
    val is_paid: Boolean = false,
    val message: String? = null
)

data class BountyStatusData(
    val current_pool: Double,
    val total_entries: Int,
    val difficulty_level: String? = null
)

// Free Questions Check
data class FreeQuestionsCheckResponse(
    val success: Boolean,
    val eligible: Boolean,
    val questions_remaining: Int = 0,
    val questions_used: Int = 0,
    val is_paid: Boolean = false,
    val is_anonymous: Boolean = false,
    val message: String? = null,
    val source: String? = null
)

// NFT Verification
data class NftStatusResponse(
    val success: Boolean,
    val has_nft: Boolean = false,
    val verified: Boolean = false,
    val is_mock: Boolean = false,
    val questions_remaining: Int = 0,
    val message: String? = null
)

data class NftVerifyRequest(
    val wallet_address: String,
    val signature: String
)

data class NftVerifyResponse(
    val success: Boolean,
    val verified: Boolean = false,
    val is_mock: Boolean = false,
    val questions_granted: Int = 0,
    val questions_remaining: Int = 0,
    val message: String? = null,
    val error: String? = null  // Error field for backend compatibility
)

// ==============================================================================
// V2 SMART CONTRACT REQUEST/RESPONSE MODELS
// ==============================================================================

/**
 * Request to process V2 entry payment
 * Note: Actual transaction signing happens client-side
 */
data class V2ProcessPaymentRequest(
    val user_wallet_address: String,
    val bounty_id: Int = 1,
    val entry_amount_usdc: Double
)

/**
 * Response from V2 payment processing
 */
data class V2ProcessPaymentResponse(
    val success: Boolean,
    val transaction_signature: String? = null,
    val explorer_url: String? = null,
    val bounty_id: Int,
    val amount: Int, // Amount in smallest unit (6 decimals for USDC)
    val error: String? = null
)

/**
 * V2 bounty status response
 */
data class V2BountyStatusResponse(
    val success: Boolean,
    val bounty_id: Int,
    val bounty_pda: String? = null,
    val error: String? = null
)

/**
 * V2 contract configuration response
 * Contains public configuration needed for client-side transaction building
 */
data class V2ConfigResponse(
    val success: Boolean,
    val enabled: Boolean,
    val program_id: String,
    val usdc_mint: String,
    val bounty_pool_wallet: String,
    val operational_wallet: String,
    val buyback_wallet: String,
    val staking_wallet: String,
    val rpc_endpoint: String
)
