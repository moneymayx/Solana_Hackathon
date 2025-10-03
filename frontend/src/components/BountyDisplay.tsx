'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Coins, Users, Clock, TrendingUp, Award, AlertCircle } from 'lucide-react'
import { formatCurrency, formatPercentage, formatTimeAgo } from '@/lib/utils'

interface bountyStatus {
  current_pool: number
  total_entries: number
  next_rollover_at?: string
  win_rate: number
  recent_winners?: Array<{
    user_id: number
    prize_amount: number
    won_at: string
  }>
  escape_plan?: {
    is_active: boolean
    time_since_last_question?: string
    time_until_escape?: string
    message: string
    should_trigger?: boolean
  }
}

interface UserHistory {
  total_entries: number
  total_spent: number
  wins: number
  last_entry?: string
}

export default function BountyDisplay() {
  const { connected } = useWallet()
  const [bountyStatus, setBountyStatus] = useState<bountyStatus | null>(null)
  const [userHistory, setUserHistory] = useState<UserHistory | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchBountyData()
    const interval = setInterval(fetchBountyData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchBountyData = async () => {
    try {
      const [statusResponse, historyResponse] = await Promise.all([
        fetch('/api/bounty/status'),
        connected ? fetch('/api/bounty/history') : Promise.resolve(null)
      ])

      if (statusResponse.ok) {
        const statusData = await statusResponse.json()
        setBountyStatus(statusData)
      }

      if (historyResponse?.ok) {
        const historyData = await historyResponse.json()
        setUserHistory(historyData)
      }
    } catch (error) {
      console.error('Failed to fetch bounty data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400">Loading bounty data...</p>
      </div>
    )
  }

  if (!bountyStatus) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-400">Failed to load bounty data</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <Coins className="h-8 w-8 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white">Current Pool</h3>
          </div>
          <p className="text-3xl font-bold text-yellow-400">
            {formatCurrency(bountyStatus.current_pool)}
          </p>
          <p className="text-sm text-yellow-200 mt-1">Prize Pool</p>
        </div>

        <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <Users className="h-8 w-8 text-blue-400" />
            <h3 className="text-lg font-semibold text-white">Total Entries</h3>
          </div>
          <p className="text-3xl font-bold text-blue-400">
            {bountyStatus.total_entries.toLocaleString()}
          </p>
          <p className="text-sm text-blue-200 mt-1">All Time</p>
        </div>

        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-2">
            <TrendingUp className="h-8 w-8 text-green-400" />
            <h3 className="text-lg font-semibold text-white">Win Rate</h3>
          </div>
          <p className="text-3xl font-bold text-green-400">
            {formatPercentage(bountyStatus.win_rate)}
          </p>
          <p className="text-sm text-green-200 mt-1">Success Rate</p>
        </div>
      </div>

      {/* Escape Plan Status */}
      {bountyStatus.escape_plan && bountyStatus.escape_plan.is_active && (
        <div className={`backdrop-blur-sm rounded-lg p-6 ${
          bountyStatus.escape_plan.should_trigger 
            ? 'bg-red-500/20 border border-red-500/30' 
            : 'bg-orange-500/20 border border-orange-500/30'
        }`}>
          <div className="flex items-center space-x-3 mb-4">
            <AlertCircle className={`h-6 w-6 ${
              bountyStatus.escape_plan.should_trigger ? 'text-red-400' : 'text-orange-400'
            }`} />
            <h3 className={`text-lg font-semibold ${
              bountyStatus.escape_plan.should_trigger ? 'text-red-400' : 'text-orange-400'
            }`}>
              {bountyStatus.escape_plan.should_trigger ? '🚨 ESCAPE PLAN READY!' : 'Escape Plan Timer'}
            </h3>
          </div>
          <p className="text-white font-medium mb-2">
            {bountyStatus.escape_plan.message}
          </p>
          {bountyStatus.escape_plan.time_since_last_question && (
            <p className="text-sm text-gray-300">
              Time since last question: {bountyStatus.escape_plan.time_since_last_question}
            </p>
          )}
          {bountyStatus.escape_plan.time_until_escape && !bountyStatus.escape_plan.should_trigger && (
            <p className="text-sm text-gray-300">
              Time until escape: {bountyStatus.escape_plan.time_until_escape}
            </p>
          )}
          <div className="mt-3 p-3 bg-gray-800/50 rounded-lg">
            <p className="text-sm text-gray-300">
              <strong>Escape Plan:</strong> If no questions are asked for 24 hours, 
              80% of the bounty will be distributed equally among all participants, 
              and 20% will go to the last person who asked a question.
            </p>
          </div>
        </div>
      )}

      {/* Next Rollover */}
      {bountyStatus.next_rollover_at && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Clock className="h-6 w-6 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">Next Rollover</h3>
          </div>
          <p className="text-gray-300">
            {formatTimeAgo(new Date(bountyStatus.next_rollover_at))}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            If no winner is found, the pool will roll over to the next round
          </p>
        </div>
      )}

      {/* User History */}
      {connected && userHistory && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Award className="h-6 w-6 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">Your Stats</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{userHistory.total_entries}</p>
              <p className="text-sm text-gray-400">Entries</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{formatCurrency(userHistory.total_spent)}</p>
              <p className="text-sm text-gray-400">Spent</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-400">{userHistory.wins}</p>
              <p className="text-sm text-gray-400">Wins</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-400">
                {userHistory.wins > 0 ? formatPercentage(userHistory.wins / userHistory.total_entries) : '0%'}
              </p>
              <p className="text-sm text-gray-400">Win Rate</p>
            </div>
          </div>
        </div>
      )}

      {/* Recent Winners */}
      {bountyStatus.recent_winners && bountyStatus.recent_winners.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Award className="h-6 w-6 text-yellow-400" />
            <h3 className="text-lg font-semibold text-white">Recent Winners</h3>
          </div>
          <div className="space-y-3">
            {bountyStatus.recent_winners.slice(0, 5).map((winner: any, index: number) => (
              <div key={index} className="flex items-center justify-between bg-gray-700/50 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-black font-bold text-sm">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-white font-medium">User #{winner.user_id}</p>
                    <p className="text-sm text-gray-400">{formatTimeAgo(new Date(winner.won_at))}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-yellow-400 font-bold">{formatCurrency(winner.prize_amount)}</p>
                  <p className="text-sm text-gray-400">Prize</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* How to Play */}
      <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">How to Play</h3>
        <div className="space-y-2 text-gray-300">
          <p>• Connect your Solana wallet to start playing</p>
          <p>• Chat with the AI guardian and try to convince them to transfer funds</p>
          <p>• Each message costs $10 (with $8 going to the prize pool)</p>
          <p>• Win rate is currently {formatPercentage(bountyStatus.win_rate)}</p>
          <p>• If you win, the AI will transfer the prize to your wallet!</p>
        </div>
      </div>
    </div>
  )
}
