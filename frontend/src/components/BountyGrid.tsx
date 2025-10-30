'use client'

import { useState, useEffect, useCallback } from 'react'
import BountyCard from './BountyCard'
import { Loader2, AlertCircle, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import { fetchBounties, Bounty } from '@/lib/api/bounties'

interface BountyGridProps {
  className?: string
  limit?: number
  initialBounties?: Bounty[]
}

export default function BountyGrid({ className, limit, initialBounties = [] }: BountyGridProps) {
  const [bounties, setBounties] = useState<Bounty[]>(initialBounties)
  const [loading, setLoading] = useState(!initialBounties.length)
  const [error, setError] = useState<string | null>(null)

  const loadBounties = useCallback(async () => {
    console.log('🎨 [BountyGrid] loadBounties called, limit:', limit)
    try {
      setLoading(true)
      setError(null)
      console.log('🎨 [BountyGrid] Calling fetchBounties...')
      const bountyList = await fetchBounties()
      console.log('🎨 [BountyGrid] Received bounties:', bountyList.length)
      const displayList = limit ? bountyList.slice(0, limit) : bountyList
      console.log('🎨 [BountyGrid] Setting bounties to display:', displayList.length)
      setBounties(displayList)
    } catch (err) {
      console.error('🎨 [BountyGrid] Error fetching bounties:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect to server'
      console.error('🎨 [BountyGrid] Error message:', errorMessage)
      setError(errorMessage)
    } finally {
      console.log('🎨 [BountyGrid] Setting loading to false')
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    console.log('🎨 [BountyGrid] Mount/update effect triggered', {
      isClient: typeof window !== 'undefined',
      initialBountiesLength: initialBounties.length,
      hasInitialBounties: initialBounties.length > 0
    })
    
    // Only fetch if we don't have initial bounties
    if (typeof window !== 'undefined' && !initialBounties.length) {
      console.log('🎨 [BountyGrid] No initial bounties, calling loadBounties')
      loadBounties()
    } else {
      console.log('🎨 [BountyGrid] Skipping loadBounties (server-side or has initial bounties)')
    }
  }, [initialBounties.length, loadBounties])
  
  // Update bounties when initialBounties prop changes
  useEffect(() => {
    console.log('🎨 [BountyGrid] initialBounties prop changed:', {
      length: initialBounties.length,
      bounties: initialBounties
    })
    
    if (initialBounties.length > 0) {
      console.log('🎨 [BountyGrid] Using initial bounties from props')
      setBounties(limit ? initialBounties.slice(0, limit) : initialBounties)
      setLoading(false)
    }
  }, [initialBounties, limit])

  console.log('🎨 [BountyGrid] Render state:', { loading, error, bountiesCount: bounties.length })

  if (loading) {
    console.log('🎨 [BountyGrid] Rendering loading state')
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
    console.log('🎨 [BountyGrid] Rendering error state:', error)
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <p className="text-slate-600 mb-4">{error}</p>
        <button
          onClick={loadBounties}
          className="flex items-center space-x-2 px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg transition-colors border border-slate-300"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Retry</span>
        </button>
      </div>
    )
  }

  if (bounties.length === 0) {
    console.log('🎨 [BountyGrid] Rendering empty state')
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

  console.log('🎨 [BountyGrid] Rendering bounty cards:', bounties.length)

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
