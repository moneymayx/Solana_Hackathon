'use client'

/**
 * Token Dashboard Component
 * 
 * Displays user's $100Bs token balance and platform benefits
 */

import { useState, useEffect } from 'react'
import { tokenAPI, DiscountTier, TokenBalance, TokenMetrics } from '@/lib/api/enhancements'

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
      const tiersData = await tokenAPI.getDiscountTiers()
      setTiers(tiersData.tiers ?? [])

      // Fetch platform metrics
      const metricsData = await tokenAPI.getMetrics()
      setMetrics(metricsData ?? null)

      // Fetch user balance if wallet connected
      if (walletAddress) {
        try {
          const balanceData = await tokenAPI.checkBalance(walletAddress, userId)
          setBalance(balanceData ?? null)
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
      const balanceData = await tokenAPI.checkBalance(walletAddress, userId)
      setBalance(balanceData ?? null)
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
            
            <p className="text-xs opacity-75 mt-4">
              Last verified: {new Date(balance.last_verified).toLocaleTimeString()}
            </p>
            
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded">
              <p className="text-xs text-blue-200">
                💡 <strong>Tip:</strong> Stake your $100Bs tokens to earn from 10% of platform revenue!
              </p>
            </div>
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

      {/* Token Utility - UPDATED (Removed Discounts) */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">💎 $100Bs Token Utility</h3>
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-purple-900/20 border border-purple-500/30">
            <div className="flex items-center gap-3">
              <div className="text-3xl">🏆</div>
              <div>
                <p className="text-white font-semibold">Staking Rewards</p>
                <p className="text-sm text-gray-400">
                  Earn 10% of platform revenue by staking tokens (30/60/90 day periods)
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-500/30">
            <div className="flex items-center gap-3">
              <div className="text-3xl">🔥</div>
              <div>
                <p className="text-white font-semibold">Deflationary Model</p>
                <p className="text-sm text-gray-400">
                  10% of revenue used to buy back and burn $100Bs tokens
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-lg bg-green-900/20 border border-green-500/30">
            <div className="flex items-center gap-3">
              <div className="text-3xl">💰</div>
              <div>
                <p className="text-white font-semibold">Revenue Share</p>
                <p className="text-sm text-gray-400">
                  Stakers receive proportional share of rewards based on lock period
                </p>
              </div>
            </div>
          </div>
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
            <div className="text-3xl mb-2">💰</div>
            <p className="text-white font-semibold">Revenue Share</p>
            <p className="text-sm text-gray-400">10% to stakers monthly</p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">📈</div>
            <p className="text-white font-semibold">Revenue Share</p>
            <p className="text-sm text-gray-400">Earn from platform success</p>
          </div>
          <div className="text-center p-4">
            <div className="text-3xl mb-2">🔥</div>
            <p className="text-white font-semibold">Buyback & Burn</p>
            <p className="text-sm text-gray-400">10% revenue to buyback</p>
          </div>
        </div>
      </div>
    </div>
  )
}

