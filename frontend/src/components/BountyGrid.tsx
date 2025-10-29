'use client'

import { useState, useEffect } from 'react'
import BountyCard from './BountyCard'
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Bounty {
  id: number
  name: string
  llm_provider: string
  current_pool: number
  total_entries: number
  win_rate: number
  difficulty_level: string
  is_active: boolean
}

interface BountyGridProps {
  className?: string
  limit?: number
}

export default function BountyGrid({ className, limit }: BountyGridProps) {
  const [bounties, setBounties] = useState<Bounty[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBounties = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('http://localhost:8000/api/bounties')
      const data = await response.json()
      
      if (data.success) {
        const bountyList = limit ? data.bounties.slice(0, limit) : data.bounties
        setBounties(bountyList)
      } else {
        setError('Failed to load bounties')
      }
    } catch (err) {
      console.error('Error fetching bounties:', err)
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Only fetch on client-side
    if (typeof window !== 'undefined') {
      fetchBounties()
    }
  }, [limit])

  if (loading) {
    return (
      <div className={cn("flex items-center justify-center py-12", className)}>
        <div className="flex items-center space-x-3">
          <Loader2 className="h-6 w-6 animate-spin text-yellow-500" />
          <span className="text-slate-600">Loading bounties...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <p className="text-slate-600 mb-4">{error}</p>
        <button
          onClick={fetchBounties}
          className="flex items-center space-x-2 px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg transition-colors border border-slate-300"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Retry</span>
        </button>
      </div>
    )
  }

  if (bounties.length === 0) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <div className="mb-4">
          <img 
            src="/images/logos/claude-ai.svg" 
            alt="Bounty Target" 
            className="w-16 h-16 mx-auto"
          />
        </div>
        <h3 className="text-slate-900 text-lg font-semibold mb-2">No Bounties Available</h3>
        <p className="text-slate-600 text-center max-w-md">
          New bounties are being prepared. Check back soon for exciting challenges!
        </p>
      </div>
    )
  }

  return (
    <div className={cn(
      "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6",
      className
    )}>
      {bounties.map((bounty) => (
        <BountyCard
          key={bounty.id}
          bounty={bounty}
          className="animate-fade-in"
        />
      ))}
    </div>
  )
}
