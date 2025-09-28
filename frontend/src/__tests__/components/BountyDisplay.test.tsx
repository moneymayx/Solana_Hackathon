import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import BountyDisplay from '@/components/BountyDisplay'

// Mock the wallet hook
const mockUseWallet = {
  connected: false,
  connecting: false,
  publicKey: null,
  wallet: null,
  connect: jest.fn(),
  disconnect: jest.fn(),
}

jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => mockUseWallet,
}))

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('BountyDisplay', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    mockUseWallet.connected = false
  })

  it('renders loading state initially', () => {
    render(<BountyDisplay />)
    
    expect(screen.getByText('Loading bounty data...')).toBeInTheDocument()
    // The loading spinner div doesn't have a status role, just check for the spinner element
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })

  it('renders error state when API fails', async () => {
    mockFetch.mockRejectedValue(new Error('API Error'))

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load bounty data')).toBeInTheDocument()
    })
  })

  it('displays bounty statistics correctly', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01,
      next_rollover_at: '2024-01-01T12:00:00Z'
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Current Pool')).toBeInTheDocument()
      expect(screen.getByText('$5,000.00')).toBeInTheDocument()
      expect(screen.getByText('Total Entries')).toBeInTheDocument()
      expect(screen.getByText('150')).toBeInTheDocument()
      expect(screen.getByText('Win Rate')).toBeInTheDocument()
      expect(screen.getByText('1.0000%')).toBeInTheDocument()
    })
  })

  it('displays next rollover information when available', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01,
      next_rollover_at: '2024-01-01T12:00:00Z'
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Next Rollover')).toBeInTheDocument()
      expect(screen.getByText(/If no winner is found/)).toBeInTheDocument()
    })
  })

  it('displays user history when wallet is connected', async () => {
    mockUseWallet.connected = true
    
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01
    }

    const mockUserHistory = {
      total_entries: 5,
      total_spent: 50,
      wins: 1,
      last_entry: '2024-01-01T10:00:00Z'
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockbountyData
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockUserHistory
      })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Your Stats')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument() // Total entries
      expect(screen.getByText('$50.00')).toBeInTheDocument() // Total spent
      expect(screen.getByText('1')).toBeInTheDocument() // Wins
      expect(screen.getByText('20.0000%')).toBeInTheDocument() // Win rate
    })
  })

  it('displays recent winners when available', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01,
      recent_winners: [
        {
          user_id: 1,
          prize_amount: 1000,
          won_at: '2024-01-01T10:00:00Z'
        },
        {
          user_id: 2,
          prize_amount: 500,
          won_at: '2024-01-01T09:00:00Z'
        }
      ]
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Recent Winners')).toBeInTheDocument()
      expect(screen.getByText('User #1')).toBeInTheDocument()
      expect(screen.getByText('User #2')).toBeInTheDocument()
      expect(screen.getByText('$1,000.00')).toBeInTheDocument()
      expect(screen.getByText('$500.00')).toBeInTheDocument()
    })
  })

  it('displays how to play instructions', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('How to Play')).toBeInTheDocument()
      expect(screen.getByText(/Connect your Solana wallet/)).toBeInTheDocument()
      expect(screen.getByText(/Chat with the AI guardian/)).toBeInTheDocument()
      expect(screen.getByText(/Each message costs \$10/)).toBeInTheDocument()
      expect(screen.getByText(/Win rate is currently/)).toBeInTheDocument()
    })
  })

  it('updates data every 5 seconds', async () => {
    jest.useFakeTimers()
    
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Current Pool')).toBeInTheDocument()
    })

    // Fast-forward time by 5 seconds
    jest.advanceTimersByTime(5000)
    
    await waitFor(() => {
      // Should have been called twice: once on mount, once after 5 seconds
      expect(mockFetch).toHaveBeenCalledTimes(2)
    })

    jest.useRealTimers()
  })

  it('handles partial data gracefully', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.01
      // Missing next_rollover_at and recent_winners
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('Current Pool')).toBeInTheDocument()
      expect(screen.getByText('$5,000.00')).toBeInTheDocument()
      // Should not show next rollover section
      expect(screen.queryByText('Next Rollover')).not.toBeInTheDocument()
      // Should not show recent winners section
      expect(screen.queryByText('Recent Winners')).not.toBeInTheDocument()
    })
  })

  it('calculates win rate percentage correctly', async () => {
    const mockbountyData = {
      current_pool: 5000,
      total_entries: 150,
      win_rate: 0.0001 // 0.01%
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('0.0100%')).toBeInTheDocument()
    })
  })

  it('formats currency correctly', async () => {
    const mockbountyData = {
      current_pool: 1234567.89,
      total_entries: 150,
      win_rate: 0.01
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockbountyData
    })

    render(<BountyDisplay />)
    
    await waitFor(() => {
      expect(screen.getByText('$1,234,567.89')).toBeInTheDocument()
    })
  })
})
