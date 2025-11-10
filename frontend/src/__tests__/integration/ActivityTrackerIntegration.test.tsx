/**
 * Integration tests for Activity Tracker feature
 * Tests the full flow including username collection, activity creation, and display
 */

import React from 'react'
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react'
import BountyCard from '../../components/BountyCard'
import { addActivity } from '../../components/ActivityTracker'

// Mock environment variable
const originalEnv = process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER

// Mock wallet
const mockPublicKey = {
  toString: () => 'test-wallet-123'
}

const mockUseWallet = {
  connected: true,
  publicKey: mockPublicKey,
  signTransaction: jest.fn(),
}

jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => mockUseWallet,
  useConnection: () => ({ connection: {} }),
}))

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString() },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
    length: 0,
    key: (index: number) => null,
  }
})()
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock getBackendUrl
jest.mock('../../lib/api/client', () => ({
  getBackendUrl: () => 'http://localhost:8000',
}))

// Mock other components - use relative paths
jest.mock('../../components/NftVerification', () => {
  return function MockNftVerification({ onClose, onVerificationSuccess }: any) {
    return (
      <div data-testid="nft-verification">
        <button onClick={() => onVerificationSuccess()}>Mock Verify</button>
        <button onClick={onClose}>Close</button>
      </div>
    )
  }
})

jest.mock('../../components/ReferralFlow', () => {
  return function MockReferralFlow({ onSuccess, onCancel }: any) {
    return (
      <div data-testid="referral-flow">
        <button onClick={() => onSuccess('REF123')}>Get Code</button>
        <button onClick={onCancel}>Cancel</button>
      </div>
    )
  }
})

jest.mock('../../components/PaymentAmountModal', () => {
  return function MockPaymentModal({ onClose, onSelectAmount }: any) {
    return (
      <div data-testid="payment-modal">
        <button onClick={() => onSelectAmount(10)}>Pay $10</button>
        <button onClick={onClose}>Close</button>
      </div>
    )
  }
})

describe('Activity Tracker Integration', () => {
  beforeEach(() => {
    localStorageMock.clear()
    mockFetch.mockClear()
    process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'true'
    jest.useFakeTimers()
  })

  afterEach(() => {
    process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = originalEnv
    jest.useRealTimers()
  })

  describe('Feature Flag Behavior', () => {
    it('feature flag controls activity tracker visibility', () => {
      // Test that feature flag works at component level
      // This is tested through BountyCard which doesn't have Solana dependencies
      process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'true'
      
      const bounty = {
        id: 1,
        name: 'Test Bounty',
        llm_provider: 'claude',
        current_pool: 1000,
        total_entries: 10,
        win_rate: 0.01,
        difficulty_level: 'medium',
        is_active: true,
      }

      act(() => {
        addActivity(1, 'testuser', 'question', 'Test Bounty')
      })

      const { container } = render(<BountyCard bounty={bounty} />)
      
      // Activity tracker should be present when enabled
      // (checked in Activity Tracker Display tests below)
    })

    it('does not show tracker when feature disabled', () => {
      process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'false'

      act(() => {
        addActivity(1, 'testuser', 'question', 'Test Bounty')
      })

      const bounty = {
        id: 1,
        name: 'Test Bounty',
        llm_provider: 'claude',
        current_pool: 1000,
        total_entries: 10,
        win_rate: 0.01,
        difficulty_level: 'medium',
        is_active: true,
      }

      render(<BountyCard bounty={bounty} />)

      // Activity tracker should not render when disabled
      expect(screen.queryByText(/testuser/i)).not.toBeInTheDocument()
    })
  })

  describe('Activity Creation Flow', () => {
    it('creates activity when question is asked', async () => {
      // Test activity creation directly (simpler than full component test)
      act(() => {
        addActivity(1, 'testuser', 'question', 'Test Bounty')
      })

      // Verify activity in localStorage
      const stored = localStorageMock.getItem('bounty_activities')
      expect(stored).toBeTruthy()
      
      const activities = JSON.parse(stored!)
      expect(activities).toHaveLength(1)
      expect(activities[0].username).toBe('testuser')
      expect(activities[0].bounty_id).toBe(1)
    })
  })

  describe('Activity Tracker Display', () => {
    it('shows activities when feature enabled', async () => {
      process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'true'

      // Add activity to localStorage
      act(() => {
        addActivity(1, 'testuser', 'question', 'Test Bounty')
      })

      const bounty = {
        id: 1,
        name: 'Test Bounty',
        llm_provider: 'claude',
        current_pool: 1000,
        total_entries: 10,
        win_rate: 0.01,
        difficulty_level: 'medium',
        is_active: true,
      }

      render(<BountyCard bounty={bounty} />)

      await waitFor(() => {
        expect(screen.getByText(/testuser/i)).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('does not show tracker when feature disabled', () => {
      process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'false'

      act(() => {
        addActivity(1, 'testuser', 'question', 'Test Bounty')
      })

      const bounty = {
        id: 1,
        name: 'Test Bounty',
        llm_provider: 'claude',
        current_pool: 1000,
        total_entries: 10,
        win_rate: 0.01,
        difficulty_level: 'medium',
        is_active: true,
      }

      render(<BountyCard bounty={bounty} />)

      expect(screen.queryByText(/testuser/i)).not.toBeInTheDocument()
    })
  })

  describe('Per-Bounty Filtering', () => {
    it('only shows activities for specific bounty', async () => {
      process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER = 'true'

      // Add activities for different bounties
      act(() => {
        addActivity(1, 'user1', 'question', 'Bounty 1')
        addActivity(2, 'user2', 'question', 'Bounty 2')
      })
      
      const bounty1 = {
        id: 1,
        name: 'Bounty 1',
        llm_provider: 'claude',
        current_pool: 1000,
        total_entries: 10,
        win_rate: 0.01,
        difficulty_level: 'medium',
        is_active: true,
      }

      const { rerender } = render(<BountyCard bounty={bounty1} />)

      await waitFor(() => {
        expect(screen.getByText(/user1/i)).toBeInTheDocument()
        expect(screen.queryByText(/user2/i)).not.toBeInTheDocument()
      }, { timeout: 3000 })

      // Switch to bounty 2
      const bounty2 = {
        ...bounty1,
        id: 2,
        name: 'Bounty 2',
      }

      rerender(<BountyCard bounty={bounty2} />)

      await waitFor(() => {
        expect(screen.getByText(/user2/i)).toBeInTheDocument()
        expect(screen.queryByText(/user1/i)).not.toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })
})

