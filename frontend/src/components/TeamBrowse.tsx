'use client'

/**
 * Team Browse Component
 * 
 * Browse and join public teams
 */

import { useState, useEffect } from 'react'
import { teamAPI } from '@/lib/api/enhancements'

interface Team {
  id: number
  name: string
  description: string
  leader_id: number
  max_members: number
  total_pool: number
  total_attempts: number
  member_count: number
  created_at: string
}

interface TeamBrowseProps {
  userId: number
  onJoinTeam?: (teamId: number) => void
}

export default function TeamBrowse({ userId, onJoinTeam }: TeamBrowseProps) {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [joining, setJoining] = useState<number | null>(null)
  const [inviteCode, setInviteCode] = useState('')

  useEffect(() => {
    fetchTeams()
  }, [])

  const fetchTeams = async () => {
    try {
      setLoading(true)
      const data = await teamAPI.browse(50)
      setTeams(data.teams || [])
    } catch (err) {
      console.error('Failed to fetch teams:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleJoinByCode = async () => {
    if (!inviteCode.trim()) {
      alert('Please enter an invite code')
      return
    }

    try {
      const result = await teamAPI.joinByCode(inviteCode, userId)
      alert(`✅ Successfully joined ${result.membership.team_name}!`)
      setInviteCode('')
      await fetchTeams()
      
      if (onJoinTeam) {
        onJoinTeam(result.membership.team_id)
      }
    } catch (err: any) {
      alert(`❌ Failed to join: ${err.message}`)
    }
  }

  const handleViewTeam = (teamId: number) => {
    window.location.href = `/teams/${teamId}`
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-gray-700 rounded-lg"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Join by Code */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-xl font-bold text-white mb-4">Join Team by Invite Code</h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
            placeholder="Enter invite code (e.g., ABC12XYZ)"
            className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500 focus:outline-none font-mono"
            maxLength={8}
          />
          <button
            onClick={handleJoinByCode}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Join Team
          </button>
        </div>
      </div>

      {/* Teams List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">Public Teams ({teams.length})</h3>
          <button
            onClick={fetchTeams}
            className="text-blue-400 hover:text-blue-300 text-sm"
          >
            🔄 Refresh
          </button>
        </div>

        {teams.length === 0 ? (
          <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
            <div className="text-5xl mb-4">👥</div>
            <p className="text-white font-medium mb-2">No public teams yet</p>
            <p className="text-gray-400">Be the first to create one!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {teams.map((team) => (
              <div
                key={team.id}
                className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-white mb-2">{team.name}</h4>
                    {team.description && (
                      <p className="text-gray-400 mb-4">{team.description}</p>
                    )}
                    
                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">👥</span>
                        <span className="text-white">
                          {team.member_count}/{team.max_members} members
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">💰</span>
                        <span className="text-white">
                          ${team.total_pool.toFixed(2)} pool
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">🎯</span>
                        <span className="text-white">
                          {team.total_attempts} attempts
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleViewTeam(team.id)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors ml-4"
                  >
                    View Team
                  </button>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-700 flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    Created {new Date(team.created_at).toLocaleDateString()}
                  </p>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    team.member_count < team.max_members
                      ? 'bg-green-900/30 text-green-400 border border-green-500/30'
                      : 'bg-gray-700 text-gray-400'
                  }`}>
                    {team.member_count < team.max_members ? '✅ Open' : '🔒 Full'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}










