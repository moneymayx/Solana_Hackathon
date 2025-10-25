'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { MessageCircle, BarChart3, CreditCard, User } from 'lucide-react'

interface MobileNavProps {
  freeQuestionsCount?: number
}

/**
 * MobileNav Component - Mobile Bottom Navigation
 * Bottom navigation bar for mobile devices (≤1023px)
 */
export default function MobileNav({ freeQuestionsCount = 0 }: MobileNavProps) {
  const pathname = usePathname()
  
  const navItems = [
    {
      label: 'Chat',
      href: '/',
      icon: <MessageCircle className="h-6 w-6" />
    },
    {
      label: 'Stats',
      href: '/stats',
      icon: <BarChart3 className="h-6 w-6" />
    },
    {
      label: 'Fund',
      href: '/funding',
      icon: <CreditCard className="h-6 w-6" />,
      badge: freeQuestionsCount > 0 ? freeQuestionsCount : undefined
    },
    {
      label: 'Profile',
      href: '/profile',
      icon: <User className="h-6 w-6" />
    }
  ]
  
  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }
  
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-700 z-50">
      <div className="flex items-center justify-around px-2 py-3">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex flex-col items-center gap-1 px-4 py-2 rounded-lg transition-all duration-200',
              'min-w-[64px] relative',
              isActive(item.href)
                ? 'text-blue-500'
                : 'text-slate-400 hover:text-slate-300'
            )}
          >
            <div className="relative">
              {item.icon}
              {item.badge && (
                <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                  {item.badge}
                </span>
              )}
            </div>
            <span className={cn(
              'text-xs font-medium',
              isActive(item.href) ? 'text-blue-500' : 'text-slate-400'
            )}>
              {item.label}
            </span>
            {isActive(item.href) && (
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-blue-500 rounded-full" />
            )}
          </Link>
        ))}
      </div>
    </nav>
  )
}

