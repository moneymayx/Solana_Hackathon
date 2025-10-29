/**
 * API Client for Platform Enhancements
 * 
 * Provides typed access to:
 * - Phase 1: Context Management
 * - Phase 2: Token Economics
 * - Phase 3: Team Collaboration
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Simple fetch wrapper with error handling
async function apiCall<T>(
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
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`📦 Data:`, data);
    return data;
  } catch (error) {
    console.error(`❌ API call failed: ${endpoint}`, error);
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

export const tokenAPI = {
  /**
   * Check user's token balance (on-chain verification)
   */
  checkBalance: (walletAddress: string, userId: number) =>
    apiCall('/api/token/balance/check', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, user_id: userId }),
    }),
  
  /**
   * Get cached token balance (faster)
   */
  getBalance: (walletAddress: string) =>
    apiCall(`/api/token/balance/${walletAddress}`),
  
  /**
   * Calculate discount for a price
   */
  calculateDiscount: (walletAddress: string, basePrice: number) =>
    apiCall('/api/token/discount/calculate', {
      method: 'POST',
      body: JSON.stringify({ wallet_address: walletAddress, base_price: basePrice }),
    }),
  
  /**
   * Get all discount tiers
   */
  getDiscountTiers: () => apiCall('/api/token/discount/tiers'),
  
  /**
   * Create a staking position
   */
  stake: (userId: number, walletAddress: string, amount: number, periodDays: number, txSignature?: string) =>
    apiCall('/api/token/stake', {
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
    apiCall(`/api/token/staking/user/${userId}`),
  
  /**
   * Unstake tokens
   */
  unstake: (positionId: number, userId: number) =>
    apiCall(`/api/token/staking/unstake/${positionId}`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    }),
  
  /**
   * Get platform-wide token metrics
   */
  getMetrics: () => apiCall('/api/token/metrics'),
  
  /**
   * Get staking tier statistics
   */
  getTierStats: () => apiCall('/api/token/staking/tier-stats'),
  
  /**
   * Get platform revenue statistics for staking dashboard
   */
  getPlatformRevenue: () => apiCall('/api/token/revenue/platform-stats'),
  
  /**
   * Check token service health
   */
  checkHealth: () => apiCall('/api/token/health'),
};

// =====================================================================
// PHASE 3: TEAM COLLABORATION API
// =====================================================================

export const teamAPI = {
  /**
   * Create a new team
   */
  create: (leaderId: number, name: string, description?: string, maxMembers = 5, isPublic = true) =>
    apiCall('/api/teams/create', {
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
  get: (teamId: number) => apiCall(`/api/teams/${teamId}`),
  
  /**
   * Browse all public teams
   */
  browse: (limit = 50, offset = 0) =>
    apiCall(`/api/teams/?limit=${limit}&offset=${offset}`),
  
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
  getMembers: (teamId: number) => apiCall(`/api/teams/${teamId}/members`),
  
  /**
   * Join team by invite code
   */
  joinByCode: (inviteCode: string, userId: number) =>
    apiCall('/api/teams/join', {
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
  getStats: (teamId: number) => apiCall(`/api/teams/${teamId}/stats`),
  
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

