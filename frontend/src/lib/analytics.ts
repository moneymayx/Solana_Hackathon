import type { Bounty } from '@/lib/api/bounties'

export const sumBountyPools = (bountyList: Bounty[] | null): number => {
  // Aggregating each bounty prize pool keeps the analytics jackpot aligned with the on-chain payout treasury exposure.
  if (!bountyList?.length) {
    return 0
  }

  return bountyList.reduce((accumulator: number, bounty: Bounty) => accumulator + (bounty.current_pool || 0), 0)
}

