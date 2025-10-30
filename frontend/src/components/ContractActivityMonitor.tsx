'use client'

/**
 * Smart Contract Activity Monitor
 * 
 * Displays live smart contract transactions with clickable explorer links
 * Perfect for demos to show real blockchain activity
 */

import { useState, useEffect } from 'react'
import { ExternalLink, CheckCircle, Clock, XCircle, Zap, Coins, Trophy } from 'lucide-react'

interface ContractTransaction {
  id: number
  type: 'lottery_entry' | 'winner_payout' | 'staking' | 'unstaking' | 'team_contribution'
  transaction_signature: string
  wallet_address: string
  amount: number
  status: 'pending' | 'confirmed' | 'failed'
  created_at: string
  explorer_url?: string
}

interface ContractActivityMonitorProps {
  autoRefresh?: boolean
  refreshInterval?: number // milliseconds
  maxTransactions?: number
}

export default function ContractActivityMonitor({
  autoRefresh = true,
  refreshInterval = 5000, // 5 seconds
  maxTransactions = 10
}: ContractActivityMonitorProps) {
  const [transactions, setTransactions] = useState<ContractTransaction[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  // Generate explorer URL based on network
  const getExplorerUrl = (signature: string, network: 'devnet' | 'mainnet' = 'devnet'): string => {
    const cluster = network === 'devnet' ? '?cluster=devnet' : ''
    return `https://explorer.solana.com/tx/${signature}${cluster}`
  }

  // Fetch recent contract transactions
  const fetchTransactions = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${backendUrl}/api/contract/activity`)
      if (!response.ok) throw new Error('Failed to fetch transactions')
      
      const data = await response.json()
      if (data.success && data.transactions) {
        // Add explorer URLs to each transaction
        const transactionsWithExplorer = data.transactions.map((tx: ContractTransaction) => ({
          ...tx,
          explorer_url: tx.transaction_signature 
            ? getExplorerUrl(tx.transaction_signature) 
            : undefined
        }))
        setTransactions(transactionsWithExplorer.slice(0, maxTransactions))
        setLastUpdate(new Date())
      }
    } catch (error) {
      console.error('Error fetching contract activity:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTransactions()
    
    if (autoRefresh) {
      const interval = setInterval(fetchTransactions, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'lottery_entry':
        return <Coins className="h-4 w-4" />
      case 'winner_payout':
        return <Trophy className="h-4 w-4" />
      case 'staking':
      case 'unstaking':
        return <Zap className="h-4 w-4" />
      case 'team_contribution':
        return <Coins className="h-4 w-4" />
      default:
        return <Coins className="h-4 w-4" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600 animate-pulse" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount)
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  if (isLoading && transactions.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Zap className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Smart Contract Activity</h3>
        </div>
        <div className="text-gray-600 text-sm">Loading transactions...</div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Zap className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Smart Contract Activity</h3>
          {autoRefresh && (
            <span className="text-xs text-green-600 flex items-center">
              <span className="w-2 h-2 bg-green-600 rounded-full animate-pulse mr-1"></span>
              Live
            </span>
          )}
        </div>
        <div className="text-xs text-gray-500">
          Updated {formatTime(lastUpdate.toISOString())}
        </div>
      </div>

      {/* Transactions List */}
      {transactions.length === 0 ? (
        <div className="text-center py-8 text-gray-600">
          <Coins className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No recent transactions</p>
          <p className="text-sm mt-2">Transactions will appear here when contracts are triggered</p>
        </div>
      ) : (
        <div className="space-y-3">
          {transactions.map((tx) => (
            <div
              key={tx.id}
              className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between">
                {/* Left: Transaction Info */}
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {getTransactionIcon(tx.type)}
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {tx.type.replace('_', ' ')}
                    </span>
                    {getStatusIcon(tx.status)}
                  </div>
                  
                  <div className="text-xs text-gray-600 mb-2">
                    <div className="font-mono">
                      {tx.wallet_address.slice(0, 8)}...{tx.wallet_address.slice(-8)}
                    </div>
                    <div className="mt-1">{formatAmount(tx.amount)}</div>
                  </div>

                  {/* Transaction Signature */}
                  {tx.transaction_signature && (
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-xs text-gray-500 font-mono">
                        {tx.transaction_signature.slice(0, 8)}...{tx.transaction_signature.slice(-8)}
                      </span>
                      {tx.explorer_url && (
                        <a
                          href={tx.explorer_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700 text-xs flex items-center space-x-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="h-3 w-3" />
                          <span>View on Explorer</span>
                        </a>
                      )}
                    </div>
                  )}
                </div>

                {/* Right: Timestamp */}
                <div className="text-xs text-gray-500 ml-4">
                  {formatTime(tx.created_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
        All transactions are verified on-chain via Solana smart contracts
      </div>
    </div>
  )
}

