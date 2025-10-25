'use client'

/**
 * Staking Interface Component
 * 
 * Allows users to stake $100Bs tokens and earn revenue share
 * Shows revenue-based rewards (not fixed APY)
 */

import { useState, useEffect } from 'react'
import { tokenAPI } from '@/lib/api/enhancements'

interface StakingPosition {
  position_id: number
  staked_amount: number
  lock_period_days: number
  tier_allocation: number
  unlocks_at: string
  claimed_rewards: number
  projected_monthly_earnings: number
  projected_remaining_earnings: number
  share_of_tier: number
  days_remaining: number
}

interface StakingInterfaceProps {
  userId: number
  walletAddress?: string
  currentBalance?: number
}

export default function StakingInterface({ userId, walletAddress, currentBalance = 0 }: StakingInterfaceProps) {
  const [positions, setPositions] = useState<StakingPosition[]>([])
  const [tierStats, setTierStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [staking, setStaking] = useState(false)
  
  // Staking form
  const [stakeAmount, setStakeAmount] = useState('')
  const [selectedPeriod, setSelectedPeriod] = useState<30 | 60 | 90>(90)

  useEffect(() => {
    fetchStakingData()
  }, [userId])

  const fetchStakingData = async () => {
    try {
      setLoading(true)

      // Fetch user's positions
      const positionsData = await tokenAPI.getStakingPositions(userId) as any
      setPositions(positionsData.positions || [])

      // Fetch tier stats
      const stats = await tokenAPI.getTierStats()
      setTierStats(stats)
    } catch (err) {
      console.error('Failed to fetch staking data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStake = async () => {
    if (!walletAddress) {
      alert('Please connect your wallet first')
      return
    }

    const amount = parseFloat(stakeAmount)
    if (isNaN(amount) || amount <= 0) {
      alert('Please enter a valid amount')
      return
    }

    if (amount > currentBalance) {
      alert('Insufficient balance')
      return
    }

    setStaking(true)
    try {
      // In production, execute on-chain transaction first
      // const tx = await executeStakingTransaction(...)
      
      const result = await tokenAPI.stake(
        userId,
        walletAddress,
        amount,
        selectedPeriod
        // transaction_signature from on-chain tx
      )

      alert(`✅ Successfully staked ${amount} tokens for ${selectedPeriod} days!`)
      setStakeAmount('')
      await fetchStakingData()
    } catch (err: any) {
      alert(`❌ Staking failed: ${err.message}`)
    } finally {
      setStaking(false)
    }
  }

  const getTierInfo = (days: number) => {
    const info: Record<number, { allocation: number; color: string; label: string }> = {
      30: { allocation: 20, color: 'blue', label: 'Flexible' },
      60: { allocation: 30, color: 'purple', label: 'Balanced' },
      90: { allocation: 50, color: 'green', label: 'Best Rewards' }
    }
    return info[days] || info[90]
  }

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 border border-gray-700">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/3"></div>
          <div className="h-32 bg-gray-700 rounded"></div>
        </div>
      </div>
    )
  }

  const tierInfo = getTierInfo(selectedPeriod)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Stake & Earn</h2>
        <p className="text-gray-400">Lock tokens to earn from 30% of platform revenue</p>
      </div>

      {/* Revenue Model Explanation */}
      <div className="bg-gradient-to-r from-purple-900/40 to-blue-900/40 border border-purple-500/30 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-3">📊 Revenue-Based Staking Model</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-purple-200 font-semibold">30% of Revenue</p>
            <p className="text-gray-300">Goes to stakers monthly</p>
          </div>
          <div>
            <p className="text-purple-200 font-semibold">Tiered Distribution</p>
            <p className="text-gray-300">Longer locks = bigger share</p>
          </div>
          <div>
            <p className="text-purple-200 font-semibold">No Fixed APY</p>
            <p className="text-gray-300">Earnings vary with platform</p>
          </div>
        </div>
      </div>

      {/* Staking Form */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Create Staking Position</h3>
        
        {/* Lock Period Selection */}
        <div className="mb-6">
          <label className="block text-white font-medium mb-3">Lock Period</label>
          <div className="grid grid-cols-3 gap-3">
            {[30, 60, 90].map((days) => {
              const info = getTierInfo(days)
              return (
                <button
                  key={days}
                  onClick={() => setSelectedPeriod(days as 30 | 60 | 90)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedPeriod === days
                      ? `bg-${info.color}-900/30 border-${info.color}-500`
                      : 'bg-gray-700/30 border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <p className="text-white font-bold text-lg">{days} Days</p>
                  <p className={`text-sm ${selectedPeriod === days ? `text-${info.color}-200` : 'text-gray-400'}`}>
                    {info.allocation}% of pool
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{info.label}</p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Amount Input */}
        <div className="mb-6">
          <label className="block text-white font-medium mb-2">Amount to Stake</label>
          <div className="relative">
            <input
              type="number"
              value={stakeAmount}
              onChange={(e) => setStakeAmount(e.target.value)}
              placeholder="Enter amount"
              className="w-full bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
            <span className="absolute right-4 top-3 text-gray-400">$100Bs</span>
          </div>
          {currentBalance > 0 && (
            <p className="text-sm text-gray-400 mt-2">
              Available: {currentBalance.toLocaleString()} tokens
            </p>
          )}
        </div>

        {/* Estimated Rewards Preview */}
        {parseFloat(stakeAmount) > 0 && (
          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 mb-6">
            <p className="text-blue-200 font-semibold mb-2">📈 Estimated Rewards</p>
            <p className="text-sm text-gray-300">
              Based on recent platform revenue, you could earn approximately:
            </p>
            <p className="text-2xl font-bold text-white mt-2">
              ~$15/month <span className="text-sm text-gray-400">(per 1M tokens)</span>
            </p>
            <p className="text-xs text-gray-400 mt-2">
              * Actual rewards vary based on platform performance and tier size
            </p>
          </div>
        )}

        {/* Stake Button */}
        <button
          onClick={handleStake}
          disabled={staking || !walletAddress || !stakeAmount}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white py-4 rounded-lg font-bold text-lg transition-all"
        >
          {staking ? '🔄 Staking...' : walletAddress ? `Stake for ${selectedPeriod} Days` : '👛 Connect Wallet First'}
        </button>
      </div>

      {/* Active Positions */}
      {positions.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Your Staking Positions</h3>
          <div className="space-y-4">
            {positions.map((position) => (
              <div key={position.position_id} className="bg-gray-700/30 rounded-lg p-4 border border-gray-600">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-white font-bold text-lg">
                      {position.staked_amount.toLocaleString()} $100Bs
                    </p>
                    <p className="text-sm text-gray-400">
                      {position.lock_period_days}-day lock • {position.tier_allocation}% tier
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-green-400 font-bold">
                      ${position.projected_monthly_earnings.toFixed(2)}/mo
                    </p>
                    <p className="text-xs text-gray-400">
                      {position.share_of_tier.toFixed(2)}% of tier
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <div>
                    <span className="text-gray-400">Claimed: </span>
                    <span className="text-white">${position.claimed_rewards.toFixed(2)}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Unlocks: </span>
                    <span className="text-white">
                      {new Date(position.unlocks_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Days left: </span>
                    <span className="text-white">{position.days_remaining}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tier Statistics */}
      {tierStats && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">Platform Staking Tiers</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(tierStats.tiers || {}).map(([tierName, tierData]: [string, any]) => (
              <div key={tierName} className="bg-gray-700/30 rounded-lg p-4">
                <p className="text-gray-400 text-sm mb-1">{tierName.replace('_', ' ')}</p>
                <p className="text-white font-bold text-xl">
                  {tierData.total_staked.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
                <p className="text-sm text-gray-400">
                  {tierData.staker_count} stakers • {tierData.tier_allocation}% allocation
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

