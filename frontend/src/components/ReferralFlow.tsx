'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Mail, Share2, Copy, Check } from 'lucide-react'
import { getBackendUrl } from '@/lib/api/client'

interface ReferralFlowProps {
  onSuccess: (referralCode: string) => void
  onCancel: () => void
}

export default function ReferralFlow({ onSuccess, onCancel }: ReferralFlowProps) {
  const { publicKey } = useWallet()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [referralCode, setReferralCode] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [checkingExisting, setCheckingExisting] = useState(true)

  // Check for existing referral code when component loads
  useEffect(() => {
    const checkExistingReferralCode = async () => {
      if (!publicKey) {
        setCheckingExisting(false)
        return
      }

      try {
        const response = await fetch(`${getBackendUrl()}/api/free-questions/${publicKey.toString()}`)
        const data = await response.json()
        
        if (data.success && data.referral_code) {
          setReferralCode(data.referral_code)
          setEmail(data.email || '')
        }
      } catch (err) {
        console.error('Failed to check existing referral code:', err)
      } finally {
        setCheckingExisting(false)
      }
    }

    checkExistingReferralCode()
  }, [publicKey])

  const handleSubmitEmail = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username || !email || !publicKey) return

    // Validate username
    if (username.length < 3) {
      setError('Username must be at least 3 characters')
      return
    }

    // Validate email
    if (!email.includes('@') || !email.includes('.com')) {
      setError('Email must contain @ and .com')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${getBackendUrl()}/api/referral/submit-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: publicKey.toString(),
          username: username,
          email: email,
          ip_address: await getClientIP()
        })
      })

      const data = await response.json()

      if (data.success) {
        setReferralCode(data.referral_code)
      } else {
        setError(data.detail || 'Failed to submit email')
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const getClientIP = async (): Promise<string> => {
    try {
      const response = await fetch('https://api.ipify.org?format=json')
      const data = await response.json()
      return data.ip
    } catch (error) {
      console.error('Failed to get IP address:', error)
      return 'unknown'
    }
  }

  const copyReferralCode = () => {
    if (referralCode) {
      navigator.clipboard.writeText(referralCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const shareReferralCode = () => {
    if (referralCode) {
      const shareText = `Join me on BILLION$! Use my referral code: ${referralCode} to get 5 free questions!`
      if (navigator.share) {
        navigator.share({
          title: 'BILLION$ Referral',
          text: shareText,
          url: 'https://billionsbounty.com'
        })
      } else {
        navigator.clipboard.writeText(shareText)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }
    }
  }

  if (checkingExisting) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Checking for existing referral code...</h3>
        <p className="text-slate-600">Please wait while we check your account.</p>
      </div>
    )
  }

  if (referralCode) {
    return (
      <div className="text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Share2 className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-2">Your Referral Code is Ready!</h3>
          <p className="text-slate-600">Share this code with friends to get 5 free questions for each person who uses it!</p>
          {email && (
            <p className="text-sm text-slate-500 mt-2">Registered with: {email}</p>
          )}
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <code className="text-lg font-mono text-slate-900">{referralCode}</code>
            <button
              onClick={copyReferralCode}
              className="flex items-center space-x-2 px-3 py-2 bg-slate-200 hover:bg-slate-300 rounded-lg transition-colors"
            >
              {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
              <span className="text-sm">{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
        </div>

        <div className="space-y-3">
          <button
            onClick={shareReferralCode}
            className="w-full px-4 py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg hover:from-green-500 hover:to-blue-600 font-medium flex items-center justify-center space-x-2"
          >
            <Share2 className="h-5 w-5" />
            <span>Share Referral Code</span>
          </button>
          
          <button
            onClick={() => onSuccess(referralCode)}
            className="w-full px-4 py-3 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 font-medium"
          >
            Continue to Chat
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <Mail className="h-8 w-8 text-white" />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Get Your Referral Code</h3>
        <p className="text-slate-600">Enter your username and email to get a referral code. Share it with friends to earn 5 free questions for each person who uses it!</p>
      </div>

      <form onSubmit={handleSubmitEmail} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-slate-700 mb-2">
            Username
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username (min 3 characters)"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-slate-900 bg-white"
            required
            minLength={3}
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-slate-900 bg-white"
            required
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
            {error}
          </div>
        )}

        <div className="space-y-3">
          <button
            type="submit"
            disabled={isLoading || !username || !email}
            className="w-full px-4 py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg hover:from-green-500 hover:to-blue-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Generating Code...</span>
              </>
            ) : (
              <>
                <Mail className="h-5 w-5" />
                <span>Get Referral Code</span>
              </>
            )}
          </button>
          
          <button
            type="button"
            onClick={onCancel}
            className="w-full px-4 py-3 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 font-medium"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
