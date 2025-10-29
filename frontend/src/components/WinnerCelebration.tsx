'use client'

import { useState, useEffect } from 'react'
import { Trophy, X, Sparkles, Gift } from 'lucide-react'

interface WinnerCelebrationProps {
  winnerData: any
  onClose: () => void
}

export default function WinnerCelebration({ winnerData, onClose }: WinnerCelebrationProps) {
  const [showConfetti, setShowConfetti] = useState(false)

  useEffect(() => {
    if (winnerData) {
      setShowConfetti(true)
      // Auto-close after 10 seconds
      const timer = setTimeout(() => {
        onClose()
      }, 10000)
      return () => clearTimeout(timer)
    }
  }, [winnerData, onClose])

  if (!winnerData) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-8 max-w-md w-full relative overflow-hidden">
        {/* Confetti Effect */}
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute animate-bounce"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 2}s`
                }}
              >
                <Sparkles className="h-4 w-4 text-yellow-500" />
              </div>
            ))}
          </div>
        )}

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-slate-100 rounded-full transition-colors"
        >
          <X className="h-5 w-5 text-slate-500" />
        </button>

        {/* Winner Content */}
        <div className="text-center">
          <div className="mb-6">
            <div className="mx-auto w-20 h-20 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center mb-4">
              <Trophy className="h-10 w-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-2">
              🎉 JACKPOT WINNER! 🎉
            </h2>
            <p className="text-slate-600">
              Congratulations! You successfully convinced the AI to transfer funds!
            </p>
          </div>

          <div className="bg-gradient-to-r from-yellow-100 to-orange-100 border-2 border-yellow-300 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Gift className="h-6 w-6 text-yellow-600" />
              <span className="text-lg font-semibold text-slate-900">Prize Won</span>
            </div>
            <div className="text-4xl font-bold text-yellow-600 mb-2">
              ${winnerData.prize_payout?.toFixed(2) || '0.00'}
            </div>
            <p className="text-sm text-slate-600">
              Funds will be transferred to your wallet automatically
            </p>
          </div>

          <div className="space-y-3">
            <div className="text-sm text-slate-600">
              <strong>Transaction Details:</strong>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-left">
              <div className="text-xs text-slate-500 space-y-1">
                <div>Model: {winnerData.model_used || 'Unknown'}</div>
                <div>Attempts: {winnerData.attempts || 'N/A'}</div>
                <div>Success Rate: {winnerData.success_rate || 'N/A'}</div>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="mt-6 px-6 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600 font-medium transition-all duration-200"
          >
            Continue Playing
          </button>
        </div>
      </div>
    </div>
  )
}
