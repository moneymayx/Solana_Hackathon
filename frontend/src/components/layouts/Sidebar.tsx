'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { 
  MessageCircle, 
  BarChart3, 
  CreditCard, 
  Gift, 
  Gem, 
  Users, 
  LayoutDashboard,
  Settings,
  Crown,
  TrendingUp
} from 'lucide-react'

interface NavItem {
  label: string
  href: string
  icon: React.ReactNode
  badge?: string | number
  adminOnly?: boolean
}

interface SidebarProps {
  isAdmin?: boolean
  freeQuestionsCount?: number
}

/**
 * Sidebar Component - Desktop Navigation
 * Persistent sidebar navigation for desktop (≥1024px)
 */
export default function Sidebar({ isAdmin = false, freeQuestionsCount = 0 }: SidebarProps) {
  const pathname = usePathname()
  
  const navItems: NavItem[] = [
    {
      label: 'Chat',
      href: '/',
      icon: <MessageCircle className="h-5 w-5" />
    },
    {
      label: 'Bounty Stats',
      href: '/stats',
      icon: <BarChart3 className="h-5 w-5" />
    },
    {
      label: 'Funding',
      href: '/funding',
      icon: <CreditCard className="h-5 w-5" />
    },
    {
      label: 'Referrals',
      href: '/referrals',
      icon: <Gift className="h-5 w-5" />,
      badge: freeQuestionsCount > 0 ? freeQuestionsCount : undefined
    },
    {
      label: 'Staking',
      href: '/staking',
      icon: <Gem className="h-5 w-5" />
    },
    {
      label: 'Teams',
      href: '/teams',
      icon: <Users className="h-5 w-5" />
    },
    {
      label: 'Analytics',
      href: '/analytics',
      icon: <LayoutDashboard className="h-5 w-5" />
    },
    {
      label: 'Settings',
      href: '/settings',
      icon: <Settings className="h-5 w-5" />
    }
  ]
  
  if (isAdmin) {
    navItems.push({
      label: 'Admin',
      href: '/admin',
      icon: <Crown className="h-5 w-5" />,
      adminOnly: true
    })
  }
  
  const isActive = (href: string) => {
    if (href === '/') return pathname === '/'
    return pathname.startsWith(href)
  }
  
  return (
    <aside className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-60 lg:border-r lg:border-slate-700 lg:bg-slate-900">
      {/* Logo Section */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-700">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
          <TrendingUp className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-slate-50 font-bold text-lg leading-none">Billions</h1>
          <p className="text-slate-400 text-xs">AI Research</p>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg',
              'text-sm font-medium transition-all duration-200',
              'hover:bg-slate-800',
              isActive(item.href)
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-300 hover:text-slate-50',
              item.adminOnly && 'border border-amber-500/30'
            )}
          >
            <div className="flex items-center gap-3">
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span className="bg-blue-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                {item.badge}
              </span>
            )}
          </Link>
        ))}
      </nav>
      
      {/* Progress Widget - Desktop Only */}
      <div className="px-4 py-6 border-t border-slate-700">
        <div className="bg-slate-800 rounded-lg p-4">
          <h3 className="text-slate-50 font-semibold text-sm mb-3">Your Progress</h3>
          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-400">Level 5 Researcher</span>
                <span className="text-slate-300">68%</span>
              </div>
              <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-violet-500 to-violet-600 rounded-full transition-all duration-500"
                  style={{ width: '68%' }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-1">340/500 XP</p>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">🔥 Streak</span>
              <span className="text-orange-400 font-bold">7 days</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">🏆 Achievements</span>
              <span className="text-yellow-400 font-bold">3</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

