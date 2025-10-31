package com.billionsbounty.mobile.data.repository

import com.billionsbounty.mobile.data.api.*
import retrofit2.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for API calls to the FastAPI backend
 * Implements the repository pattern for clean architecture
 */
@Singleton
class ApiRepository @Inject constructor(
    private val apiClient: ApiClient
) {
    
    // ==================== Chat Endpoints ====================
    
    suspend fun sendChatMessage(request: ChatRequest): Response<ChatResponse> {
        return apiClient.sendChatMessage(request)
    }
    
    suspend fun sendChatMessage(
        message: String,
        userId: Int? = null,
        sessionId: String? = null,
        walletAddress: String? = null,
        ipAddress: String? = null
    ): Result<ChatResponse> {
        return handleApiCall {
            apiClient.sendChatMessage(
                ChatRequest(message, userId, sessionId, walletAddress, ipAddress)
            )
        }
    }
    
    suspend fun getConversationHistory(userId: Int? = null): Result<ConversationHistoryResponse> {
        return handleApiCall {
            apiClient.getConversationHistory(userId)
        }
    }
    
    // ==================== Lottery/Bounty Endpoints ====================
    
    suspend fun getLotteryStatus(): Result<LotteryStatusResponse> {
        return handleApiCall {
            apiClient.getLotteryStatus()
        }
    }
    
    suspend fun getAllBounties(): Result<BountiesResponse> {
        return handleApiCall {
            apiClient.getAllBounties()
        }
    }
    
    suspend fun getBountyDetails(id: Int): Response<BountyDetailsResponse> {
        return apiClient.getBountyDetails(id)
    }
    
    suspend fun getBountyStatus(bountyId: Int): Response<BountyStatusResponse> {
        return apiClient.getBountyStatus(bountyId)
    }
    
    suspend fun getWinningPrompts(bountyId: Int): Response<WinningPromptsResponse> {
        return apiClient.getWinningPrompts(bountyId)
    }
    
    suspend fun selectWinner(): Result<SelectWinnerResponse> {
        return handleApiCall {
            apiClient.selectWinner()
        }
    }
    
    // ==================== Dashboard Endpoints ====================
    
    suspend fun getDashboardOverview(): Result<DashboardOverviewResponse> {
        return handleApiCall {
            apiClient.getDashboardOverview()
        }
    }
    
    suspend fun getFundVerification(): Result<FundVerificationResponse> {
        return handleApiCall {
            apiClient.getFundVerification()
        }
    }
    
    suspend fun getSecurityStatus(): Result<SecurityStatusResponse> {
        return handleApiCall {
            apiClient.getSecurityStatus()
        }
    }
    
    // ==================== Wallet Endpoints ====================
    
    suspend fun connectWallet(request: WalletConnectRequest): Response<WalletConnectResponse> {
        return apiClient.connectWallet(request)
    }
    
    suspend fun connectWallet(
        walletAddress: String,
        publicKey: String
    ): Result<WalletConnectResponse> {
        return handleApiCall {
            apiClient.connectWallet(
                WalletConnectRequest(walletAddress, publicKey)
            )
        }
    }
    
    // ==================== Payment Endpoints ====================
    
    suspend fun createPayment(
        amountUsd: Double,
        paymentMethod: String,
        walletAddress: String? = null
    ): Result<PaymentResponse> {
        return handleApiCall {
            apiClient.createPayment(
                PaymentRequest(amountUsd, paymentMethod, walletAddress)
            )
        }
    }
    
    suspend fun verifyPayment(
        transactionSignature: String,
        walletAddress: String,
        amountUsd: Double? = null
    ): Result<TransactionVerifyResponse> {
        return handleApiCall {
            apiClient.verifyPayment(
                TransactionVerifyRequest(
                    tx_signature = transactionSignature,
                    wallet_address = walletAddress,
                    payment_method = "wallet",
                    amount_usd = amountUsd
                )
            )
        }
    }
    
    // ==================== Referral Endpoints ====================
    
    suspend fun generateReferralCode(userId: Int): Result<ReferralResponse> {
        return handleApiCall {
            apiClient.generateReferralCode(
                GenerateReferralRequest(userId)
            )
        }
    }
    
    suspend fun checkReferralCode(code: String): Result<ReferralCheckResponse> {
        return handleApiCall {
            apiClient.checkReferralCode(code)
        }
    }
    
    suspend fun getReferralStats(userId: Int): Result<ReferralStatsResponse> {
        return handleApiCall {
            apiClient.getReferralStats(userId)
        }
    }
    
    suspend fun useReferralCode(
        walletAddress: String,
        referralCode: String,
        email: String
    ): Response<UseReferralCodeResponse> {
        return apiClient.useReferralCode(
            UseReferralCodeRequest(walletAddress, referralCode, email)
        )
    }
    
    suspend fun processReferral(
        refereeUserId: Int,
        referralCode: String,
        walletAddress: String
    ): Response<ProcessReferralResponse> {
        return apiClient.processReferral(
            ProcessReferralRequest(refereeUserId, referralCode, walletAddress)
        )
    }
    
    suspend fun useFreeQuestion(userId: Int): Response<UseFreeQuestionResponse> {
        return apiClient.useFreeQuestion(
            UseFreeQuestionRequest(userId)
        )
    }
    
    // ==================== User Profile Endpoints ====================
    
    suspend fun getUserProfile(walletAddress: String): Response<UserProfileResponse> {
        return apiClient.getUserProfile(walletAddress)
    }
    
    suspend fun linkEmailToWallet(
        walletAddress: String,
        email: String
    ): Response<LinkEmailResponse> {
        return apiClient.linkEmailToWallet(
            LinkEmailRequest(walletAddress, email)
        )
    }
    
    // ==================== Staking Endpoints ====================
    
    suspend fun getStakingStatus(): Result<StakingStatusResponse> {
        return handleApiCall {
            apiClient.getStakingStatus()
        }
    }
    
    suspend fun stakeTokens(amount: Double, userId: Int): Result<StakeResponse> {
        return handleApiCall {
            apiClient.stakeTokens(
                StakeRequest(amount, userId)
            )
        }
    }
    
    suspend fun unstakeTokens(amount: Double, userId: Int): Result<UnstakeResponse> {
        return handleApiCall {
            apiClient.unstakeTokens(
                UnstakeRequest(amount, userId)
            )
        }
    }
    
    // ==================== Team Endpoints ====================
    
    suspend fun getAllTeams(): Response<TeamsResponse> {
        return apiClient.getAllTeams()
    }
    
    suspend fun createTeam(request: CreateTeamRequest): Response<CreateTeamResponse> {
        return apiClient.createTeam(request)
    }
    
    suspend fun createTeam(name: String, userId: Int): Result<CreateTeamResponse> {
        return handleApiCall {
            apiClient.createTeam(
                CreateTeamRequest(name, userId)
            )
        }
    }
    
    suspend fun getUserTeam(userId: Int): Response<UserTeamResponse> {
        return apiClient.getUserTeam(userId)
    }
    
    suspend fun joinTeam(request: JoinTeamRequest): Response<JoinTeamResponse> {
        return apiClient.joinTeam(request)
    }
    
    suspend fun getTeamDetails(teamId: String): Result<TeamDetailsResponse> {
        return handleApiCall {
            apiClient.getTeamDetails(teamId)
        }
    }
    
    // ==================== Token Endpoints ====================
    
    suspend fun getTokenStatus(): Result<TokenStatusResponse> {
        return handleApiCall {
            apiClient.getTokenStatus()
        }
    }
    
    suspend fun getTokenEconomics(): Result<TokenEconomicsResponse> {
        return handleApiCall {
            apiClient.getTokenEconomics()
        }
    }
    
    // ==================== User Eligibility & Free Questions ====================
    
    suspend fun checkUserEligibility(request: UserEligibilityRequest): Response<UserEligibilityResponse> {
        return apiClient.checkUserEligibility(request)
    }
    
    suspend fun getFreeQuestions(userId: Int): Response<FreeQuestionsResponse> {
        return apiClient.getFreeQuestions(userId)
    }
    
    // ==================== Stats ====================
    
    suspend fun getPlatformStats(): Result<PlatformStatsResponse> {
        return handleApiCall {
            apiClient.getPlatformStats()
        }
    }
    
    // ==================== Bounty Messages ====================
    
    suspend fun getBountyMessages(bountyId: Int, limit: Int = 50): Result<BountyMessagesResponse> {
        return handleApiCall {
            apiClient.getBountyMessages(bountyId, limit)
        }
    }
    
    // ==================== Bounty Chat (New) ====================
    
    /**
     * Send a message to a specific bounty's chat
     * Uses the bounty-specific chat endpoint with eligibility checks
     */
    suspend fun sendBountyChatMessage(
        bountyId: Int,
        message: String,
        walletAddress: String? = null,
        sessionId: String? = null
    ): Result<BountyChatResponse> {
        return handleApiCall {
            apiClient.sendBountyChatMessage(
                bountyId,
                BountyChatRequest(message, walletAddress, sessionId)
            )
        }
    }
    
    /**
     * Check free questions eligibility for a wallet
     */
    suspend fun checkFreeQuestions(walletAddress: String): Result<FreeQuestionsCheckResponse> {
        return handleApiCall {
            apiClient.checkFreeQuestions(walletAddress)
        }
    }
    
    // ==================== V2 Smart Contract Endpoints ====================
    // V2 endpoints for smart contract-based payments
    // All fund routing happens on-chain via V2 smart contracts
    // Backend only provides API endpoints - no fund routing in backend code
    
    /**
     * Get V2 bounty status
     * @param bountyId The bounty ID (typically 1)
     */
    suspend fun getV2BountyStatus(bountyId: Int): Result<V2BountyStatusResponse> {
        return handleApiCall {
            apiClient.getV2BountyStatus(bountyId)
        }
    }
    
    /**
     * Process V2 entry payment
     * Note: This endpoint requires client-side transaction signing
     * The backend provides configuration, but the transaction is signed by the user
     * @param userWalletAddress User's wallet address (base58)
     * @param bountyId The bounty ID (typically 1)
     * @param entryAmountUsdc Payment amount in USDC (e.g., 15.0)
     */
    suspend fun processV2Payment(
        userWalletAddress: String,
        bountyId: Int = 1,
        entryAmountUsdc: Double
    ): Result<V2ProcessPaymentResponse> {
        return handleApiCall {
            apiClient.processV2Payment(
                V2ProcessPaymentRequest(userWalletAddress, bountyId, entryAmountUsdc)
            )
        }
    }
    
    /**
     * Get V2 contract configuration (public info only)
     * Returns program ID, USDC mint, wallet addresses, etc.
     * Used by client to build transactions
     */
    suspend fun getV2Config(): Result<V2ConfigResponse> {
        return handleApiCall {
            apiClient.getV2Config()
        }
    }
    
    // ==================== Helper Functions ====================
    
    /**
     * Handle API response and convert to Result type
     */
    private suspend fun <T> handleApiCall(apiCall: suspend () -> Response<T>): Result<T> {
        return try {
            val response = apiCall()
            if (response.isSuccessful) {
                response.body()?.let {
                    Result.success(it)
                } ?: Result.failure(Exception("Response body is null"))
            } else {
                Result.failure(Exception("Error: ${response.code()} - ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
