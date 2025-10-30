'use client'

/**
 * Staking Interface Component
 * 
 * Allows users to stake $100Bs tokens and earn revenue share
 * Shows revenue-based rewards (not fixed APY)
 */

import { useState, useEffect, useCallback } from 'react'
import {
  tokenAPI,
  StakingPosition,
  StakingPositionsResponse,
  TokenTierStatsResponse,
  TokenPlatformRevenueResponse,
  ApiError,
  TokenTierStatsEntry,
} from '@/lib/api/enhancements'

const DEVNET_PARAM_KEY = 'payment_method'
const DEVNET_PARAM_DISABLED_VALUE = 'false'
const DEVNET_MONTHLY_REVENUE = 25000
const DEVNET_STAKING_PERCENTAGE = 10
const DEVNET_BUYBACK_PERCENTAGE = 10
const DEVNET_STAKING_POOL_MONTHLY = DEVNET_MONTHLY_REVENUE * (DEVNET_STAKING_PERCENTAGE / 100)

const createDevnetPlatformRevenue = (): TokenPlatformRevenueResponse => {
  const monthlyBuyback = DEVNET_MONTHLY_REVENUE * (DEVNET_BUYBACK_PERCENTAGE / 100)
  const distributedMonthly = DEVNET_STAKING_POOL_MONTHLY + monthlyBuyback

  return {
    total_revenue: {
      monthly: DEVNET_MONTHLY_REVENUE,
      weekly: DEVNET_MONTHLY_REVENUE / 4,
      daily: DEVNET_MONTHLY_REVENUE / 30,
    },
    distributed_portion: {
      percentage: DEVNET_STAKING_PERCENTAGE + DEVNET_BUYBACK_PERCENTAGE,
      monthly: distributedMonthly,
      weekly: distributedMonthly / 4,
      breakdown: {
        staking_pool: {
          percentage: DEVNET_STAKING_PERCENTAGE,
          monthly: DEVNET_STAKING_POOL_MONTHLY,
          weekly: DEVNET_STAKING_POOL_MONTHLY / 4,
          daily: DEVNET_STAKING_POOL_MONTHLY / 30,
        },
        buyback: {
          percentage: DEVNET_BUYBACK_PERCENTAGE,
          monthly: monthlyBuyback,
          weekly: monthlyBuyback / 4,
          daily: monthlyBuyback / 30,
        },
      },
    },
  }
}

const createDevnetTierStats = (): TokenTierStatsResponse => ({
  tiers: {
    '30_DAYS': {
      total_staked: 120_000,
      staker_count: 48,
      tier_allocation: 20,
      average_lock_days: 30,
    },
    '60_DAYS': {
      total_staked: 240_000,
      staker_count: 32,
      tier_allocation: 30,
      average_lock_days: 60,
    },
    '90_DAYS': {
      total_staked: 400_000,
      staker_count: 20,
      tier_allocation: 50,
      average_lock_days: 90,
    },
  },
  updated_at: new Date().toISOString(),
})

const createDevnetProjectionContext = (): StakingPositionsResponse['projection_context'] => ({
  monthly_platform_revenue: DEVNET_MONTHLY_REVENUE,
  monthly_staking_pool: DEVNET_STAKING_POOL_MONTHLY,
  staking_pool_percentage: DEVNET_STAKING_PERCENTAGE,
  explanation:
    'Devnet test mode mirrors the 60/20/10 distribution by projecting staking rewards from a simulated revenue baseline.',
})

interface StakingInterfaceProps {
  userId: number
  walletAddress?: string
  currentBalance?: number
}

export default function StakingInterface({ userId, walletAddress, currentBalance = 0 }: StakingInterfaceProps) {
  const [positions, setPositions] = useState<StakingPosition[]>([])
  const [tierStats, setTierStats] = useState<TokenTierStatsResponse | null>(null)
  const [platformRevenue, setPlatformRevenue] = useState<TokenPlatformRevenueResponse | null>(null)
  const [projectionContext, setProjectionContext] = useState<StakingPositionsResponse['projection_context'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [staking, setStaking] = useState(false)
  const [claiming, setClaiming] = useState(false)
  const [apiUnavailable, setApiUnavailable] = useState(false)
  const [apiNotice, setApiNotice] = useState<string | null>(null)
  const [devnetFallback, setDevnetFallback] = useState<boolean>(() => {
    if (typeof window === 'undefined') {
      return Boolean(process.env.NEXT_PUBLIC_STAKING_DEVNET?.toLowerCase() === 'true')
    }

    const params = new URLSearchParams(window.location.search)
    const urlToggle = params.get(DEVNET_PARAM_KEY)
    const envToggle = process.env.NEXT_PUBLIC_STAKING_DEVNET?.toLowerCase() === 'true'

    return envToggle || urlToggle === DEVNET_PARAM_DISABLED_VALUE
  })
  
  useEffect(() => {
    if (!devnetFallback) {
      return
    }

    // Make it explicit that we are simulating the on-chain staking vault while the REST service is offline.
    setApiUnavailable(false)
    setApiNotice('Devnet staking mode active. Transactions are simulated locally because the staking service is disabled in this environment.')

    setTierStats((previous) => previous ?? createDevnetTierStats())
    setPlatformRevenue((previous) => previous ?? createDevnetPlatformRevenue())
    setProjectionContext((previous) => previous ?? createDevnetProjectionContext())
    setLoading(false)
  }, [devnetFallback])
  
  // Staking form
  const [stakeAmount, setStakeAmount] = useState('')
  const [selectedPeriod, setSelectedPeriod] = useState<30 | 60 | 90>(90)

  const fetchStakingData = useCallback(async () => {
    if (devnetFallback) {
      return
    }

    try {
      setLoading(true)
      setApiUnavailable(false)
      setApiNotice(null)

      // Fetch user's positions
      const [positionsData, stats, revenueStats] = await Promise.all([
        tokenAPI.getStakingPositions(userId),
        tokenAPI.getTierStats(),
        tokenAPI.getPlatformRevenue(),
      ])

      setPositions(positionsData.positions ?? [])
      setProjectionContext(positionsData.projection_context ?? null)
      setTierStats(stats)
      setPlatformRevenue(revenueStats)
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        console.warn('Staking API unavailable in this environment. Falling back to safe defaults.', err)
        setApiUnavailable(true)
        // Notify the UI so developers know to start the Phase 2 service locally.
        setApiNotice('Staking endpoints are not active on this backend. Displaying read-only defaults until the token service is enabled.')
        setPositions([])
        setProjectionContext(null)
        setTierStats(null)
        setPlatformRevenue(null)
      } else {
      console.error('Failed to fetch staking data:', err)
        setApiNotice('Unable to load staking metrics right now. Please try again in a few minutes.')
      }
    } finally {
      setLoading(false)
    }
  }, [userId, devnetFallback])

  useEffect(() => {
    fetchStakingData()
  }, [fetchStakingData])

  const simulateDevnetStake = useCallback(
    async (amount: number) => {
      // Simulate the staking vault mutation that would normally happen on the Solana program.
      await new Promise((resolve) => setTimeout(resolve, 1500))

      const tierKey = `${selectedPeriod}_DAYS` as keyof TokenTierStatsResponse['tiers']
      const tierInfo = getTierInfo(selectedPeriod)

      const baselineTierStats = tierStats ?? createDevnetTierStats()
      const currentTierTotal = baselineTierStats.tiers?.[tierKey]?.total_staked ?? 0
      const totalAfterStake = currentTierTotal + amount

      const revenueSnapshot = platformRevenue ?? createDevnetPlatformRevenue()
      const stakingPercentage = revenueSnapshot.distributed_portion?.breakdown?.staking_pool?.percentage ?? DEVNET_STAKING_PERCENTAGE
      const monthlyRevenue = revenueSnapshot.total_revenue?.monthly ?? DEVNET_MONTHLY_REVENUE
      const monthlyStakingPool = monthlyRevenue * (stakingPercentage / 100)
      const tierAllocation = tierInfo.allocation / 100
      const tierPool = monthlyStakingPool * tierAllocation
      const shareOfTier = totalAfterStake === 0 ? 0 : amount / totalAfterStake
      const projectedMonthly = tierPool * shareOfTier
      const projectedPeriod = projectedMonthly * (selectedPeriod / 30)
      const unlockDate = new Date(Date.now() + selectedPeriod * 86_400_000)

      setTierStats((previous) => {
        const next = previous
          ? { ...previous, tiers: { ...previous.tiers } }
          : createDevnetTierStats()

        const existingTier = next.tiers?.[tierKey]
        const updatedTier: TokenTierStatsEntry = existingTier
          ? { ...existingTier }
          : {
              total_staked: 0,
              staker_count: 0,
              tier_allocation: tierInfo.allocation,
              average_lock_days: selectedPeriod,
            }

        updatedTier.total_staked = Number((updatedTier.total_staked + amount).toFixed(2))
        updatedTier.staker_count += 1
        updatedTier.average_lock_days = selectedPeriod

        next.tiers = {
          ...next.tiers,
          [tierKey]: updatedTier,
        }
        next.updated_at = new Date().toISOString()
        return next
      })

      setPlatformRevenue((previous) => previous ?? createDevnetPlatformRevenue())
      setProjectionContext((previous) => previous ?? createDevnetProjectionContext())

      setPositions((previous) => [
        ...previous,
        {
          position_id: Date.now(),
          staked_amount: amount,
          lock_period_days: selectedPeriod,
          tier_allocation: tierInfo.allocation,
          unlocks_at: unlockDate.toISOString(),
          claimed_rewards: 0,
          claimable_rewards: projectedMonthly,
          projected_monthly_earnings: projectedMonthly,
          projected_remaining_earnings: projectedPeriod,
          share_of_tier: Number((shareOfTier * 100).toFixed(2)),
          days_remaining: selectedPeriod,
          status: 'active',
          is_unlocked: false,
        },
      ])

      alert(`✅ Successfully staked ${amount} tokens for ${selectedPeriod} days! (Devnet Mode)`)
      setStakeAmount('')
    },
    [platformRevenue, selectedPeriod, tierStats]
  )

  const handleDevnetClaim = useCallback(async () => {
    const claimable = positions
      .filter((position) => position.status === 'active')
      .reduce((sum, position) => sum + (position.claimable_rewards ?? 0), 0)

    if (claimable <= 0) {
      alert('No active positions to claim from')
      return
    }

    // Mirror the latency a wallet signer would experience on devnet.
    await new Promise((resolve) => setTimeout(resolve, 1000))

    setPositions((previous) =>
      previous.map((position) => {
        if (position.status !== 'active') {
          return position
        }

        const claimableRewards = position.claimable_rewards ?? 0
        if (claimableRewards <= 0) {
          return position
        }

        return {
          ...position,
          claimed_rewards: Number((position.claimed_rewards ?? 0) + claimableRewards),
          total_rewards_earned: Number((position.total_rewards_earned ?? 0) + claimableRewards),
          claimable_rewards: 0,
        }
      })
    )

    alert(`✅ Successfully claimed ${claimable.toFixed(2)} USDC in rewards! (Devnet Mode)`)
  }, [positions])

  const handleDevnetUnstake = useCallback(
    (positionId: number) => {
      const target = positions.find((position) => (position.position_id ?? position.id) === positionId)
      if (!target) {
        return
      }

      const tierKey = `${target.lock_period_days}_DAYS` as keyof TokenTierStatsResponse['tiers']
      const amount = target.staked_amount ?? target.amount_staked ?? 0

      setPositions((previous) =>
        previous.map((position) => {
          if ((position.position_id ?? position.id) !== positionId) {
            return position
          }

          return {
            ...position,
            status: 'unstaked',
            is_unlocked: true,
            claimable_rewards: 0,
            days_remaining: 0,
          }
        })
      )

      setTierStats((previous) => {
        if (!previous) {
          return previous
        }

        const existingTier = previous.tiers?.[tierKey]
        if (!existingTier) {
          return previous
        }

        const updatedTier: TokenTierStatsEntry = {
          ...existingTier,
          total_staked: Number(Math.max(existingTier.total_staked - amount, 0).toFixed(2)),
        }

        return {
          ...previous,
          tiers: {
            ...previous.tiers,
            [tierKey]: updatedTier,
          },
          updated_at: new Date().toISOString(),
        }
      })

      alert(`✅ Successfully unstaked ${amount} tokens! (Devnet Mode)`)
    },
    [positions]
  )

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

    if (devnetFallback) {
      setStaking(true)
      try {
        await simulateDevnetStake(amount)
      } finally {
        setStaking(false)
      }
      return
    }

    setStaking(true)
    try {
      const result = await tokenAPI.stake(userId, walletAddress, amount, selectedPeriod)
      
      // Check if this is a mock payment (test mode)
      if (result.is_mock) {
        console.log('🧪 MOCK STAKING MODE - Simulating transaction')
        alert('🧪 TEST MODE: Simulating staking (no real tokens will be transferred)')
        
        // Simulate a delay like a real transaction
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        console.log('Mock staking transaction complete')
        alert(`✅ Successfully staked ${amount} tokens for ${selectedPeriod} days! (Mock Mode)`)
      } else {
        // Real blockchain transaction (production)
        console.log('💰 REAL STAKING MODE - Processing actual blockchain transaction')
        // TODO: In production, execute on-chain transaction here
        // For now, the backend handles it
        alert(`✅ Successfully staked ${amount} tokens for ${selectedPeriod} days!`)
      }

      setStakeAmount('')
      await fetchStakingData()
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        console.warn('Staking API returned 404. Enabling devnet simulation mode.')
        setDevnetFallback(true)
        await simulateDevnetStake(amount)
      } else {
        console.error('Staking error:', err)
        const message = err instanceof Error ? err.message : 'Unknown error'
        alert(`❌ Staking failed: ${message}`)
      }
    } finally {
      setStaking(false)
    }
  }

  const handleClaimRewards = async () => {
    if (!walletAddress) {
      alert('Please connect your wallet first')
      return
    }

    const hasActivePositions = positions.some((p) => p.status === 'active')
    if (!hasActivePositions) {
      alert('No active positions to claim from')
      return
    }

    if (devnetFallback) {
      setClaiming(true)
      try {
        await handleDevnetClaim()
      } finally {
        setClaiming(false)
      }
      return
    }

    setClaiming(true)
    try {
      const result = await tokenAPI.claimRewards(userId, walletAddress)
      
      if (result.success) {
        alert(`✅ Successfully claimed ${result.amount_claimed} USDC in rewards!`)
        await fetchStakingData()
      } else {
        alert(`❌ Claim failed: ${result.error}`)
      }
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setDevnetFallback(true)
        await handleDevnetClaim()
      } else {
        const message = err instanceof Error ? err.message : 'Unknown error'
        alert(`❌ Claim failed: ${message}`)
      }
    } finally {
      setClaiming(false)
    }
  }

  const handleUnstake = async (positionId: number) => {
    if (!walletAddress) {
      alert('Please connect your wallet first')
      return
    }

    if (!confirm('Are you sure you want to unstake? This will return your tokens.')) {
      return
    }

    if (devnetFallback) {
      handleDevnetUnstake(positionId)
      return
    }

    try {
      const result = await tokenAPI.unstake(positionId, userId)
      
      if (result.success) {
        alert(`✅ Successfully unstaked ${result.amount_returned} tokens!`)
        await fetchStakingData()
      } else {
        alert(`❌ Unstake failed: ${result.error}`)
      }
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setDevnetFallback(true)
        handleDevnetUnstake(positionId)
      } else {
        const message = err instanceof Error ? err.message : 'Unknown error'
        alert(`❌ Unstake failed: ${message}`)
      }
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

  // Calculate estimated monthly earnings based on current platform revenue
  const calculateEstimatedMonthlyEarnings = (amount: number, periodDays: number): number => {
    if (!platformRevenue || !tierStats || amount <= 0) return 0
    
    const monthlyRevenue = platformRevenue.total_revenue?.monthly || 0
    const stakingPoolPercentage = platformRevenue.distributed_portion?.breakdown?.staking_pool?.percentage || 10
    const monthlyStakingPool = monthlyRevenue * (stakingPoolPercentage / 100)
    
    // Get tier allocation (20%, 30%, or 50%)
    const tierInfo = getTierInfo(periodDays)
    const tierAllocation = tierInfo.allocation / 100
    
    // Get total staked in this tier
    const tierKey = `${periodDays}_DAYS` as keyof typeof tierStats.tiers
    const tierTotalStaked = tierStats.tiers?.[tierKey]?.total_staked || amount
    
    // Calculate tier pool
    const tierPool = monthlyStakingPool * tierAllocation
    
    // Calculate user's share
    const userShare = amount / (tierTotalStaked + amount)
    
    return tierPool * userShare
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-8 border border-slate-200">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-200 rounded w-1/3"></div>
          <div className="h-32 bg-slate-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-slate-900 mb-2">Stake & Earn</h2>
        <p className="text-slate-600">
          Lock tokens to earn from {platformRevenue?.distributed_portion?.breakdown?.staking_pool?.percentage || 10}% of platform revenue
        </p>
      </div>

      {apiNotice && (
        <div
          className={`rounded-lg border p-4 ${
            apiUnavailable
              ? 'bg-yellow-50 border-yellow-200 text-yellow-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          <p className="text-sm font-medium">
            {apiUnavailable ? 'Staking service offline' : 'Staking data unavailable'}
          </p>
          <p className="text-xs mt-1">{apiNotice}</p>
        </div>
      )}

      {/* Revenue Model Explanation - UPDATED */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
        <h3 className="text-xl font-bold text-slate-900 mb-3">📊 Revenue-Based Staking Model</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-blue-600 font-semibold">{platformRevenue?.distributed_portion?.breakdown?.staking_pool?.percentage || 10}% of Revenue</p>
            <p className="text-slate-600">Goes to stakers monthly</p>
          </div>
          <div>
            <p className="text-blue-600 font-semibold">Tiered Distribution</p>
            <p className="text-slate-600">Longer locks = bigger share</p>
          </div>
          <div>
            <p className="text-blue-600 font-semibold">No Fixed APY</p>
            <p className="text-slate-600">Earnings based on actual revenue</p>
          </div>
        </div>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-xs text-yellow-800">
            ⚠️ <strong>Important:</strong> Rewards are based on actual platform revenue. Earnings will vary month-to-month based on platform performance. This is not a fixed APY product.
          </p>
        </div>
        
        {/* Revenue Allocation Breakdown */}
        {platformRevenue && (
          <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg shadow-md shadow-slate-900/5">
            <h4 className="text-sm font-semibold text-slate-900 mb-3">📊 Revenue Allocation Breakdown</h4>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Platform Revenue (Monthly):</span>
                <span className="font-semibold text-slate-900">${platformRevenue.total_revenue?.monthly?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-slate-200">
                <span className="text-slate-600">Staking Pool ({platformRevenue.distributed_portion?.breakdown?.staking_pool?.percentage || 10}%):</span>
                <span className="font-semibold text-emerald-600">${platformRevenue.distributed_portion?.breakdown?.staking_pool?.monthly?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-600">Buyback & Burn ({platformRevenue.distributed_portion?.breakdown?.buyback?.percentage || 10}%):</span>
                <span className="font-semibold text-orange-600">${platformRevenue.distributed_portion?.breakdown?.buyback?.monthly?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}</span>
              </div>
              <div className="flex justify-between items-center pt-2 border-t border-slate-200">
                <span className="text-slate-500 italic text-xs">Total Distributed ({platformRevenue.distributed_portion?.percentage || 20}%):</span>
                <span className="font-semibold text-slate-700">${platformRevenue.distributed_portion?.monthly?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Staking Form */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Create Staking Position</h3>
        
        {/* Lock Period Selection */}
        <div className="mb-6">
          <label className="block text-slate-900 font-medium mb-3">Lock Period</label>
          <div className="grid grid-cols-3 gap-3">
            {[30, 60, 90].map((days) => {
              const info = getTierInfo(days)
              const isSelected = selectedPeriod === days
              return (
                <button
                  key={days}
                  onClick={() => setSelectedPeriod(days as 30 | 60 | 90)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    isSelected
                      ? `bg-blue-50 border-blue-500`
                      : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <p className={`font-bold text-lg ${isSelected ? 'text-blue-600' : 'text-slate-900'}`}>{days} Days</p>
                  <p className={`text-sm ${isSelected ? 'text-blue-600' : 'text-slate-600'}`}>
                    {info.allocation}% of pool
                  </p>
                  <p className="text-xs text-slate-500 mt-1">{info.label}</p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Amount Input */}
        <div className="mb-6">
          <label className="block text-slate-900 font-medium mb-2">Amount to Stake</label>
          <div className="relative">
            <input
              type="number"
              value={stakeAmount}
              onChange={(e) => setStakeAmount(e.target.value)}
              placeholder="Enter amount"
              className="w-full bg-white text-slate-900 rounded-lg px-4 py-3 border border-slate-300 focus:border-blue-500 focus:outline-none"
            />
            <span className="absolute right-4 top-3 text-slate-500">$100Bs</span>
          </div>
          {currentBalance > 0 && (
            <p className="text-sm text-slate-600 mt-2">
              Available: {currentBalance.toLocaleString()} tokens
            </p>
          )}
        </div>

        {/* Estimated Rewards Preview */}
        {parseFloat(stakeAmount) > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-700 font-semibold mb-2">📈 Estimated Monthly Rewards</p>
            {platformRevenue && tierStats ? (
              <>
                <p className="text-sm text-slate-700 mb-2">
                  Based on current platform revenue (${platformRevenue.total_revenue?.monthly?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}/month):
                </p>
                <p className="text-2xl font-bold text-slate-900 mt-2">
                  ~${calculateEstimatedMonthlyEarnings(parseFloat(stakeAmount), selectedPeriod).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}/month
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  * Estimates assume current tier size and revenue. Actual rewards vary based on platform performance and tier participation.
                </p>
              </>
            ) : (
              <>
                <p className="text-sm text-slate-700">
                  Calculating based on platform revenue...
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  * Loading revenue data
                </p>
              </>
            )}
          </div>
        )}

        {/* Stake Button */}
        <button
          onClick={handleStake}
          disabled={staking || !walletAddress || !stakeAmount}
          className="w-full bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 disabled:opacity-50 text-white py-4 rounded-lg font-bold text-lg transition-all"
        >
          {staking ? '🔄 Staking...' : walletAddress ? `Stake for ${selectedPeriod} Days` : '👛 Connect Wallet First'}
        </button>
      </div>

      {/* Claim Rewards Section */}
      {positions.length > 0 && positions.some((p) => p.status === 'active') && (
        <div className="bg-white border border-emerald-200 rounded-xl p-6 shadow-2xl shadow-emerald-900/10">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">💰 Claimable Rewards</h3>
              <p className="text-slate-600 text-sm">
                Claim accumulated rewards from all your active staking positions
              </p>
              <p className="text-2xl font-bold text-emerald-600 mt-2">
                ~${positions
                  .filter((p) => p.status === 'active')
                  .reduce((sum, p) => sum + (p.claimable_rewards || 0), 0)
                  .toFixed(2)} USDC
              </p>
            </div>
            <button
              onClick={handleClaimRewards}
              disabled={claiming || !walletAddress}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 text-white px-8 py-4 rounded-lg font-bold text-lg transition-all"
            >
              {claiming ? '🔄 Claiming...' : '🎁 Claim Rewards'}
            </button>
          </div>
        </div>
      )}

      {/* Active Positions */}
      {positions.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
          <h3 className="text-xl font-bold text-slate-900 mb-4">Your Staking Positions</h3>
          {projectionContext && (
            <p className="text-xs text-slate-500 mb-4">
              Projections assume ${projectionContext.monthly_platform_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} in monthly platform revenue with {projectionContext.staking_pool_percentage.toFixed(1)}% routed to staking, funding a {projectionContext.monthly_staking_pool.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} rewards pool. Actual payouts fluctuate with platform revenue and tier participation.
            </p>
          )}
          <div className="space-y-4">
            {positions.map((position, index) => {
              const isUnlocked = position.is_unlocked || false
              const canUnstake = isUnlocked && position.status === 'active'
              const key = position.position_id ?? position.id ?? index
              const positionId = position.position_id ?? position.id
              
              const unlockDate = position.unlocks_at ?? position.unlock_date
              const formattedUnlockDate = unlockDate
                ? new Date(unlockDate).toLocaleDateString()
                : 'Pending'
              const projectedMonthly = Number(position.projected_monthly_earnings ?? position.claimable_rewards ?? 0)

              return (
                <div key={key} className="bg-slate-50 rounded-lg p-4 border border-slate-200 shadow-md shadow-slate-900/5 hover:shadow-lg hover:shadow-slate-900/10 transition-all duration-200">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-slate-900 font-bold text-lg">
                        {position.staked_amount?.toLocaleString() || position.amount_staked?.toLocaleString()} $100Bs
                      </p>
                      <p className="text-sm text-slate-600">
                        {position.lock_period_days}-day lock • {position.tier_allocation}% tier
                      </p>
                      <span className={`text-xs px-2 py-1 rounded ${
                        position.status === 'active' ? 'bg-emerald-100 text-emerald-600' : 'bg-slate-200 text-slate-600'
                      }`}>
                        {position.status || 'active'}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-wide text-slate-500">Projected</p>
                      <p className="text-emerald-600 font-bold">
                        ~${projectedMonthly.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}/mo
                      </p>
                      {position.share_of_tier && (
                        <p className="text-xs text-slate-500">
                          {position.share_of_tier.toFixed(2)}% of tier
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm mb-3">
                    <div>
                      <span className="text-slate-600">Claimed: </span>
                      <span className="text-slate-900">${(position.claimed_rewards || position.total_rewards_earned || 0).toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-slate-600">Unlocks: </span>
                      <span className="text-slate-900">{formattedUnlockDate}</span>
                    </div>
                    <div>
                      <span className={`${isUnlocked ? 'text-emerald-600' : 'text-slate-600'}`}>
                        {isUnlocked ? '🔓 Unlocked' : `🔒 ${position.days_remaining || 0} days left`}
                      </span>
                    </div>
                  </div>

                  {canUnstake && positionId != null && (
                    <button
                      onClick={() => handleUnstake(positionId)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-medium text-sm transition-all"
                    >
                      Unstake Tokens
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Tier Statistics */}
      {tierStats && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
          <h3 className="text-xl font-bold text-slate-900 mb-4">Platform Staking Tiers</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(tierStats.tiers ?? {}).map(([tierName, tierData]) => {
              const stats = tierData as TokenTierStatsEntry
              return (
              <div key={tierName} className="bg-slate-50 rounded-lg p-4 border border-slate-200 shadow-md shadow-slate-900/5">
                <p className="text-slate-600 text-sm mb-1">{tierName.replace('_', ' ')}</p>
                <p className="text-slate-900 font-bold text-xl">
                    {stats.total_staked.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
                <p className="text-sm text-slate-600">
                    {stats.staker_count} stakers • {stats.tier_allocation}% allocation
                </p>
              </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

