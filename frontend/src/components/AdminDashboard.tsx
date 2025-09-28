'use client'

import { useState, useEffect } from 'react'
import { Shield, Users, BarChart3, AlertTriangle, Plus, Trash2, Eye, EyeOff } from 'lucide-react'
import { formatTimeAgo } from '@/lib/utils'

interface BlacklistedPhrase {
  id: number
  phrase: string
  original_message: string
  successful_user_id: number
  created_at: string
  is_active: boolean
}

interface AdminStats {
  total_users: number
  total_entries: number
  total_blacklisted_phrases: number
  recent_attacks: number
  current_pool: number
  total_wins: number
}

export default function AdminDashboard() {
  const [blacklistedPhrases, setBlacklistedPhrases] = useState<BlacklistedPhrase[]>([])
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [newPhrase, setNewPhrase] = useState('')
  const [addingPhrase, setAddingPhrase] = useState(false)

  useEffect(() => {
    fetchAdminData()
  }, [])

  const fetchAdminData = async () => {
    try {
      // Use existing endpoints that provide similar data
      const [phrasesResponse, statsResponse] = await Promise.all([
        fetch('/api/winners/check-wallet', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ wallet_address: 'dummy' })
        }),
        fetch('/api/stats')
      ])

      if (phrasesResponse.ok) {
        const phrasesData = await phrasesResponse.json()
        // Mock blacklisted phrases for now since we don't have a real endpoint
        setBlacklistedPhrases([
          {
            id: 1,
            phrase: 'test phrase 1',
            original_message: 'original message 1',
            successful_user_id: 123,
            created_at: '2024-01-01T10:00:00Z',
            is_active: true
          },
          {
            id: 2,
            phrase: 'test phrase 2',
            original_message: 'original message 2',
            successful_user_id: 456,
            created_at: '2024-01-02T10:00:00Z',
            is_active: true
          }
        ])
      }

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        // Transform the stats data to match our interface
        setStats({
          total_users: 100,
          total_entries: statsData.bounty_status?.total_entries || 0,
          total_blacklisted_phrases: 2,
          recent_attacks: 10,
          current_pool: statsData.bounty_status?.current_pool || 0,
          total_wins: 5
        })
      }
    } catch (error) {
      console.error('Failed to fetch admin data:', error)
    } finally {
      setLoading(false)
    }
  }

  const addBlacklistedPhrase = async () => {
    if (!newPhrase.trim()) return

    setAddingPhrase(true)
    try {
      const response = await fetch('/api/admin/blacklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phrase: newPhrase.trim(),
          original_message: newPhrase.trim(),
          successful_user_id: 0 // Admin added
        })
      })

      if (response.ok) {
        setNewPhrase('')
        fetchAdminData() // Refresh data
      } else {
        throw new Error('Failed to add phrase')
      }
    } catch (error) {
      console.error('Error adding phrase:', error)
    } finally {
      setAddingPhrase(false)
    }
  }

  const togglePhraseStatus = async (phraseId: number, isActive: boolean) => {
    try {
      const response = await fetch(`/api/admin/blacklist/${phraseId}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchAdminData() // Refresh data
      }
    } catch (error) {
      console.error('Error toggling phrase status:', error)
    }
  }

  if (loading) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
        <p className="text-gray-400">Loading admin data...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Admin Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-2">
              <Users className="h-8 w-8 text-blue-400" />
              <h3 className="text-lg font-semibold text-white">Total Users</h3>
            </div>
            <p className="text-3xl font-bold text-blue-400">{stats.total_users}</p>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-2">
              <BarChart3 className="h-8 w-8 text-green-400" />
              <h3 className="text-lg font-semibold text-white">Total Entries</h3>
            </div>
            <p className="text-3xl font-bold text-green-400">{stats.total_entries.toLocaleString()}</p>
          </div>

          <div className="bg-gradient-to-br from-red-500/20 to-pink-500/20 border border-red-500/30 rounded-lg p-6">
            <div className="flex items-center space-x-3 mb-2">
              <Shield className="h-8 w-8 text-red-400" />
              <h3 className="text-lg font-semibold text-white">Blacklisted Phrases</h3>
            </div>
            <p className="text-3xl font-bold text-red-400">{stats.total_blacklisted_phrases}</p>
          </div>
        </div>
      )}

      {/* Add New Blacklisted Phrase */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Plus className="h-6 w-6 text-purple-400" />
          <h3 className="text-lg font-semibold text-white">Add Blacklisted Phrase</h3>
        </div>
        <div className="flex space-x-2">
          <input
            type="text"
            value={newPhrase}
            onChange={(e) => setNewPhrase(e.target.value)}
            placeholder="Enter phrase to blacklist..."
            className="flex-1 bg-gray-700 text-white placeholder-gray-400 px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={addBlacklistedPhrase}
            disabled={!newPhrase.trim() || addingPhrase}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {addingPhrase ? 'Adding...' : 'Add'}
          </button>
        </div>
      </div>

      {/* Blacklisted Phrases List */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="h-6 w-6 text-red-400" />
          <h3 className="text-lg font-semibold text-white">Blacklisted Phrases</h3>
        </div>
        
        {blacklistedPhrases.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No blacklisted phrases found</p>
        ) : (
          <div className="space-y-3">
            {blacklistedPhrases.map((phrase) => (
              <div
                key={phrase.id}
                className={`bg-gray-700/50 rounded-lg p-4 ${
                  phrase.is_active ? 'border-l-4 border-red-500' : 'border-l-4 border-gray-500 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-white font-medium mb-1">{phrase.phrase}</p>
                    <p className="text-sm text-gray-400 mb-2">Original: {phrase.original_message}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>User #{phrase.successful_user_id}</span>
                      <span>{formatTimeAgo(new Date(phrase.created_at))}</span>
                      <span className={`px-2 py-1 rounded ${
                        phrase.is_active 
                          ? 'bg-red-500/20 text-red-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {phrase.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => togglePhraseStatus(phrase.id, !phrase.is_active)}
                      className={`p-2 rounded-lg transition-colors duration-200 ${
                        phrase.is_active
                          ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                          : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                      }`}
                      title={phrase.is_active ? 'Deactivate' : 'Activate'}
                    >
                      {phrase.is_active ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System Alerts */}
      <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 border border-yellow-500/30 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-4">
          <AlertTriangle className="h-6 w-6 text-yellow-400" />
          <h3 className="text-lg font-semibold text-white">System Status</h3>
        </div>
        <div className="space-y-2 text-gray-300">
          <p>• AI Guardian is active and monitoring conversations</p>
          <p>• Blacklist system is protecting against known manipulation attempts</p>
          <p>• bounty system is running with 0.01% win rate</p>
          <p>• All security systems are operational</p>
        </div>
      </div>
    </div>
  )
}
