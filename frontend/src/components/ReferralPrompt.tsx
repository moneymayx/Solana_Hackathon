'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Share2, X, Gift, Users } from 'lucide-react'

interface FreeQuestions {
  free_questions_available: number
}

interface ReferralStats {
  referral_code: string
  total_referrals: number
  total_free_questions_earned: number
  total_free_questions_used: number
  free_questions_remaining: number
}

interface ReferralPromptProps {
  onClose: () => void
  onGetReferralCode: () => void
}

export default function ReferralPrompt({ onClose, onGetReferralCode }: ReferralPromptProps) {
  const { connected, publicKey } = useWallet()
  const [freeQuestions, setFreeQuestions] = useState<FreeQuestions | null>(null)
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (connected && publicKey) {
      fetchReferralData()
    }
  }, [connected, publicKey])

  const fetchReferralData = async () => {
    try {
      // Get user ID from wallet address
      const userResponse = await fetch(`/api/user/profile/${publicKey?.toString()}`)
      if (userResponse.ok) {
        const userData = await userResponse.json()
        
        // Fetch free questions
        const questionsResponse = await fetch(`/api/referral/free-questions/${userData.user_id}`)
        if (questionsResponse.ok) {
          const questions = await questionsResponse.json()
          setFreeQuestions(questions)
        }
        
        // Fetch referral stats
        const statsResponse = await fetch(`/api/referral/stats/${userData.user_id}`)
        if (statsResponse.ok) {
          const stats = await statsResponse.json()
          setReferralStats(stats)
        }
      }
    } catch (error) {
      console.error('Failed to fetch referral data:', error)
    } finally {
      setLoading(false)
    }
  }

  const shouldShowPrompt = () => {
    // Only show if:
    // 1. User is connected
    // 2. No referral code in URL (main domain)
    // 3. User has no free questions available
    // 4. User doesn't already have a referral code
    const urlParams = new URLSearchParams(window.location.search)
    const hasReferralCodeInUrl = urlParams.get('ref') !== null
    const hasNoFreeQuestions = freeQuestions?.free_questions_available === 0
    const hasNoReferralCode = !referralStats?.referral_code
    
    return connected && !hasReferralCodeInUrl && hasNoFreeQuestions && hasNoReferralCode
  }

  if (loading) {
    return null
  }

  if (!shouldShowPrompt()) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-md w-full relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Share2 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Earn Free Research Attempts!</h2>
            <p className="text-gray-400 text-sm">Share your referral code with others</p>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-4">
          <div className="bg-gray-800/50 rounded-lg p-4">
            <h3 className="text-green-400 font-semibold mb-2 flex items-center space-x-2">
              <Gift className="h-4 w-4" />
              <span>How It Works</span>
            </h3>
            <div className="space-y-2 text-sm text-gray-300">
              <p>• Get your unique referral code</p>
              <p>• Share it with others</p>
              <p>• When they make their first deposit: <span className="text-green-400 font-semibold">5 free research attempts each!</span></p>
              <p>• No conflicts allowed - must use different wallets/emails</p>
            </div>
          </div>

          <div className="bg-blue-600/20 border border-blue-500/30 rounded-lg p-4">
            <h4 className="text-blue-400 font-semibold mb-2 flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>Why Now?</span>
            </h4>
            <p className="text-blue-200 text-sm">
              You've used up your free research attempts. Get more by referring others to the platform!
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex space-x-3 mt-6">
          <button
            onClick={onGetReferralCode}
            className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold px-4 py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 flex items-center justify-center space-x-2"
          >
            <Share2 className="h-4 w-4" />
            <span>Get My Referral Code</span>
          </button>
          <button
            onClick={onClose}
            className="px-4 py-3 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
          >
            Maybe Later
          </button>
        </div>
      </div>
    </div>
  )
}
