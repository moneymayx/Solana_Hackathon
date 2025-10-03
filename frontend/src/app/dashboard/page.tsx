'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface DashboardData {
  lottery_status: {
    current_jackpot_usdc: number
    total_entries: number
    is_active: boolean
    fund_verified: boolean
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

interface FundVerificationData {
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
  }
  last_updated: string
}

interface SecurityStatusData {
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

export default function Dashboard() {
  const [overviewData, setOverviewData] = useState<DashboardData | null>(null)
  const [fundData, setFundData] = useState<FundVerificationData | null>(null)
  const [securityData, setSecurityData] = useState<SecurityStatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'funds' | 'security'>('overview')

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [overviewRes, fundRes, securityRes] = await Promise.all([
        fetch('/api/dashboard/overview'),
        fetch('/api/dashboard/fund-verification'),
        fetch('/api/dashboard/security-status')
      ])

      const [overview, fund, security] = await Promise.all([
        overviewRes.json(),
        fundRes.json(),
        securityRes.json()
      ])

      if (overview.success) setOverviewData(overview.data)
      if (fund.success) setFundData(fund.data)
      if (security.success) setSecurityData(security.data)

      if (!overview.success && !fund.success && !security.success) {
        setError('Failed to load dashboard data')
      }
    } catch (err) {
      setError('Network error loading dashboard data')
      console.error('Dashboard fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  }

  const getStatusColor = (status: boolean) => {
    return status ? 'text-green-400' : 'text-red-400'
  }

  const getStatusIcon = (status: boolean) => {
    return status ? '✅' : '❌'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-white mb-4">Dashboard Error</h2>
          <p className="text-gray-300 mb-6">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Public Dashboard</h1>
              <p className="text-gray-300">Real-time system status and fund verification</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Last updated</p>
              <p className="text-white font-mono">
                {overviewData?.last_updated ? 
                  new Date(overviewData.last_updated).toLocaleTimeString() : 
                  'Unknown'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-center mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-1 flex gap-1">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'funds', label: 'Fund Verification', icon: '💰' },
              { id: 'security', label: 'Security Status', icon: '🔒' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={cn(
                  "px-6 py-3 rounded-md font-medium transition-all duration-200 flex items-center gap-2",
                  activeTab === tab.id
                    ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg"
                    : "text-gray-400 hover:text-white hover:bg-gray-700/50"
                )}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && overviewData && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Current Jackpot</p>
                    <p className="text-2xl font-bold text-white">
                      {formatCurrency(overviewData.lottery_status.current_jackpot_usdc)}
                    </p>
                  </div>
                  <div className="text-3xl">💰</div>
                </div>
                <div className="mt-2">
                  <span className={cn(
                    "text-sm font-medium",
                    overviewData.lottery_status.fund_verified ? "text-green-400" : "text-red-400"
                  )}>
                    {overviewData.lottery_status.fund_verified ? 'Verified' : 'Unverified'}
                  </span>
                </div>
              </div>

              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Users</p>
                    <p className="text-2xl font-bold text-white">
                      {formatNumber(overviewData.platform_stats.total_users)}
                    </p>
                  </div>
                  <div className="text-3xl">👥</div>
                </div>
                <div className="mt-2">
                  <span className="text-green-400 text-sm font-medium">
                    +{overviewData.recent_activity.new_users_24h} today
                  </span>
                </div>
              </div>

              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Research Attempts</p>
                    <p className="text-2xl font-bold text-white">
                      {formatNumber(overviewData.platform_stats.total_attempts)}
                    </p>
                  </div>
                  <div className="text-3xl">🔬</div>
                </div>
                <div className="mt-2">
                  <span className="text-blue-400 text-sm font-medium">
                    +{overviewData.recent_activity.attempts_24h} today
                  </span>
                </div>
              </div>

              <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Success Rate</p>
                    <p className="text-2xl font-bold text-white">
                      {overviewData.platform_stats.success_rate.toFixed(3)}%
                    </p>
                  </div>
                  <div className="text-3xl">🎯</div>
                </div>
                <div className="mt-2">
                  <span className="text-purple-400 text-sm font-medium">
                    {overviewData.platform_stats.total_successes} successes
                  </span>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">System Health</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {Object.entries(overviewData.system_health).map(([key, status]) => (
                  <div key={key} className="flex items-center gap-3">
                    <span className="text-2xl">{getStatusIcon(status)}</span>
                    <div>
                      <p className="text-white font-medium capitalize">
                        {key.replace(/_/g, ' ')}
                      </p>
                      <p className={cn("text-sm", getStatusColor(status))}>
                        {status ? 'Active' : 'Inactive'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Recent Activity (24h)</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-400">
                    {formatNumber(overviewData.recent_activity.new_users_24h)}
                  </p>
                  <p className="text-gray-400">New Users</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-400">
                    {formatNumber(overviewData.recent_activity.questions_24h)}
                  </p>
                  <p className="text-gray-400">Questions Asked</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-400">
                    {formatNumber(overviewData.recent_activity.attempts_24h)}
                  </p>
                  <p className="text-gray-400">Research Attempts</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Fund Verification Tab */}
        {activeTab === 'funds' && fundData && (
          <div className="space-y-6">
            {/* Fund Status */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">Fund Verification Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">Lottery Funds (USDC)</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current Jackpot:</span>
                      <span className="text-white font-mono">
                        {formatCurrency(fundData.lottery_funds.current_jackpot_usdc)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Actual Balance:</span>
                      <span className="text-white font-mono">
                        {formatCurrency(fundData.lottery_funds.jackpot_balance_usdc)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Verification:</span>
                      <span className={cn(
                        "font-medium",
                        fundData.lottery_funds.fund_verified ? "text-green-400" : "text-red-400"
                      )}>
                        {fundData.lottery_funds.fund_verified ? '✅ Verified' : '❌ Unverified'}
                      </span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3">Treasury Funds (SOL)</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">SOL Balance:</span>
                      <span className="text-white font-mono">
                        {fundData.treasury_funds.balance_sol.toFixed(4)} SOL
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">USD Value:</span>
                      <span className="text-white font-mono">
                        {formatCurrency(fundData.treasury_funds.balance_usd)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Verification Links */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4">On-Chain Verification</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-gray-400 text-sm mb-2">Lottery PDA Address:</p>
                  <div className="bg-gray-900/50 rounded-lg p-3 font-mono text-sm text-white break-all">
                    {fundData.lottery_funds.lottery_pda || 'Not available'}
                  </div>
                </div>
                <div className="flex gap-4">
                  <a
                    href={fundData.verification_links.solana_explorer}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center gap-2"
                  >
                    🔗 View on Solana Explorer
                  </a>
                  <a
                    href={fundData.verification_links.program_id}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-purple-500 hover:bg-purple-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center gap-2"
                  >
                    🔗 View Program ID
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Security Status Tab */}
        {activeTab === 'security' && securityData && (
          <div className="space-y-6">
            {/* Security Overview */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">Security Status</h3>
                <div className="bg-green-500/20 border border-green-500/50 rounded-lg px-4 py-2">
                  <span className="text-green-400 font-semibold">
                    {securityData.overall_security_score} Security
                  </span>
                </div>
              </div>
              <p className="text-gray-300">
                All security systems are active and monitoring for threats. The platform uses 
                multiple layers of protection including AI manipulation detection, sybil prevention, 
                and rate limiting.
              </p>
            </div>

            {/* Rate Limiting */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">Rate Limiting</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">
                    {securityData.rate_limiting.requests_per_minute}
                  </p>
                  <p className="text-gray-400">Requests/Minute</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">
                    {securityData.rate_limiting.requests_per_hour}
                  </p>
                  <p className="text-gray-400">Requests/Hour</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">
                    {securityData.rate_limiting.cooldown_seconds}s
                  </p>
                  <p className="text-gray-400">Transfer Cooldown</p>
                </div>
              </div>
            </div>

            {/* Sybil Detection */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">Sybil Detection</h4>
              <div className="space-y-3">
                <p className="text-gray-300">
                  Advanced multi-factor analysis to prevent duplicate accounts and fraud:
                </p>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {securityData.sybil_detection.detection_methods.map((method, index) => (
                    <li key={index} className="flex items-center gap-2 text-gray-300">
                      <span className="text-green-400">✓</span>
                      {method}
                    </li>
                  ))}
                </ul>
                <p className="text-sm text-gray-400 mt-3">
                  {securityData.sybil_detection.blacklisted_phrases}
                </p>
              </div>
            </div>

            {/* AI Security */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">AI Security System</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-400 text-sm">Personality System</p>
                  <p className="text-white font-medium">{securityData.ai_security.personality_system}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Manipulation Detection</p>
                  <p className="text-white font-medium">{securityData.ai_security.manipulation_detection}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Blacklisting System</p>
                  <p className="text-white font-medium">{securityData.ai_security.blacklisting_system}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Success Rate Target</p>
                  <p className="text-white font-medium">{securityData.ai_security.success_rate_target}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
