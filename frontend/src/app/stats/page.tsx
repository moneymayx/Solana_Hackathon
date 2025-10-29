'use client'

import AppLayout from '@/components/layouts/AppLayout'
import BountyDisplay from '@/components/BountyDisplay'

export default function StatsPage() {
  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-4 lg:p-8">
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold text-slate-50 mb-2">Bounty Statistics</h1>
          <p className="text-slate-400">Track the prize pool, win rates, and recent winners</p>
        </div>
        
        <BountyDisplay />
      </div>
    </AppLayout>
  )
}

