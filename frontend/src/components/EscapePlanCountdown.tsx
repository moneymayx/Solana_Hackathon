'use client'

import { useState, useEffect } from 'react'
import { Clock, User, AlertTriangle } from 'lucide-react'

interface EscapePlanData {
  is_active: boolean
  time_since_last_question?: string
  time_until_escape?: string
  message: string
  should_trigger?: boolean
  last_participant_id?: number
  last_question_at?: string
}

interface UserData {
  id: number
  display_name?: string
  wallet_address?: string
}

export default function EscapePlanCountdown() {
  const [escapePlanData, setEscapePlanData] = useState<EscapePlanData | null>(null)
  const [lastParticipant, setLastParticipant] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEscapePlanData()
    const interval = setInterval(fetchEscapePlanData, 1000) // Update every second
    return () => clearInterval(interval)
  }, [])

  const fetchEscapePlanData = async () => {
    try {
      const response = await fetch('/api/bounty/escape-plan/status')
      if (response.ok) {
        const data = await response.json()
        setEscapePlanData(data.escape_plan)
        setLastParticipant(data.last_participant)
      }
    } catch (error) {
      console.error('Failed to fetch escape plan data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 mb-6">
        <div className="animate-pulse flex items-center space-x-3">
          <div className="w-6 h-6 bg-gray-600 rounded"></div>
          <div className="h-4 bg-gray-600 rounded w-48"></div>
        </div>
      </div>
    )
  }

  if (!escapePlanData || !escapePlanData.is_active) {
    return null
  }

  const getDisplayName = () => {
    if (!lastParticipant && !escapePlanData.last_participant_id) {
      return "No one yet"
    }
    if (lastParticipant?.display_name) {
      return lastParticipant.display_name
    }
    if (lastParticipant?.wallet_address) {
      return `${lastParticipant.wallet_address.slice(0, 6)}...${lastParticipant.wallet_address.slice(-4)}`
    }
    return `User #${escapePlanData.last_participant_id}`
  }

  return (
    <div className={`backdrop-blur-sm rounded-lg p-4 mb-6 ${
      escapePlanData.should_trigger 
        ? 'bg-red-500/20 border border-red-500/30' 
        : 'bg-orange-500/20 border border-orange-500/30'
    }`}>
      <div className="flex items-center space-x-3 mb-2">
        <Clock className={`h-5 w-5 ${
          escapePlanData.should_trigger ? 'text-red-400' : 'text-orange-400'
        }`} />
        <h3 className={`text-lg font-semibold ${
          escapePlanData.should_trigger ? 'text-red-400' : 'text-orange-400'
        }`}>
          {escapePlanData.should_trigger ? '🚨 ESCAPE PLAN READY!' : 'Escape Plan Timer'}
        </h3>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <User className="h-4 w-4 text-gray-400" />
          <span className="text-white">
            Last question by: <span className="font-semibold text-blue-400">{getDisplayName()}</span>
          </span>
        </div>
        
        {escapePlanData.time_since_last_question && (
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-gray-400" />
            <span className="text-white">
              Time since last question: <span className="font-semibold text-yellow-400">{escapePlanData.time_since_last_question}</span>
            </span>
          </div>
        )}
        
        {escapePlanData.time_until_escape && !escapePlanData.should_trigger && (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-4 w-4 text-gray-400" />
              <span className="text-white">
                Time until escape: <span className="font-semibold text-orange-400">{escapePlanData.time_until_escape}</span>
              </span>
            </div>
            {/* Progress bar showing time elapsed */}
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-orange-400 to-red-500 h-2 rounded-full transition-all duration-1000"
                style={{ 
                  width: escapePlanData.time_since_last_question 
                    ? `${Math.min(100, (parseFloat(escapePlanData.time_since_last_question.split('h')[0]) / 24) * 100)}%` 
                    : '0%' 
                }}
              ></div>
            </div>
          </div>
        )}
        
        <div className="mt-3 p-3 bg-gray-800/50 rounded-lg">
          <p className="text-sm text-gray-300">
            <strong>Escape Plan:</strong> If no questions are asked for 24 hours, 
            80% of the bounty will be distributed equally among all participants, 
            and 20% will go to <span className="font-semibold text-blue-400">{getDisplayName()}</span>.
          </p>
        </div>
      </div>
    </div>
  )
}
