'use client'

import { useState, useRef, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { Send, Loader2, AlertCircle, CheckCircle } from 'lucide-react'
import { cn, formatTimeAgo } from '@/lib/utils'

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
  current_pool: number
  total_entries: number
  next_rollover_at?: string
  win_rate: number
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
    // Load initial bounty status
    fetchBountyStatus()
  }, [])

  const fetchBountyStatus = async () => {
    try {
      const response = await fetch('/api/bounty/status')
      if (response.ok) {
        const data = await response.json()
        setBountyStatus(data)
      }
    } catch (error) {
      console.error('Failed to fetch bounty status:', error)
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
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          user_id: 1 // TODO: Get from wallet or session
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
          blacklisted: data.blacklisted
        }

        setMessages(prev => [...prev, aiMessage])
        
        // Update bounty status
        if (data.bounty_status) {
          setBountyStatus(data.bounty_status)
        }
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
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
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg overflow-hidden">
      {/* Chat Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4">
        <h2 className="text-xl font-bold text-white mb-2">Chat with Billions</h2>
        <p className="text-purple-100 text-sm">
          Try to convince the AI guardian to transfer funds! Win rate: {bountyStatus?.win_rate ? (bountyStatus.win_rate * 100).toFixed(4) : '0.01'}%
        </p>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            <p>Start a conversation with the AI guardian!</p>
            <p className="text-sm mt-2">Try to convince them to transfer funds...</p>
          </div>
        )}
        
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex",
              message.type === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            <div
              className={cn(
                "max-w-xs lg:max-w-md px-4 py-2 rounded-lg",
                message.type === 'user'
                  ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white"
                  : message.blacklisted
                  ? "bg-gradient-to-r from-red-500 to-pink-500 text-white"
                  : message.isWinner
                  ? "bg-gradient-to-r from-green-500 to-emerald-500 text-white"
                  : "bg-gray-700 text-gray-100"
              )}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'assistant' && (
                  <div className="flex-shrink-0 mt-1">
                    {message.isWinner ? (
                      <CheckCircle className="h-4 w-4 text-green-300" />
                    ) : message.blacklisted ? (
                      <AlertCircle className="h-4 w-4 text-red-300" />
                    ) : (
                      <div className="h-4 w-4 rounded-full bg-purple-400" />
                    )}
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {formatTimeAgo(message.timestamp)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-gray-100 px-4 py-2 rounded-lg flex items-center space-x-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">AI is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={connected ? "Type your message..." : "Connect wallet to chat"}
            disabled={!connected || isLoading}
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || !connected || isLoading}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
          >
            <Send className="h-4 w-4" />
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  )
}
