'use client'

/**
 * Token Dashboard Component
 * 
 * Displays user's $100Bs token balance, discount tier, and benefits
 */

import { useState, useEffect } from 'react'
import { tokenAPI } from '@/lib/api/enhancements'

interface TokenBalance {
  wallet_address: string
  token_balance: number
  discount_rate: number
  tokens_to_next_tier: number
  last_verified: string
}

interface DiscountTier {
  min_token_balance: number
  discount_percentage: number
  description: string
}

interface TokenMetrics {
  token_symbol: string
  total_supply: number
  total_staked: number
  staking_ratio: number
  staking_revenue_percentage: number
}

interface TokenDashboardProps {
  userId: number
  walletAddress?: string
}

export default function TokenDashboard({ userId, walletAddress }: TokenDashboardProps) {
  const [balance, setBalance] = useState<TokenBalance | null>(null)
  const [tiers, setTiers] = useState<DiscountTier[]>([])
  const [metrics, setMetrics] = useState<TokenMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchTokenData()
  }, [userId, walletAddress])

  const fetchTokenData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch discount tiers (always available)
      const tiersData = await tokenAPI.getDiscountTiers() as any
      setTiers(tiersData.tiers)

      // Fetch platform metrics
      const metricsData = await tokenAPI.getMetrics() as any
      setMetrics(metricsData)

      // Fetch user balance if wallet connected
      if (walletAddress) {
        try {
          const balanceData = await tokenAPI.checkBalance(walletAddress, userId) as any
          setBalance(balanceData)
        } catch (balanceError) {
          console.warn('Could not fetch balance:', balanceError)
          // Continue even if balance check fails
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load token data')
      console.error('Token data fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const refreshBalance = async () => {
    if (!walletAddress) return
    
    setRefreshing(true)
    try {
      const balanceData = await tokenAPI.checkBalance(walletAddress, userId) as any
      setBalance(balanceData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 border border-gray-700">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/3"></div>
          <div className="h-32 bg-gray-700 rounded"></div>
          <div className="h-24 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">$100Bs Token</h2>
          <p className="text-gray-400">Your token balance and benefits</p>
        </div>
        {walletAddress && (
          <button
            onClick={refreshBalance}
            disabled={refreshing}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {refreshing ? '🔄 Refreshing...' : '🔄 Refresh Balance'}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Token Balance Card */}
      {walletAddress ? (
        balance ? (
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm opacity-90">Your Balance</p>
                <p className="text-5xl font-bold">
                  {balance.token_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                </p>
                <p className="text-xl opacity-90">$100Bs</p>
              </div>
              <div className="text-6xl">💎</div>
            </div>
            
            <div className="bg-white bg-opacity-20 rounded-lg p-4 mt-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm opacity-90">Current Discount</p>
                  <p className="text-3xl font-bold">{(balance.discount_rate * 100).toFixed(0)}%</p>
                </div>
                {balance.tokens_to_next_tier > 0 && (
                  <div className="text-right">
                    <p className="text-sm opacity-90">To Next Tier</p>
                    <p className="text-lg font-medium">
                      {balance.tokens_to_next_tier.toLocaleString()} tokens
                    </p>
                  </div>
                )}
              </div>
            </div>
            
            <p className="text-xs opacity-75 mt-4">
              Last verified: {new Date(balance.last_verified).toLocaleTimeString()}
            </p>
          </div>
        ) : (
          <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
            <div className="text-4xl mb-4">🔍</div>
            <p className="text-white font-medium mb-2">Balance Not Loaded</p>
            <p className="text-gray-400 mb-4">Click refresh to check your on-chain balance</p>
            <button
              onClick={refreshBalance}
              disabled={refreshing}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium"
            >
              Check Balance
            </button>
          </div>
        )
      ) : (
        <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
          <div className="text-4xl mb-4">👛</div>
          <p className="text-white font-medium mb-2">Connect Your Wallet</p>
          <p className="text-gray-400">Connect your Solana wallet to see your $100Bs balance</p>
        </div>
      )}

      {/* Discount Tiers */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">💰 Discount Tiers</h3>
        <div className="space-y-3">
          {tiers.map((tier, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border-2 transition-all ${
                balance && balance.token_balance >= tier.min_token_balance
                  ? 'bg-green-900/20 border-green-500'
                  : 'bg-gray-700/20 border-gray-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-semibold">{tier.description}</p>
                  <p className="text-sm text-gray-400">
                    Hold {tier.min_token_balance.toLocaleString()}+ tokens
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-400">
                    {tier.discount_percentage}%
                  </p>
                  <p className="text-sm text-gray-400">off queries</p>
                </div>
                {balance && balance.token_balance >= tier.min_token_balance && (
                  <div className="text-2xl">✅</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Platform Metrics */}
      {metrics && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">📊 Platform Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-700/30 rounded-lg p-4">
              <p className="text-sm text-gray-400">Total Supply</p>
              <p className="text-2xl font-bold text-white">
                {metrics.total_supply.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">{metrics.token_symbol}</p>
            </div>
            
            <div className="bg-gray-700/30 rounded-lg p-4">
              <p className="text-sm text-gray-400">Total Staked</p>
              <p className="text-2xl font-bold text-white">
                {metrics.total_staked.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </p>
              <p className="text-xs text-gray-500">tokens locked</p>
            </div>
            
            <div className="bg-gray-700/30 rounded-lg p-4">
              <p className="text-sm text-gray-400">Staking Ratio</p>
              <p className="text-2xl font-bold text-white">
                {metrics.staking_ratio.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">of supply staked</p>
            </div>
            
            <div className="bg-gray-700/30 rounded-lg p-4">
              <p className="text-sm text-gray-400">Revenue to Stakers</p>
              <p className="text-2xl font-bold text-white">
                {metrics.staking_revenue_percentage}%
              </p>
              <p className="text-xs text-gray-500">monthly distribution</p>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <p className="text-sm text-blue-200">
              💡 <strong>Revenue-Based Staking:</strong> Stakers earn from 30% of platform revenue. 
              No fixed APY - rewards depend on platform success!
            </p>
          </div>
        </div>
      )}

      {/* Benefits Summary */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">🎁 Token Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4">
            <div className="text-3xl mb-2">💸</div>
            <p className="text-white font-semibold">Discounts</p>
            <p className="text-sm text-gray-400">Up to 50% off queries</p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">📈</div>
            <p className="text-white font-semibold">Revenue Share</p>
            <p className="text-sm text-gray-400">Earn from platform success</p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">🔥</div>
            <p className="text-white font-semibold">Buyback & Burn</p>
            <p className="text-sm text-gray-400">5% revenue to buyback</p>
          </div>
        </div>
      </div>
    </div>
  )
}

