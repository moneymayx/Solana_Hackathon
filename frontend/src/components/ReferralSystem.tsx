'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Share2, Copy, Users, Gift, CheckCircle } from 'lucide-react'

interface ReferralStats {
  referral_code: string
  total_referrals: number
  total_free_questions_earned: number
  total_free_questions_used: number
  free_questions_remaining: number
}

interface FreeQuestions {
  free_questions_available: number
}

export default function ReferralSystem() {
  const { connected, publicKey } = useWallet()
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null)
  const [freeQuestions, setFreeQuestions] = useState<FreeQuestions | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (connected && publicKey) {
      fetchReferralData()
    }
  }, [connected, publicKey])

  const fetchReferralData = async () => {
    try {
      // Get user ID from wallet address (you'll need to implement this)
      const userResponse = await fetch(`/api/user/profile/${publicKey?.toString()}`)
      if (userResponse.ok) {
        const userData = await userResponse.json()
        
        // Fetch referral stats
        const statsResponse = await fetch(`/api/referral/stats/${userData.user_id}`)
        if (statsResponse.ok) {
          const stats = await statsResponse.json()
          setReferralStats(stats)
        }
        
        // Fetch free questions
        const questionsResponse = await fetch(`/api/referral/free-questions/${userData.user_id}`)
        if (questionsResponse.ok) {
          const questions = await questionsResponse.json()
          setFreeQuestions(questions)
        }
      }
    } catch (error) {
      console.error('Failed to fetch referral data:', error)
    } finally {
      setLoading(false)
    }
  }

  const copyReferralCode = async () => {
    if (referralStats?.referral_code) {
      const referralLink = `${window.location.origin}?ref=${referralStats.referral_code}`
      await navigator.clipboard.writeText(referralLink)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const shareReferralCode = async () => {
    if (referralStats?.referral_code) {
      const referralLink = `${window.location.origin}?ref=${referralStats.referral_code}`
      
      if (navigator.share) {
        try {
          await navigator.share({
            title: 'Join AI Security Research',
            text: 'Join me in AI security research and get 5 free research attempts!',
            url: referralLink
          })
        } catch (error) {
          console.error('Error sharing:', error)
        }
      } else {
        // Fallback to copying
        await copyReferralCode()
      }
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400">Loading referral data...</p>
      </div>
    )
  }

  if (!connected) {
    return (
      <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">🔗 Connect Wallet to Access Referral System</h3>
        <p className="text-gray-300">
          Connect your wallet to get your unique referral code and start earning free research attempts!
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Referral Code Section */}
      <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Share2 className="h-6 w-6 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">Your Referral Code</h3>
        </div>
        
        {referralStats?.referral_code ? (
          <div className="space-y-4">
            <div className="bg-gray-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Referral Code</p>
                  <p className="text-2xl font-bold text-white font-mono">
                    {referralStats.referral_code}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={copyReferralCode}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg transition-colors"
                  >
                    {copied ? <CheckCircle className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </button>
                  <button
                    onClick={shareReferralCode}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors"
                  >
                    <Share2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="bg-green-600/20 border border-green-500/30 rounded-lg p-4">
              <h4 className="text-green-400 font-semibold mb-2">🎁 Referral Rewards</h4>
              <div className="space-y-1 text-sm text-gray-300">
                <p>• Share your code with others</p>
                <p>• For every successful referral: <span className="text-green-400 font-semibold">5 free research attempts</span></p>
                <p>• Your referee also gets: <span className="text-green-400 font-semibold">5 free research attempts</span></p>
                <p>• No wallet or email conflicts allowed</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center">
            <p className="text-gray-400 mb-4">Generating your referral code...</p>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          </div>
        )}
      </div>

      {/* Referral Stats */}
      {referralStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Users className="h-6 w-6 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Referral Stats</h3>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Total Referrals:</span>
                <span className="text-white font-semibold">{referralStats.total_referrals}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Questions Earned:</span>
                <span className="text-green-400 font-semibold">{referralStats.total_free_questions_earned}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Questions Used:</span>
                <span className="text-yellow-400 font-semibold">{referralStats.total_free_questions_used}</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Gift className="h-6 w-6 text-purple-400" />
              <h3 className="text-lg font-semibold text-white">Free Questions</h3>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-400 mb-2">
                {freeQuestions?.free_questions_available || 0}
              </p>
              <p className="text-gray-400">Available for Research</p>
            </div>
          </div>
        </div>
      )}

      {/* How It Works */}
      <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">How the Referral System Works</h3>
        <div className="space-y-3 text-gray-300">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">1</div>
            <p>Share your unique referral code with others</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">2</div>
            <p>When someone uses your code and makes their first deposit, both of you get 5 free research attempts</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">3</div>
            <p>Free questions can be used instead of paying the $10 research fee</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">4</div>
            <p>No conflicts allowed - referees must use different wallets and emails than referrers</p>
          </div>
        </div>
      </div>
    </div>
  )
}
