'use client'

/**
 * Token Page
 * 
 * Main page for $100Bs token dashboard
 * Shows balance, discounts, and platform metrics
 */

import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import dynamic from 'next/dynamic'
import TokenDashboard from '@/components/TokenDashboard'

// Dynamically import wallet button to avoid SSR hydration issues
const WalletMultiButton = dynamic(
  async () => (await import('@solana/wallet-adapter-react-ui')).WalletMultiButton,
  { ssr: false }
)

export default function TokenPage() {
  const [userId] = useState(1) // TODO: Get from auth when implemented
  
  // Use REAL Solana wallet
  const { publicKey, connected, connect, disconnect } = useWallet()
  const walletAddress = publicKey?.toBase58()

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">$100Bs Token</h1>
              <p className="text-gray-300">Manage your tokens and view benefits</p>
            </div>
            <div>
              <WalletMultiButton className="!bg-blue-600 hover:!bg-blue-700 !rounded-lg !font-semibold" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <TokenDashboard userId={userId} walletAddress={walletAddress} />
        
        {/* Navigation Hint */}
        <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="text-3xl">💡</div>
            <div>
              <p className="text-blue-200 font-semibold mb-2">Next Steps:</p>
              <ul className="text-blue-100 space-y-1 text-sm">
                <li>• Connect your Solana wallet to see your actual balance</li>
                <li>• Visit <a href="/staking" className="underline hover:text-white">/staking</a> to stake tokens and earn revenue share</li>
                <li>• Visit <a href="/teams" className="underline hover:text-white">/teams</a> to join a team and collaborate</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

