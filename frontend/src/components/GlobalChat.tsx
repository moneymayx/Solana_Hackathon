'use client'

import { useState, useEffect, useRef } from 'react'
import { Send, Users, MessageCircle, Trophy, Clock } from 'lucide-react'
import { getBackendUrl } from '@/lib/api/client'

interface Message {
  id: number
  user_id: number
  message_type: 'user' | 'assistant'
  content: string
  timestamp: string
  is_winner: boolean
  cost?: number
  model_used?: string
}

interface GlobalChatProps {
  bountyId: number
  bountyName: string
  onSendMessage?: (message: string) => void
  isWatching?: boolean
}

export default function GlobalChat({ 
  bountyId, 
  bountyName, 
  onSendMessage, 
  isWatching = false 
}: GlobalChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const hasScrolledRef = useRef(false)
  const previousMessagesLengthRef = useRef(0)

  // Auto-scroll to bottom only when NEW messages arrive (not on initial load)
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
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

  // Fetch messages for this bounty
  const fetchMessages = async () => {
    try {
      const response = await fetch(`${getBackendUrl()}/api/bounty/${bountyId}/messages/public?limit=50`)
      const data = await response.json()
      
      if (data.success) {
        setMessages(data.messages.reverse()) // Reverse to show oldest first
      } else {
        setError('Failed to load messages')
      }
    } catch (err) {
      setError('Failed to connect to chat')
    }
  }

  // Load messages on component mount
  useEffect(() => {
    fetchMessages()
    
    // Set up polling for new messages every 3 seconds
    const interval = setInterval(fetchMessages, 3000)
    return () => clearInterval(interval)
  }, [bountyId])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newMessage.trim() || isLoading) return

    // Mark that user has interacted - enable auto-scroll
    hasScrolledRef.current = true

    const messageText = newMessage.trim()
    setNewMessage('')
    setIsLoading(true)

    try {
      // Call parent component's send message handler
      if (onSendMessage) {
        onSendMessage(messageText)
      }
      
      // Refresh messages after sending
      setTimeout(fetchMessages, 1000)
    } catch (err) {
      setError('Failed to send message')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getMessageStyle = (message: Message) => {
    if (message.is_winner) {
      return 'bg-gradient-to-r from-yellow-100 to-orange-100 border-yellow-300 border-2'
    }
    
    if (message.message_type === 'assistant') {
      return 'bg-slate-100 border-slate-200'
    }
    
    return 'bg-blue-50 border-blue-200'
  }

  return (
    <div className="flex flex-col h-full bg-white border border-slate-200 rounded-xl shadow-2xl shadow-slate-900/10">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100">
        <div className="flex items-center space-x-3">
          <MessageCircle className="h-6 w-6 text-slate-600" />
          <div>
            <h3 className="font-semibold text-slate-900">{bountyName} Chat</h3>
            <p className="text-sm text-slate-600">Watch others challenge this AI</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-sm text-slate-600">
          <Users className="h-4 w-4" />
          <span>Live</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {error && (
          <div className="text-center text-red-600 text-sm py-4">
            {error}
          </div>
        )}
        
        {messages.length === 0 && !error && (
          <div className="text-center text-slate-500 py-8">
            <MessageCircle className="h-12 w-12 mx-auto mb-3 text-slate-300" />
            <p>No messages yet. Be the first to challenge this AI!</p>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`p-3 rounded-lg border ${getMessageStyle(message)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-slate-700">
                  {message.message_type === 'user' ? 'User' : 'AI'}
                </span>
                {message.is_winner && (
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
                Cost: ${message.cost.toFixed(4)} | Model: {message.model_used}
              </div>
            )}
          </div>
        ))}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!isWatching && (
        <div className="p-4 border-t border-slate-200 bg-slate-50">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Ask a question to challenge this AI..."
              className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent bg-white placeholder:text-slate-400"
              style={{ color: '#000000' }}
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!newMessage.trim() || isLoading}
              className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>{isLoading ? 'Sending...' : 'Send'}</span>
            </button>
          </form>
        </div>
      )}

      {isWatching && (
        <div className="p-4 border-t border-slate-200 bg-slate-50 text-center">
          <p className="text-sm text-slate-600">
            You're watching this chat. Click "Beat the Bot" to participate!
          </p>
        </div>
      )}
    </div>
  )
}
