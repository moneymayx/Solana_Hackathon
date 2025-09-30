"use client"

import React, { useState, useEffect } from 'react'
import { AlertTriangle, Shield, FileText } from 'lucide-react'


export default function RegulatoryCompliance() {
  const [showDisclaimers, setShowDisclaimers] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(false)
  }, [])


  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-700 rounded w-1/3 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-32 bg-gray-700 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Shield className="h-8 w-8 text-blue-400" />
            <h1 className="text-3xl font-bold text-white">Regulatory Compliance & Transparency</h1>
          </div>
          <button
            onClick={() => setShowDisclaimers(!showDisclaimers)}
            className="flex items-center space-x-2 px-4 py-2 bg-yellow-600/20 text-yellow-400 border border-yellow-500/30 rounded-lg hover:bg-yellow-600/30 transition-colors"
          >
            <FileText className="h-4 w-4" />
            <span>{showDisclaimers ? 'Hide' : 'Show'} Disclaimers</span>
          </button>
        </div>

        {/* Risk Warning Banner */}
        <div className="mb-8 p-6 bg-red-500/20 border border-red-500/30 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-6 w-6 text-red-400 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-red-400 mb-2">⚠️ HIGH RISK WARNING</h3>
              <p className="text-red-200 mb-2">
                This is an experimental platform. You may lose 100% of your funds.
                Only participate with money you can afford to lose completely.
              </p>
              <ul className="text-sm text-red-300 space-y-1">
                <li>• No regulatory protection or guarantees</li>
                <li>• Potential for total loss of funds</li>
                <li>• Experimental technology with unknown risks</li>
                <li>• Legal uncertainty in many jurisdictions</li>
              </ul>
            </div>
          </div>
        </div>


        {/* Disclaimers */}
        {showDisclaimers && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-4">Regulatory Disclaimers</h2>
            
            <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-400 mb-3">⚠️ Regulatory Status</h3>
              <div className="text-yellow-200 space-y-2 text-sm">
                <p>This platform is a research project and proof-of-concept demonstration.</p>
                <p>It is NOT a licensed gambling, gaming, or financial services platform.</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Not licensed as a gambling or gaming platform in any jurisdiction</li>
                  <li>Not regulated by any financial services authority</li>
                  <li>Participation is at your own risk</li>
                  <li>No guarantee of winnings or returns</li>
                  <li>Funds may be lost permanently</li>
                </ul>
              </div>
            </div>

            <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-red-400 mb-3">🚨 Risk Warning</h3>
              <div className="text-red-200 space-y-2 text-sm">
                <p>This is a high-risk experimental platform. You may lose 100% of your investment.</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>No guarantee of returns or winnings</li>
                  <li>Smart contract bugs or vulnerabilities</li>
                  <li>Blockchain network failures</li>
                  <li>Regulatory changes may affect platform legality</li>
                  <li>No regulatory protection</li>
                </ul>
              </div>
            </div>

            <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-400 mb-3">📊 Transparency Notice</h3>
              <div className="text-blue-200 space-y-2 text-sm">
                <p>This platform operates with full transparency and fairness:</p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>All transactions recorded on Solana blockchain</li>
                  <li>Smart contracts are open source and auditable</li>
                  <li>No hidden fees or charges</li>
                  <li>Win probability calculated based on current entries</li>
                  <li>Funds locked in smart contracts with no manual intervention</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
