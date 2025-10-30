import { backendFetch } from './client'

export interface Bounty {
  id: number
  name: string
  llm_provider: string
  current_pool: number
  total_entries: number
  win_rate: number
  difficulty_level: string
  is_active: boolean
  description?: string
  starting_pool?: number
  created_at?: string
  updated_at?: string
}

interface BountiesResponse {
  success: boolean
  bounties: Bounty[]
  error?: string
}

interface BountyDetailsResponse {
  success: boolean
  bounty: Bounty
  error?: string
}

/**
 * Fetch all public bounties from the backend API.
 * Throws an error when the backend reports a failure so the caller can surface a UI state.
 */
export async function fetchBounties(): Promise<Bounty[]> {
  console.log('🎯 [Bounties] Starting fetchBounties...')
  
  try {
    const data = await backendFetch<BountiesResponse>('/api/bounties')
    
    console.log('🎯 [Bounties] Response data:', {
      success: data.success,
      bountiesCount: data.bounties?.length || 0,
      bounties: data.bounties,
      hasError: !!data.error
    })

    if (!data.success) {
      console.error('🎯 [Bounties] Backend reported failure:', data.error)
      throw new Error(data.error || 'Failed to load bounties')
    }

    if (!data.bounties || data.bounties.length === 0) {
      console.warn('🎯 [Bounties] No bounties returned from backend')
    } else {
      console.log('🎯 [Bounties] Successfully loaded', data.bounties.length, 'bounties')
    }

    return data.bounties
  } catch (error) {
    console.error('🎯 [Bounties] fetchBounties failed:', error)
    throw error
  }
}

/**
 * Retrieve a single bounty by id.
 * The backend returns a success flag that we enforce here for consistent error handling.
 */
export async function fetchBountyById(bountyId: string | number): Promise<Bounty> {
  const data = await backendFetch<BountyDetailsResponse>(`/api/bounty/${bountyId}`)

  if (!data.success) {
    throw new Error(data.error || 'Bounty not found')
  }

  return data.bounty
}

