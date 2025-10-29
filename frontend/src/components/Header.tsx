'use client'

import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useWallet } from '@solana/wallet-adapter-react'
import { Crown, Coins } from 'lucide-react'
import Link from 'next/link'

export default function Header() {
  const { connected, publicKey } = useWallet()

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            {/* Logo/Home */}
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <Crown className="h-8 w-8 text-yellow-500" />
              <h1 className="text-2xl font-bold text-gray-900">Billions Bounty</h1>
            </Link>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-6">
              <button
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="text-gray-700 hover:text-yellow-600 font-medium transition-colors duration-200"
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection('bounties')}
                className="text-gray-700 hover:text-yellow-600 font-medium transition-colors duration-200"
              >
                Bounties
              </button>
              <button
                onClick={() => scrollToSection('winners')}
                className="text-gray-700 hover:text-yellow-600 font-medium transition-colors duration-200"
              >
                Winners
              </button>
            </nav>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Legal Links */}
            <div className="hidden md:flex items-center space-x-4 text-sm">
              <a
                href="/terms"
                className="text-gray-500 hover:text-gray-700 transition-colors duration-200"
              >
                Terms
              </a>
              <a
                href="/privacy"
                className="text-gray-500 hover:text-gray-700 transition-colors duration-200"
              >
                Privacy
              </a>
            </div>
            
            {connected && publicKey && (
              <div className="hidden md:block text-sm text-gray-600">
                <span className="text-gray-400">Wallet:</span>
                <span className="ml-2 font-mono text-gray-700">
                  {publicKey.toString().slice(0, 4)}...{publicKey.toString().slice(-4)}
                </span>
              </div>
            )}
            <WalletMultiButton className="!bg-gradient-to-r !from-yellow-500 !to-orange-500 !text-white !font-semibold !px-6 !py-2 !rounded-lg !border-0 !shadow-md hover:!shadow-lg !transition-all !duration-200" />
          </div>
        </div>
      </div>
    </header>
  )
}
