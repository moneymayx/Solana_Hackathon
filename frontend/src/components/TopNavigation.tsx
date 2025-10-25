'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { 
  Wallet
} from 'lucide-react'
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

// No navigation items - just logo and wallet button

export default function TopNavigation() {
  const { connected, publicKey } = useWallet()

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <nav 
      className="sticky top-0 z-50 shadow-lg"
      style={{ backgroundColor: '#0f172a' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button 
              onClick={() => scrollToTop()}
              className="flex items-center hover:opacity-80 transition-opacity"
            >
              <span 
                className="text-white font-bold text-3xl"
                style={{ 
                  fontFamily: 'var(--font-bricolage), sans-serif',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                  letterSpacing: '1px'
                }}
              >
                BILLIONS
              </span>
            </button>
          </div>

          {/* Right side - Wallet & Mobile menu */}
          <div className="flex items-center space-x-4">
            {/* Wallet Info (Desktop) */}
            {connected && publicKey && (
              <div className="hidden lg:flex items-center space-x-2 text-sm">
                <Wallet className="h-4 w-4 text-blue-200" />
                <span className="text-blue-200">
                  {publicKey.toString().slice(0, 4)}...{publicKey.toString().slice(-4)}
                </span>
              </div>
            )}

            {/* Wallet Connect Button */}
            <DynamicWalletMultiButton />

          </div>
        </div>
      </div>
    </nav>
  )
}
