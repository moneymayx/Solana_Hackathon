'use client'

/**
 * Enhanced Navigation Component
 * 
 * Main navigation with links to all platform features
 */

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import dynamic from 'next/dynamic'

// Dynamically import WalletButton to ensure proper cleanup
const DynamicWalletButton = dynamic(
  () => import('./WalletButton'),
  { 
    ssr: false,
    loading: () => (
      <button className="wallet-adapter-button wallet-adapter-button-trigger" disabled>
        Loading...
      </button>
    )
  }
)

export default function Navigation() {
  const pathname = usePathname()

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(path + '/')
  }

  const navItems = [
    { href: '/', label: 'Home', icon: '🏠' },
    { href: '/token', label: 'Token', icon: '💎' },
    { href: '/staking', label: 'Staking', icon: '📈' },
    { href: '/teams', label: 'Teams', icon: '👥' },
    { href: '/analytics', label: 'Analytics', icon: '📊' },
    { href: '/test-api', label: 'Test API', icon: '🧪' },
  ]

  return (
    <nav className="bg-gray-800/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">💰</span>
            <span className="text-xl font-bold text-white">BILLION$</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  isActive(item.href)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                <span>{item.icon}</span>
                <span className="hidden sm:inline">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* Real Wallet Button */}
          <DynamicWalletButton />
        </div>
      </div>
    </nav>
  )
}

