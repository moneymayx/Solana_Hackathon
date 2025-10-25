'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Coins, Users, Clock, TrendingUp, Award, AlertCircle, Target } from 'lucide-react'
import { formatCurrency, formatPercentage, formatTimeAgo } from '@/lib/utils'
import { StatCard, Card } from './ui/Card'

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
      const statusResponse = await fetch('http://localhost:8000/api/lottery/status')

      if (statusResponse.ok) {
        const statusData = await statusResponse.json()
        setBountyStatus(statusData)
      }
    } catch (error) {
      console.error('Failed to fetch bounty data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-slate-400">Loading bounty data...</p>
      </Card>
    )
  }

  if (!bountyStatus) {
    return (
      <Card className="p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-slate-400">Failed to load bounty data</p>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={<Coins className="h-10 w-10 text-emerald-400" />}
          label="Current Prize Pool"
          value={formatCurrency(bountyStatus.current_pool)}
          trend={{ value: '+$450 today', positive: true }}
        />
        
        <StatCard
          icon={<Users className="h-10 w-10 text-blue-400" />}
          label="Total Entries"
          value={bountyStatus.total_entries.toLocaleString()}
          trend={{ value: '+89 today', positive: true }}
        />
        
        <StatCard
          icon={<Target className="h-10 w-10 text-violet-400" />}
          label="Win Rate"
          value={formatPercentage(bountyStatus.win_rate)}
          trend={{ value: `${bountyStatus.recent_winners?.length || 0} winners`, positive: true }}
        />
      </div>

      {/* Escape Plan Status */}
      {bountyStatus.escape_plan && bountyStatus.escape_plan.is_active && (
        <Card className={`${
          bountyStatus.escape_plan.should_trigger 
            ? 'bg-red-500/10 border-red-500' 
            : 'bg-amber-500/10 border-amber-500'
        }`}>
          <div className="flex items-center space-x-3 mb-4">
            <AlertCircle className={`h-6 w-6 ${
              bountyStatus.escape_plan.should_trigger ? 'text-red-400' : 'text-amber-400'
            }`} />
            <h3 className={`text-lg font-semibold ${
              bountyStatus.escape_plan.should_trigger ? 'text-red-400' : 'text-amber-400'
            }`}>
              {bountyStatus.escape_plan.should_trigger ? '🚨 ESCAPE PLAN READY!' : 'Escape Plan Timer'}
            </h3>
          </div>
          <p className="text-slate-100 font-medium mb-2">
            {bountyStatus.escape_plan.message}
          </p>
          {bountyStatus.escape_plan.time_since_last_question && (
            <p className="text-sm text-slate-300">
              Time since last question: {bountyStatus.escape_plan.time_since_last_question}
            </p>
          )}
          {bountyStatus.escape_plan.time_until_escape && !bountyStatus.escape_plan.should_trigger && (
            <p className="text-sm text-slate-300">
              Time until escape: {bountyStatus.escape_plan.time_until_escape}
            </p>
          )}
          <div className="mt-3 p-3 bg-slate-800/70 rounded-lg">
            <p className="text-sm text-slate-300">
              <strong className="text-slate-100">Escape Plan:</strong> If no questions are asked for 24 hours, 
              80% of the bounty will be distributed equally among all participants, 
              and 20% will go to the last person who asked a question.
            </p>
          </div>
        </Card>
      )}

      {/* Next Rollover */}
      {bountyStatus.next_rollover_at && (
        <Card>
          <div className="flex items-center space-x-3 mb-4">
            <Clock className="h-6 w-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-slate-50">Next Rollover</h3>
          </div>
          <p className="text-slate-100">
            {formatTimeAgo(new Date(bountyStatus.next_rollover_at))}
          </p>
          <p className="text-sm text-slate-400 mt-1">
            If no winner is found, the pool will roll over to the next round
          </p>
        </Card>
      )}

      {/* User History */}
      {connected && userHistory && (
        <Card>
          <div className="flex items-center space-x-3 mb-6">
            <Award className="h-6 w-6 text-violet-400" />
            <h3 className="text-lg font-semibold text-slate-50">Your Stats</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-slate-50 mb-1">{userHistory.total_entries}</p>
              <p className="text-sm text-slate-400">Entries</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-slate-50 mb-1">{formatCurrency(userHistory.total_spent)}</p>
              <p className="text-sm text-slate-400">Spent</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-emerald-400 mb-1">{userHistory.wins}</p>
              <p className="text-sm text-slate-400">Wins</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-violet-400 mb-1">
                {userHistory.wins > 0 ? formatPercentage(userHistory.wins / userHistory.total_entries) : '0%'}
              </p>
              <p className="text-sm text-slate-400">Win Rate</p>
            </div>
          </div>
        </Card>
      )}

      {/* Recent Winners */}
      {bountyStatus.recent_winners && bountyStatus.recent_winners.length > 0 && (
        <Card>
          <div className="flex items-center space-x-3 mb-6">
            <Award className="h-6 w-6 text-yellow-400" />
            <h3 className="text-lg font-semibold text-slate-50">Recent Winners</h3>
          </div>
          <div className="space-y-3">
            {bountyStatus.recent_winners.slice(0, 5).map((winner: any, index: number) => (
              <div key={index} className="flex items-center justify-between bg-slate-700/30 rounded-lg p-4 hover:bg-slate-700/50 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center font-bold text-slate-900">
                    #{index + 1}
                  </div>
                  <div>
                    <p className="text-slate-50 font-medium">User #{winner.user_id}</p>
                    <p className="text-sm text-slate-400">{formatTimeAgo(new Date(winner.won_at))}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-yellow-400 font-bold text-lg">{formatCurrency(winner.prize_amount)}</p>
                  <p className="text-xs text-slate-400">Prize</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* How to Play */}
      <Card className="bg-blue-600/5 border-blue-500/30">
        <h3 className="text-lg font-semibold text-slate-50 mb-4">How to Play</h3>
        <div className="space-y-3 text-slate-300">
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">1</span>
            <p>Connect your Solana wallet to start playing</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">2</span>
            <p>Chat with the AI guardian and try to convince them to transfer funds</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">3</span>
            <p>Each message costs $10 (with $8 going to the prize pool)</p>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">4</span>
            <p>Win rate is currently {formatPercentage(bountyStatus.win_rate)} - Good luck!</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
