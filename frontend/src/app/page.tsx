'use client'

import { useState, useEffect } from 'react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useWallet } from '@solana/wallet-adapter-react'
import ChatInterface from '@/components/ChatInterface'
import bountyDisplay from '@/components/bountyDisplay'
import AdminDashboard from '@/components/AdminDashboard'
import PaymentFlow from '@/components/PaymentFlow'
import Header from '@/components/Header'
import { cn } from '@/lib/utils'

export default function Home() {
  const { connected } = useWallet()
  const [activeTab, setActiveTab] = useState<'chat' | 'bounty' | 'admin' | 'payment'>('chat')

  return (
    <main className="min-h-screen">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-white mb-4 bg-gradient-to-r from-yellow-400 via-red-500 to-pink-500 bg-clip-text text-transparent">
            Billions Bounty
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Challenge the AI guardian to win the treasure! A sophisticated bounty system with a 0.01% win rate.
          </p>
          
          {!connected && (
            <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-6 mb-8 max-w-md mx-auto">
              <p className="text-yellow-200 mb-4">
                Connect your wallet to start playing!
              </p>
              <WalletMultiButton className="!bg-gradient-to-r !from-yellow-400 !to-orange-500 !text-black !font-bold !px-6 !py-3 !rounded-lg" />
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-1 flex">
            <button
              onClick={() => setActiveTab('chat')}
              className={cn(
                "px-6 py-3 rounded-md font-medium transition-all duration-200",
                activeTab === 'chat'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Chat with AI
            </button>
            <button
              onClick={() => setActiveTab('bounty')}
              className={cn(
                "px-6 py-3 rounded-md font-medium transition-all duration-200",
                activeTab === 'bounty'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              bounty Status
            </button>
            <button
              onClick={() => setActiveTab('admin')}
              className={cn(
                "px-6 py-3 rounded-md font-medium transition-all duration-200",
                activeTab === 'admin'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Admin
            </button>
            <button
              onClick={() => setActiveTab('payment')}
              className={cn(
                "px-6 py-3 rounded-md font-medium transition-all duration-200",
                activeTab === 'payment'
                  ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg"
                  : "text-gray-400 hover:text-white hover:bg-gray-700/50"
              )}
            >
              Payment
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'bounty' && <bountyDisplay />}
          {activeTab === 'admin' && <AdminDashboard />}
          {activeTab === 'payment' && <PaymentFlow />}
        </div>
      </div>
    </main>
  )
}