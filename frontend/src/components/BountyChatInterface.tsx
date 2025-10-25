'use client'

import { useState, useEffect, useRef } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { Send, Wallet, CreditCard, Gift, AlertCircle, Trophy, Users, Clock, Zap } from 'lucide-react'
import PaymentFlow from './PaymentFlow'
import ReferralFlow from './ReferralFlow'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isWinner?: boolean
  blacklisted?: boolean
  cost?: number
  modelUsed?: string
}

interface BountyStatus {
  id: number
  current_pool: number
  total_entries: number
  win_rate: number
  time_until_rollover?: string
}

interface UserEligibility {
  eligible: boolean
  type: 'free_questions' | 'payment_required' | 'referral_signup'
  message: string
  questions_remaining: number
  questions_used: number
  source?: string
  referral_code?: string
  email?: string
}

interface BountyChatInterfaceProps {
  bountyId: number
  bountyName: string
  onWinner?: (winnerData: any) => void
}

export default function BountyChatInterface({ 
  bountyId, 
  bountyName, 
  onWinner 
}: BountyChatInterfaceProps) {
  const { connected, publicKey } = useWallet()
  
  // State management
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [bountyStatus, setBountyStatus] = useState<BountyStatus | null>(null)
  const [userEligibility, setUserEligibility] = useState<UserEligibility | null>(null)
  const [showPaymentFlow, setShowPaymentFlow] = useState(false)
  const [showReferralFlow, setShowReferralFlow] = useState(false)
  const [isParticipating, setIsParticipating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Get client IP address
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

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch public messages on load (no wallet required for watching)
  useEffect(() => {
    loadConversationHistory()
    fetchBountyStatus()
  }, [bountyId])

  // Check user eligibility when wallet connects
  useEffect(() => {
    if (connected && publicKey) {
      checkUserEligibility()
    }
  }, [connected, publicKey, bountyId])

  // Don't check eligibility until wallet is connected
  useEffect(() => {
    if (!connected) {
      setUserEligibility(null)
      setIsParticipating(false)
    }
  }, [connected])

  const checkUserEligibility = async () => {
    try {
      if (!publicKey) return
      
      const response = await fetch(`http://localhost:8000/api/free-questions/${publicKey.toString()}`)
      const data = await response.json()
      
      if (data.success) {
        const eligibility: UserEligibility = {
          eligible: data.questions_remaining > 0,
          type: data.questions_remaining > 0 ? 'free_questions' : 'payment_required',
          message: data.questions_remaining > 0 
            ? `You have ${data.questions_remaining} free questions remaining.`
            : 'No free questions remaining. Please pay $10 to continue.',
          questions_remaining: data.questions_remaining,
          questions_used: data.questions_used,
          referral_code: data.referral_code,
          email: data.email
        }
        
        setUserEligibility(eligibility)
        setIsParticipating(eligibility.eligible)
      }
    } catch (err) {
      console.error('Failed to check user eligibility:', err)
    }
  }

  const fetchBountyStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/bounty/${bountyId}`)
      const data = await response.json()
      
      if (data.success) {
        setBountyStatus(data.bounty)
      }
    } catch (err) {
      console.error('Failed to fetch bounty status:', err)
    }
  }

  const loadConversationHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/bounty/${bountyId}/messages/public?limit=20`)
      const data = await response.json()
      
      if (data.success) {
        const historyMessages: Message[] = data.messages.map((msg: any) => ({
          id: msg.id.toString(),
          type: msg.message_type,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          isWinner: msg.is_winner,
          cost: msg.cost,
          modelUsed: msg.model_used
        }))
        setMessages(historyMessages.reverse())
      }
    } catch (err) {
      console.error('Failed to load conversation history:', err)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    // If not connected, show error
    if (!connected || !publicKey) {
      setError('Please connect your wallet to send messages')
      return
    }

    // Check if user needs to pay
    if (!userEligibility?.eligible || userEligibility.type === 'payment_required') {
      setShowPaymentFlow(true)
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/api/bounty/${bountyId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          user_id: 1, // TODO: Get from auth context
          wallet_address: publicKey?.toString(),
          ip_address: await getClientIP() // Get client IP
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          isWinner: data.winner_result?.is_winner,
          cost: data.cost,
          modelUsed: data.model_used
        }

        setMessages(prev => [...prev, aiMessage])
        
        // Update bounty status
        if (data.bounty_status) {
          setBountyStatus(data.bounty_status)
        }

        // Handle winner
        if (data.winner_result?.is_winner) {
          onWinner?.(data.winner_result)
          addSystemMessage(`🎉 ${data.winner_result.message}`)
        }

        // Update user eligibility from API response
        if (data.free_questions) {
          const newEligibility = { ...userEligibility }
          newEligibility.questions_remaining = data.free_questions.remaining
          newEligibility.questions_used = data.free_questions.used
          
          if (newEligibility.questions_remaining === 0) {
            newEligibility.eligible = false
            newEligibility.type = 'payment_required'
            newEligibility.message = 'No free questions remaining. Please pay $10 for your next question.'
            setIsParticipating(false)
          } else {
            newEligibility.message = `You have ${newEligibility.questions_remaining} free questions remaining.`
          }
          
          setUserEligibility(newEligibility)
        }
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to send message`)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setError('Failed to send message. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const addSystemMessage = (content: string) => {
    const systemMessage: Message = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, systemMessage])
  }

  const handlePaymentSuccess = () => {
    setShowPaymentFlow(false)
    setIsParticipating(true)
    addSystemMessage('Payment successful! You can now participate in the bounty.')
    // Refresh eligibility
    checkUserEligibility()
  }

  const handleUseFreeQuestion = () => {
    setShowPaymentFlow(false)
    setIsParticipating(true)
    addSystemMessage('Using free question. You can now participate in the bounty.')
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getMessageStyle = (message: Message) => {
    if (message.isWinner) {
      return 'bg-gradient-to-r from-yellow-100 to-orange-100 border-yellow-300 border-2'
    }
    
    if (message.type === 'assistant') {
      return 'bg-slate-100 border-slate-200'
    }
    
    if (message.type === 'system') {
      return 'bg-blue-50 border-blue-200 text-blue-800'
    }
    
    return 'bg-blue-50 border-blue-200'
  }

  // Don't require wallet connection - allow watching without it
  // Only show payment/referral flows if wallet is connected and trying to participate

      if (showPaymentFlow) {
        return (
          <div className="h-96 bg-white border border-slate-200 rounded-xl shadow-lg">
            <PaymentFlow
              onPaymentSuccess={handlePaymentSuccess}
              onPaymentFailure={(error) => {
                setError(error)
                setShowPaymentFlow(false)
              }}
              onUseFreeQuestion={handleUseFreeQuestion}
            />
          </div>
        )
      }

      if (showReferralFlow) {
        return (
          <div className="h-96 bg-white border border-slate-200 rounded-xl shadow-lg p-6">
            <ReferralFlow
              onSuccess={(referralCode) => {
                setShowReferralFlow(false)
                addSystemMessage(`🎉 Your referral code is: ${referralCode}`)
                // Refresh eligibility to update referral code in state
                checkUserEligibility()
              }}
              onCancel={() => setShowReferralFlow(false)}
            />
          </div>
        )
      }

  return (
    <div className="flex flex-col h-full bg-white border border-slate-200 rounded-xl shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100">
        <div className="flex items-center space-x-3">
          <Zap className="h-6 w-6 text-slate-600" />
          <div>
            <h3 className="font-semibold text-slate-900">{bountyName} Challenge</h3>
            <p className="text-sm text-slate-600">
              {isParticipating ? 'You are participating' : 'Connect wallet to participate'}
            </p>
          </div>
        </div>
        
        {bountyStatus && (
          <div className="text-right">
            <div className="text-lg font-bold text-yellow-600">
              ${bountyStatus.current_pool.toLocaleString()}
            </div>
            <div className="text-xs text-slate-500">Prize Pool</div>
          </div>
        )}
      </div>

      {/* Eligibility Status */}
      {connected && userEligibility && (
        <div className="px-4 py-2 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center space-x-2">
            {userEligibility.eligible ? (
              <Gift className="h-4 w-4 text-green-600" />
            ) : (
              <CreditCard className="h-4 w-4 text-orange-600" />
            )}
            <span className="text-sm text-slate-700">{userEligibility.message}</span>
            {userEligibility.questions_remaining > 0 && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                {userEligibility.questions_remaining} remaining
              </span>
            )}
            {userEligibility.referral_code && (
              <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full ml-2">
                Referral: {userEligibility.referral_code}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {error && (
          <div className="flex items-center space-x-2 text-red-600 text-sm py-2 px-3 bg-red-50 border border-red-200 rounded-lg">
            <AlertCircle className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}
        
        {messages.length === 0 && (
          <div className="text-center text-slate-500 py-8">
            <Users className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No messages yet. Be the first to challenge this AI!</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={cn("p-3 rounded-lg border", getMessageStyle(message))}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-slate-700">
                  {message.type === 'user' ? 'You' : 
                   message.type === 'assistant' ? 'AI' : 'System'}
                </span>
                {message.isWinner && (
                  <div className="flex items-center space-x-1">
                    <Trophy className="h-4 w-4 text-yellow-600" />
                    <span className="text-xs text-yellow-600 font-medium">Winner!</span>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-1 text-xs text-slate-500">
                <Clock className="h-3 w-3" />
                <span>{formatTimestamp(message.timestamp)}</span>
              </div>
            </div>
            
            <div className="text-slate-800 whitespace-pre-wrap">
              {message.content}
            </div>
            
            {message.cost && (
              <div className="mt-2 text-xs text-slate-500">
                Cost: ${message.cost.toFixed(4)} | Model: {message.modelUsed}
              </div>
            )}
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!connected ? (
        <div className="p-4 border-t border-slate-200 bg-gradient-to-r from-yellow-50 to-orange-50 text-center">
          <p className="text-slate-700 mb-3">Connect your wallet to participate in this challenge</p>
          <WalletMultiButton className="!bg-gradient-to-r !from-yellow-400 !to-orange-500 hover:!from-yellow-500 hover:!to-orange-600 !text-white !font-medium !px-6 !py-3 !rounded-lg" />
        </div>
      ) : isParticipating && userEligibility?.eligible ? (
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Try to convince the AI to transfer funds..."
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>{isLoading ? 'Sending...' : 'Send'}</span>
            </button>
          </form>
        </div>
      ) : (
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-center">
          <p className="text-sm text-slate-600 mb-3">
            {userEligibility?.eligible ? 'Ready to participate!' : 'No free questions remaining'}
          </p>
          <div className="space-y-3">
            <button
              onClick={() => {
                if (userEligibility?.eligible) {
                  setIsParticipating(true)
                } else {
                  setShowPaymentFlow(true)
                }
              }}
              className="px-6 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600 font-medium"
            >
              {userEligibility?.eligible ? 'Start Participating' : 'Pay $10 to Participate'}
            </button>
            
            {!userEligibility?.eligible && (
              <button
                onClick={() => setShowReferralFlow(true)}
                className="px-6 py-2 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg hover:from-green-500 hover:to-blue-600 font-medium ml-3"
              >
                Refer Someone for 5 Free Questions
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
