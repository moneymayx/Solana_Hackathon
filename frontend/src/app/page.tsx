'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { useState, useEffect, useCallback } from 'react'
import AppLayout from '@/components/layouts/AppLayout'
import ScrollingBanner from '@/components/ScrollingBanner'
import BountyGrid from '@/components/BountyGrid'
import AppDownloadSection from '@/components/AppDownloadSection'
import HowItWorksSection from '@/components/HowItWorksSection'
import WinnersSection from '@/components/WinnersSection'
import FAQSection from '@/components/FAQSection'
import { Target, Crown, Zap, Users, TrendingUp } from 'lucide-react'
import { fetchBounties, Bounty } from '@/lib/api/bounties'

export default function Home() {
  const { connected } = useWallet()
  const [totalBountyAmount, setTotalBountyAmount] = useState(0)
  const [bounties, setBounties] = useState<Bounty[]>([])

  const loadBounties = useCallback(async () => {
    console.log('🏠 [HomePage] loadBounties called')
    try {
      console.log('🏠 [HomePage] Fetching bounties...')
      const bountyList = await fetchBounties()
      console.log('🏠 [HomePage] Received bounties:', bountyList.length, bountyList)
      setBounties(bountyList)
      const total = bountyList.reduce((sum: number, bounty: Bounty) => sum + (bounty.current_pool || 0), 0)
      console.log('🏠 [HomePage] Total bounty amount:', total)
      setTotalBountyAmount(total)
    } catch (error) {
      console.error('🏠 [HomePage] Failed to fetch bounty amount:', error)
    }
  }, [])

  useEffect(() => {
    console.log('🏠 [HomePage] Effect triggered, window:', typeof window !== 'undefined' ? 'client' : 'server')
    // Only fetch on client-side
    if (typeof window === 'undefined') {
      console.log('🏠 [HomePage] Skipping fetch (server-side)')
      return
    }

    console.log('🏠 [HomePage] Starting initial fetch and setting up interval')
    loadBounties()
    // Update every 30 seconds instead of 5 (reduce server load)
    const interval = setInterval(() => {
      console.log('🏠 [HomePage] Interval triggered, fetching bounties...')
      loadBounties()
    }, 30000)
    return () => {
      console.log('🏠 [HomePage] Cleanup: clearing interval')
      clearInterval(interval)
    }
  }, [loadBounties])

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
            
            <BountyGrid initialBounties={bounties} />
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