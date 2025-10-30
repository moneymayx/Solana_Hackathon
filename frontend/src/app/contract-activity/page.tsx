'use client'

/**
 * Contract Activity Demo Page
 * 
 * Dedicated page to showcase smart contract activity
 * Perfect for demos to show real blockchain interactions
 */

import AppLayout from '@/components/layouts/AppLayout'
import ContractActivityMonitor from '@/components/ContractActivityMonitor'

export default function ContractActivityPage() {
  return (
    <AppLayout>
      <div className="min-h-screen bg-gray-900">
        <div className="max-w-6xl mx-auto p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              Smart Contract Activity
            </h1>
            <p className="text-gray-400 text-lg">
              Real-time monitoring of all blockchain transactions on the Billions Bounty platform.
              All transactions are verified on-chain via Solana smart contracts.
            </p>
          </div>

          {/* Activity Monitor */}
          <div className="mb-8">
            <ContractActivityMonitor 
              autoRefresh={true}
              refreshInterval={5000}
              maxTransactions={20}
            />
          </div>

          {/* Info Section */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-white mb-2">🔍 Transaction Types</h3>
                <ul className="text-gray-400 space-y-2 text-sm">
                  <li>• <strong className="text-white">Lottery Entries</strong> - When users pay to enter</li>
                  <li>• <strong className="text-white">Winner Payouts</strong> - Automated prize distributions</li>
                  <li>• <strong className="text-white">Staking</strong> - Token staking deposits</li>
                  <li>• <strong className="text-white">Unstaking</strong> - Token withdrawal transactions</li>
                  <li>• <strong className="text-white">Team Contributions</strong> - Team funding transactions</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-white mb-2">✅ Verification</h3>
                <ul className="text-gray-400 space-y-2 text-sm">
                  <li>• All transactions are recorded on-chain</li>
                  <li>• Click any transaction to view on Solana Explorer</li>
                  <li>• Automatic updates every 5 seconds</li>
                  <li>• Status indicators show confirmation state</li>
                  <li>• Full transaction signatures for transparency</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Explorer Links */}
          <div className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">🔗 View on Solana Explorer</h3>
            <p className="text-gray-400 text-sm mb-4">
              Click any transaction to view full details on Solana Explorer. You can see:
            </p>
            <ul className="text-gray-400 space-y-1 text-sm">
              <li>• Transaction signature and status</li>
              <li>• All accounts involved</li>
              <li>• Amount transferred</li>
              <li>• Block time and confirmation</li>
              <li>• Program instruction data</li>
            </ul>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}


