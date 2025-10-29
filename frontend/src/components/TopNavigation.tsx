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

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <nav 
      className="sticky top-0 z-50 shadow-lg"
      style={{ backgroundColor: '#0f172a' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button 
              onClick={() => scrollToTop()}
              className="flex items-center hover:opacity-80 transition-opacity"
            >
              <img 
                src="/images/billions-logo.png"
                alt="BILLIONS$"
                className="h-24 w-auto"
              />
            </button>
          </div>

          {/* Navigation Menu - Left aligned next to logo */}
          <div className="flex items-center space-x-8 ml-8">
            {/* Separator */}
            <div className="text-gray-400 text-xl">|</div>
            
            {/* Navigation Links */}
            <nav className="hidden md:flex items-center space-x-6">
              <button 
                onClick={() => scrollToSection('bounties')}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                Bounties
              </button>
              <button 
                onClick={() => scrollToSection('how-it-works')}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                How It Works
              </button>
              <button 
                onClick={() => scrollToSection('winners')}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                Winners
              </button>
              <button 
                onClick={() => scrollToSection('faq')}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                FAQ
              </button>
              <button 
                onClick={() => scrollToSection('download-app')}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                Download App
              </button>
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
      </div>
    </nav>
  )
}
