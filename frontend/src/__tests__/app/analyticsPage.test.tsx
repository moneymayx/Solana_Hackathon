import { sumBountyPools } from '@/lib/analytics'
import type { Bounty } from '@/lib/api/bounties'

describe('sumBountyPools', () => {
  it('returns 0 when no bounty data is available', () => {
    expect(sumBountyPools(null)).toBe(0)
    expect(sumBountyPools([])).toBe(0)
  })

  it('aggregates the current pool for each bounty', () => {
    const mockBounties: Bounty[] = [
      { id: 1, name: 'Alpha', llm_provider: 'claude', current_pool: 1250, total_entries: 10, win_rate: 0.25, difficulty_level: 'easy', is_active: true },
      { id: 2, name: 'Bravo', llm_provider: 'gpt-4', current_pool: 500, total_entries: 5, win_rate: 0.4, difficulty_level: 'medium', is_active: true },
      { id: 3, name: 'Charlie', llm_provider: 'gemini', current_pool: 0, total_entries: 1, win_rate: 0.1, difficulty_level: 'hard', is_active: false }
    ]

    // Verifies the analytics jackpot display stays in lockstep with the homepage bounty totals.
    expect(sumBountyPools(mockBounties)).toBe(1750)
  })
})

