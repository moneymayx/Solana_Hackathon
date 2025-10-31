/**
 * NFT Verification Component
 * 
 * Allows users to verify NFT ownership to receive 5 free questions
 */

import { useState, useEffect } from 'react'
import { useWallet, useConnection } from '@solana/wallet-adapter-react'
import { 
  checkNftOwnership, 
  verifyNftOwnership, 
  getNftStatus,
  AUTHORIZED_NFT_MINT 
} from '../services/nftService'

interface NftVerificationProps {
  onClose: () => void
  onVerificationSuccess: () => void
}

export default function NftVerification({ onClose, onVerificationSuccess }: NftVerificationProps) {
  const { publicKey, connected } = useWallet()
  const { connection } = useConnection()
  const wallet = useWallet()
  
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)
  const [ownsNft, setOwnsNft] = useState(false)
  const [alreadyVerified, setAlreadyVerified] = useState(false)
  const [questionsRemaining, setQuestionsRemaining] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    checkOwnership()
  }, [connected, publicKey])

  const checkOwnership = async () => {
    if (!connected || !publicKey) {
      setChecking(false)
      return
    }

    setChecking(true)
    setError(null)

    try {
      // Check if already verified
      const status = await getNftStatus(publicKey.toString())
      
      if (status.verified) {
        setAlreadyVerified(true)
        setQuestionsRemaining(status.questionsRemaining)
        setChecking(false)
        return
      }

      // Check if owns NFT
      const owns = await checkNftOwnership(connection, publicKey.toString())
      setOwnsNft(owns)
    } catch (err) {
      console.error('Error checking ownership:', err)
      setError('Failed to check NFT ownership. Please try again.')
    } finally {
      setChecking(false)
    }
  }

  const handleVerify = async () => {
    if (!connected || !publicKey) {
      setError('Please connect your wallet first.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      console.log('🎨 Starting NFT verification...')
      const result = await verifyNftOwnership(connection, wallet)
      console.log('🎨 NFT verification result:', {
        success: result.success,
        verified: result.verified,
        message: result.message,
        questionsGranted: result.questionsGranted
      })

      if (result.success && result.verified) {
        console.log('✅ NFT verification successful!', result.message)
        setSuccess(true)
        
        // Wait briefly to show success message, then trigger callback
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        console.log('🎨 Calling onVerificationSuccess callback...')
        await onVerificationSuccess()
        
        console.log('🎨 Closing modal...')
        onClose()
      } else {
        const errorMsg = result.message || 'Verification failed. Please try again.'
        console.error('❌ NFT verification failed:', errorMsg)
        setError(errorMsg)
      }
    } catch (err) {
      console.error('❌ Error verifying NFT:', err)
      setError(err instanceof Error ? err.message : 'Failed to verify NFT ownership')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-slate-800">NFT Verification</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          {checking ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
              <p className="mt-4 text-slate-600">Checking NFT ownership...</p>
            </div>
          ) : alreadyVerified ? (
            <div className="text-center py-6">
              <div className="text-green-500 text-6xl mb-4">✓</div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Already Verified!</h3>
              <p className="text-slate-600 mb-4">
                You've already verified your NFT ownership.
              </p>
              <p className="text-sm text-slate-500">
                Questions remaining: <span className="font-bold text-purple-600">{questionsRemaining}</span>
              </p>
            </div>
          ) : success ? (
            <div className="text-center py-6">
              <div className="text-green-500 text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Verification Successful!</h3>
              <p className="text-slate-600">
                You've been granted <span className="font-bold text-purple-600">5 free questions</span>!
              </p>
            </div>
          ) : (
            <>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="font-bold text-purple-900 mb-2">How it works:</h3>
                <ol className="text-sm text-purple-800 space-y-1 list-decimal list-inside">
                  <li>We check if you own the required NFT</li>
                  <li>You sign a transaction to verify ownership on-chain</li>
                  <li>Receive 5 free questions instantly</li>
                </ol>
              </div>

              {!connected ? (
                <div className="text-center py-4">
                  <p className="text-slate-600 mb-4">Please connect your wallet to verify NFT ownership.</p>
                </div>
              ) : !ownsNft ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">
                    <strong>NFT Not Found:</strong> You don't own the required NFT to verify.
                  </p>
                  <p className="text-red-600 text-xs mt-2">
                    Required NFT: <code className="bg-red-100 px-1 py-0.5 rounded">{AUTHORIZED_NFT_MINT.slice(0, 8)}...{AUTHORIZED_NFT_MINT.slice(-8)}</code>
                  </p>
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-green-800 text-sm">
                    <strong>✓ NFT Found:</strong> You own the required NFT! Click verify to get 5 free questions.
                  </p>
                </div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 font-medium"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  onClick={handleVerify}
                  disabled={!connected || !ownsNft || loading}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Verifying...
                    </span>
                  ) : (
                    'Verify Genesis NFT'
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}


