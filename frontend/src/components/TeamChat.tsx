'use client'

/**
 * Team Chat Component
 * 
 * Real-time team messaging for strategy collaboration
 */

import { useState, useEffect, useRef } from 'react'
import { teamAPI } from '@/lib/api/enhancements'

interface Message {
  id: number
  user_id: number
  display_name: string
  content: string
  message_type: string
  created_at: string
}

interface TeamChatProps {
  teamId: number
  userId: number
  currentUserName?: string
}

export default function TeamChat({ teamId, userId, currentUserName = 'You' }: TeamChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchMessages()
    // Poll for new messages every 3 seconds
    const interval = setInterval(fetchMessages, 3000)
    return () => clearInterval(interval)
  }, [teamId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchMessages = async () => {
    try {
      const data = await teamAPI.getMessages(teamId, userId, 50) as any
      setMessages(data.messages || [])
      setLoading(false)
    } catch (err) {
      console.error('Failed to fetch messages:', err)
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    setSending(true)
    try {
      await teamAPI.sendMessage(teamId, userId, newMessage.trim())
      setNewMessage('')
      await fetchMessages() // Refresh to show new message
    } catch (err: any) {
      alert(`Failed to send message: ${err.message}`)
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'strategy':
        return 'bg-purple-900/30 border-purple-500/30'
      case 'system':
        return 'bg-gray-700/30 border-gray-500/30'
      case 'attempt_result':
        return 'bg-yellow-900/30 border-yellow-500/30'
      default:
        return 'bg-gray-700/30 border-gray-600'
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white">Team Chat</h3>
          <p className="text-sm text-gray-400">
            {messages.length} messages • Updates every 3s
          </p>
        </div>
        <button
          onClick={fetchMessages}
          className="text-blue-400 hover:text-blue-300 text-sm"
        >
          🔄 Refresh
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400">Loading messages...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <div className="text-4xl mb-2">💬</div>
              <p className="text-gray-400">No messages yet</p>
              <p className="text-sm text-gray-500">Be the first to say hello!</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.user_id === userId ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-3 border ${
                  message.user_id === userId
                    ? 'bg-blue-600 text-white border-blue-500'
                    : getMessageTypeColor(message.message_type)
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold opacity-90">
                    {message.user_id === userId ? currentUserName : message.display_name}
                  </span>
                  {message.message_type === 'strategy' && (
                    <span className="px-2 py-0.5 bg-purple-500/30 rounded text-xs">
                      Strategy
                    </span>
                  )}
                </div>
                <div className={message.user_id === userId ? 'text-white' : 'text-gray-200'}>
                  {message.content}
                </div>
                <div className={`text-xs mt-1 ${message.user_id === userId ? 'text-blue-200' : 'text-gray-500'}`}>
                  {new Date(message.created_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message... (Press Enter to send)"
            className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500 focus:outline-none"
            disabled={sending}
          />
          <button
            onClick={sendMessage}
            disabled={sending || !newMessage.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            {sending ? '⏳' : '📤'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 Tip: Share strategies, coordinate attempts, and plan together
        </p>
      </div>
    </div>
  )
}

