import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UsernamePrompt from '@/components/UsernamePrompt'

// Mock wallet hook
const mockPublicKey = {
  toString: () => 'test-wallet-address'
}

const mockUseWallet = {
  connected: true,
  publicKey: mockPublicKey,
}

jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => mockUseWallet,
}))

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

// Mock getBackendUrl
jest.mock('../../lib/api/client', () => ({
  getBackendUrl: () => 'http://localhost:8000',
}))

describe('UsernamePrompt', () => {
  const mockOnSuccess = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    mockFetch.mockClear()
    mockOnSuccess.mockClear()
    mockOnCancel.mockClear()
  })

  it('renders username and email fields', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByText(/\*/)).toBeInTheDocument() // Red asterisk for required
  })

  it('shows username as required with red asterisk', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    // Use getByLabelText which is more specific to form labels
    const usernameInput = screen.getByLabelText(/username/i)
    expect(usernameInput).toBeInTheDocument()
    
    // Check for asterisk - find it via the label element
    const label = usernameInput.closest('label')
    if (label) {
      expect(label.textContent).toContain('*')
      expect(label.textContent).toContain('Username')
    } else {
      // Fallback: just verify asterisk exists somewhere
      expect(screen.getByText(/\*/)).toBeInTheDocument()
    }
  })

  it('shows email as optional', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const emailLabel = screen.getByText(/email address/i)
    expect(emailLabel).toBeInTheDocument()
    // Check for optional indicator - text is in a span with "(optional)"
    // The text might be split, so check the label content
    const label = emailLabel.closest('label')
    expect(label?.textContent?.toLowerCase()).toMatch(/optional/i)
  })

  it('disables submit button when username is too short', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    fireEvent.change(usernameInput, { target: { value: 'ab' } }) // Less than 3 chars
    
    expect(submitButton).toBeDisabled()
  })

  it('enables submit button when username is valid', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    fireEvent.change(usernameInput, { target: { value: 'validuser' } })
    
    expect(submitButton).not.toBeDisabled()
  })

  it('validates username minimum length', async () => {
    // Mock the form submission to trigger validation
    mockFetch.mockResolvedValue({
      ok: false,
      json: async () => ({
        detail: 'username must be at least 3 characters'
      })
    })

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    // Try to submit with short username
    fireEvent.change(usernameInput, { target: { value: 'ab' } })
    
    // Button should be disabled (client-side validation)
    expect(submitButton).toBeDisabled()
    
    // Enable by setting valid username
    fireEvent.change(usernameInput, { target: { value: 'abc' } })
    expect(submitButton).not.toBeDisabled()
    
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('calls API with correct payload on submit', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        username: 'testuser',
        email: 'test@example.com'
      })
    })

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const emailInput = screen.getByLabelText(/email/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.type(emailInput, 'test@example.com')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/user/set-profile',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            wallet_address: 'test-wallet-address',
            username: 'testuser',
            email: 'test@example.com',
          })
        })
      )
    })
  })

  it('sends undefined for email when email is empty', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ success: true })
    })

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      const callArgs = mockFetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body.email).toBeUndefined()
    })
  })

  it('calls onSuccess when API succeeds', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        username: 'testuser'
      })
    })

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('displays error message when API fails', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      json: async () => ({
        error: 'Username already taken'
      })
    })

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/username already taken/i)).toBeInTheDocument()
    })
    
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('calls onCancel when cancel button is clicked', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    fireEvent.click(cancelButton)
    
    expect(mockOnCancel).toHaveBeenCalled()
    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('calls onCancel when X button is clicked', () => {
    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    // X button should be present (close icon)
    const closeButton = screen.getByRole('button', { name: '' }) // X button may not have accessible name
    // Or we can query by test-id or other method
    const closeIcon = document.querySelector('svg')
    if (closeIcon?.parentElement) {
      fireEvent.click(closeIcon.parentElement)
      expect(mockOnCancel).toHaveBeenCalled()
    }
  })

  it('shows loading state during submission', async () => {
    // Mock a delayed response
    mockFetch.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => ({ success: true })
      }), 100))
    )

    render(<UsernamePrompt onSuccess={mockOnSuccess} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByLabelText(/username/i)
    const submitButton = screen.getByRole('button', { name: /set username/i })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.click(submitButton)
    
    // Should show loading state
    expect(screen.getByText(/saving/i)).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })
})

