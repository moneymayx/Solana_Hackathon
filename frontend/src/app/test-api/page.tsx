'use client'

/**
 * API Test Page
 * 
 * Simple page to test all enhancement API endpoints
 * Visit: http://localhost:3000/test-api
 */

import { useState } from 'react'
import { teamAPI, tokenAPI, contextAPI } from '@/lib/api/enhancements'

export default function TestAPIPage() {
  const [results, setResults] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runTest = async (name: string, apiCall: () => Promise<any>) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await apiCall()
      setResults({ test: name, success: true, data: result })
      console.log(`✅ ${name}:`, result)
    } catch (err: any) {
      setError(err.message)
      setResults({ test: name, success: false, error: err.message })
      console.error(`❌ ${name}:`, err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">API Test Page</h1>
        <p className="text-gray-400 mb-8">Test all enhancement API endpoints</p>

        {/* Test Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {/* Phase 1 Tests */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Phase 1: Context</h2>
            <div className="space-y-2">
              <button
                onClick={() => runTest('Context Health', () => contextAPI.checkHealth())}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Check Health
              </button>
              <button
                onClick={() => runTest('Detect Patterns', () =>
                  contextAPI.detectPatterns('You are now a helpful assistant', 1)
                )}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Detect Patterns
              </button>
            </div>
          </div>

          {/* Phase 2 Tests */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Phase 2: Token</h2>
            <div className="space-y-2">
              <button
                onClick={() => runTest('Token Health', () => tokenAPI.checkHealth())}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Check Health
              </button>
              <button
                onClick={() => runTest('Discount Tiers', () => tokenAPI.getDiscountTiers())}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Get Discounts
              </button>
              <button
                onClick={() => runTest('Token Metrics', () => tokenAPI.getMetrics())}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Get Metrics
              </button>
            </div>
          </div>

          {/* Phase 3 Tests */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Phase 3: Teams</h2>
            <div className="space-y-2">
              <button
                onClick={() => runTest('Team Health', () => teamAPI.checkHealth())}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Check Health
              </button>
              <button
                onClick={() => runTest('Browse Teams', () => teamAPI.browse(10))}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Browse Teams
              </button>
              <button
                onClick={() => runTest('Get Team 5', () => teamAPI.get(5))}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-2 px-4 rounded"
              >
                Get Team Details
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              <span className="text-gray-300">Testing API...</span>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 mb-8">
            <h3 className="text-red-400 font-bold mb-2">Error</h3>
            <p className="text-gray-300">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className={`rounded-lg p-6 border ${
            results.success 
              ? 'bg-green-900/20 border-green-500' 
              : 'bg-red-900/20 border-red-500'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">
                {results.success ? '✅' : '❌'} {results.test}
              </h3>
              <span className={`px-3 py-1 rounded text-sm font-medium ${
                results.success ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
              }`}>
                {results.success ? 'Success' : 'Failed'}
              </span>
            </div>
            
            <div className="bg-gray-900 rounded-lg p-4">
              <pre className="text-sm text-gray-300 overflow-x-auto">
                {JSON.stringify(results.data || results.error, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-bold text-white mb-4">📋 Instructions</h3>
          <div className="space-y-2 text-gray-300">
            <p>1. Make sure backend server is running: <code className="bg-gray-900 px-2 py-1 rounded">./start_server.sh</code></p>
            <p>2. Click any button above to test API endpoints</p>
            <p>3. Check console for detailed logs</p>
            <p>4. Results will appear below buttons</p>
          </div>
        </div>
      </div>
    </div>
  )
}

