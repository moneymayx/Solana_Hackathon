import '@testing-library/jest-dom'

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    }
  },
}))

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock fetch globally
global.fetch = jest.fn()

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Mock crypto for wallet functionality - needs getRandomValues for Keypair.generate() and PDA derivation
import { webcrypto } from 'crypto';

// Create a proper crypto object that Solana libraries can use
const cryptoPolyfill = {
  ...webcrypto,
  randomUUID: () => 'mock-uuid',
  getRandomValues: (array) => {
    return webcrypto.getRandomValues(array);
  },
  subtle: webcrypto.subtle,
};

// Set crypto globally - must be done before any Solana imports
Object.defineProperty(global, 'crypto', {
  value: cryptoPolyfill,
  writable: true,
  configurable: true,
});

// Also set on window if available (for browser-like environments)
if (typeof globalThis !== 'undefined') {
  Object.defineProperty(globalThis, 'crypto', {
    value: cryptoPolyfill,
    writable: true,
    configurable: true,
  });
}

// Note: @solana/web3.js and @solana/spl-token are NOT mocked here
// They will be transformed by Babel according to transformIgnorePatterns
// This allows V3 tests to use real implementations

// Mock Solana wallet adapters
jest.mock('@solana/wallet-adapter-react', () => ({
  useWallet: () => ({
    connected: false,
    connecting: false,
    publicKey: null,
    wallet: null,
    connect: jest.fn(),
    disconnect: jest.fn(),
    signTransaction: jest.fn(),
  }),
  useConnection: () => ({
    connection: {},
  }),
  WalletProvider: ({ children }) => children,
}))

// Mock wallet adapter UI
jest.mock('@solana/wallet-adapter-react-ui', () => ({
  WalletMultiButton: ({ children, ...props }) => (
    <button data-testid="wallet-multi-button" {...props}>
      {children || 'Connect Wallet'}
    </button>
  ),
}))

// Polyfill TextEncoder/TextDecoder for Solana dependencies
const { TextEncoder, TextDecoder } = require('util')
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Polyfill Buffer for Solana/Anchor dependencies
global.Buffer = require('buffer').Buffer

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks()
})
