import type { Bounty } from '@/lib/api/bounties'

export const sumBountyPools = (bountyList: Bounty[] | null): number => {
  // Aggregating each bounty prize pool keeps the analytics jackpot aligned with the on-chain payout treasury exposure.
  if (!bountyList?.length) {
    return 0
  }

  return bountyList.reduce((accumulator: number, bounty: Bounty) => {
    const normalizedPool = Number(bounty.current_pool ?? bounty.starting_pool ?? 0)
    // Normalizing the pool value guards against string responses and missing fields so the UI sum mirrors live bounty funding accurately.
    return accumulator + (Number.isFinite(normalizedPool) ? normalizedPool : 0)
  }, 0)
}

