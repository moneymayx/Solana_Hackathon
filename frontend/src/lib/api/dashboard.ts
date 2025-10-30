import { backendFetch } from './client'

export interface DashboardOverviewData {
  lottery_status: {
    current_jackpot_usdc: number
    total_entries: number
    fund_verified: boolean
    is_active: boolean
    target_jackpot_usdc?: number
    jackpot_balance_usdc?: number
    balance_gap_usdc?: number
    surplus_usdc?: number
  }
  platform_stats: {
    total_users: number
    total_questions: number
    total_attempts: number
    total_successes: number
    success_rate: number
  }
  recent_activity: {
    new_users_24h: number
    questions_24h: number
    attempts_24h: number
  }
  system_health: {
    ai_agent_active: boolean
    smart_contract_connected: boolean
    database_connected: boolean
    rate_limiter_active: boolean
    sybil_detection_active: boolean
  }
  last_updated: string
}

export interface FundVerificationData {
  lottery_funds: {
    current_jackpot_usdc: number
    jackpot_balance_usdc: number
    fund_verified: boolean
    balance_gap_usdc: number
    surplus_usdc: number
    lottery_pda: string
    program_id: string
    jackpot_token_account: string
    last_prize_pool_update: string | null
  }
  jackpot_wallet: {
    address: string
    token_account: string
    mint?: string
    balance_usdc: number
    balance_sol: number | null
    verification_status: 'verified' | 'shortfall' | 'uninitialized'
    last_balance_check: string
  }
  treasury_wallet?: {
    address: string
    balance_sol: number | null
    balance_usd: number | null
    last_balance_check: string
  } | null
  fund_activity: {
    total_completed_usdc: number
    total_pending_usdc: number
    total_failed_usdc: number
    pending_count: number
    failed_count: number
    total_entries_recorded: number
    last_deposit_at: string | null
  }
  verification_links: {
    solana_explorer: string
    program_id: string
    jackpot_token_account: string
    jackpot_wallet?: string | null
    treasury_wallet?: string | null
  }
  last_updated: string
}

export interface SecurityStatusData {
  rate_limiting: {
    active: boolean
    requests_per_minute: number
    requests_per_hour: number
    cooldown_seconds: number
  }
  sybil_detection: {
    active: boolean
    detection_methods: string[]
    blacklisted_phrases: string
  }
  ai_security: {
    personality_system: string
    manipulation_detection: string
    blacklisting_system: string
    success_rate_target: string
    learning_enabled: boolean
  }
  overall_security_score: string
  last_updated: string
}

interface DashboardOverviewResponse {
  success: boolean
  data?: DashboardOverviewData
  error?: string
}

interface FundVerificationResponse {
  success: boolean
  data?: FundVerificationData
  error?: string
}

interface SecurityStatusResponse {
  success: boolean
  data?: SecurityStatusData
  error?: string
}

export async function fetchDashboardOverview(): Promise<DashboardOverviewData | null> {
  const response = await backendFetch<DashboardOverviewResponse>('/api/dashboard/overview')
  if (!response.success) {
    throw new Error(response.error || 'Failed to load dashboard overview')
  }
  return response.data ?? null
}

export async function fetchFundVerification(): Promise<FundVerificationData | null> {
  const response = await backendFetch<FundVerificationResponse>('/api/dashboard/fund-verification')
  if (!response.success) {
    throw new Error(response.error || 'Failed to load fund verification data')
  }
  return response.data ?? null
}

export async function fetchSecurityStatus(): Promise<SecurityStatusData | null> {
  const response = await backendFetch<SecurityStatusResponse>('/api/dashboard/security-status')
  if (!response.success) {
    throw new Error(response.error || 'Failed to load security status data')
  }
  return response.data ?? null
}
