'use client'

import { useState, useEffect } from 'react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useWallet } from '@solana/wallet-adapter-react'
import ChatInterface from '@/components/ChatInterface'
import BountyDisplay from '@/components/BountyDisplay'
import AdminDashboard from '@/components/AdminDashboard'
import PaymentFlow from '@/components/PaymentFlow'
import ReferralPrompt from '@/components/ReferralPrompt'
import ReferralSystem from '@/components/ReferralSystem'
import Header from '@/components/Header'
import AgeVerification from '@/components/AgeVerification'
import { cn } from '@/lib/utils'

export default function Home() {
  const { connected } = useWallet()
  const [activeTab, setActiveTab] = useState<'chat' | 'research' | 'admin' | 'payment' | 'referrals'>('chat')
  const [showReferralPrompt, setShowReferralPrompt] = useState(false)
  const [hasCheckedReferralPrompt, setHasCheckedReferralPrompt] = useState(false)
  const [showAgeVerification, setShowAgeVerification] = useState(true)
  const [ageVerified, setAgeVerified] = useState(false)

  // Check if age verification has been completed
  useEffect(() => {
    const hasVerifiedAge = localStorage.getItem('ageVerified')
    if (hasVerifiedAge === 'true') {
      setAgeVerified(true)
      setShowAgeVerification(false)
    }
  }, [])

  // Check if referral prompt should be shown
  useEffect(() => {
    const checkReferralPrompt = async () => {
      if (!connected || hasCheckedReferralPrompt || !ageVerified) return

      try {
        // Check if there's a referral code in URL
        const urlParams = new URLSearchParams(window.location.search)
        const hasReferralCodeInUrl = urlParams.get('ref') !== null

        if (hasReferralCodeInUrl) {
          setHasCheckedReferralPrompt(true)
          return
        }

        // Get user's free questions status
        const userResponse = await fetch(`/api/user/profile/${window.location.pathname}`)
        if (userResponse.ok) {
          const userData = await userResponse.json()
          const questionsResponse = await fetch(`/api/referral/free-questions/${userData.user_id}`)
          
          if (questionsResponse.ok) {
            const questions = await questionsResponse.json()
            const statsResponse = await fetch(`/api/referral/stats/${userData.user_id}`)
            
            if (statsResponse.ok) {
              const stats = await statsResponse.json()
              
              // Show prompt if:
              // 1. No free questions available
              // 2. User doesn't have a referral code yet
              if (questions.free_questions_available === 0 && !stats.referral_code) {
                setShowReferralPrompt(true)
              }
            }
          }
        }
      } catch (error) {
        console.error('Error checking referral prompt:', error)
      } finally {
        setHasCheckedReferralPrompt(true)
      }
    }

    checkReferralPrompt()
  }, [connected, hasCheckedReferralPrompt, ageVerified])

  const handleAgeVerification = () => {
    setAgeVerified(true)
    setShowAgeVerification(false)
    localStorage.setItem('ageVerified', 'true')
  }

  const handleAgeRejection = () => {
    setShowAgeVerification(false)
    // Redirect to educational content or show message
    alert('This platform is only available to users 18 and older. Please visit our educational resources for younger users.')
  }

  return (
    <main className="min-h-screen">
      <Header />
      
      {/* Age Verification Modal */}
      {showAgeVerification && (
        <AgeVerification
          onVerified={handleAgeVerification}
          onRejected={handleAgeRejection}
        />
      )}

      {/* Educational Disclaimer Banner */}
      {ageVerified && (
        <div className="bg-yellow-500/20 border-b border-yellow-500/50 py-3">
          <div className="container mx-auto px-4 text-center">
            <p className="text-yellow-200 text-sm font-semibold">
              🔬 Educational Research Platform - This platform is for educational and research purposes only. 
              It is NOT a gambling, lottery, or gaming platform.
            </p>
          </div>
        </div>
      )}
      
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            AI Security Research
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Educational platform for studying AI security vulnerabilities and human psychology. 
            A research-based cybersecurity training system.
          </p>
          
          {!connected && ageVerified && (
            <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-6 mb-8 max-w-md mx-auto">
              <p className="text-blue-200 mb-4">
                Connect your wallet to start researching!
              </p>
              <WalletMultiButton className="!bg-gradient-to-r !from-blue-400 !to-purple-500 !text-white !font-bold !px-6 !py-3 !rounded-lg" />
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-1 flex flex-wrap gap-1">
            <button
              onClick={() => setActiveTab('chat')}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm",
                activeTab === 'chat'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Research Chat
            </button>
            <button
              onClick={() => setActiveTab('research')}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm",
                activeTab === 'research'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Research Fund
            </button>
            <button
              onClick={() => setActiveTab('referrals')}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm",
                activeTab === 'referrals'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Referrals
            </button>
            <button
              onClick={() => setActiveTab('payment')}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm",
                activeTab === 'payment'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Funding
            </button>
            <button
              onClick={() => setActiveTab('admin')}
              className={cn(
                "px-4 py-2 rounded-md font-medium transition-all duration-200 text-sm",
                activeTab === 'admin'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Admin
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {ageVerified ? (
            <>
              {activeTab === 'chat' && <ChatInterface />}
              {activeTab === 'research' && <BountyDisplay />}
              {activeTab === 'referrals' && <ReferralSystem />}
              {activeTab === 'admin' && <AdminDashboard />}
              {activeTab === 'payment' && <PaymentFlow />}
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔒</div>
              <h2 className="text-2xl font-bold text-white mb-4">Age Verification Required</h2>
              <p className="text-gray-300 mb-6">
                Please complete age verification to access the research platform.
              </p>
              <button
                onClick={() => setShowAgeVerification(true)}
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white font-bold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all duration-200"
              >
                Verify Age
              </button>
            </div>
          )}
        </div>

        {/* Referral Prompt Modal */}
        {showReferralPrompt && (
          <ReferralPrompt
            onClose={() => setShowReferralPrompt(false)}
            onGetReferralCode={() => {
              setShowReferralPrompt(false)
              setActiveTab('referrals')
            }}
          />
        )}
      </div>
    </main>
  )
}