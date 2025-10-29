'use client'

import React from 'react'
import { X, DollarSign, Zap } from 'lucide-react'

interface PaymentAmountModalProps {
  onClose: () => void
  onSelectAmount: (amount: number) => void
  isProcessing?: boolean
  currentQuestionCost: number
}

export default function PaymentAmountModal({ 
  onClose, 
  onSelectAmount,
  isProcessing = false,
  currentQuestionCost
}: PaymentAmountModalProps) {
  const handleSelectAmount = (amount: number) => {
    if (isProcessing) return
    onSelectAmount(amount)
  }

  // Calculate questions dynamically based on current question cost
  const calculateQuestions = (amount: number): string => {
    const questions = Math.floor(amount / currentQuestionCost)
    const remainder = amount % currentQuestionCost
    
    if (questions === 0) {
      return `Insufficient (need $${currentQuestionCost.toFixed(2)})`
    } else if (remainder > 0) {
      return `${questions} question${questions > 1 ? 's' : ''} + $${remainder.toFixed(2)} credit`
    } else {
      return `${questions} question${questions > 1 ? 's' : ''}`
    }
  }

  const PAYMENT_AMOUNTS = [
    { amount: 1, label: '$1' },
    { amount: 10, label: '$10', highlighted: true },
    { amount: 20, label: '$20' },
    { amount: 50, label: '$50' },
    { amount: 100, label: '$100' },
    { amount: 1000, label: '$1,000', premium: true }
  ]

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">Try Your Luck</h2>
              <p className="text-sm text-slate-600">Select your entry amount</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
            disabled={isProcessing}
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Amount Options */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {PAYMENT_AMOUNTS.map((option) => {
              const questionText = calculateQuestions(option.amount)
              const isInsufficient = option.amount < currentQuestionCost
              
              return (
                <button
                  key={option.amount}
                  onClick={(e) => {
                    e.stopPropagation()
                    handleSelectAmount(option.amount)
                  }}
                  disabled={isProcessing || isInsufficient}
                  className={`
                    relative p-6 rounded-xl border-2 transition-all
                    ${isInsufficient 
                      ? 'border-red-300 bg-red-50 opacity-60 cursor-not-allowed'
                      : option.highlighted 
                      ? 'border-yellow-400 bg-gradient-to-br from-yellow-50 to-orange-50' 
                      : option.premium
                      ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-pink-50'
                      : 'border-slate-200 bg-white hover:border-yellow-300 hover:bg-yellow-50'
                    }
                    ${isProcessing ? 'opacity-50 cursor-not-allowed' : !isInsufficient ? 'cursor-pointer hover:scale-105' : ''}
                  `}
                >
                  {option.highlighted && !isInsufficient && (
                    <div className="absolute -top-2 -right-2 bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                      POPULAR
                    </div>
                  )}
                  {option.premium && !isInsufficient && (
                    <div className="absolute -top-2 -right-2 bg-purple-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                      PREMIUM
                    </div>
                  )}
                  {isInsufficient && (
                    <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                      TOO LOW
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-3 mb-2">
                    <DollarSign className={`h-6 w-6 ${
                      isInsufficient ? 'text-red-600' :
                      option.highlighted ? 'text-yellow-600' :
                      option.premium ? 'text-purple-600' :
                      'text-slate-600'
                    }`} />
                    <div className="text-left">
                      <div className={`text-2xl font-bold ${
                        isInsufficient ? 'text-red-600' :
                        option.highlighted ? 'text-yellow-600' :
                        option.premium ? 'text-purple-600' :
                        'text-slate-900'
                      }`}>
                        {option.label}
                      </div>
                      <div className={`text-sm ${
                        isInsufficient ? 'text-red-600 font-medium' : 'text-slate-600'
                      }`}>
                        {questionText}
                      </div>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Info */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>How it works:</strong> Each question currently costs <strong>${currentQuestionCost.toFixed(2)}</strong> (grows by 0.78% per entry). 
              Your payment goes toward the bounty prize pool (60%), operational costs (20%), token buyback (10%), and staking rewards (10%).
              {currentQuestionCost > 1 && (
                <span className="block mt-1 text-xs">
                  💡 Tip: Amounts below ${currentQuestionCost.toFixed(2)} are insufficient for a question.
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="w-full px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

