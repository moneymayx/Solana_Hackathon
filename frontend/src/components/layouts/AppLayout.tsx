'use client'

import { ReactNode } from 'react'
import TopNavigation from '../TopNavigation'

interface AppLayoutProps {
  children: ReactNode
}

/**
 * AppLayout Component
 * Main layout wrapper with top navigation (Jackpot-style)
 */
export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <TopNavigation />
      
      {/* Main Content */}
      <main className="min-h-screen">
        {children}
      </main>
    </div>
  )
}

