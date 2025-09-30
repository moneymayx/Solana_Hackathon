'use client'

import { useState, useEffect } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { 
  Coins, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Shield, 
  Zap,
  Lock,
  Unlock,
  Trophy,
  Clock
} from 'lucide-react'

interface LotteryState {
  success: boolean
  program_id: string
  current_jackpot: number
  total_entries: number
  is_active: boolean
  research_fund_floor: number
  research_fee: number
  last_rollover: string
  next_rollover: string
}

interface SmartContractIntegrationProps {
  onLotteryEntry?: (result: any) => void
  onWinnerSelected?: (result: any) => void
}

export default function SmartContractIntegration({ 
  onLotteryEntry, 
  onWinnerSelected 
}: SmartContractIntegrationProps) {
  const { connected, publicKey, signTransaction } = useWallet()
  const [lotteryState, setLotteryState] = useState<LotteryState | null>(null)
  const [loading, setLoading] = useState(false)
  const [entryStatus, setEntryStatus] = useState<'idle' | 'processing' | 'success' | 'failed'>('idle')
  const [winnerStatus, setWinnerStatus] = useState<'idle' | 'selecting' | 'selected' | 'failed'>('idle')
  const [lastEntry, setLastEntry] = useState<any>(null)
  const [lastWinner, setLastWinner] = useState<any>(null)

  useEffect(() => {
    if (connected) {
      fetchLotteryState()
    }
  }, [connected])

  const fetchLotteryState = async () => {
    try {
      const response = await fetch('/api/lottery/status')
      if (response.ok) {
        const data = await response.json()
        setLotteryState(data)
      }
    } catch (error) {
      console.error('Failed to fetch lottery state:', error)
    }
  }

  const processLotteryEntry = async () => {
    if (!connected || !publicKey) {
      alert('Please connect your wallet first')
      return
    }

    setLoading(true)
    setEntryStatus('processing')

    try {
      const response = await fetch('/api/payment/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_method: 'wallet',
          amount_usd: 10, // Fixed $10 entry fee
          wallet_address: publicKey.toString(),
          token_symbol: 'USDC'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setLastEntry(data)
        setEntryStatus('success')
        onLotteryEntry?.(data)
        
        // Refresh lottery state
        await fetchLotteryState()
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to process lottery entry')
      }
    } catch (error) {
      console.error('Lottery entry failed:', error)
      setEntryStatus('failed')
    } finally {
      setLoading(false)
    }
  }

  const selectWinner = async () => {
    setLoading(true)
    setWinnerStatus('selecting')

    try {
      const response = await fetch('/api/lottery/select-winner', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (response.ok) {
        const data = await response.json()
        setLastWinner(data)
        setWinnerStatus('selected')
        onWinnerSelected?.(data)
        
        // Refresh lottery state
        await fetchLotteryState()
      } else {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to select winner')
      }
    } catch (error) {
      console.error('Winner selection failed:', error)
      setWinnerStatus('failed')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatTimeUntilRollover = (nextRollover: string) => {
    const now = new Date()
    const rollover = new Date(nextRollover)
    const diff = rollover.getTime() - now.getTime()
    
    if (diff <= 0) return 'Now'
    
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Shield className="h-6 w-6 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Autonomous Lottery System</h3>
      </div>

      {/* Lottery State Display */}
      {lotteryState && (
        <div className="mb-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Trophy className="h-5 w-5 text-yellow-400" />
                <h4 className="text-yellow-400 font-semibold">Current Jackpot</h4>
              </div>
              <p className="text-2xl font-bold text-white">
                {formatCurrency(lotteryState.current_jackpot)}
              </p>
              <p className="text-yellow-200 text-sm">
                Floor: {formatCurrency(lotteryState.research_fund_floor)}
              </p>
            </div>

            <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="h-5 w-5 text-blue-400" />
                <h4 className="text-blue-400 font-semibold">Next Rollover</h4>
              </div>
              <p className="text-lg font-bold text-white">
                {formatTimeUntilRollover(lotteryState.next_rollover)}
              </p>
              <p className="text-blue-200 text-sm">
                {lotteryState.total_entries} entries
              </p>
            </div>
          </div>

          <div className="bg-gray-700/50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-300 mb-3">Smart Contract Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Program ID:</span>
                <p className="text-white font-mono text-xs break-all">
                  {lotteryState.program_id.slice(0, 8)}...{lotteryState.program_id.slice(-8)}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Entry Fee:</span>
                <p className="text-white font-bold">
                  {formatCurrency(lotteryState.research_fee)}
                </p>
              </div>
              <div>
                <span className="text-gray-400">Status:</span>
                <p className={`font-bold ${lotteryState.is_active ? 'text-green-400' : 'text-red-400'}`}>
                  {lotteryState.is_active ? 'Active' : 'Inactive'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fund Distribution Info */}
      <div className="mb-6 bg-green-600/20 border border-green-500/30 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-2">
          <Lock className="h-5 w-5 text-green-400" />
          <h4 className="text-green-400 font-semibold">Autonomous Fund Management</h4>
        </div>
        <div className="text-green-200 text-sm space-y-1">
          <p>• Funds are immediately locked in smart contract upon entry</p>
          <p>• 80% goes to research fund, 20% operational fee</p>
          <p>• Winner selection is completely autonomous and tamper-proof</p>
          <p>• No backend control over fund transfers</p>
        </div>
      </div>

      {/* Entry Status */}
      {entryStatus !== 'idle' && (
        <div className="mb-6">
          {entryStatus === 'processing' && (
            <div className="flex items-center space-x-3 bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
              <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
              <div>
                <p className="text-blue-300 font-medium">Processing Lottery Entry</p>
                <p className="text-blue-200 text-sm">Signing transaction and locking funds...</p>
              </div>
            </div>
          )}
          
          {entryStatus === 'success' && lastEntry && (
            <div className="flex items-center space-x-3 bg-green-500/20 border border-green-500/30 rounded-lg p-4">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div>
                <p className="text-green-300 font-medium">Entry Successful!</p>
                <p className="text-green-200 text-sm">
                  Transaction: {lastEntry.transaction_signature?.slice(0, 8)}...
                </p>
                <p className="text-green-200 text-sm">
                  Research contribution: {formatCurrency(lastEntry.research_contribution || 8)}
                </p>
              </div>
            </div>
          )}
          
          {entryStatus === 'failed' && (
            <div className="flex items-center space-x-3 bg-red-500/20 border border-red-500/30 rounded-lg p-4">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div>
                <p className="text-red-300 font-medium">Entry Failed</p>
                <p className="text-red-200 text-sm">Please try again</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Winner Selection Status */}
      {winnerStatus !== 'idle' && (
        <div className="mb-6">
          {winnerStatus === 'selecting' && (
            <div className="flex items-center space-x-3 bg-purple-500/20 border border-purple-500/30 rounded-lg p-4">
              <Loader2 className="h-5 w-5 text-purple-400 animate-spin" />
              <div>
                <p className="text-purple-300 font-medium">Selecting Winner</p>
                <p className="text-purple-200 text-sm">Using secure randomness to select winner...</p>
              </div>
            </div>
          )}
          
          {winnerStatus === 'selected' && lastWinner && (
            <div className="flex items-center space-x-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-4">
              <Trophy className="h-5 w-5 text-yellow-400" />
              <div>
                <p className="text-yellow-300 font-medium">Winner Selected!</p>
                <p className="text-yellow-200 text-sm">
                  Winner: {lastWinner.winner_wallet?.slice(0, 8)}...{lastWinner.winner_wallet?.slice(-8)}
                </p>
                <p className="text-yellow-200 text-sm">
                  Jackpot: {formatCurrency(lastWinner.jackpot_amount || 0)}
                </p>
              </div>
            </div>
          )}
          
          {winnerStatus === 'failed' && (
            <div className="flex items-center space-x-3 bg-red-500/20 border border-red-500/30 rounded-lg p-4">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div>
                <p className="text-red-300 font-medium">Winner Selection Failed</p>
                <p className="text-red-200 text-sm">Please try again</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={processLotteryEntry}
          disabled={!connected || loading || !lotteryState?.is_active}
          className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold px-6 py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {loading && entryStatus === 'processing' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              <Coins className="h-4 w-4" />
              <span>Enter Lottery ($10)</span>
            </>
          )}
        </button>

        <button
          onClick={selectWinner}
          disabled={loading || !lotteryState?.is_active || lotteryState?.total_entries === 0}
          className="flex-1 bg-gradient-to-r from-yellow-500 to-orange-500 text-white font-bold px-6 py-3 rounded-lg hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {loading && winnerStatus === 'selecting' ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              <Zap className="h-4 w-4" />
              <span>Select Winner</span>
            </>
          )}
        </button>
      </div>

      {!connected && (
        <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <p className="text-yellow-200 text-sm text-center">
            Please connect your wallet to interact with the smart contract
          </p>
        </div>
      )}

      {lotteryState && !lotteryState.is_active && (
        <div className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
          <p className="text-red-200 text-sm text-center">
            Lottery is currently inactive
          </p>
        </div>
      )}
    </div>
  )
}
