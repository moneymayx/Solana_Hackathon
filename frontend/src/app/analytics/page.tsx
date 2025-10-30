'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import {
  fetchDashboardOverview,
  fetchFundVerification,
  fetchSecurityStatus,
  DashboardOverviewData,
  FundVerificationData,
  SecurityStatusData,
} from '@/lib/api/dashboard'
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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('overview')

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [overview, fund, security] = await Promise.all([
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
      ])

      setOverviewData(overview)
      setFundData(fund)
      setSecurityData(security)

      if (!overview && !fund && !security) {
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

const jackpotWalletStatusStyles: Record<string, { label: string; color: string }> = {
  verified: { label: 'Verified coverage', color: 'text-green-600' },
  shortfall: { label: 'Funding shortfall', color: 'text-red-600' },
  uninitialized: { label: 'Awaiting initial funding', color: 'text-gray-500' }
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
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Current Jackpot</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(overviewData.lottery_status.current_jackpot_usdc)}
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
                        <p className="text-2xl font-bold text-gray-900">
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
                        <p className="text-gray-600 text-sm">Research Attempts</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatNumber(overviewData.platform_stats.total_attempts)}
                        </p>
                      </div>
                      <div className="text-3xl">🔬</div>
                    </div>
                    <div className="mt-2">
                      <span className="text-blue-600 text-sm font-medium">
                        +{overviewData.recent_activity.attempts_24h} today
                      </span>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-gray-600 text-sm">Success Rate</p>
                        <p className="text-2xl font-bold text-gray-900">
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
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                    <div className="text-center">
                      <p className="text-3xl font-bold text-purple-600">
                        {formatNumber(overviewData.recent_activity.attempts_24h)}
                      </p>
                      <p className="text-gray-600">Research Attempts</p>
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
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Lottery Funds (USDC)</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Target Jackpot</span>
                        <span className="text-gray-900 font-mono">
                          {formatCurrency(fundData.lottery_funds.current_jackpot_usdc)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">On-Chain Balance</span>
                        <span className="text-gray-900 font-mono">
                          {formatCurrency(fundData.lottery_funds.jackpot_balance_usdc)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Coverage</span>
                        <span className={cn(
                          "font-medium",
                          fundData.lottery_funds.fund_verified ? "text-green-600" : "text-red-600"
                        )}>
                          {fundData.lottery_funds.fund_verified ? '✅ Fully Verified' : '❌ Shortfall Detected'}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Difference</span>
                        <span className="font-medium">
                          {(() => {
                            if (fundData.lottery_funds.balance_gap_usdc > 0) {
                              return (
                                <span className="text-red-600">
                                  -{formatCurrency(fundData.lottery_funds.balance_gap_usdc)} (Shortfall)
                                </span>
                              )
                            }
                            if (fundData.lottery_funds.surplus_usdc > 0) {
                              return (
                                <span className="text-green-600">
                                  +{formatCurrency(fundData.lottery_funds.surplus_usdc)} (Surplus)
                                </span>
                              )
                            }
                            return <span className="text-gray-500">Balanced</span>
                          })()}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {fundData.lottery_funds.last_prize_pool_update
                          ? `Last prize pool update: ${new Date(fundData.lottery_funds.last_prize_pool_update).toLocaleString()}`
                          : 'No prize pool updates recorded yet.'}
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">Jackpot Wallet</h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-gray-600 text-sm">Wallet Address</p>
                        <p className="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 font-mono text-xs break-all">
                          {fundData.jackpot_wallet.address || 'Not configured'}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm">Token Account</p>
                        <p className="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 font-mono text-xs break-all">
                          {fundData.jackpot_wallet.token_account || 'Not detected'}
                        </p>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">USDC Balance</span>
                        <span className="text-gray-900 font-mono">
                          {formatCurrency(fundData.jackpot_wallet.balance_usdc)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">SOL Balance</span>
                        <span className="text-gray-900 font-mono">
                          {fundData.jackpot_wallet.balance_sol !== null
                            ? `${fundData.jackpot_wallet.balance_sol.toFixed(4)} SOL`
                            : 'N/A'}
                        </span>
                      </div>
                      <div>
                        {(() => {
                          const walletStatus = jackpotWalletStatusStyles[fundData.jackpot_wallet.verification_status] ?? jackpotWalletStatusStyles.uninitialized
                          return (
                            <span className={cn("text-sm font-medium", walletStatus.color)}>
                              {walletStatus.label}
                            </span>
                          )
                        })()}
                      </div>
                      <div className="text-sm text-gray-500">
                        Balance checked: {new Date(fundData.jackpot_wallet.last_balance_check).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {fundData.treasury_wallet && (
                    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                      <h3 className="text-xl font-bold text-gray-900 mb-4">Treasury Wallet</h3>
                      <div className="space-y-3">
                        <div>
                          <p className="text-gray-600 text-sm">Address</p>
                          <p className="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 font-mono text-xs break-all">
                            {fundData.treasury_wallet.address}
                          </p>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">SOL Balance</span>
                          <span className="text-gray-900 font-mono">
                            {fundData.treasury_wallet.balance_sol !== null
                              ? `${fundData.treasury_wallet.balance_sol.toFixed(4)} SOL`
                              : 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-600">USD Estimate</span>
                          <span className="text-gray-900 font-mono">
                            {fundData.treasury_wallet.balance_usd !== null
                              ? formatCurrency(fundData.treasury_wallet.balance_usd)
                              : 'N/A'}
                          </span>
                        </div>
                        <div className="text-sm text-gray-500">
                          Balance checked: {new Date(fundData.treasury_wallet.last_balance_check).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Fund Activity Summary</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
                      <p className="text-sm text-gray-600">Completed Contributions</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {formatCurrency(fundData.fund_activity.total_completed_usdc)}
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
                      <p className="text-sm text-gray-600">Pending Contributions</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {formatCurrency(fundData.fund_activity.total_pending_usdc)}
                      </p>
                      <p className="text-sm text-gray-500">{fundData.fund_activity.pending_count} pending</p>
                    </div>
                    <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
                      <p className="text-sm text-gray-600">Failed Contributions</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {formatCurrency(fundData.fund_activity.total_failed_usdc)}
                      </p>
                      <p className="text-sm text-gray-500">{fundData.fund_activity.failed_count} failed</p>
                    </div>
                    <div className="bg-gray-50 rounded-md p-4 border border-gray-200">
                      <p className="text-sm text-gray-600">Recorded Entries</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {formatNumber(fundData.fund_activity.total_entries_recorded)}
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-500">
                    {fundData.fund_activity.last_deposit_at
                      ? `Last contribution observed: ${new Date(fundData.fund_activity.last_deposit_at).toLocaleString()}`
                      : 'No fund contributions have been recorded yet.'}
                  </div>
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
                        { label: 'Treasury Wallet', href: fundData.verification_links.treasury_wallet, tone: 'bg-slate-600 hover:bg-slate-700' }
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
