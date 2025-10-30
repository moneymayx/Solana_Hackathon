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
    lottery_pda: string
    program_id: string
  }
  treasury_funds: {
    balance_sol: number
    balance_usd: number
  }
  verification_links: {
    solana_explorer: string
    program_id: string
    jackpot_token_account?: string
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
