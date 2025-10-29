'use client'

/**
 * Team Dashboard Page
 * 
 * Complete team management interface with stats, members, and chat
 */

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import TeamChat from '@/components/TeamChat'
import { teamAPI } from '@/lib/api/enhancements'

interface Team {
  id: number
  name: string
  description: string
  leader_id: number
  max_members: number
  is_public: boolean
  invite_code: string
  total_pool: number
  total_attempts: number
  total_spent: number
  member_count: number
  is_active: boolean
  created_at: string
}

interface TeamMember {
  user_id: number
  display_name: string
  role: string
  total_contributed: number
  contribution_percentage: number
  joined_at: string
}

interface TeamStats {
  team_id: number
  name: string
  member_count: number
  total_pool: number
  total_attempts: number
  successful_attempts: number
  success_rate: number
  total_spent: number
  avg_cost_per_attempt: number
}

export default function TeamDashboardPage() {
  const params = useParams()
  const teamId = parseInt(params.teamId as string)
  const [userId] = useState(1)
  
  const [team, setTeam] = useState<Team | null>(null)
  const [members, setMembers] = useState<TeamMember[]>([])
  const [stats, setStats] = useState<TeamStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [contributing, setContributing] = useState(false)

  useEffect(() => {
    fetchTeamData()
  }, [teamId])

  const fetchTeamData = async () => {
    try {
      setLoading(true)

      // Fetch team details
      const teamData = await teamAPI.get(teamId)
      setTeam(teamData)

      // Fetch members
      const membersData = await teamAPI.getMembers(teamId)
      setMembers(membersData.members || [])

      // Fetch stats
      const statsData = await teamAPI.getStats(teamId)
      setStats(statsData)
    } catch (err) {
      console.error('Failed to fetch team data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleContribute = async () => {
    const amount = prompt('Enter amount to contribute (USD):')
    if (!amount) return

    const numAmount = parseFloat(amount)
    if (isNaN(numAmount) || numAmount <= 0) {
      alert('Invalid amount')
      return
    }

    setContributing(true)
    try {
      await teamAPI.contribute(teamId, userId, numAmount)
      alert(`✅ Contributed $${numAmount} to team pool!`)
      await fetchTeamData()
    } catch (err: any) {
      alert(`❌ Failed: ${err.message}`)
    } finally {
      setContributing(false)
    }
  }

  const copyInviteCode = () => {
    if (team) {
      navigator.clipboard.writeText(team.invite_code)
      alert(`✅ Invite code copied: ${team.invite_code}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading team...</p>
        </div>
      </div>
    )
  }

  if (!team) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-white mb-4">Team Not Found</h2>
          <a href="/teams" className="text-blue-400 hover:underline">
            ← Back to Teams
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <a href="/teams" className="text-blue-400 hover:underline text-sm mb-2 inline-block">
                ← Back to Teams
              </a>
              <h1 className="text-3xl font-bold text-white">{team.name}</h1>
              {team.description && (
                <p className="text-gray-300 mt-1">{team.description}</p>
              )}
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-400">Invite Code</p>
              <button
                onClick={copyInviteCode}
                className="text-2xl font-mono font-bold text-white hover:text-blue-400 transition-colors"
                title="Click to copy"
              >
                {team.invite_code}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Team Info & Members */}
          <div className="lg:col-span-1 space-y-6">
            {/* Team Stats */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-bold text-white mb-4">Team Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Pool Balance</span>
                  <span className="text-white font-bold">${team.total_pool.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Members</span>
                  <span className="text-white font-bold">{team.member_count}/{team.max_members}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Attempts</span>
                  <span className="text-white font-bold">{team.total_attempts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Spent</span>
                  <span className="text-white font-bold">${team.total_spent.toFixed(2)}</span>
                </div>
                {stats && (
                  <div className="flex justify-between">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="text-green-400 font-bold">{stats.success_rate.toFixed(1)}%</span>
                  </div>
                )}
              </div>

              <button
                onClick={handleContribute}
                disabled={contributing}
                className="w-full mt-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2 rounded-lg font-semibold transition-colors"
              >
                {contributing ? '⏳ Processing...' : '➕ Contribute to Pool'}
              </button>
            </div>

            {/* Members List */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-bold text-white mb-4">Members ({members.length})</h3>
              <div className="space-y-2">
                {members.map((member) => (
                  <div
                    key={member.user_id}
                    className="flex items-center justify-between p-3 bg-gray-700/30 rounded-lg"
                  >
                    <div>
                      <p className="text-white font-medium">{member.display_name}</p>
                      <p className="text-xs text-gray-400">{member.role}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-white">${member.total_contributed.toFixed(2)}</p>
                      <p className="text-xs text-gray-400">
                        {member.contribution_percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Chat */}
          <div className="lg:col-span-2">
            <TeamChat
              teamId={teamId}
              userId={userId}
              currentUserName={members.find(m => m.user_id === userId)?.display_name || 'You'}
            />
          </div>
        </div>
      </div>
    </div>
  )
}








