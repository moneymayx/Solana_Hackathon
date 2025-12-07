'use client'

import { useState, useEffect, useRef } from 'react'
import { useWallet, useConnection } from '@solana/wallet-adapter-react'
import { Send, Wallet, CreditCard, Gift, AlertCircle, Trophy, Users, Clock, Zap, Loader2, Target, Crown, Shield } from 'lucide-react'
import dynamic from 'next/dynamic'
import { Transaction, PublicKey, SystemProgram } from '@solana/web3.js'
import { getAssociatedTokenAddress, createTransferInstruction, TOKEN_PROGRAM_ID } from '@solana/spl-token'
import ReferralFlow from './ReferralFlow'
import NftVerification from './NftVerification'
import Toast from './Toast'
import PaymentAmountModal from './PaymentAmountModal'
import UsernamePrompt from './UsernamePrompt'
import { addActivity } from './ActivityTracker'
import { useActivityTracking } from '@/hooks/useActivityTracking'
import { cn } from '@/lib/utils'
import { getBackendUrl } from '@/lib/api/client'

// Dynamically import WalletButton to avoid hydration issues and ensure proper cleanup
const DynamicWalletButton = dynamic(
  () => import('./WalletButton'),
  { 
    ssr: false,
    loading: () => (
      <button className="wallet-adapter-button wallet-adapter-button-trigger" disabled>
        Loading...
      </button>
    )
  }
)

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
  difficulty_level: string
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
  is_paid?: boolean  // Indicates if questions are from paid transactions vs free/referral
  credit_balance?: number
}

interface BountyChatInterfaceProps {
  bountyId: number
  bountyName: string
  onWinner?: (winnerData: any) => void
}

// Helper function to get starting question cost based on difficulty
const getStartingQuestionCost = (difficulty: string): number => {
  const difficultyMap: Record<string, number> = {
    'easy': 0.50,
    'medium': 2.50,
    'hard': 5.00,
    'expert': 10.00
  }
  return difficultyMap[difficulty.toLowerCase()] || 0.50
}

// Helper function to calculate current question cost
const getCurrentQuestionCost = (startingCost: number, totalEntries: number): number => {
  return startingCost * Math.pow(1.0078, totalEntries)
}

// Helper function to get difficulty icon
const getDifficultyIcon = (difficulty: string | undefined) => {
  if (!difficulty) return <Target className="h-5 w-5 text-slate-600" />
  
  switch (difficulty.toLowerCase()) {
    case 'expert':
      return <Crown className="h-5 w-5 text-red-600" />
    case 'hard':
      return <Zap className="h-5 w-5 text-orange-600" />
    case 'medium':
      return <Target className="h-5 w-5 text-blue-600" />
    case 'easy':
      return <Shield className="h-5 w-5 text-emerald-600" />
    default:
      return <Target className="h-5 w-5 text-slate-600" />
  }
}

// Helper function to get difficulty color
const getDifficultyColor = (difficulty: string | undefined) => {
  if (!difficulty) return 'text-slate-600 bg-slate-100 border-slate-300'
  
  switch (difficulty.toLowerCase()) {
    case 'expert':
      return 'text-red-600 bg-red-100 border-red-300'
    case 'hard':
      return 'text-orange-600 bg-orange-100 border-orange-300'
    case 'medium':
      return 'text-blue-600 bg-blue-100 border-blue-300'
    case 'easy':
      return 'text-emerald-600 bg-emerald-100 border-emerald-300'
    default:
      return 'text-slate-600 bg-slate-100 border-slate-300'
  }
}

export default function BountyChatInterface({ 
  bountyId, 
  bountyName, 
  onWinner 
}: BountyChatInterfaceProps) {
  const { connected, publicKey, signTransaction } = useWallet()
  const { connection } = useConnection()
  
  // State management
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [bountyStatus, setBountyStatus] = useState<BountyStatus | null>(null)
  const [userEligibility, setUserEligibility] = useState<UserEligibility | null>(null)
  const [isProcessingPayment, setIsProcessingPayment] = useState(false)
  const [showReferralFlow, setShowReferralFlow] = useState(false)
  const [showNftFlow, setShowNftFlow] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [showUsernamePrompt, setShowUsernamePrompt] = useState(false)
  const [pendingAction, setPendingAction] = useState<(() => void) | null>(null)
  const [username, setUsername] = useState<string | null>(null)
  const [isParticipating, setIsParticipating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' | 'warning' } | null>(null)
  
  // Check if activity tracker feature is enabled
  const isActivityTrackerEnabled = process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER === 'true'
  
  // Activity tracking hook for backend streak/points system
  const { recordActivity } = useActivityTracking()
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const hasScrolledRef = useRef(false)
  const previousMessagesLengthRef = useRef(0)
  const isFirstQuestionRef = useRef(true) // Track if this is user's first question

  // Get client IP address (mock for now - CSP blocks external API)
  const getClientIP = async (): Promise<string> => {
    // Return 'browser' instead of fetching from external API
    // Backend can get real IP from request headers if needed
    return 'browser'
  }

  // Auto-scroll to bottom only when NEW messages arrive (not on initial load)
  // Use container scrollTop to avoid scrolling the entire page
  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    // Only scroll if:
    // 1. We've already scrolled before (user has interacted)
    // 2. New messages were added (not initial load)
    if (hasScrolledRef.current && messages.length > previousMessagesLengthRef.current) {
      scrollToBottom()
    }
    previousMessagesLengthRef.current = messages.length
  }, [messages])

  // Check if username exists for current wallet
  const checkUsername = async () => {
    if (!publicKey || !isActivityTrackerEnabled) return
    
    try {
      const response = await fetch(`${getBackendUrl()}/api/user/profile/${publicKey.toString()}`)
      if (response.ok) {
        const data = await response.json()
        if (data.display_name) {
          setUsername(data.display_name)
        }
      } else {
        // User doesn't exist or no username set
        setUsername(null)
      }
    } catch (err) {
      console.error('Failed to check username:', err)
      setUsername(null)
    }
  }

  // Fetch public messages on load (no wallet required for watching)
  useEffect(() => {
    loadConversationHistory()
    fetchBountyStatus()
  }, [bountyId])

  // Check user eligibility when wallet connects
  useEffect(() => {
    if (connected && publicKey) {
      checkUserEligibility()
      if (isActivityTrackerEnabled) {
        checkUsername()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connected, publicKey, bountyId, isActivityTrackerEnabled])

  // Don't check eligibility until wallet is connected
  useEffect(() => {
    if (!connected) {
      setUserEligibility(null)
      setIsParticipating(false)
      setUsername(null)
      isFirstQuestionRef.current = true // Reset first question flag when wallet disconnects
    }
  }, [connected])

  // Handle action with username check (if feature enabled)
  const handleActionWithUsernameCheck = (action: () => void) => {
    if (!isActivityTrackerEnabled) {
      // Feature disabled, proceed normally
      action()
      return
    }

    if (!username) {
      // Username not set, show prompt and save action
      setPendingAction(() => action)
      setShowUsernamePrompt(true)
    } else {
      // Username exists, proceed with action
      action()
    }
  }

  // Handle username prompt success
  const handleUsernameSuccess = async () => {
    setShowUsernamePrompt(false)
    // Refresh username
    await checkUsername()
    // Execute pending action if exists
    if (pendingAction) {
      pendingAction()
      setPendingAction(null)
    }
  }

  const checkUserEligibility = async () => {
    try {
      if (!publicKey) return
      
      const response = await fetch(`${getBackendUrl()}/api/free-questions/${publicKey.toString()}`)
      const data = await response.json()
      
      if (data.success) {
        // Calculate dynamic question cost
        const startingCost = bountyStatus ? getStartingQuestionCost(bountyStatus.difficulty_level || 'easy') : 0.50
        const currentCost = bountyStatus ? getCurrentQuestionCost(startingCost, bountyStatus.total_entries || 0) : 10
        
        const eligibility: UserEligibility = {
          eligible: data.questions_remaining > 0,
          type: data.questions_remaining > 0 ? 'free_questions' : 'payment_required',
          message: data.questions_remaining > 0 
            ? `You have ${data.questions_remaining} free questions remaining.`
            : `No free questions remaining. Please pay $${currentCost.toFixed(2)} to continue.`,
          questions_remaining: data.questions_remaining,
          questions_used: data.questions_used,
          referral_code: data.referral_code,
          email: data.email,
          is_paid: data.is_paid || false,  // Include is_paid from API response
          credit_balance: data.credit_balance || 0
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
      const response = await fetch(`${getBackendUrl()}/api/bounty/${bountyId}`)
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
      console.log(`Loading conversation history for bounty ${bountyId}...`)
      const response = await fetch(`${getBackendUrl()}/api/bounty/${bountyId}/messages/public?limit=20`)
      
      if (!response.ok) {
        console.error(`Failed to fetch messages: ${response.status} ${response.statusText}`)
        return
      }
      
      const data = await response.json()
      console.log('Messages response:', data)
      
      if (data.success && data.messages && Array.isArray(data.messages)) {
        const historyMessages: Message[] = data.messages.map((msg: any) => ({
          id: msg.id.toString(),
          type: msg.message_type,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          isWinner: msg.is_winner,
          cost: msg.cost,
          modelUsed: msg.model_used
        }))
        console.log(`Loaded ${historyMessages.length} messages`)
        setMessages(historyMessages.reverse())
      } else {
        console.log('No messages found or invalid response format')
        setMessages([])
      }
    } catch (err) {
      console.error('Failed to load conversation history:', err)
      setMessages([])
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    // Mark that user has interacted - enable auto-scroll
    hasScrolledRef.current = true

    // If not connected, show error
    if (!connected || !publicKey) {
      setError('Please connect your wallet to send messages')
      return
    }

    // Check if user needs to pay
    if (!userEligibility?.eligible || userEligibility.type === 'payment_required') {
      setError('Please complete payment to send messages')
      return
    }

    const userMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${getBackendUrl()}/api/bounty/${bountyId}/chat`, {
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
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          isWinner: data.winner_result?.is_winner,
          cost: data.cost,
          modelUsed: data.model_used
        }

        setMessages(prev => [...prev, aiMessage])
        
        // Update bounty status only if it has actual data
        // (backend may return empty {} if agent doesn't provide status)
        if (data.bounty_status && data.bounty_status.current_pool !== undefined) {
          setBountyStatus(data.bounty_status)
        }

        // Handle winner (jailbreak success)
        if (data.winner_result?.is_winner) {
          onWinner?.(data.winner_result)
          addSystemMessage(`🎉 ${data.winner_result.message}`)
          
          // Track jailbreak success for gamification (10x multiplier)
          if (publicKey) {
            recordActivity(publicKey.toString()).catch(err => 
              console.error('Failed to record jailbreak activity:', err)
            )
          }
        }

        // Track activity for UI display and backend gamification
        if (isActivityTrackerEnabled && username) {
          const activityType = isFirstQuestionRef.current ? 'first_question' : 'question'
          // Track in localStorage for ActivityTracker UI component
          addActivity(bountyId, username, activityType, bountyName)
          isFirstQuestionRef.current = false
        }
        
        // Track question activity for backend streak/points system
        if (publicKey) {
          recordActivity(publicKey.toString()).catch(err => 
            console.error('Failed to record question activity:', err)
          )
        }

        // Update user eligibility from API response
        if (data.free_questions) {
          const newEligibility = { ...userEligibility }
          newEligibility.questions_remaining = data.free_questions.remaining
          newEligibility.questions_used = data.free_questions.used
          
          // Check if these are paid questions or free questions
          const isPaid = data.free_questions.is_paid || false
          newEligibility.is_paid = isPaid  // Preserve is_paid status
          
          if (newEligibility.questions_remaining === 0) {
            newEligibility.eligible = false
            newEligibility.type = 'payment_required'
            
            // Calculate dynamic question cost based on bounty difficulty and entries
            const startingCost = bountyStatus ? getStartingQuestionCost(bountyStatus.difficulty_level || 'easy') : 0.50
            const currentCost = bountyStatus ? getCurrentQuestionCost(startingCost, bountyStatus.total_entries || 0) : 10
            
            newEligibility.message = `No questions remaining. Please pay $${currentCost.toFixed(2)} for your next question.`
            setIsParticipating(false)
          } else {
            newEligibility.message = isPaid
              ? `You have ${newEligibility.questions_remaining} questions remaining.`
              : `You have ${newEligibility.questions_remaining} free questions remaining.`
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

  const showToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    setToast({ message, type })
  }

  const addSystemMessage = (content: string) => {
    // Don't add payment/mock mode messages to chat
    // Show them as toasts instead
    const isPaymentMessage = content.includes('TEST MODE') || 
                            content.includes('Mock transaction') || 
                            content.includes('Payment successful') ||
                            content.includes('Payment warning')
    
    if (isPaymentMessage) {
      const type = content.includes('✅') ? 'success' : 
                   content.includes('⚠️') ? 'warning' : 'info'
      showToast(content, type)
      return
    }
    
    // Only add non-payment system messages to chat
    const systemMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'system',
      content,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, systemMessage])
  }

  const handleWalletPayment = async (selectedAmount: number) => {
    if (!connected || !publicKey || !signTransaction) {
      setError('Please connect your wallet first')
      return
    }

    setIsProcessingPayment(true)
    setError(null)
    setShowPaymentModal(false) // Close the modal

    try {
      // Use the selected amount from the modal
      const currentCost = selectedAmount

      console.log(`Initiating payment: $${currentCost.toFixed(2)} USDC`)

      // Step 1: Create payment transaction via backend
      const createResponse = await fetch(`${getBackendUrl()}/api/payment/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: publicKey.toString(),
          amount_usd: currentCost,
          payment_method: 'wallet'
        })
      })

      if (!createResponse.ok) {
        const errorData = await createResponse.json().catch(() => ({}))
        throw new Error(errorData.error || 'Failed to create payment transaction')
      }

      const paymentData = await createResponse.json()
      console.log('Payment transaction created:', paymentData)

      if (!paymentData.success || !paymentData.transaction) {
        throw new Error(paymentData.error || 'Invalid payment response')
      }

      // Show warning if present (but still proceed)
      if (paymentData.warning) {
        console.warn('⚠️ Payment warning:', paymentData.warning)
        addSystemMessage(`⚠️ ${paymentData.warning}`)
      }

      const txData = paymentData.transaction
      let signature: string

      // Check if this is a mock payment (test mode)
      if (paymentData.is_mock) {
        console.log('🧪 MOCK PAYMENT MODE - Simulating transaction')
        addSystemMessage('🧪 TEST MODE: Simulating payment (no real funds will be charged)')
        
        // Simulate a delay like a real transaction
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Generate a mock signature
        signature = `MOCK_${Date.now()}_${Math.random().toString(36).substring(7)}`
        console.log('Mock transaction "sent":', signature)
        addSystemMessage(`✅ Mock transaction complete: ${signature.slice(0, 20)}...`)
        
      } else {
        // Real blockchain transaction (production)
        console.log('💰 REAL PAYMENT MODE - Processing actual blockchain transaction')
        
        // Step 2: Build USDC SPL token transfer transaction
        const fromPubkey = new PublicKey(publicKey.toString())
        const toPubkey = new PublicKey(txData.recipient)
        const mintPubkey = new PublicKey(txData.mint)

        // Get associated token addresses
        const fromAta = new PublicKey(txData.from_ata)
        const toAta = new PublicKey(txData.to_ata)

        // Create transfer instruction
        const transferInstruction = createTransferInstruction(
          fromAta,
          toAta,
          fromPubkey,
          txData.units, // Amount in smallest units (6 decimals for USDC)
          [],
          TOKEN_PROGRAM_ID
        )

        // Build transaction
        const transaction = new Transaction().add(transferInstruction)
        transaction.feePayer = fromPubkey
        transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash

        // Step 3: Sign transaction
        console.log('Requesting wallet signature...')
        const signedTransaction = await signTransaction(transaction)

        // Step 4: Send transaction
        console.log('Sending transaction...')
        signature = await connection.sendRawTransaction(signedTransaction.serialize())

        console.log('Transaction sent:', signature)
        addSystemMessage(`Transaction sent: ${signature.slice(0, 8)}...`)

        // Step 5: Confirm transaction
        console.log('Confirming transaction...')
        await connection.confirmTransaction(signature, 'confirmed')
      }

      // Step 6: Verify with backend
      const verifyResponse = await fetch(`${getBackendUrl()}/api/payment/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tx_signature: signature,
          wallet_address: publicKey.toString(),
          payment_method: 'wallet',
          amount_usd: currentCost,
          bounty_id: bountyId  // Pass bounty_id for per-bounty pool tracking
        })
      })

      if (!verifyResponse.ok) {
        throw new Error('Failed to verify payment with backend')
      }

      const verifyData = await verifyResponse.json()
      console.log('Payment verified:', verifyData)

      if (verifyData.success) {
        const grantedQuestions = typeof verifyData.questions_granted === 'number'
          ? verifyData.questions_granted
          : 0
        const creditRemainder = typeof verifyData.credit_remainder === 'number'
          ? verifyData.credit_remainder
          : 0
        const perQuestionCostRaw = verifyData.question_cost_usd
        const perQuestionCost = typeof perQuestionCostRaw === 'number'
          ? perQuestionCostRaw
          : perQuestionCostRaw !== undefined
            ? Number(perQuestionCostRaw)
            : undefined
        const hasValidCost = typeof perQuestionCost === 'number' && Number.isFinite(perQuestionCost)

        // Refresh user eligibility and bounty status so UI stays aligned with backend state
        await checkUserEligibility()
        await fetchBountyStatus()

        const hasUnlockedQuestions = grantedQuestions > 0
        const eligibilityMessage = hasUnlockedQuestions
          ? `You have ${grantedQuestions} ${grantedQuestions === 1 ? 'question' : 'questions'} remaining.`
          : creditRemainder > 0
            ? `Payment received! You have $${creditRemainder.toFixed(2)} credit toward your next question.`
            : 'Payment received.'

        setUserEligibility({
          eligible: hasUnlockedQuestions,
          type: hasUnlockedQuestions ? 'free_questions' : 'payment_required',
          message: eligibilityMessage,
          questions_remaining: grantedQuestions,
          questions_used: 0,
          is_paid: hasUnlockedQuestions,
          credit_balance: creditRemainder
        })

        setIsParticipating(hasUnlockedQuestions)

        if (hasUnlockedQuestions) {
          const costSuffix = hasValidCost
            ? ` Current price per question: $${perQuestionCost!.toFixed(2)}.`
            : ''
          addSystemMessage(`✅ Payment successful! ${grantedQuestions} ${grantedQuestions === 1 ? 'question' : 'questions'} unlocked.${costSuffix}`)
        } else if (creditRemainder > 0) {
          const remainingToUnlock = hasValidCost
            ? Math.max(perQuestionCost! - creditRemainder, 0)
            : 0
          const warningMessage = remainingToUnlock > 0
            ? `⚠️ Payment warning: Add $${remainingToUnlock.toFixed(2)} more to unlock your next question.`
            : '⚠️ Payment warning: Credit stored, but no questions unlocked yet.'
          addSystemMessage(warningMessage)
        } else {
          addSystemMessage('✅ Payment successful! Payment verified with no questions unlocked.')
        }
      } else {
        throw new Error(verifyData.error || 'Payment verification failed')
      }

    } catch (err: any) {
      console.error('Payment error:', err)
      
      // Provide helpful message for common errors
      let errorMessage = err.message || 'Payment failed. Please try again.'
      if (errorMessage.includes('403') || errorMessage.includes('forbidden') || errorMessage.includes('recent blockhash')) {
        errorMessage = '⚠️ RPC endpoint issue detected. Please restart your backend server to enable mock payment mode, or get a proper RPC endpoint.'
      }
      
      setError(errorMessage)
      addSystemMessage(`❌ Payment failed: ${errorMessage}`)
      showToast(errorMessage, 'error')
    } finally {
      setIsProcessingPayment(false)
    }
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

      if (showReferralFlow) {
        return (
          <div className="h-96 bg-white border border-slate-200 rounded-xl shadow-2xl shadow-slate-900/10 p-6">
        <ReferralFlow
          onSuccess={async (referralCode) => {
            console.log('🎉 Referral Success - Starting unlock sequence')
            console.log('🎉 BEFORE - isParticipating:', isParticipating)
            console.log('🎉 BEFORE - userEligibility:', userEligibility)
            
            setShowReferralFlow(false)
            showToast(`🎉 Your referral code is: ${referralCode}`, 'success')
            
            // Track activity if enabled
            if (isActivityTrackerEnabled && username) {
              addActivity(bountyId, username, 'referral', bountyName)
            }
            
            // Force refresh the eligibility state (same as NFT flow)
            const eligibility = await fetch(`${getBackendUrl()}/api/free-questions/${publicKey?.toString()}`)
            if (eligibility.ok) {
              const data = await eligibility.json()
              console.log('🎉 Referral eligibility data:', data)
              
              const newEligibility = {
                eligible: data.questions_remaining > 0,
                message: `You have ${data.questions_remaining} free questions remaining.`,
                questions_remaining: data.questions_remaining,
                questions_used: data.questions_used || 0,
                referral_code: referralCode,
                type: 'free_questions' as const,
                is_paid: data.is_paid || false  // Use API value, default to false if not provided
              }
              console.log('🎉 Setting new eligibility:', newEligibility)
              setUserEligibility(newEligibility)
              
              // Only set participating if user has questions (same logic as NFT flow)
              if (newEligibility.eligible) {
              console.log('🎉 Setting isParticipating to TRUE')
              setIsParticipating(true)
              
              // Log the condition that controls chat input visibility
              console.log('🎉 AFTER STATE UPDATE:')
              console.log('  - isParticipating will be:', true)
              console.log('  - userEligibility.eligible will be:', newEligibility.eligible)
              console.log('  - Condition (isParticipating && userEligibility?.eligible) will be:', true && newEligibility.eligible)
              } else {
                console.log('⚠️ User has no questions remaining - keeping isParticipating as false')
              }
            } else {
              console.error('❌ Failed to fetch eligibility:', eligibility.status)
            }
            
            console.log('✅ Referral: Unlock sequence complete')
          }}
          onCancel={() => setShowReferralFlow(false)}
        />
          </div>
        )
      }

  return (
    <>
      {/* Toast Notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      
      <div className="flex flex-col h-full bg-white border border-slate-200 rounded-xl shadow-2xl shadow-slate-900/10">
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
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-3xl font-bold text-yellow-600">
                  ${(bountyStatus.current_pool || 0).toLocaleString()}
                </div>
                <div className="text-xs text-slate-500">Prize Pool</div>
              </div>
              <div className={cn(
                "px-3 py-1 rounded-full border text-sm font-medium flex items-center space-x-1",
                getDifficultyColor(bountyStatus.difficulty_level)
              )}>
                {getDifficultyIcon(bountyStatus.difficulty_level)}
                <span className="capitalize">{bountyStatus.difficulty_level}</span>
              </div>
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
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3">
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
          <DynamicWalletButton />
        </div>
      ) : isParticipating && userEligibility?.eligible ? (
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <form 
            onSubmit={(e) => { 
              e.preventDefault(); 
              e.stopPropagation();
              sendMessage(); 
            }} 
            className="flex space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Try to convince the AI to transfer funds..."
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent bg-white placeholder:text-slate-400"
              style={{ color: '#000000' }}
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
            {userEligibility?.eligible ? 'Ready to participate!' : 'No questions remaining'}
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <button
              onClick={() => {
                handleActionWithUsernameCheck(() => {
                  if (userEligibility?.eligible) {
                    setIsParticipating(true)
                  } else {
                    setShowPaymentModal(true)
                  }
                })
              }}
              disabled={isProcessingPayment}
              className="flex-1 min-w-[200px] px-6 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isProcessingPayment ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : userEligibility?.eligible ? 'Start Participating' : 'Try Your Luck'}
            </button>
            
            {!userEligibility?.eligible && (
              <>
                <button
                  onClick={() => handleActionWithUsernameCheck(() => setShowNftFlow(true))}
                  className="flex-1 min-w-[200px] px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 font-medium"
                >
                  Solana Seekers
                </button>
                <button
                  onClick={() => handleActionWithUsernameCheck(() => setShowReferralFlow(true))}
                  className="flex-1 min-w-[200px] px-6 py-2 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg hover:from-green-500 hover:to-blue-600 font-medium"
                >
                  Refer Someone for 5 Free Questions
                </button>
              </>
            )}
          </div>
        </div>
      )}
      
      {/* Payment Amount Modal */}
      {showPaymentModal && bountyStatus && (
        <PaymentAmountModal
          onClose={() => setShowPaymentModal(false)}
          onSelectAmount={handleWalletPayment}
          isProcessing={isProcessingPayment}
          currentQuestionCost={getCurrentQuestionCost(
            getStartingQuestionCost(bountyStatus.difficulty_level || 'easy'),
            bountyStatus.total_entries || 0
          )}
        />
      )}

      {/* NFT Verification Modal */}
      {showNftFlow && (
        <NftVerification
          onClose={() => setShowNftFlow(false)}
          onVerificationSuccess={async () => {
            console.log('🎨 NFT Verification Success - Starting unlock sequence')
            console.log('🎨 BEFORE - isParticipating:', isParticipating)
            console.log('🎨 BEFORE - userEligibility:', userEligibility)
            
            setShowNftFlow(false)
            showToast('✅ NFT verified! 5 free questions granted', 'success')
            
            // Track activity if enabled
            if (isActivityTrackerEnabled && username) {
              addActivity(bountyId, username, 'nft_redeem', bountyName)
            }
            
            // Force refresh the eligibility state
            const eligibility = await fetch(`${getBackendUrl()}/api/free-questions/${publicKey?.toString()}`)
            if (eligibility.ok) {
              const data = await eligibility.json()
              console.log('🎨 NFT eligibility data:', data)
              
              const newEligibility = {
                eligible: data.remaining > 0,
                message: `You have ${data.remaining} free questions remaining.`,
                questions_remaining: data.remaining,
                questions_used: 0,
                type: 'free_questions' as const,
                is_paid: data.is_paid || false  // Use API value, default to false if not provided
              }
              console.log('🎨 Setting new eligibility:', newEligibility)
              setUserEligibility(newEligibility)
              
              console.log('🎨 Setting isParticipating to TRUE')
              setIsParticipating(true)
              
              // Log the condition that controls chat input visibility
              console.log('🎨 AFTER STATE UPDATE:')
              console.log('  - isParticipating will be:', true)
              console.log('  - userEligibility.eligible will be:', newEligibility.eligible)
              console.log('  - Condition (isParticipating && userEligibility?.eligible) will be:', true && newEligibility.eligible)
            } else {
              console.error('❌ Failed to fetch eligibility:', eligibility.status)
            }
            
            console.log('✅ NFT: Unlock sequence complete')
          }}
        />
      )}

      {/* Username Prompt Modal */}
      {showUsernamePrompt && isActivityTrackerEnabled && (
        <UsernamePrompt
          onSuccess={handleUsernameSuccess}
          onCancel={() => {
            setShowUsernamePrompt(false)
            setPendingAction(null)
          }}
        />
      )}
      </div>
    </>
  )
}
