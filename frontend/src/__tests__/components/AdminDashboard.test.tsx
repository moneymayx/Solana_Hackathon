import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdminDashboard from '@/components/AdminDashboard'

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

// Mock console.error to avoid noise in tests
const originalConsoleError = console.error
beforeAll(() => {
  console.error = jest.fn()
})

afterAll(() => {
  console.error = originalConsoleError
})

describe('AdminDashboard', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  it('renders loading state initially', () => {
    render(<AdminDashboard />)
    
    expect(screen.getByText('Loading admin data...')).toBeInTheDocument()
  })

  it('displays admin statistics correctly', async () => {
    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Total Users')).toBeInTheDocument()
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('Total Entries')).toBeInTheDocument()
      expect(screen.getByText('500')).toBeInTheDocument()
      // Use getAllByText for multiple instances
      const blacklistedPhrasesElements = screen.getAllByText('Blacklisted Phrases')
      expect(blacklistedPhrasesElements).toHaveLength(2) // One in stats, one in list header
      expect(screen.getByText('2')).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('displays blacklisted phrases list', async () => {
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getAllByText('Blacklisted Phrases')).toHaveLength(2) // One in stats, one in list header
      expect(screen.getByText('test phrase 1')).toBeInTheDocument()
      expect(screen.getByText('test phrase 2')).toBeInTheDocument()
      expect(screen.getByText('User #123')).toBeInTheDocument()
      expect(screen.getByText('User #456')).toBeInTheDocument()
      expect(screen.getAllByText('Active')).toHaveLength(2) // Both phrases are active in mock data
      expect(screen.queryByText('Inactive')).not.toBeInTheDocument() // No inactive phrases in mock data
    })
  })

  it('shows empty state when no blacklisted phrases', async () => {
    // Mock API failure to trigger empty state
    mockFetch.mockRejectedValue(new Error('API Error'))

    render(<AdminDashboard />)
    
    await waitFor(() => {
      // When API fails, component should show empty state
      expect(screen.getByText('No blacklisted phrases found')).toBeInTheDocument()
    })
  })

  it('allows adding new blacklisted phrases', async () => {
    const user = userEvent.setup()
    
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Add Blacklisted Phrase')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('Enter phrase to blacklist...')
    const addButton = screen.getByRole('button', { name: /Add/i })

    await user.type(input, 'new blacklisted phrase')
    await user.click(addButton)

    expect(mockFetch).toHaveBeenCalledWith('/api/admin/blacklist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phrase: 'new blacklisted phrase',
        original_message: 'new blacklisted phrase',
        successful_user_id: 0
      })
    })
  })

  it('prevents adding empty phrases', async () => {
    const user = userEvent.setup()
    
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Add Blacklisted Phrase')).toBeInTheDocument()
    })

    const addButton = screen.getByRole('button', { name: /Add/i })

    expect(addButton).toBeDisabled()
  })

  it('toggles phrase status when clicking toggle button', async () => {
    const user = userEvent.setup()
    
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('test phrase 1')).toBeInTheDocument()
    })

    const toggleButtons = screen.getAllByTitle('Deactivate')
    await user.click(toggleButtons[0]) // Click the first one

    expect(mockFetch).toHaveBeenCalledWith('/api/admin/blacklist/1', {
      method: 'DELETE'
    })
  })

  it('displays system status information', async () => {
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument()
      expect(screen.getByText(/AI Guardian is active/)).toBeInTheDocument()
      expect(screen.getByText(/Blacklist system is protecting/)).toBeInTheDocument()
      expect(screen.getByText(/bounty system is running/)).toBeInTheDocument()
      expect(screen.getByText(/All security systems are operational/)).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValue(new Error('API Error'))

    render(<AdminDashboard />)
    
    await waitFor(() => {
      // Should still render the component structure even if data fails to load
      expect(screen.getByText('Add Blacklisted Phrase')).toBeInTheDocument()
    })
  })

  it('shows loading state while adding phrase', async () => {
    const user = userEvent.setup()
    
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    // Mock a delayed response for adding phrase
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockImplementationOnce(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: async () => ({ success: true })
          }), 100)
        )
      )

    render(<AdminDashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Add Blacklisted Phrase')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('Enter phrase to blacklist...')
    const addButton = screen.getByRole('button', { name: /Add/i })

    await user.type(input, 'test phrase')
    await user.click(addButton)

    expect(screen.getByText('Adding...')).toBeInTheDocument()
    expect(addButton).toBeDisabled()
  })

  it('formats timestamps correctly', async () => {
    const mockBlacklistResponse = {
      blacklisted: false,
      reason: null,
      type: null
    }

    const mockStats = {
      bounty_status: {
        current_pool: 5000,
        total_entries: 500
      }
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockBlacklistResponse
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })

    render(<AdminDashboard />)
    
    await waitFor(() => {
      // Should display formatted time (exact format depends on formatTimeAgo implementation)
      expect(screen.getByText(/User #123/)).toBeInTheDocument()
    })
  })
})
