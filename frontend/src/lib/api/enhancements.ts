/**
 * API Client for Platform Enhancements
 * 
 * Provides typed access to:
 * - Phase 1: Context Management
 * - Phase 2: Token Economics
 * - Phase 3: Team Collaboration
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Rich error type so callers can distinguish transport issues (e.g. 404 mocks)
 * without parsing message strings.
 */
export class ApiError extends Error {
  status: number
  endpoint: string
  details?: unknown

  constructor(message: string, status: number, endpoint: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.endpoint = endpoint
    this.details = details
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}

// Simple fetch wrapper with error handling
/* eslint-disable-next-line @typescript-eslint/no-explicit-any --
 * This helper underpins legacy callers that still expect permissive typing while
 * we gradually add endpoint-specific interfaces. Keeping it as `any` prevents
 * TypeScript breakage across the app while we migrate.
 */
async function apiCall<T = any>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Debug logging
  console.log(`🔍 API Call: ${options?.method || 'GET'} ${url}`);
  
  try {
    const response = await fetch(url, {
      ...options,
      mode: 'cors', // Explicitly set CORS mode
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    
    console.log(`✅ Response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({ detail: 'Unknown error' })) as {
        detail?: string
        error?: string
        [key: string]: unknown
      }
      const message = errorBody.detail || errorBody.error || `HTTP ${response.status}`;
      throw new ApiError(message, response.status, endpoint, errorBody);
    }
    
    const data = await response.json();
    console.log(`📦 Data:`, data);
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      const logContext = {
        endpoint: error.endpoint,
        status: error.status,
        message: error.message,
        details: error.details,
      };

      if (error.status === 404) {
        console.warn(`⚠️ API endpoint not available (likely disabled in this environment): ${endpoint}`, logContext);
      } else {
        console.error(`❌ API call failed: ${endpoint}`, logContext);
      }
    } else {
      console.error(`❌ API call failed: ${endpoint}`, error);
    }
    throw error;
  }
}

// =====================================================================
// PHASE 1: CONTEXT MANAGEMENT API
// =====================================================================

export const contextAPI = {
  /**
   * Detect attack patterns in a message
   */
  detectPatterns: (message: string, userId: number) =>
    apiCall('/api/context/detect-patterns', {
      method: 'POST',
      body: JSON.stringify({ message, user_id: userId }),
    }),
  
  /**
   * Get comprehensive context insights
   */
  getInsights: (userId: number, currentMessage: string) =>
    apiCall('/api/context/insights', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, current_message: currentMessage }),
    }),
  
  /**
   * Check context service health
   */
  checkHealth: () => apiCall('/api/context/health'),
};

// =====================================================================
// PHASE 2: TOKEN ECONOMICS API
// =====================================================================

export interface TokenBalance {
  wallet_address: string
  token_balance: number
  last_verified: string
  [key: string]: unknown
}

export interface DiscountTier {
  id?: number
  name?: string
  tier_name?: string
  min_balance?: number
  min_tokens?: number
  discount_percentage?: number
  discount_rate?: number
  description?: string
  perks?: string[]
  [key: string]: unknown
}

export interface DiscountTiersResponse {
  tiers: DiscountTier[]
  updated_at?: string
  [key: string]: unknown
}

export interface TokenMetrics {
  token_symbol: string
  total_supply: number
  total_staked: number
  staking_ratio: number
  staking_revenue_percentage: number
  circulating_supply?: number
  market_cap?: number
  [key: string]: unknown
}

export interface StakingPosition {
  position_id: number
  id?: number
  staked_amount?: number
  amount_staked?: number
  lock_period_days: number
  tier_allocation?: number
  unlocks_at?: string
  unlock_date?: string
  claimed_rewards?: number
  total_rewards_earned?: number
  projected_monthly_earnings?: number
  projected_remaining_earnings?: number
  claimable_rewards?: number
  share_of_tier?: number
  days_remaining?: number
  status?: string
  is_unlocked?: boolean
  [key: string]: unknown
}

export interface StakingPositionsResponse {
  positions: StakingPosition[]
  user_id?: number
  summary?: {
    total_staked?: number
    total_rewards_earned?: number
    active_positions?: number
    [key: string]: unknown
  }
  [key: string]: unknown
}

export interface TokenTierStatsEntry {
  total_staked: number
  staker_count: number
  tier_allocation: number
  average_lock_days?: number
  [key: string]: unknown
}

export interface TokenTierStatsResponse {
  tiers: Record<string, TokenTierStatsEntry>
  updated_at?: string
  [key: string]: unknown
}

export interface RevenueBreakdownEntry {
  percentage?: number
  monthly?: number
  weekly?: number
  daily?: number
  [key: string]: unknown
}

export interface TokenPlatformRevenueResponse {
  total_revenue?: {
    monthly?: number
    weekly?: number
    daily?: number
    [key: string]: unknown
  }
  distributed_portion?: {
    percentage?: number
    monthly?: number
    weekly?: number
    breakdown?: {
      staking_pool?: RevenueBreakdownEntry
      buyback?: RevenueBreakdownEntry
      [key: string]: RevenueBreakdownEntry | undefined
    }
    [key: string]: unknown
  }
  [key: string]: unknown
}

export interface StakeResponse {
  success?: boolean
  is_mock?: boolean
  error?: string
  [key: string]: unknown
}

export interface ClaimRewardsResponse {
  success?: boolean
  amount_claimed?: number
  error?: string
  [key: string]: unknown
}

export interface UnstakeResponse {
  success?: boolean
  amount_returned?: number
  error?: string
  [key: string]: unknown
}

export const tokenAPI = {
  /**
   * Check user's token balance (on-chain verification)
   */
  checkBalance: (walletAddress: string, userId: number) =>
    apiCall<TokenBalance>('/api/token/balance/check', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, user_id: userId }),
    }),
  
  /**
   * Get cached token balance (faster)
   */
  getBalance: (walletAddress: string) =>
    apiCall<TokenBalance>(`/api/token/balance/${walletAddress}`),
  
  /**
   * Calculate discount for a price
   */
  calculateDiscount: (walletAddress: string, basePrice: number) =>
    apiCall<{ discount_amount: number; final_price: number; discount_rate: number }>('/api/token/discount/calculate', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, base_price: basePrice }),
    }),
  
  /**
   * Get all discount tiers
   */
  getDiscountTiers: () => apiCall<DiscountTiersResponse>('/api/token/discount/tiers'),
  
  /**
   * Create a staking position
   */
  stake: (userId: number, walletAddress: string, amount: number, periodDays: number, txSignature?: string) =>
    apiCall<StakeResponse>('/api/token/stake', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        wallet_address: walletAddress,
        amount,
        period_days: periodDays,
        transaction_signature: txSignature,
      }),
    }),
  
  /**
   * Get user's staking positions
   */
  getStakingPositions: (userId: number) =>
    apiCall<StakingPositionsResponse>(`/api/token/staking/user/${userId}`),
  
  /**
   * Unstake tokens
   */
  unstake: (positionId: number, userId: number): Promise<UnstakeResponse> =>
    apiCall<UnstakeResponse>(`/api/token/staking/unstake/${positionId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),

  /**
   * Claim staking rewards
   */
  claimRewards: (userId: number, walletAddress: string) =>
    apiCall<ClaimRewardsResponse>('/api/token/staking/claim', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        wallet_address: walletAddress,
      }),
    }),
  
  /**
   * Get platform-wide token metrics
   */
  getMetrics: () => apiCall<TokenMetrics>('/api/token/metrics'),
  
  /**
   * Get staking tier statistics
   */
  getTierStats: () => apiCall<TokenTierStatsResponse>('/api/token/staking/tier-stats'),
  
  /**
   * Get platform revenue statistics for staking dashboard
   */
  getPlatformRevenue: () => apiCall<TokenPlatformRevenueResponse>('/api/token/revenue/platform-stats'),
  
  /**
   * Check token service health
   */
  checkHealth: () => apiCall('/api/token/health'),
};

// =====================================================================
// PHASE 3: TEAM COLLABORATION API
// =====================================================================

export interface TeamSummary {
  id: number
  name: string
  description?: string
  leader_id: number
  max_members: number
  total_pool: number
  total_attempts: number
  total_spent?: number
  total_entries?: number
  member_count: number
  created_at: string
  is_public?: boolean
  is_active?: boolean
}

export interface TeamDetails extends TeamSummary {
  invite_code?: string
}

export interface TeamMember {
  user_id: number
  display_name: string
  role: string
  total_contributed: number
  contribution_percentage: number
  joined_at: string
}

export interface TeamMembersResponse {
  members: TeamMember[]
}

export interface TeamBrowseResponse {
  teams: TeamSummary[]
  total?: number
  limit?: number
  offset?: number
}

export interface TeamCreateResponse {
  team: TeamDetails & { invite_code: string }
  message?: string
}

export interface TeamJoinResponse {
  membership: {
    team_id: number
    team_name: string
    role?: string
    joined_at?: string
  }
  message?: string
}

export interface TeamStatsResponse {
  team_id: number
  name: string
  member_count: number
  total_pool: number
  total_attempts: number
  successful_attempts: number
  success_rate: number
  total_spent: number
  avg_cost_per_attempt: number
}

export const teamAPI = {
  /**
   * Create a new team
   */
  create: (leaderId: number, name: string, description?: string, maxMembers = 5, isPublic = true) =>
    apiCall<TeamCreateResponse>('/api/teams/create', {
      method: 'POST',
      body: JSON.stringify({
        leader_id: leaderId,
        name,
        description,
        max_members: maxMembers,
        is_public: isPublic,
      }),
    }),
  
  /**
   * Get team details
   */
  get: (teamId: number) => apiCall<TeamDetails>(`/api/teams/${teamId}`),
  
  /**
   * Browse all public teams
   */
  browse: (limit = 50, offset = 0) =>
    apiCall<TeamBrowseResponse>(`/api/teams/?limit=${limit}&offset=${offset}`),
  
  /**
   * Update team settings (leader only)
   */
  update: (teamId: number, userId: number, updates: { description?: string; max_members?: number; is_public?: boolean }) =>
    apiCall(`/api/teams/${teamId}?user_id=${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    }),
  
  /**
   * Get team members
   */
  getMembers: (teamId: number) => apiCall<TeamMembersResponse>(`/api/teams/${teamId}/members`),
  
  /**
   * Join team by invite code
   */
  joinByCode: (inviteCode: string, userId: number) =>
    apiCall<TeamJoinResponse>('/api/teams/join', {
      method: 'POST',
      body: JSON.stringify({ invite_code: inviteCode, user_id: userId }),
    }),
  
  /**
   * Leave team
   */
  leave: (teamId: number, userId: number) =>
    apiCall(`/api/teams/${teamId}/leave`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
  
  /**
   * Contribute to team pool
   */
  contribute: (teamId: number, userId: number, amount: number, txSignature?: string) =>
    apiCall(`/api/teams/${teamId}/contribute`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        amount,
        transaction_signature: txSignature,
      }),
    }),
  
  /**
   * Send team message
   */
  sendMessage: (teamId: number, userId: number, content: string, messageType = 'text') =>
    apiCall(`/api/teams/${teamId}/messages`, {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        content,
        message_type: messageType,
      }),
    }),
  
  /**
   * Get team messages
   */
  getMessages: (teamId: number, userId: number, limit = 50) =>
    apiCall(`/api/teams/${teamId}/messages?user_id=${userId}&limit=${limit}`),
  
  /**
   * Get team statistics
   */
  getStats: (teamId: number) => apiCall<TeamStatsResponse>(`/api/teams/${teamId}/stats`),
  
  /**
   * Check team service health
   */
  checkHealth: () => apiCall('/api/teams/health'),
};

// Export all APIs
export default {
  context: contextAPI,
  token: tokenAPI,
  team: teamAPI,
};

