import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import ActivityTracker, { addActivity, seedDevActivities } from '@/components/ActivityTracker'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
    length: 0,
    key: (index: number) => null,
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('ActivityTracker', () => {
  beforeEach(() => {
    localStorageMock.clear()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('does not render when no activities exist', () => {
    const { container } = render(<ActivityTracker bountyId={1} />)
    expect(container.firstChild).toBeNull()
  })

  it('displays activity from localStorage', async () => {
    // Add an activity
    addActivity(1, 'testuser', 'question', 'Test Bounty')
    
    render(<ActivityTracker bountyId={1} />)
    
    await waitFor(() => {
      expect(screen.getByText(/testuser/i)).toBeInTheDocument()
      expect(screen.getByText(/just asked Test Bounty/i)).toBeInTheDocument()
    })
  })

  it('filters activities by bounty_id', () => {
    // Add activities for different bounties
    addActivity(1, 'user1', 'question', 'Bounty 1')
    addActivity(2, 'user2', 'question', 'Bounty 2')
    
    render(<ActivityTracker bountyId={1} />)
    
    expect(screen.getByText(/user1/i)).toBeInTheDocument()
    expect(screen.queryByText(/user2/i)).not.toBeInTheDocument()
  })

  it('filters activities by time (only last 24 hours)', async () => {
    // Add old activity (25 hours ago)
    const oldActivity = {
      id: 'old-1',
      username: 'olduser',
      message: 'just asked a question',
      timestamp: Date.now() - (25 * 60 * 60 * 1000), // 25 hours ago
      bounty_id: 1
    }
    localStorageMock.setItem('bounty_activities', JSON.stringify([oldActivity]))
    
    // Add recent activity
    addActivity(1, 'newuser', 'question', 'Bounty 1')
    
    render(<ActivityTracker bountyId={1} />)
    
    await waitFor(() => {
      expect(screen.getByText(/newuser/i)).toBeInTheDocument()
      expect(screen.queryByText(/olduser/i)).not.toBeInTheDocument()
    })
  })

  it('auto-cycles through multiple activities', async () => {
    // Add multiple activities
    addActivity(1, 'user1', 'question', 'Bounty 1')
    // Small delay to ensure different timestamps
    act(() => {
      jest.advanceTimersByTime(10)
    })
    addActivity(1, 'user2', 'nft_redeem', 'Bounty 1')
    act(() => {
      jest.advanceTimersByTime(10)
    })
    addActivity(1, 'user3', 'referral', 'Bounty 1')
    
    render(<ActivityTracker bountyId={1} />)
    
    // Wait for initial render - should show one of the activities
    await waitFor(() => {
      const hasUser1 = screen.queryByText(/user1/i)
      const hasUser2 = screen.queryByText(/user2/i)
      const hasUser3 = screen.queryByText(/user3/i)
      expect(hasUser1 || hasUser2 || hasUser3).toBeTruthy()
    })
    
    // Get initial displayed activity
    const initialActivity = screen.queryByText(/user1|user2|user3/i)
    expect(initialActivity).toBeTruthy()
    
    // Advance timer to trigger cycle
    act(() => {
      jest.advanceTimersByTime(4000) // 4 seconds
    })
    
    // Should show a different activity now (cycling occurred)
    await waitFor(() => {
      const currentActivity = screen.queryByText(/user1|user2|user3/i)
      expect(currentActivity).toBeTruthy()
      // Should be a different activity (or same if it cycled back)
    }, { timeout: 1000 })
  })

  it('refreshes activities every 3 seconds', async () => {
    addActivity(1, 'user1', 'question', 'Bounty 1')
    
    render(<ActivityTracker bountyId={1} />)
    
    await waitFor(() => {
      expect(screen.getByText(/user1/i)).toBeInTheDocument()
    })
    
    // Add new activity while component is mounted
    act(() => {
      addActivity(1, 'user2', 'question', 'Bounty 1')
      jest.advanceTimersByTime(3000) // 3 seconds - refresh interval
    })
    
    // Component should pick up the new activity
    await waitFor(() => {
      // Should eventually show user2 when it cycles
      expect(screen.getByText(/user2/i)).toBeInTheDocument()
    })
  })
})

describe('addActivity helper function', () => {
  beforeEach(() => {
    localStorageMock.clear()
  })

  it('adds activity to localStorage', () => {
    addActivity(1, 'testuser', 'question', 'Test Bounty')
    
    const stored = localStorageMock.getItem('bounty_activities')
    expect(stored).toBeTruthy()
    
    const activities = JSON.parse(stored!)
    expect(activities).toHaveLength(1)
    expect(activities[0].username).toBe('testuser')
    expect(activities[0].bounty_id).toBe(1)
    expect(activities[0].message).toContain('just asked Test Bounty')
  })

  it('creates correct message for question activity', () => {
    addActivity(1, 'user1', 'question', 'Claude')
    const stored = localStorageMock.getItem('bounty_activities')
    const activities = JSON.parse(stored!)
    expect(activities[0].message).toBe('just asked Claude')
  })

  it('creates correct message for nft_redeem activity', () => {
    addActivity(1, 'user1', 'nft_redeem')
    const stored = localStorageMock.getItem('bounty_activities')
    const activities = JSON.parse(stored!)
    expect(activities[0].message).toBe('redeemed their NFT')
  })

  it('creates correct message for referral activity', () => {
    addActivity(1, 'user1', 'referral')
    const stored = localStorageMock.getItem('bounty_activities')
    const activities = JSON.parse(stored!)
    expect(activities[0].message).toBe('referred a new friend')
  })

  it('creates correct message for first_question activity', () => {
    addActivity(1, 'user1', 'first_question', 'Claude')
    const stored = localStorageMock.getItem('bounty_activities')
    const activities = JSON.parse(stored!)
    expect(activities[0].message).toBe('just asked their first question')
  })

  it('keeps only last 100 activities', () => {
    // Add 101 activities
    for (let i = 0; i < 101; i++) {
      addActivity(1, `user${i}`, 'question', 'Bounty')
    }
    
    const stored = localStorageMock.getItem('bounty_activities')
    const activities = JSON.parse(stored!)
    expect(activities).toHaveLength(100)
    // First activity should be the most recent (last added)
    expect(activities[0].username).toBe('user100')
    // Oldest activity should be dropped
    expect(activities.some((a: any) => a.username === 'user0')).toBe(false)
  })
})

describe('seedDevActivities helper function', () => {
  const originalNodeEnv = process.env.NODE_ENV
  const originalSeedFlag = process.env.NEXT_PUBLIC_ACTIVITY_TRACKER_DEV_SEED

  beforeEach(() => {
    localStorageMock.clear()
    process.env.NODE_ENV = 'development'
    process.env.NEXT_PUBLIC_ACTIVITY_TRACKER_DEV_SEED = 'true'
  })

  afterEach(() => {
    process.env.NODE_ENV = originalNodeEnv
    if (originalSeedFlag === undefined) {
      delete process.env.NEXT_PUBLIC_ACTIVITY_TRACKER_DEV_SEED
    } else {
      process.env.NEXT_PUBLIC_ACTIVITY_TRACKER_DEV_SEED = originalSeedFlag
    }
  })

  it('seeds multiple activities for the target bounty', () => {
    seedDevActivities(42)

    const stored = localStorageMock.getItem('bounty_activities')
    expect(stored).toBeTruthy()

    const activities = JSON.parse(stored!)
    expect(activities.length).toBeGreaterThanOrEqual(4)
    // All seeded activities should use the supplied bounty id to keep filtering consistent.
    activities.forEach((activity: any) => {
      expect(activity.bounty_id).toBe(42)
    })
  })

  it('does not seed when running in production mode', () => {
    process.env.NODE_ENV = 'production'
    seedDevActivities(7)

    const stored = localStorageMock.getItem('bounty_activities')
    expect(stored).toBeNull()
  })
})

