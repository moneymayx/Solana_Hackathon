'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { sumBountyPools } from '@/lib/analytics'
import {
  fetchDashboardOverview,
  fetchFundVerification,
  fetchSecurityStatus,
  DashboardOverviewData,
  FundVerificationData,
  SecurityStatusData,
} from '@/lib/api/dashboard'
import { fetchBounties } from '@/lib/api/bounties'
import ContractActivityMonitor from '@/components/ContractActivityMonitor'
import TopNavigation from '@/components/TopNavigation'

type AnalyticsTab = 'overview' | 'funds' | 'security' | 'contracts'

const ANALYTICS_TABS: Array<{ id: AnalyticsTab; label: string; icon: string }> = [
  { id: 'overview', label: 'Overview', icon: '📊' },
  { id: 'funds', label: 'Fund Verification', icon: '💰' },
  { id: 'security', label: 'Security Status', icon: '🔒' },
  { id: 'contracts', label: 'Contract Activity', icon: '⚡' },
]

export default function Analytics() {
  const [overviewData, setOverviewData] = useState<DashboardOverviewData | null>(null)
  const [fundData, setFundData] = useState<FundVerificationData | null>(null)
  const [securityData, setSecurityData] = useState<SecurityStatusData | null>(null)
  const [totalBounties, setTotalBounties] = useState<number>(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('overview')

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [overview, fund, security, bounties] = await Promise.all([
        fetchDashboardOverview().catch((err: unknown) => {
          console.warn('Overview fetch failed', err)
          return null
        }),
        fetchFundVerification().catch((err: unknown) => {
          console.warn('Fund verification fetch failed', err)
          return null
        }),
        fetchSecurityStatus().catch((err: unknown) => {
          console.warn('Security status fetch failed', err)
          return null
        }),
        fetchBounties().catch((err: unknown) => {
          console.warn('Bounty fetch failed', err)
          return null
        }),
      ])

      setOverviewData(overview)
      setFundData(fund)
      setSecurityData(security)
      const bountyTotalAmount = sumBountyPools(bounties)
      // Persisting the aggregated bounty total lets us surface the combined jackpot exposure alongside wallet verification data.
      setTotalBounties(bountyTotalAmount)

      if (!overview && !fund && !security && (!bounties || bounties.length === 0)) {
        setError('Failed to load analytics data. Check console for details.')
      }
    } catch (err) {
      setError(`Network error loading analytics data: ${err instanceof Error ? err.message : 'Unknown error'}`)
      console.error('Analytics fetch error:', err)
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
    return status ? 'text-green-600' : 'text-red-600'
  }

  const getStatusIcon = (status: boolean) => {
    return status ? '✅' : '❌'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <TopNavigation />
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </div>
    )
  }

  const displayedBountyTotal = totalBounties > 0
    ? totalBounties
    : overviewData?.lottery_status.current_jackpot_usdc ?? 0
  // Falling back to the on-chain jackpot snapshot keeps the overview resilient while still prioritizing the live bounty aggregation across environments.

  return (
    <div className="min-h-screen bg-white">
      <TopNavigation />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
              <p className="text-gray-600">Real-time system status and fund verification</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Last updated</p>
              <p className="text-gray-900 font-mono">
                {overviewData?.last_updated ? 
                  new Date(overviewData.last_updated).toLocaleTimeString() : 
                  'Unknown'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-red-800 font-medium">Error Loading Data</h3>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
              <button
                onClick={fetchDashboardData}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 rounded-lg p-1 flex gap-1">
            {ANALYTICS_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "px-6 py-3 rounded-md font-medium transition-all duration-200 flex items-center gap-2",
                  activeTab === tab.id
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                )}
              >
                <span>{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {overviewData ? (
              <>
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Total Bounty Amount</p>
                        <p className="text-2xl font-bold text-gray-900 break-words break-all">
                          {formatCurrency(displayedBountyTotal)}
                        </p>
                      </div>
                      <div className="text-3xl">💰</div>
                    </div>
                    <div className="mt-2">
                      <span className={cn(
                        "text-sm font-medium",
                        overviewData.lottery_status.fund_verified ? "text-green-600" : "text-red-600"
                      )}>
                        {overviewData.lottery_status.fund_verified ? 'Verified' : 'Unverified'}
                      </span>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Total Users</p>
                        <p className="text-2xl font-bold text-gray-900 break-words break-all">
                          {formatNumber(overviewData.platform_stats.total_users)}
                        </p>
                      </div>
                      <div className="text-3xl">👥</div>
                    </div>
                    <div className="mt-2">
                      <span className="text-green-600 text-sm font-medium">
                        +{overviewData.recent_activity.new_users_24h} today
                      </span>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Success Rate</p>
                        <p className="text-2xl font-bold text-gray-900 break-words break-all">
                          {overviewData.platform_stats.success_rate.toFixed(3)}%
                        </p>
                      </div>
                      <div className="text-3xl">🎯</div>
                    </div>
                    <div className="mt-2">
                      <span className="text-purple-600 text-sm font-medium">
                        {overviewData.platform_stats.total_successes} successes
                      </span>
                    </div>
                  </div>
                </div>

                {/* System Health */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">System Health</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    {Object.entries(overviewData.system_health).map(([key, status]) => (
                      <div key={key} className="flex items-center gap-3">
                        <span className="text-2xl">{getStatusIcon(status)}</span>
                        <div>
                          <p className="text-gray-900 font-medium capitalize">
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
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity (24h)</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-600">
                        {formatNumber(overviewData.recent_activity.new_users_24h)}
                      </p>
                      <p className="text-gray-600">New Users</p>
                    </div>
                    <div className="text-center">
                      <p className="text-3xl font-bold text-blue-600">
                        {formatNumber(overviewData.recent_activity.questions_24h)}
                      </p>
                      <p className="text-gray-600">Questions Asked</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Overview Data</h3>
                <p className="text-gray-600 mb-4">Unable to load overview data. Check your console for details.</p>
                <button
                  onClick={fetchDashboardData}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        )}

        {/* Fund Verification Tab */}
        {activeTab === 'funds' && (
          <div className="space-y-6">
            {fundData ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Jackpot Wallet</h3>
                    <div className="space-y-4">
                      <div>
                        <p className="text-gray-600 text-sm">Address</p>
                        <div className="font-mono text-xs text-gray-900 break-words break-all">
                          {fundData.jackpot_wallet.address || 'Not configured'}
                        </div>
                      </div>
                      <p className="text-sm text-gray-500">
                        Primary jackpot treasury for bounty payouts. View on explorer to confirm balances.
                      </p>
                      <div>
                        <p className="text-gray-600 text-sm">USDC Balance</p>
                        <div className="text-gray-900 font-mono break-words break-all">
                          {formatCurrency(fundData.jackpot_wallet.balance_usdc)}
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        Balance checked: {new Date(fundData.jackpot_wallet.last_balance_check).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {fundData.staking_wallet && (
                    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                      <h3 className="text-xl font-bold text-gray-900 mb-4">Staking Wallet</h3>
                      <div className="space-y-4">
                        <div>
                          <p className="text-gray-600 text-sm">Address</p>
                          <div className="font-mono text-xs text-gray-900 break-words break-all">
                            {fundData.staking_wallet.address}
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">
                          On-chain staking reserve for reward distributions. View on explorer to confirm balances.
                        </p>
                        <div>
                          <p className="text-gray-600 text-sm">USDC Balance</p>
                          <div className="text-gray-900 font-mono break-words break-all">
                            {formatCurrency(fundData.staking_wallet.balance_usd ?? 0)}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          Balance checked: {new Date(fundData.staking_wallet.last_balance_check).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">On-Chain Verification</h3>
                  <div className="space-y-4">
                    <div>
                      <p className="text-gray-600 text-sm mb-2">Lottery PDA</p>
                      <div className="bg-gray-50 rounded-lg p-3 font-mono text-sm text-gray-900 break-all border border-gray-200">
                        {fundData.lottery_funds.lottery_pda || 'Not available'}
                      </div>
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm mb-2">Jackpot Token Account</p>
                      <div className="bg-gray-50 rounded-lg p-3 font-mono text-sm text-gray-900 break-all border border-gray-200">
                        {fundData.lottery_funds.jackpot_token_account || 'Not available'}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-3">
                      {[
                        { label: 'View Lottery PDA', href: fundData.verification_links.solana_explorer, tone: 'bg-blue-600 hover:bg-blue-700' },
                        { label: 'Program ID', href: fundData.verification_links.program_id, tone: 'bg-purple-600 hover:bg-purple-700' },
                        { label: 'Jackpot Token Account', href: fundData.verification_links.jackpot_token_account, tone: 'bg-emerald-600 hover:bg-emerald-700' },
                        { label: 'Jackpot Wallet', href: fundData.verification_links.jackpot_wallet, tone: 'bg-orange-500 hover:bg-orange-600' },
                        { label: 'Staking Wallet', href: fundData.verification_links.staking_wallet, tone: 'bg-slate-600 hover:bg-slate-700' }
                      ].filter(link => link.href).map(link => (
                        <a
                          key={link.label}
                          href={link.href as string}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={cn(link.tone, "text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm flex items-center gap-2")}
                        >
                          🔗 {link.label}
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">💰</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Fund Data</h3>
                <p className="text-gray-600 mb-4">Unable to load fund verification data. Check your console for details.</p>
                <button
                  onClick={fetchDashboardData}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        )}

        {/* Security Status Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {securityData ? (
              <>
                {/* Security Overview */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900">Security Status</h3>
                    <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2">
                      <span className="text-green-700 font-semibold">
                        {securityData.overall_security_score} Security
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-600">
                    All security systems are active and monitoring for threats. The platform uses 
                    multiple layers of protection including AI manipulation detection, sybil prevention, 
                    and rate limiting.
                  </p>
                </div>

                {/* Rate Limiting */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Rate Limiting</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {securityData.rate_limiting.requests_per_minute}
                      </p>
                      <p className="text-gray-600">Requests/Minute</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {securityData.rate_limiting.requests_per_hour}
                      </p>
                      <p className="text-gray-600">Requests/Hour</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {securityData.rate_limiting.cooldown_seconds}s
                      </p>
                      <p className="text-gray-600">Transfer Cooldown</p>
                    </div>
                  </div>
                </div>

                {/* Sybil Detection */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Sybil Detection</h4>
                  <div className="space-y-3">
                    <p className="text-gray-600">
                      Advanced multi-factor analysis to prevent duplicate accounts and fraud:
                    </p>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {securityData.sybil_detection.detection_methods.map((method, index) => (
                        <li key={index} className="flex items-center gap-2 text-gray-700">
                          <span className="text-green-600">✓</span>
                          {method}
                        </li>
                      ))}
                    </ul>
                    <p className="text-sm text-gray-500 mt-3">
                      {securityData.sybil_detection.blacklisted_phrases}
                    </p>
                  </div>
                </div>

                {/* AI Security */}
                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">AI Security System</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-gray-600 text-sm">Personality System</p>
                      <p className="text-gray-900 font-medium">{securityData.ai_security.personality_system}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Manipulation Detection</p>
                      <p className="text-gray-900 font-medium">{securityData.ai_security.manipulation_detection}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Blacklisting System</p>
                      <p className="text-gray-900 font-medium">{securityData.ai_security.blacklisting_system}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 text-sm">Success Rate Target</p>
                      <p className="text-gray-900 font-medium">{securityData.ai_security.success_rate_target}</p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Security Data</h3>
                <p className="text-gray-600 mb-4">Unable to load security status data. Check your console for details.</p>
                <button
                  onClick={fetchDashboardData}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        )}

        {/* Contract Activity Tab */}
        {activeTab === 'contracts' && (
          <div className="space-y-6">
            <ContractActivityMonitor 
              autoRefresh={true}
              refreshInterval={5000}
              maxTransactions={20}
            />
          </div>
        )}
      </div>
    </div>
  )
}
