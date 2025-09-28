'use client'

import { useState, useEffect, useRef } from 'react'
import { useWallet } from '@solana/wallet-adapter-react'
import { CreditCard, Coins, ExternalLink, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

interface PaymentQuote {
  baseCurrencyAmount: number
  quoteCurrencyAmount: number
  quoteCurrencyPrice: number
  feeAmount: number
  networkFeeAmount: number
  totalAmount: number
}

interface PaymentFlowProps {
  onPaymentSuccess?: (transactionId: string) => void
  onPaymentFailure?: (error: string) => void
}

export default function PaymentFlow({ onPaymentSuccess, onPaymentFailure }: PaymentFlowProps) {
  const { connected, publicKey } = useWallet()
  const [paymentMethod, setPaymentMethod] = useState<'wallet' | 'fiat'>('fiat')
  const [amount, setAmount] = useState(10)
  const [quote, setQuote] = useState<PaymentQuote | null>(null)
  const [loading, setLoading] = useState(false)
  const [paymentUrl, setPaymentUrl] = useState('')
  const [transactionId, setTransactionId] = useState('')
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'failed'>('idle')
  const [pollingTxId, setPollingTxId] = useState<string | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const pollingAttemptsRef = useRef<number>(0)

  useEffect(() => {
    if (paymentMethod === 'fiat' && amount > 0) {
      fetchQuote()
    }
  }, [paymentMethod, amount])

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [])

  // Handle polling state changes for testing
  useEffect(() => {
    if (paymentStatus === 'success' || paymentStatus === 'failed') {
      stopPolling()
    }
  }, [paymentStatus])

  const fetchQuote = async () => {
    try {
      const response = await fetch(`/api/moonpay/quote?currency_code=sol&amount_usd=${amount}`)
      if (response.ok) {
        const data = await response.json()
        setQuote(data.quote)
      }
    } catch (error) {
      console.error('Failed to fetch quote:', error)
    }
  }

  const createPayment = async () => {
    if (!connected || !publicKey) {
      onPaymentFailure?.('Please connect your wallet first')
      return
    }

    setLoading(true)
    setPaymentStatus('processing')

    try {
      const response = await fetch('/api/moonpay/create-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: publicKey.toString(),
          amount_usd: amount,
          currency_code: 'sol'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setPaymentUrl(data.payment_url)
        setTransactionId(data.transaction_id)
        
        // Open payment URL in new tab
        window.open(data.payment_url, '_blank')
        
        // Start polling for payment status
        startPolling(data.transaction_id)
      } else {
        throw new Error('Failed to create payment')
      }
    } catch (error) {
      console.error('Payment creation failed:', error)
      setPaymentStatus('failed')
      onPaymentFailure?.(error instanceof Error ? error.message : 'Payment failed')
    } finally {
      setLoading(false)
    }
  }

  const checkPaymentStatus = async (txId: string): Promise<'completed' | 'failed' | 'pending'> => {
    try {
      const response = await fetch(`/api/moonpay/transaction/${txId}`)
      if (response.ok) {
        const data = await response.json()
        const status = data.transaction.status

        if (status === 'completed') {
          return 'completed'
        } else if (status === 'failed' || status === 'cancelled') {
          return 'failed'
        }
        return 'pending'
      }
      return 'pending'
    } catch (error) {
      console.error('Failed to check payment status:', error)
      return 'pending'
    }
  }

  const startPolling = (txId: string) => {
    const maxAttempts = 60 // Poll for up to 5 minutes
    pollingAttemptsRef.current = 0
    setPollingTxId(txId)

    const poll = async () => {
      pollingAttemptsRef.current++
      const status = await checkPaymentStatus(txId)

      if (status === 'completed') {
        setPaymentStatus('success')
        onPaymentSuccess?.(txId)
        stopPolling()
        return
      } else if (status === 'failed') {
        setPaymentStatus('failed')
        onPaymentFailure?.('Payment was cancelled or failed')
        stopPolling()
        return
      }

      if (pollingAttemptsRef.current >= maxAttempts) {
        setPaymentStatus('failed')
        onPaymentFailure?.('Payment timeout')
        stopPolling()
        return
      }
    }

    // Start polling immediately
    poll()
    
    // Set up interval for subsequent polls
    pollingIntervalRef.current = setInterval(poll, 5000)
  }

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
    setPollingTxId(null)
    pollingAttemptsRef.current = 0
  }

  const handleAmountChange = (newAmount: number) => {
    setAmount(newAmount)
    setPaymentStatus('idle')
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <CreditCard className="h-6 w-6 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Purchase bounty Entry</h3>
      </div>

      {/* Payment Method Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-3">Payment Method</label>
        <div className="flex space-x-4">
          <button
            onClick={() => setPaymentMethod('fiat')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              paymentMethod === 'fiat'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <CreditCard className="h-4 w-4" />
            <span>Credit Card</span>
          </button>
          <button
            onClick={() => setPaymentMethod('wallet')}
            disabled={!connected}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
              paymentMethod === 'wallet'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed'
            }`}
          >
            <Coins className="h-4 w-4" />
            <span>Wallet</span>
          </button>
        </div>
      </div>

      {/* Amount Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-3">Amount (USD)</label>
        <div className="grid grid-cols-3 gap-2">
          {[5, 10, 25, 50, 100, 500].map((value) => (
            <button
              key={value}
              onClick={() => handleAmountChange(value)}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                amount === value
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              ${value}
            </button>
          ))}
        </div>
        <div className="mt-3">
          <input
            type="number"
            value={amount}
            onChange={(e) => handleAmountChange(Number(e.target.value))}
            min="1"
            max="1000"
            className="w-full bg-gray-700 text-white placeholder-gray-400 px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="Custom amount"
          />
        </div>
      </div>

      {/* Quote Display */}
      {paymentMethod === 'fiat' && quote && (
        <div className="mb-6 bg-gray-700/50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-300 mb-3">Payment Summary</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Amount:</span>
              <span className="text-white">{formatCurrency(quote.baseCurrencyAmount)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">You'll receive:</span>
              <span className="text-white">{quote.quoteCurrencyAmount.toFixed(6)} SOL</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Rate:</span>
              <span className="text-white">${quote.quoteCurrencyPrice.toFixed(2)}/SOL</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Fee:</span>
              <span className="text-white">{formatCurrency(quote.feeAmount)}</span>
            </div>
            <div className="border-t border-gray-600 pt-2 flex justify-between font-medium">
              <span className="text-gray-300">Total:</span>
              <span className="text-white">{formatCurrency(quote.totalAmount)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Payment Status */}
      {paymentStatus !== 'idle' && (
        <div className="mb-6">
          {paymentStatus === 'processing' && (
            <div className="flex items-center space-x-3 bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
              <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
              <div>
                <p className="text-blue-300 font-medium">Processing Payment</p>
                <p className="text-blue-200 text-sm">Please complete the payment in the new tab</p>
              </div>
            </div>
          )}
          
          {paymentStatus === 'success' && (
            <div className="flex items-center space-x-3 bg-green-500/20 border border-green-500/30 rounded-lg p-4">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div>
                <p className="text-green-300 font-medium">Payment Successful!</p>
                <p className="text-green-200 text-sm">Transaction: {transactionId}</p>
              </div>
            </div>
          )}
          
          {paymentStatus === 'failed' && (
            <div className="flex items-center space-x-3 bg-red-500/20 border border-red-500/30 rounded-lg p-4">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div>
                <p className="text-red-300 font-medium">Payment Failed</p>
                <p className="text-red-200 text-sm">Please try again</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={createPayment}
          disabled={!connected || loading || amount <= 0}
          className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold px-6 py-3 rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              <CreditCard className="h-4 w-4" />
              <span>Pay with {paymentMethod === 'fiat' ? 'Credit Card' : 'Wallet'}</span>
            </>
          )}
        </button>
        
        {paymentUrl && (
          <button
            onClick={() => window.open(paymentUrl, '_blank')}
            className="bg-gray-700 text-white px-4 py-3 rounded-lg hover:bg-gray-600 transition-all duration-200 flex items-center space-x-2"
          >
            <ExternalLink className="h-4 w-4" />
            <span>Open Payment</span>
          </button>
        )}
      </div>

      {!connected && (
        <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <p className="text-yellow-200 text-sm text-center">
            Please connect your wallet to make a payment
          </p>
        </div>
      )}
    </div>
  )
}
