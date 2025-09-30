'use client'

import { useState } from 'react'

interface AgeVerificationProps {
  onVerified: () => void
  onRejected: () => void
}

export default function AgeVerification({ onVerified, onRejected }: AgeVerificationProps) {
  const [isVerified, setIsVerified] = useState(false)
  const [hasConfirmed, setHasConfirmed] = useState(false)

  const handleVerification = () => {
    if (hasConfirmed) {
      setIsVerified(true)
      setTimeout(() => onVerified(), 500)
    }
  }

  const handleRejection = () => {
    onRejected()
  }

  if (isVerified) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-gradient-to-br from-green-900 to-emerald-900 rounded-lg p-8 max-w-md mx-4 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-white mb-4">Age Verified</h2>
          <p className="text-green-200">You may proceed to the research platform.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 rounded-lg p-8 max-w-2xl mx-4">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="text-6xl mb-4">🔬</div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Educational Research Platform
          </h1>
          <p className="text-xl text-gray-300">
            Billions Bounty - AI Security Research
          </p>
        </div>

        {/* Age Verification */}
        <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-red-400 mb-4 text-center">
            Age Verification Required
          </h2>
          <p className="text-red-200 text-center mb-4">
            You must be at least <strong className="text-white">18 years old</strong> to use this platform.
          </p>
          <p className="text-red-200 text-center text-sm">
            This platform is designed for educational and research purposes only.
          </p>
        </div>

        {/* Educational Purpose Disclaimer */}
        <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-yellow-400 mb-3">
            ⚠️ Important Disclaimers
          </h3>
          <ul className="text-yellow-200 space-y-2 text-sm">
            <li>• This platform is for <strong>educational and research purposes only</strong></li>
            <li>• It is <strong>NOT</strong> a gambling, lottery, or gaming platform</li>
            <li>• All interactions are designed to study AI security and human psychology</li>
            <li>• No real money prizes are awarded through the platform</li>
            <li>• All monetary transactions are for research participation fees only</li>
          </ul>
        </div>

        {/* Research Consent */}
        <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold text-blue-400 mb-3">
            🔬 Research Participation
          </h3>
          <p className="text-blue-200 text-sm mb-3">
            By using this platform, you consent to participate in research activities including:
          </p>
          <ul className="text-blue-200 space-y-1 text-sm ml-4">
            <li>• Analysis of interaction patterns and behaviors</li>
            <li>• Study of manipulation attempt strategies</li>
            <li>• Research on AI security effectiveness</li>
            <li>• Academic publication of anonymized findings</li>
          </ul>
        </div>

        {/* Confirmation Checkbox */}
        <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={hasConfirmed}
              onChange={(e) => setHasConfirmed(e.target.checked)}
              className="mt-1 h-5 w-5 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
            />
            <div className="text-sm text-gray-300">
              <p className="font-semibold mb-2">I confirm that:</p>
              <ul className="space-y-1 ml-4">
                <li>• I am at least 18 years old</li>
                <li>• I understand this is an educational research platform</li>
                <li>• I consent to participate in research activities</li>
                <li>• I have read and understood the Terms of Service and Privacy Policy</li>
                <li>• I understand that no real money prizes are awarded</li>
              </ul>
            </div>
          </label>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={handleVerification}
            disabled={!hasConfirmed}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${
              hasConfirmed
                ? "bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:from-green-600 hover:to-emerald-600 shadow-lg"
                : "bg-gray-600 text-gray-400 cursor-not-allowed"
            }`}
          >
            I am 18+ and Agree to Participate
          </button>
          <button
            onClick={handleRejection}
            className="flex-1 py-3 px-6 rounded-lg font-semibold bg-gray-600 text-white hover:bg-gray-700 transition-all duration-200"
          >
            I am Under 18
          </button>
        </div>

        {/* Footer Links */}
        <div className="text-center mt-6">
          <p className="text-gray-400 text-sm mb-2">
            For more information, please read our:
          </p>
          <div className="flex justify-center space-x-4">
            <a
              href="/terms"
              className="text-blue-400 hover:text-blue-300 text-sm underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Terms of Service
            </a>
            <a
              href="/privacy"
              className="text-blue-400 hover:text-blue-300 text-sm underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              Privacy Policy
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
