import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInterface from '@/components/ChatInterface'

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

// Mock scrollIntoView
Object.defineProperty(Element.prototype, 'scrollIntoView', {
  value: jest.fn(),
  writable: true
})

describe('ChatInterface', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    mockUseWallet.connected = false
  })

  it('renders chat interface with correct elements', () => {
    render(<ChatInterface />)
    
    expect(screen.getByText('Chat with Billions')).toBeInTheDocument()
    expect(screen.getByText(/Try to convince the AI guardian/)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Connect wallet to chat/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Send/i })).toBeInTheDocument()
  })

  it('shows wallet connection prompt when not connected', () => {
    render(<ChatInterface />)
    
    expect(screen.getByPlaceholderText(/Connect wallet to chat/)).toBeDisabled()
    expect(screen.getByRole('button', { name: /Send/i })).toBeDisabled()
  })

  it('enables input when wallet is connected', () => {
    mockUseWallet.connected = true
    render(<ChatInterface />)
    
    expect(screen.getByPlaceholderText(/Type your message/)).not.toBeDisabled()
  })

  it('displays empty state message', () => {
    render(<ChatInterface />)
    
    expect(screen.getByText('Start a conversation with the AI guardian!')).toBeInTheDocument()
    expect(screen.getByText('Try to convince them to transfer funds...')).toBeInTheDocument()
  })

  it('handles message input and submission', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock successful API response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Hello! I am the AI guardian.',
        bounty_result: { success: true, new_jackpot: 1000 },
        winner_result: null,
        bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
        blacklisted: false
      })
    })

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    const sendButton = screen.getByRole('button', { name: /Send/i })
    
    await user.type(input, 'Hello AI')
    await user.click(sendButton)
    
    expect(mockFetch).toHaveBeenCalledWith('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: 'Hello AI',
        user_id: 1
      })
    })
  })

  it('handles Enter key submission', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Hello! I am the AI guardian.',
        bounty_result: { success: true, new_jackpot: 1000 },
        winner_result: null,
        bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
        blacklisted: false
      })
    })

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    
    await user.type(input, 'Hello AI')
    await user.keyboard('{Enter}')
    
    expect(mockFetch).toHaveBeenCalled()
  })

  it('displays user and AI messages correctly', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock chat API response
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Hello! I am the AI guardian.',
        bounty_result: { success: true, new_jackpot: 1000 },
        winner_result: null,
        bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
        blacklisted: false
      })
    })

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'Hello AI')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText('Hello AI')).toBeInTheDocument()
    })
    
    await waitFor(() => {
      expect(screen.getByText('Hello! I am the AI guardian.')).toBeInTheDocument()
    })
  })

  it('displays winner message with special styling', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock chat API response with winner result
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'Congratulations! You won!',
        bounty_result: { success: true, new_jackpot: 1000 },
        winner_result: { is_winner: true, prize_payout: 1000 },
        bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
        blacklisted: false
      })
    })

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'I won!')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      const winnerMessage = screen.getByText('Congratulations! You won!')
      expect(winnerMessage).toBeInTheDocument()
      // Find the parent div with the gradient classes
      const messageContainer = winnerMessage.closest('div[class*="bg-gradient-to-r"]')
      expect(messageContainer).toHaveClass('bg-gradient-to-r', 'from-green-500', 'to-emerald-500')
    })
  })

  it('displays blacklisted message with special styling', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock chat API response with blacklisted result
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        response: 'This message is blacklisted.',
        bounty_result: { success: false },
        winner_result: null,
        bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
        blacklisted: true
      })
    })

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'Blacklisted message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      const blacklistedMessage = screen.getByText('This message is blacklisted.')
      expect(blacklistedMessage).toBeInTheDocument()
      // Find the parent div with the gradient classes
      const messageContainer = blacklistedMessage.closest('div[class*="bg-gradient-to-r"]')
      expect(messageContainer).toHaveClass('bg-gradient-to-r', 'from-red-500', 'to-pink-500')
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock chat API error
    mockFetch.mockRejectedValueOnce(new Error('API Error'))

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText('Sorry, I encountered an error. Please try again.')).toBeInTheDocument()
    })
  })

  it('shows loading state during API call', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    
    // Mock initial bounty status fetch
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 1,
        win_rate: 0.01
      })
    })
    
    // Mock a delayed chat response
    mockFetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({
            response: 'Delayed response',
            bounty_result: { success: true, new_jackpot: 1000 },
            winner_result: null,
            bounty_status: { current_pool: 1000, total_entries: 1, win_rate: 0.01 },
            blacklisted: false
          })
        }), 100)
      )
    )

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')
    
    // Should show loading state
    expect(screen.getByText('AI is thinking...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('Delayed response')).toBeInTheDocument()
    }, { timeout: 200 })
  })

  it('fetches bounty status on mount', () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        current_pool: 1000,
        total_entries: 5,
        win_rate: 0.01
      })
    })

    render(<ChatInterface />)
    
    expect(mockFetch).toHaveBeenCalledWith('/api/bounty/status')
  })

  it('updates bounty status display', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          current_pool: 1000,
          total_entries: 5,
          win_rate: 0.01
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          response: 'Test response',
          bounty_result: { success: true, new_jackpot: 1200 },
          winner_result: null,
          bounty_status: { current_pool: 1200, total_entries: 6, win_rate: 0.01 },
          blacklisted: false
        })
      })

    const user = userEvent.setup()
    mockUseWallet.connected = true

    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText(/Type your message/)
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')
    
    await waitFor(() => {
      expect(screen.getByText(/Win rate: 1.0000%/)).toBeInTheDocument()
    })
  })
})
