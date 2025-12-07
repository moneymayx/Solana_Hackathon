'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import Link from 'next/link'
import dynamic from 'next/dynamic'

// Dynamically import WalletMultiButton to avoid hydration issues
const DynamicWalletMultiButton = dynamic(
  () => import('@solana/wallet-adapter-react-ui').then((mod) => ({ default: mod.WalletMultiButton })),
  { 
    ssr: false,
    loading: () => (
      <button className="wallet-adapter-button wallet-adapter-button-trigger" disabled>
        Loading...
      </button>
    )
  }
)

export default function TopNavigation() {
  const { connected, publicKey } = useWallet()

  return (
    <nav 
      className="sticky top-0 z-50 shadow-lg"
      style={{ backgroundColor: '#0f172a' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            {/* Logo */}
            <Link href="/" className="flex items-center hover:opacity-80 transition-opacity">
              <img 
                src="/images/billions-logo.png"
                alt="BILLIONS$"
                className="h-12 w-auto object-contain"
              />
            </Link>

            {/* Navigation Menu - Left aligned next to logo */}
            <div className="flex items-center space-x-8 ml-8">
              {/* Separator */}
              <div className="text-gray-400 text-xl">|</div>
              
              {/* Navigation Links */}
              <nav className="hidden md:flex items-center space-x-6">
                <Link 
                  href="/#bounties"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  Bounties
                </Link>
                <Link 
                  href="/#how-it-works"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  How It Works
                </Link>
                <Link 
                  href="/#winners"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  Winners
                </Link>
                <Link 
                  href="/#faq"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  FAQ
                </Link>
                <Link 
                  href="/#download-app"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  Download App
                </Link>
                <Link 
                  href="/staking"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  Staking
                </Link>
                <Link 
                  href="/analytics"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  Analytics
                </Link>
                <Link 
                  href="/leaderboard"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  🏆 Leaderboard
                </Link>
                <Link 
                  href="/gamification"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  🎮 Gamification
                </Link>
                <a 
                  href="https://100billioncapital.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  $100Bs
                </a>
              </nav>
            </div>
          </div>
          
          {/* Wallet Button - Right Side */}
          <div className="flex items-center">
            <DynamicWalletMultiButton className="!bg-gradient-to-r !from-purple-600 !to-pink-600 hover:!from-purple-700 hover:!to-pink-700 !rounded-lg !font-semibold !text-white !border-0" />
          </div>
        </div>
      </div>
    </nav>
  )
}
