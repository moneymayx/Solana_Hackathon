'use client'

import { useState, useEffect } from 'react'
import { Crown, Trophy, Star, TrendingUp, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getBackendUrl } from '@/lib/api/client'

interface Winner {
  id: number
  user_id: number
  bounty_id: number
  content: string
  timestamp: string
  cost: number
  model_used: string
}

interface WinnerShowcaseProps {
  className?: string
  limit?: number
}

export default function WinnerShowcase({ className, limit = 5 }: WinnerShowcaseProps) {
  const [winners, setWinners] = useState<Winner[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchWinners = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch(`${getBackendUrl()}/api/winners/recent?limit=${limit}`)
        const data = await response.json()
        
        if (data.success) {
          setWinners(data.winners)
        } else {
          setError('Failed to load winners')
        }
      } catch (err) {
        console.error('Error fetching winners:', err)
        setError('Failed to connect to server')
      } finally {
        setLoading(false)
      }
    }

    fetchWinners()
  }, [limit])

  if (loading) {
    return (
      <div className={cn("bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10", className)}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-pulse text-slate-600">Loading winners...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn("bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10", className)}>
        <div className="text-center py-8">
          <div className="text-4xl mb-2">⚠️</div>
          <p className="text-slate-600">{error}</p>
        </div>
      </div>
    )
  }

  if (winners.length === 0) {
    return (
      <div className={cn("bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10", className)}>
        <div className="flex items-center space-x-2 mb-6">
          <Crown className="h-6 w-6 text-yellow-500" />
          <h3 className="text-slate-900 text-xl font-semibold">Recent Winners</h3>
        </div>
        
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <h4 className="text-slate-900 text-lg font-semibold mb-2">No Winners Yet</h4>
          <p className="text-slate-600 mb-4">Be the first to crack the AI guardian!</p>
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg shadow-lg shadow-yellow-500/30">
            <Star className="h-4 w-4" />
            <span className="text-sm font-medium">First Winner Gets Bonus!</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn("bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10", className)}>
      <div className="flex items-center space-x-2 mb-6">
          <Crown className="h-6 w-6 text-yellow-500" />
        <h3 className="text-slate-900 text-xl font-semibold">Recent Winners</h3>
        <div className="ml-auto flex items-center space-x-1 text-slate-600 text-sm">
          <TrendingUp className="h-4 w-4" />
          <span>{winners.length} winners</span>
        </div>
      </div>

      <div className="space-y-4">
        {winners.map((winner, index) => (
          <div
            key={winner.id}
            className={cn(
              "group relative p-4 rounded-lg border transition-all duration-200 hover:scale-105",
              index === 0
                ? "bg-gradient-to-r from-yellow-100 to-orange-100 border-yellow-300 shadow-lg shadow-yellow-500/20"
                : "bg-slate-50 border-slate-200 hover:border-slate-300 hover:shadow-md"
            )}
          >
            {/* Winner Rank */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm shadow-lg",
                  index === 0
                    ? "bg-gradient-to-r from-yellow-400 to-orange-500 text-white"
                    : "bg-slate-200 text-slate-700"
                )}>
                  {index === 0 ? <Trophy className="h-5 w-5" /> : `#${index + 1}`}
                </div>
                <div>
                  <p className="text-slate-900 font-medium">
                    {index === 0 ? 'Champion' : `Winner #${index + 1}`}
                  </p>
                  <p className="text-slate-600 text-sm">
                    User #{winner.user_id} • {new Date(winner.timestamp).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className={cn(
                  "text-2xl font-bold",
                  index === 0 ? "text-yellow-600" : "text-slate-700"
                )}>
                  ${winner.cost?.toFixed(2) || '0.00'}
                </p>
                <p className="text-slate-600 text-xs">Prize</p>
              </div>
            </div>

            {/* Winning Message Preview */}
            <div className="bg-slate-100 rounded-lg p-3 mb-3">
              <p className="text-slate-700 text-sm italic">
                "{winner.content.length > 100 
                  ? `${winner.content.substring(0, 100)}...` 
                  : winner.content}"
              </p>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between text-xs text-slate-600">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <Users className="h-3 w-3" />
                  <span>Bounty #{winner.bounty_id}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Star className="h-3 w-3" />
                  <span>{winner.model_used || 'AI'}</span>
                </div>
              </div>
              
              {index === 0 && (
                <div className="flex items-center space-x-1 text-yellow-600">
                  <Crown className="h-3 w-3" />
                  <span className="font-medium">Top Winner</span>
                </div>
              )}
            </div>

            {/* Hover Effect */}
            <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-yellow-400/5 to-orange-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" />
          </div>
        ))}
      </div>

      {/* View All Winners Link */}
      <div className="mt-6 text-center">
        <button className="text-yellow-600 hover:text-orange-600 text-sm font-medium transition-colors">
          View All Winners →
        </button>
      </div>
    </div>
  )
}
