import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PaymentFlow from '@/components/PaymentFlow'

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

describe('PaymentFlow', () => {
  const mockOnPaymentSuccess = jest.fn()
  const mockOnPaymentFailure = jest.fn()

  beforeEach(() => {
    mockFetch.mockClear()
    mockOnPaymentSuccess.mockClear()
    mockOnPaymentFailure.mockClear()
    mockUseWallet.connected = false
    mockUseWallet.publicKey = null
  })

  it('renders payment flow with correct elements', () => {
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    expect(screen.getByText('Purchase bounty Entry')).toBeInTheDocument()
    expect(screen.getByText('Payment Method')).toBeInTheDocument()
    expect(screen.getByText('Credit Card')).toBeInTheDocument()
    expect(screen.getByText('Wallet')).toBeInTheDocument()
    expect(screen.getByText('Amount (USD)')).toBeInTheDocument()
  })

  it('shows wallet connection prompt when not connected', () => {
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    expect(screen.getByText('Please connect your wallet to make a payment')).toBeInTheDocument()
  })

  it('allows selecting payment method', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true // Enable wallet connection for this test
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    // Get payment method buttons by their text content
    const fiatButton = screen.getByRole('button', { name: 'Credit Card' })
    const walletButton = screen.getByRole('button', { name: 'Wallet' })
    
    expect(fiatButton).toHaveClass('bg-gradient-to-r', 'from-purple-500', 'to-pink-500')
    expect(walletButton).toHaveClass('bg-gray-700')
    
    await user.click(walletButton)
    
    expect(walletButton).toHaveClass('bg-gradient-to-r', 'from-purple-500', 'to-pink-500')
    expect(fiatButton).toHaveClass('bg-gray-700')
  })

  it('allows selecting amount from predefined options', async () => {
    const user = userEvent.setup()
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const amountButtons = [5, 10, 25, 50, 100, 500]
    
    for (const amount of amountButtons) {
      const button = screen.getByRole('button', { name: `$${amount}` })
      await user.click(button)
      expect(button).toHaveClass('bg-gradient-to-r', 'from-purple-500', 'to-pink-500')
    }
  })

  it('allows custom amount input', async () => {
    const user = userEvent.setup()
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const customInput = screen.getByPlaceholderText('Custom amount')
    await user.clear(customInput)
    await user.type(customInput, '75')
    
    expect(customInput).toHaveValue(75)
  })

  it('fetches quote when fiat payment is selected', async () => {
    const mockQuote = {
      baseCurrencyAmount: 10,
      quoteCurrencyAmount: 0.05,
      quoteCurrencyPrice: 200,
      feeAmount: 0.5,
      networkFeeAmount: 0.1,
      totalAmount: 10.6
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ quote: mockQuote })
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/moonpay/quote?currency_code=sol&amount_usd=10')
    })
  })

  it('displays payment summary when quote is available', async () => {
    const mockQuote = {
      baseCurrencyAmount: 10,
      quoteCurrencyAmount: 0.05,
      quoteCurrencyPrice: 200,
      feeAmount: 0.5,
      networkFeeAmount: 0.1,
      totalAmount: 10.6
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({ quote: mockQuote })
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    await waitFor(() => {
      expect(screen.getByText('Payment Summary')).toBeInTheDocument()
      expect(screen.getByText('$10.00')).toBeInTheDocument() // Amount
      expect(screen.getByText('0.050000 SOL')).toBeInTheDocument() // You'll receive
      expect(screen.getByText('$200.00/SOL')).toBeInTheDocument() // Rate
      expect(screen.getByText('$0.50')).toBeInTheDocument() // Fee
      expect(screen.getByText('$10.60')).toBeInTheDocument() // Total
    }, { timeout: 5000 })
  })

  it('creates payment when wallet is connected', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    const mockPaymentResponse = {
      payment_url: 'https://moonpay.com/payment/123',
      transaction_id: 'tx-123',
      amount_usd: 10,
      currency_code: 'sol'
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockPaymentResponse
    })

    // Mock window.open
    const mockOpen = jest.fn()
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    expect(mockFetch).toHaveBeenCalledWith('/api/moonpay/create-payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: 'test-wallet-address',
        amount_usd: 10,
        currency_code: 'sol'
      })
    })

    expect(mockOpen).toHaveBeenCalledWith('https://moonpay.com/payment/123', '_blank')
  })

  it('shows processing state during payment creation', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    // Mock a delayed response
    mockFetch.mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({
            payment_url: 'https://moonpay.com/payment/123',
            transaction_id: 'tx-123',
            amount_usd: 10,
            currency_code: 'sol'
          })
        }), 100)
      )
    )

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    expect(screen.getByText('Processing Payment')).toBeInTheDocument()
    expect(screen.getByText('Please complete the payment in the new tab')).toBeInTheDocument()
  })

  it('shows success state when payment is completed', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    const mockPaymentResponse = {
      payment_url: 'https://moonpay.com/payment/123',
      transaction_id: 'tx-123',
      amount_usd: 10,
      currency_code: 'sol'
    }

    // Mock quote fetch first
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        quote: {
          baseCurrencyAmount: 10,
          quoteCurrencyAmount: 0.05,
          quoteCurrencyPrice: 200,
          feeAmount: 0.5,
          networkFeeAmount: 0.1,
          totalAmount: 10.6
        }
      })
    })

    // Mock payment creation
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPaymentResponse
    })

    // Mock payment status check - completed
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        transaction: { status: 'completed' }
      })
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    await waitFor(() => {
      expect(screen.getByText('Payment Successful!')).toBeInTheDocument()
      expect(screen.getByText('Transaction: tx-123')).toBeInTheDocument()
    }, { timeout: 5000 })

    expect(mockOnPaymentSuccess).toHaveBeenCalledWith('tx-123')
  })

  it('shows failure state when payment fails', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    mockFetch.mockRejectedValue(new Error('Payment failed'))

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    await waitFor(() => {
      expect(screen.getByText('Payment Failed')).toBeInTheDocument()
      expect(screen.getByText('Please try again')).toBeInTheDocument()
    })

    expect(mockOnPaymentFailure).toHaveBeenCalledWith('Payment failed')
  })

  it('polls payment status until completion', async () => {
    jest.useFakeTimers()
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime })
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    const mockPaymentResponse = {
      payment_url: 'https://moonpay.com/payment/123',
      transaction_id: 'tx-123',
      amount_usd: 10,
      currency_code: 'sol'
    }

    // Mock quote fetch first
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        quote: {
          baseCurrencyAmount: 10,
          quoteCurrencyAmount: 0.05,
          quoteCurrencyPrice: 200,
          feeAmount: 0.5,
          networkFeeAmount: 0.1,
          totalAmount: 10.6
        }
      })
    })

    // Mock payment creation
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPaymentResponse
    })

    // Mock payment status checks - pending then completed
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          transaction: { status: 'pending' }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          transaction: { status: 'completed' }
        })
      })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    // Advance timers to trigger the polling
    act(() => {
      jest.advanceTimersByTime(5000)
    })

    await waitFor(() => {
      expect(screen.getByText('Payment Successful!')).toBeInTheDocument()
    })

    // Should have called status check twice (initial + after 5s)
    expect(mockFetch).toHaveBeenCalledWith('/api/moonpay/transaction/tx-123')
    
    jest.useRealTimers()
  })

  it('handles payment timeout', async () => {
    jest.useFakeTimers()
    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime })
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    const mockPaymentResponse = {
      payment_url: 'https://moonpay.com/payment/123',
      transaction_id: 'tx-123',
      amount_usd: 10,
      currency_code: 'sol'
    }

    // Mock quote fetch first
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        quote: {
          baseCurrencyAmount: 10,
          quoteCurrencyAmount: 0.05,
          quoteCurrencyPrice: 200,
          feeAmount: 0.5,
          networkFeeAmount: 0.1,
          totalAmount: 10.6
        }
      })
    })

    // Mock payment creation
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPaymentResponse
    })

    // Mock payment status check - always pending
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        transaction: { status: 'pending' }
      })
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    // Fast-forward time to trigger timeout (60 attempts * 5 seconds = 300 seconds)
    act(() => {
      jest.advanceTimersByTime(300000)
    })

    await waitFor(() => {
      expect(screen.getByText('Payment Failed')).toBeInTheDocument()
    })

    expect(mockOnPaymentFailure).toHaveBeenCalledWith('Payment timeout')
    
    jest.useRealTimers()
  })

  it('disables pay button when wallet is not connected', () => {
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    expect(payButton).toBeDisabled()
  })

  it('disables pay button when amount is invalid', () => {
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const customInput = screen.getByPlaceholderText('Custom amount')
    fireEvent.change(customInput, { target: { value: '0' } })
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    expect(payButton).toBeDisabled()
  })

  it('opens payment URL when clicking open payment button', async () => {
    const user = userEvent.setup()
    mockUseWallet.connected = true
    mockUseWallet.publicKey = { toString: () => 'test-wallet-address' }
    
    const mockPaymentResponse = {
      payment_url: 'https://moonpay.com/payment/123',
      transaction_id: 'tx-123',
      amount_usd: 10,
      currency_code: 'sol'
    }

    // Mock quote fetch first
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        quote: {
          baseCurrencyAmount: 10,
          quoteCurrencyAmount: 0.05,
          quoteCurrencyPrice: 200,
          feeAmount: 0.5,
          networkFeeAmount: 0.1,
          totalAmount: 10.6
        }
      })
    })

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockPaymentResponse
    })

    // Mock window.open
    const mockOpen = jest.fn()
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true
    })

    render(<PaymentFlow onPaymentSuccess={mockOnPaymentSuccess} onPaymentFailure={mockOnPaymentFailure} />)
    
    const payButton = screen.getByRole('button', { name: /Pay with Credit Card/i })
    await user.click(payButton)

    await waitFor(() => {
      const openButton = screen.getByRole('button', { name: /Open Payment/i })
      expect(openButton).toBeInTheDocument()
    })

    const openButton = screen.getByRole('button', { name: /Open Payment/i })
    await user.click(openButton)

    expect(mockOpen).toHaveBeenCalledWith('https://moonpay.com/payment/123', '_blank')
  })
})
