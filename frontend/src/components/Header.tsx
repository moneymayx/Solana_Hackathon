'use client'

import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useWallet } from '@solana/wallet-adapter-react'
import { Crown, Coins } from 'lucide-react'

export default function Header() {
  const { connected, publicKey } = useWallet()

  return (
    <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700/50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <Crown className="h-8 w-8 text-yellow-400" />
              <h1 className="text-2xl font-bold text-white">Billions Bounty</h1>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-400">
              <Coins className="h-4 w-4" />
              <span>AI Treasure Guardian</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Legal Links */}
            <div className="hidden md:flex items-center space-x-4 text-sm">
              <a
                href="/terms"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                Terms
              </a>
              <a
                href="/privacy"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                Privacy
              </a>
            </div>
            
            {connected && publicKey && (
              <div className="hidden md:block text-sm text-gray-300">
                <span className="text-gray-500">Wallet:</span>
                <span className="ml-2 font-mono">
                  {publicKey.toString().slice(0, 4)}...{publicKey.toString().slice(-4)}
                </span>
              </div>
            )}
            <WalletMultiButton className="!bg-gradient-to-r !from-purple-500 !to-pink-500 !text-white !font-bold !px-4 !py-2 !rounded-lg !border-0" />
          </div>
        </div>
      </div>
    </header>
  )
}
