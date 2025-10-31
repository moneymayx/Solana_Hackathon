import React from 'react'
import { render, waitFor, act, rerender } from '@testing-library/react'
import WalletButton from '@/components/WalletButton'

// Mock wallet adapter hooks with reactive state
let mockConnected = false
let mockConnecting = false
let mockWallet: any = null
let mockVisible = false

const mockSetVisible = jest.fn((value: boolean) => {
  mockVisible = value
})

const mockSelect = jest.fn()
const mockDisconnect = jest.fn()

// Mock the wallet adapter hooks
jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => ({
    connected: mockConnected,
    connecting: mockConnecting,
    wallet: mockWallet,
    select: mockSelect,
    disconnect: mockDisconnect,
  }),
}))

jest.mock('@solana/wallet-adapter-react-ui', () => ({
  WalletMultiButton: ({ children, ...props }: any) => (
    <button data-testid="wallet-multi-button" {...props}>
      {children || 'Connect Wallet'}
    </button>
  ),
  useWalletModal: () => ({
    visible: mockVisible,
    setVisible: mockSetVisible,
  }),
}))

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

describe('WalletButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockConnected = false
    mockConnecting = false
    mockWallet = null
    mockVisible = false
    localStorageMock.clear()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('renders WalletMultiButton', () => {
    const { getByTestId } = render(<WalletButton />)
    expect(getByTestId('wallet-multi-button')).toBeInTheDocument()
  })

  it('keeps modal open when wallet is selected', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    // Initial render
    const { rerender } = render(<WalletButton />)

    // Simulate wallet selection - update state and re-render
    act(() => {
      mockWallet = wallet
      mockConnecting = false
      mockConnected = false
      rerender(<WalletButton />)
    })

    // Advance timers to trigger useEffect
    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Wait for useEffect to run
    await waitFor(() => {
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })
  })

  it('keeps modal open during connection process', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Select wallet first
    act(() => {
      mockWallet = wallet
      mockConnecting = false
      mockConnected = false
      mockVisible = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Modal should open when wallet is selected
    expect(mockSetVisible).toHaveBeenCalledWith(true)
    mockSetVisible.mockClear()

    // Now start connecting - modal should stay open
    act(() => {
      mockConnecting = true
      mockVisible = true // Modal is now open
      rerender(<WalletButton />)
    })

    // Advance timers to trigger effects
    act(() => {
      jest.advanceTimersByTime(150)
    })

    // Modal should stay open during connection - component ensures this
    // The component will call setVisible(true) if modal closes
    // Since modal is already open (mockVisible = true), setVisible might not be called again
    // But if it closes, it will be reopened. The key is modal stays open.
    expect(mockSetVisible).not.toHaveBeenCalledWith(false)
  })

  it('closes modal when connection succeeds', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Start with wallet selected and connecting
    act(() => {
      mockWallet = wallet
      mockConnecting = true
      mockConnected = false
      mockVisible = true
      rerender(<WalletButton />)
    })

    // Advance timers
    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Simulate successful connection
    act(() => {
      mockConnected = true
      mockConnecting = false
      rerender(<WalletButton />)
    })

    // Advance timers again
    act(() => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Should close modal on successful connection
      expect(mockSetVisible).toHaveBeenCalledWith(false)
    })
  })

  it('reopens modal if it closes prematurely during connection', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Start with wallet selected and connecting
    act(() => {
      mockWallet = wallet
      mockConnecting = true
      mockConnected = false
      mockVisible = true
      rerender(<WalletButton />)
    })

    // Advance timers to set the keep open flag
    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Simulate modal closing prematurely
    act(() => {
      mockVisible = false
      rerender(<WalletButton />)
    })

    // Advance timers to trigger reopen effect
    act(() => {
      jest.advanceTimersByTime(150)
    })

    await waitFor(() => {
      // Should reopen modal if it closed during connection
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })
  })

  it('handles wallet selection correctly', async () => {
    const wallet1 = {
      adapter: {
        name: 'Phantom',
      },
    }

    const wallet2 = {
      adapter: {
        name: 'Solflare',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Select first wallet
    act(() => {
      mockWallet = wallet1
      mockConnected = false
      mockConnecting = false
      mockVisible = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })

    // Reset mocks and close modal
    mockSetVisible.mockClear()
    mockVisible = false

    // Switch to second wallet - this should be detected as a new wallet
    act(() => {
      mockWallet = wallet2
      mockConnected = false
      mockConnecting = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Should detect new wallet selection and open modal
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })
  })

  it('resets keep open flag when wallet is disconnected', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Connect wallet
    act(() => {
      mockWallet = wallet
      mockConnected = true
      mockConnecting = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Disconnect wallet
    act(() => {
      mockWallet = null
      mockConnected = false
      mockConnecting = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(600) // Wait for cleanup timeout
    })

    await waitFor(() => {
      // Should call disconnect
      expect(mockDisconnect).toHaveBeenCalled()
    })
  })

  it('does not reopen modal if wallet is already connected', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Set wallet as already connected
    act(() => {
      mockWallet = wallet
      mockConnected = true
      mockConnecting = false
      mockVisible = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(200)
    })

    // Modal should not be reopened if already connected
    await waitFor(() => {
      expect(mockSetVisible).not.toHaveBeenCalledWith(true)
    })
  })

  it('handles connection failure - keeps modal open', async () => {
    const wallet = {
      adapter: {
        name: 'Phantom',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Start connecting
    act(() => {
      mockWallet = wallet
      mockConnecting = true
      mockConnected = false
      mockVisible = false // Start with modal closed
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Verify modal was opened
    expect(mockSetVisible).toHaveBeenCalledWith(true)
    mockSetVisible.mockClear()

    // Simulate connection failure (not connected, not connecting)
    act(() => {
      mockConnecting = false
      mockConnected = false
      mockVisible = false // Modal closed
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(150) // Wait for reopen timeout
    })

    // Modal should be reopened if connection failed
    await waitFor(() => {
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })
  })

  it('handles rapid wallet selection changes', async () => {
    const wallet1 = {
      adapter: {
        name: 'Phantom',
      },
    }

    const wallet2 = {
      adapter: {
        name: 'Solflare',
      },
    }

    const { rerender } = render(<WalletButton />)

    // Rapidly change wallets - select first wallet
    act(() => {
      mockWallet = wallet1
      mockConnected = false
      mockConnecting = false
      mockVisible = false
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Verify first wallet triggered modal open
    expect(mockSetVisible).toHaveBeenCalledWith(true)
    mockSetVisible.mockClear()
    mockVisible = true

    // Rapidly switch to second wallet before effects complete
    act(() => {
      mockWallet = wallet2
      mockVisible = false // Modal closed
      rerender(<WalletButton />)
    })

    act(() => {
      jest.advanceTimersByTime(100)
    })

    // Should handle the wallet change gracefully - modal should open for new wallet
    await waitFor(() => {
      expect(mockSetVisible).toHaveBeenCalledWith(true)
    })
  })
})

