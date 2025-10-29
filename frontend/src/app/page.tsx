'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { useState, useEffect } from 'react'
import AppLayout from '@/components/layouts/AppLayout'
import ScrollingBanner from '@/components/ScrollingBanner'
import BountyGrid from '@/components/BountyGrid'
import AppDownloadSection from '@/components/AppDownloadSection'
import HowItWorksSection from '@/components/HowItWorksSection'
import WinnersSection from '@/components/WinnersSection'
import FAQSection from '@/components/FAQSection'
import { Target, Crown, Zap, Users, TrendingUp } from 'lucide-react'

export default function Home() {
  const { connected } = useWallet()
  const [totalBountyAmount, setTotalBountyAmount] = useState(0)

  useEffect(() => {
    // Only fetch on client-side
    if (typeof window === 'undefined') return

    const fetchTotalBountyAmount = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/bounties')
        const data = await response.json()
        const bounties = data.bounties || []
        const total = bounties.reduce((sum: number, bounty: any) => sum + (bounty.current_pool || 0), 0)
        setTotalBountyAmount(total)
      } catch (error) {
        console.error('Failed to fetch bounty amount:', error)
      }
    }

    fetchTotalBountyAmount()
    // Update every 5 seconds
    const interval = setInterval(fetchTotalBountyAmount, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <AppLayout>
      <div className="min-h-screen bg-white">
        {/* Hero Section */}
        <section className="relative py-8 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto text-center">
            {/* Main Headline */}
            <h1 
              className="font-bold text-gray-900 mb-4 leading-tight"
              style={{ 
                fontFamily: 'var(--font-bricolage), sans-serif',
                fontSize: 'clamp(1.25rem, 3vw, 1.75rem)',
                textAlign: 'center',
                letterSpacing: '-0.01em',
                maxWidth: '600px',
                margin: '0 auto'
              }}
            >
              Beat the Bot, Win the Pot
            </h1>
          </div>
        </section>

        {/* Scrolling Banner */}
        <section className="px-4 sm:px-6 lg:px-8 mb-6">
          <div className="max-w-7xl mx-auto">
            <ScrollingBanner />
          </div>
        </section>

        {/* Bounties Section */}
        <section id="bounties" className="px-4 sm:px-6 lg:px-8 mb-2">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            Choose Your Bounty
          </h2>
              <p className="text-gray-600 max-w-2xl mx-auto whitespace-nowrap" style={{ fontSize: 'clamp(0.875rem, 2.5vw, 1.125rem)' }}>
                Each AI model offers a unique challenge. Select your target and start your attempt.
              </p>
            </div>
            
            <BountyGrid />
          </div>
        </section>

        {/* App Download Section */}
        <AppDownloadSection />

        {/* How It Works Section */}
        <HowItWorksSection />

        {/* Winners Section */}
        <WinnersSection />

        {/* FAQ Section */}
        <FAQSection />

        {/* Educational Disclaimer Footer */}
        <footer className="bg-gray-100 border-t border-gray-200 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <p className="text-gray-600 text-sm italic mb-4">
                Educational Research Platform - For educational and research purposes only. 
                Not a gambling, lottery, or gaming platform. Users must be 18+ to participate.
              </p>
              <div className="flex items-center justify-center space-x-6 text-gray-500 text-xs">
                <span>Terms of Service</span>
                <span>Privacy Policy</span>
                <span>Contact</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </AppLayout>
  )
}