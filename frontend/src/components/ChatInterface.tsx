'use client'

import { useState, useRef, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Send, Loader2, AlertCircle, CheckCircle, Bot, User as UserIcon, Info } from 'lucide-react'
import { cn, formatTimeAgoSafe } from '@/lib/utils'
import Button from './ui/Button'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  isWinner?: boolean
  blacklisted?: boolean
}

interface bountyResult {
  entry_id: number
  is_winner: boolean
  prize_payout?: number
  cost: number
  pool_contribution: number
}

interface BountyStatus {
  success: boolean
  program_id: string
  current_jackpot: number
  total_entries: number
  is_active: boolean
  research_fund_floor: number
  research_fee: number
  last_rollover: string
  next_rollover: string
}

export default function ChatInterface() {
  const { connected } = useWallet()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [bountyStatus, setBountyStatus] = useState<BountyStatus | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    console.log('🚀 ChatInterface mounted - debugging system active')
    
    // Simple test first
    const testConnection = async () => {
      console.log('🧪 Testing connection to backend...')
      try {
        const response = await fetch('http://localhost:8000/', { mode: 'no-cors' })
        console.log('✅ Connection test passed:', response)
      } catch (error) {
        console.error('❌ Connection test failed:', error)
      }
    }
    
    testConnection()
    
    // Load initial bounty status
    setTimeout(() => {
      fetchBountyStatus()
    }, 1000)
  }, [])


  const fetchBountyStatus = async () => {
    const startTime = performance.now()
    const requestId = Math.random().toString(36).substr(2, 9)
    
    console.group(`🔍 [${requestId}] Starting fetchBountyStatus`)
    console.log('📍 URL:', 'http://localhost:8000/api/lottery/status')
    console.log('⏰ Timestamp:', new Date().toISOString())
    console.log('🌐 User Agent:', navigator.userAgent)
    console.log('🔗 Current URL:', window.location.href)
    console.log('🔒 Protocol:', window.location.protocol)
    console.log('🏠 Host:', window.location.host)
    
    try {
      // Test basic connectivity first
      console.log('🧪 Testing basic connectivity...')
      const testResponse = await fetch('http://localhost:8000/', {
        method: 'HEAD',
        mode: 'no-cors'
      })
      console.log('✅ Basic connectivity test passed')
      
      // Now try the actual request
      console.log('🚀 Making actual request...')
      const response = await fetch('http://localhost:8000/api/lottery/status', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        cache: 'no-cache'
      })
      
      const endTime = performance.now()
      const duration = endTime - startTime
      
      console.log('📊 Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        type: response.type,
        url: response.url,
        redirected: response.redirected,
        duration: `${duration.toFixed(2)}ms`
      })
      
      console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()))
      
      if (response.ok) {
        const data = await response.json()
        console.log('✅ Success! Bounty data:', data)
        console.log('🔍 current_jackpot value:', data.current_jackpot)
        console.log('🔍 typeof current_jackpot:', typeof data.current_jackpot)
        setBountyStatus(data)
      } else {
        console.error('❌ Response not ok:', response.status, response.statusText)
        const errorText = await response.text()
        console.error('❌ Error response body:', errorText)
      }
    } catch (error) {
      const endTime = performance.now()
      const duration = endTime - startTime
      
      console.error('💥 Fetch failed:', {
        error: error,
        name: (error as Error).name,
        message: (error as Error).message,
        stack: (error as Error).stack,
        duration: `${duration.toFixed(2)}ms`
      })
      
      // Try to determine the specific cause
      if ((error as Error).name === 'TypeError' && (error as Error).message === 'Failed to fetch') {
        console.error('🔍 This is a network-level error. Possible causes:')
        console.error('  1. Backend server is not running')
        console.error('  2. CORS policy is blocking the request')
        console.error('  3. Network connectivity issue')
        console.error('  4. Firewall blocking the connection')
        console.error('  5. Browser security policy blocking the request')
        
        // Test if we can reach the backend at all
        try {
          console.log('🧪 Testing with a simple fetch...')
          const simpleTest = await fetch('http://localhost:8000', { mode: 'no-cors' })
          console.log('✅ Simple fetch succeeded:', simpleTest)
        } catch (simpleError) {
          console.error('❌ Even simple fetch failed:', simpleError)
        }
      }
    } finally {
      console.groupEnd()
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || !connected || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      console.log('🔍 Sending message to http://localhost:8000/api/chat')
      console.log('🔍 Current time:', new Date().toISOString())
      
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({
          message: userMessage.content,
          user_id: 1 // TODO: Get from wallet or session
        })
      })
      
      console.log('🔍 Chat response received:', response.status, response.ok)
      console.log('🔍 Response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const data = await response.json()
        
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date(),
          isWinner: data.winner_result?.is_winner,
          blacklisted: data.blacklisted
        }

        setMessages(prev => [...prev, aiMessage])
        
        // Update bounty status
        if (data.bounty_status) {
          setBountyStatus(data.bounty_status)
        }
      } else {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to send message`)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: error instanceof Error 
          ? `I encountered an error: ${error.message}. Please try again.`
          : 'Sorry, I encountered an unexpected error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] lg:h-[calc(100vh-4rem)] max-w-4xl mx-auto">
      {/* Messages Area - Scrollable */}
      <div className="flex-1 overflow-y-auto px-4 lg:px-6 py-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center mb-4">
              <Bot className="h-8 w-8 text-white" />
            </div>
            <h3 className="text-slate-50 text-xl font-semibold mb-2">
              Start a conversation
            </h3>
            <p className="text-slate-400 text-sm max-w-md">
              Try to convince the AI guardian to transfer funds. Each attempt costs $10.
            </p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-3 animate-fade-in",
              message.type === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.type === 'assistant' && (
              <div className="flex-shrink-0 mt-1">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center",
                  message.isWinner ? 'bg-emerald-600' : message.blacklisted ? 'bg-red-600' : 'bg-slate-700'
                )}>
                  {message.isWinner ? (
                    <CheckCircle className="h-4 w-4 text-white" />
                  ) : message.blacklisted ? (
                    <AlertCircle className="h-4 w-4 text-white" />
                  ) : (
                    <Bot className="h-4 w-4 text-slate-300" />
                  )}
                </div>
              </div>
            )}
            
            <div className={cn(
              "max-w-[75%] lg:max-w-[680px]",
              message.type === 'user' && 'order-first'
            )}>
              <div
                className={cn(
                  "px-4 py-3",
                  message.type === 'user'
                    ? "bg-blue-600 text-white rounded-[18px] rounded-tr-[4px]"
                    : message.isWinner
                    ? "bg-emerald-600 text-white rounded-[18px] rounded-tl-[4px]"
                    : message.blacklisted
                    ? "bg-red-600 text-white rounded-[18px] rounded-tl-[4px]"
                    : "bg-slate-700 text-slate-50 rounded-[18px] rounded-tl-[4px]"
                )}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {message.content}
                </p>
              </div>
              <p className={cn(
                "text-xs text-slate-500 mt-1 px-1",
                message.type === 'user' ? 'text-right' : 'text-left'
              )}>
                        {formatTimeAgoSafe(message.timestamp)}
              </p>
            </div>
            
            {message.type === 'user' && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <UserIcon className="h-4 w-4 text-white" />
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="flex-shrink-0 mt-1">
              <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
                <Bot className="h-4 w-4 text-slate-300" />
              </div>
            </div>
            <div className="bg-slate-700 rounded-[18px] rounded-tl-[4px] px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse-dot" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse-dot" style={{ animationDelay: '200ms' }}></div>
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse-dot" style={{ animationDelay: '400ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Fixed Bottom */}
      <div className="border-t border-slate-700 bg-slate-900/95 backdrop-blur-sm">
        <div className="px-4 lg:px-6 py-4">
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  sendMessage()
                }
              }}
              placeholder={connected ? "Type your message..." : "Connect wallet to chat"}
              disabled={!connected || isLoading}
              rows={1}
              className="flex-1 bg-slate-800 text-slate-50 placeholder-slate-400 px-4 py-3 rounded-lg border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 resize-none max-h-32"
              style={{ minHeight: '48px' }}
            />
            <Button
              onClick={fetchBountyStatus}
              variant="secondary"
              size="lg"
              className="px-4 h-12 bg-slate-700 text-slate-300 hover:bg-slate-600"
            >
              Debug
            </Button>
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || !connected || isLoading}
              loading={isLoading}
              size="lg"
              className="px-4 h-12"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex items-center justify-between mt-2 px-1">
            <p className="text-xs text-slate-500">
              Cost: <span className="text-slate-400 font-medium">$10 per message</span>
            </p>
            {bountyStatus && (
              <p className="text-xs text-slate-500">
                Pool: <span className="text-blue-400 font-medium">
                  ${bountyStatus.current_jackpot ? bountyStatus.current_jackpot.toFixed(2) : 'Loading...'}
                </span>
              </p>
            )}
            {!bountyStatus && (
              <p className="text-xs text-slate-500">
                Pool: <span className="text-slate-400">Loading...</span>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
