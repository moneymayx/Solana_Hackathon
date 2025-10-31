'use client'

/**
 * Team Browse Component
 * 
 * Browse and join public teams
 */

import { useState, useEffect } from 'react'
import { teamAPI, TeamSummary, TeamJoinResponse } from '@/lib/api/enhancements'

interface TeamBrowseProps {
  userId: number
  onJoinTeam?: (teamId: number) => void
}

export default function TeamBrowse({ userId, onJoinTeam }: TeamBrowseProps) {
  const [teams, setTeams] = useState<TeamSummary[]>([])
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
      setTeams(data.teams ?? [])
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
      const result: TeamJoinResponse = await teamAPI.joinByCode(inviteCode, userId)
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
          <div key={i} className="h-32 bg-slate-200 rounded-lg"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Join by Code */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
        <h3 className="text-xl font-bold text-slate-900 mb-4">Join Team by Invite Code</h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={inviteCode}
            onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
            placeholder="Enter invite code (e.g., ABC12XYZ)"
            className="flex-1 bg-white rounded-lg px-4 py-3 border border-slate-300 focus:border-blue-500 focus:outline-none font-mono placeholder:text-slate-400"
            style={{ color: '#000000' }}
            maxLength={8}
          />
          <button
            onClick={handleJoinByCode}
            className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
          >
            Join Team
          </button>
        </div>
      </div>

      {/* Teams List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-slate-900">Public Teams ({teams.length})</h3>
          <button
            onClick={fetchTeams}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            🔄 Refresh
          </button>
        </div>

        {teams.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 shadow-2xl shadow-slate-900/10 text-center">
            <div className="text-5xl mb-4">👥</div>
            <p className="text-slate-900 font-medium mb-2">No public teams yet</p>
            <p className="text-slate-600">Be the first to create one!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {teams.map((team) => (
              <div
                key={team.id}
                className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10 hover:shadow-2xl hover:shadow-slate-900/20 transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-slate-900 mb-2">{team.name}</h4>
                    {team.description && (
                      <p className="text-slate-600 mb-4">{team.description}</p>
                    )}
                    
                    <div className="flex items-center gap-6 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500">👥</span>
                        <span className="text-slate-900">
                          {team.member_count}/{team.max_members} members
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500">💰</span>
                        <span className="text-slate-900">
                          ${team.total_pool.toFixed(2)} pool
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500">🎯</span>
                        <span className="text-slate-900">
                          {team.total_attempts} attempts
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleViewTeam(team.id)}
                    className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white px-6 py-2 rounded-lg font-medium transition-colors ml-4"
                  >
                    View Team
                  </button>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-200 flex items-center justify-between">
                  <p className="text-xs text-slate-500">
                    Created {new Date(team.created_at).toLocaleDateString()}
                  </p>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    team.member_count < team.max_members
                      ? 'bg-emerald-100 text-emerald-600 border border-emerald-200'
                      : 'bg-slate-200 text-slate-600'
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










