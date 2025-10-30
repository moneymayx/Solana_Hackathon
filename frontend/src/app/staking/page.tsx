'use client'

/**
 * Staking Page
 * 
 * Stake $100Bs tokens and earn from platform revenue
 */

import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import TopNavigation from '@/components/TopNavigation'
import StakingInterface from '@/components/StakingInterface'

export default function StakingPage() {
  const [userId] = useState(1)
  
  // Use REAL Solana wallet
  const { publicKey, connected } = useWallet()
  const walletAddress = publicKey?.toBase58()
  const [mockBalance] = useState(5000000) // Mock balance - in production, fetch from on-chain

  return (
    <div className="min-h-screen bg-white">
      {/* Standard Header */}
      <TopNavigation />

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Staking</h1>
          <p className="text-slate-600">Stake $100Bs tokens and earn from platform revenue</p>
        </div>
        <StakingInterface
          userId={userId}
          walletAddress={walletAddress}
          currentBalance={mockBalance}
        />
      </div>
    </div>
  )
}

