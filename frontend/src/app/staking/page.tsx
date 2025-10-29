'use client'

/**
 * Staking Page
 * 
 * Stake $100Bs tokens and earn from platform revenue
 */

import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import dynamic from 'next/dynamic'
import StakingInterface from '@/components/StakingInterface'

// Dynamically import wallet button to avoid SSR hydration issues
const WalletMultiButton = dynamic(
  async () => (await import('@solana/wallet-adapter-react-ui')).WalletMultiButton,
  { ssr: false }
)

export default function StakingPage() {
  const [userId] = useState(1)
  
  // Use REAL Solana wallet
  const { publicKey, connected } = useWallet()
  const walletAddress = publicKey?.toBase58()
  const [mockBalance] = useState(5000000) // Mock balance - in production, fetch from on-chain

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Staking</h1>
              <p className="text-gray-300">Earn from 10% of platform revenue</p>
            </div>
            <div>
              <WalletMultiButton className="!bg-blue-600 hover:!bg-blue-700 !rounded-lg !font-semibold" />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <StakingInterface
          userId={userId}
          walletAddress={walletAddress}
          currentBalance={mockBalance}
        />
      </div>
    </div>
  )
}

