'use client'

import { useState, useEffect, useRef } from 'react'

interface Activity {
  id: string
  username: string
  message: string
  timestamp: number
  bounty_id: number
}

interface ActivityTrackerProps {
  bountyId: number
}

const ACTIVITY_STORAGE_KEY = 'bounty_activities'
const ACTIVITY_CYCLE_DURATION = 4000 // 4 seconds per activity
const ACTIVITY_MAX_AGE = 24 * 60 * 60 * 1000 // 24 hours in milliseconds

export default function ActivityTracker({ bountyId }: ActivityTrackerProps) {
  const [currentActivityIndex, setCurrentActivityIndex] = useState(0)
  const [activities, setActivities] = useState<Activity[]>([])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Get activities from localStorage filtered by bounty and last 24hrs
  const getActivities = (): Activity[] => {
    if (typeof window === 'undefined') return []

    try {
      const stored = localStorage.getItem(ACTIVITY_STORAGE_KEY)
      if (!stored) return []

      const allActivities: Activity[] = JSON.parse(stored)
      const now = Date.now()
      
      // Filter: same bounty_id and within last 24 hours
      return allActivities.filter(
        (activity) =>
          activity.bounty_id === bountyId &&
          now - activity.timestamp < ACTIVITY_MAX_AGE
      )
    } catch (error) {
      console.error('Error reading activities from localStorage:', error)
      return []
    }
  }

  // Load activities and set up auto-refresh
  useEffect(() => {
    const loadActivities = () => {
      const filtered = getActivities()
      setActivities((prev) => {
        // Only update if activities actually changed to avoid unnecessary re-renders
        const prevJson = JSON.stringify(prev)
        const filteredJson = JSON.stringify(filtered)
        if (prevJson === filteredJson) {
          return prev // No change
        }
        return filtered
      })
      
      // Reset index if current index is out of bounds
      setCurrentActivityIndex((prevIndex) => {
        if (filtered.length > 0 && prevIndex >= filtered.length) {
          return 0
        }
        return prevIndex
      })
    }

    // Initial load
    loadActivities()

    // Refresh every 3 seconds to pick up new activities
    const refreshInterval = setInterval(loadActivities, 3000)

    return () => clearInterval(refreshInterval)
  }, [bountyId])

  // Auto-cycle through activities
  useEffect(() => {
    if (activities.length === 0) return

    intervalRef.current = setInterval(() => {
      setCurrentActivityIndex((prev) => (prev + 1) % activities.length)
    }, ACTIVITY_CYCLE_DURATION)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [activities.length])

  if (activities.length === 0) {
    return null
  }

  const currentActivity = activities[currentActivityIndex]

  if (!currentActivity) {
    return null
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <div
        className="bg-green-50 border border-green-200 rounded-lg px-3 py-2 text-xs text-green-800 animate-fade-in"
        style={{
          animation: 'fadeIn 0.5s ease-in-out'
        }}
      >
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="font-medium">{currentActivity.username}</span>
          <span className="text-green-700">{currentActivity.message}</span>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}

// Helper function to add activity to localStorage (called from other components)
export function addActivity(
  bountyId: number,
  username: string,
  activityType: 'question' | 'nft_redeem' | 'referral' | 'first_question',
  bountyName?: string
): void {
  if (typeof window === 'undefined') return

  try {
    const messages: Record<string, string> = {
      question: `just asked ${bountyName || 'a question'}`,
      nft_redeem: 'redeemed their NFT',
      referral: 'referred a new friend',
      first_question: `just asked their first question`
    }

    const activity: Activity = {
      id: `${Date.now()}-${Math.random()}`,
      username,
      message: messages[activityType],
      timestamp: Date.now(),
      bounty_id: bountyId
    }

    const stored = localStorage.getItem(ACTIVITY_STORAGE_KEY)
    const allActivities: Activity[] = stored ? JSON.parse(stored) : []
    
    // Add new activity at the beginning
    allActivities.unshift(activity)
    
    // Keep only last 100 activities to prevent localStorage bloat
    const trimmed = allActivities.slice(0, 100)
    
    localStorage.setItem(ACTIVITY_STORAGE_KEY, JSON.stringify(trimmed))
  } catch (error) {
    console.error('Error saving activity to localStorage:', error)
  }
}

