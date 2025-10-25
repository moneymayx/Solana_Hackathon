'use client'

/**
 * Enhanced Navigation Component
 * 
 * Main navigation with links to all platform features
 */

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import dynamic from 'next/dynamic'

// Dynamically import wallet button to avoid SSR hydration issues
const WalletMultiButton = dynamic(
  async () => (await import('@solana/wallet-adapter-react-ui')).WalletMultiButton,
  { ssr: false }
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
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/test-api', label: 'Test API', icon: '🧪' },
  ]

  return (
    <nav className="bg-gray-800/80 backdrop-blur-md border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">💰</span>
            <span className="text-xl font-bold text-white">Billions Bounty</span>
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
          <WalletMultiButton className="!bg-blue-600 hover:!bg-blue-700 !rounded-lg !font-medium !text-sm" />
        </div>
      </div>
    </nav>
  )
}

