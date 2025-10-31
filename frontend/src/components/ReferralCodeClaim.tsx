'use client'

import { useState } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Gift, Mail } from 'lucide-react'
import { getBackendUrl } from '@/lib/api/client'

interface ReferralCodeClaimProps {
  referralCode: string
  onClaimed: () => void
}

export default function ReferralCodeClaim({ referralCode, onClaimed }: ReferralCodeClaimProps) {
  const { publicKey } = useWallet()
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleClaim = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!publicKey) {
      setError('Please connect your wallet first')
      return
    }

    if (!email) {
      setError('Please enter your email address')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${getBackendUrl()}/api/referral/use-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: publicKey.toString(),
          referral_code: referralCode,
          email: email
        })
      })

      const data = await response.json()

      if (data.success) {
        alert(`🎉 Success! You now have ${data.receiver_questions} free questions! The person who referred you also got 5 questions!`)
        onClaimed()
      } else {
        setError(data.detail || data.error || 'Failed to claim referral code')
      }
    } catch (error: any) {
      setError(error.message || 'Failed to claim referral code')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 rounded-xl p-6 shadow-lg">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <Gift className="h-8 w-8 text-green-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-bold text-slate-900 mb-2">
            🎁 You've been referred! Get 5 Free Questions
          </h3>
          <p className="text-slate-600 mb-4">
            Enter your email to claim your 5 free questions. The person who referred you will also get 5 free questions!
          </p>
          
          {error && (
            <div className="mb-4 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
              {error}
            </div>
          )}

          <form onSubmit={handleClaim} className="flex space-x-3">
            <div className="flex-1 relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                required
                disabled={isLoading || !publicKey}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed bg-white placeholder:text-slate-400"
                style={{ color: '#000000' }}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !publicKey || !email}
              className="px-6 py-2 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg hover:from-green-600 hover:to-blue-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Processing...' : 'Claim 5 Questions'}
            </button>
          </form>

          {!publicKey && (
            <p className="mt-3 text-sm text-slate-500">
              Connect your wallet to claim your free questions
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
