'use client'

/**
 * Teams Page
 * 
 * Browse teams and create new ones
 */

import { useState } from 'react'
import TopNavigation from '@/components/TopNavigation'
import TeamBrowse from '@/components/TeamBrowse'
import { teamAPI } from '@/lib/api/enhancements'

interface TeamCreateResponse {
  team: {
    id: number
    invite_code: string
    name: string
    description?: string
    leader_id: number
    max_members: number
    is_public: boolean
  }
}

export default function TeamsPage() {
  const [userId] = useState(1)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [creating, setCreating] = useState(false)
  
  // Create team form
  const [teamName, setTeamName] = useState('')
  const [teamDescription, setTeamDescription] = useState('')

  const handleCreateTeam = async () => {
    if (!teamName.trim()) {
      alert('Please enter a team name')
      return
    }

    setCreating(true)
    try {
      const result = await teamAPI.create(
        userId,
        teamName,
        teamDescription || undefined,
        5,
        true
      ) as TeamCreateResponse

      alert(`✅ Team created!\nInvite Code: ${result.team.invite_code}`)
      setTeamName('')
      setTeamDescription('')
      setShowCreateForm(false)
      
      // Redirect to team page
      window.location.href = `/teams/${result.team.id}`
    } catch (err: any) {
      alert(`❌ Failed to create team: ${err.message}`)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Standard Header */}
      <TopNavigation />

      {/* Page Header */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Teams</h1>
              <p className="text-slate-300">Collaborate and share resources</p>
            </div>
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              <span>{showCreateForm ? '❌' : '➕'}</span>
              {showCreateForm ? 'Cancel' : 'Create Team'}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Create Team Form */}
        {showCreateForm && (
          <div className="mb-8 bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
            <h3 className="text-xl font-bold text-slate-900 mb-4">Create New Team</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-slate-900 font-medium mb-2">Team Name *</label>
                <input
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="e.g., Elite Jailbreakers"
                  className="w-full bg-white text-slate-900 rounded-lg px-4 py-3 border border-slate-300 focus:border-blue-500 focus:outline-none"
                  maxLength={100}
                />
              </div>

              <div>
                <label className="block text-slate-900 font-medium mb-2">Description (Optional)</label>
                <textarea
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  placeholder="What's your team about?"
                  rows={3}
                  className="w-full bg-white text-slate-900 rounded-lg px-4 py-3 border border-slate-300 focus:border-blue-500 focus:outline-none resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCreateTeam}
                  disabled={creating}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-3 rounded-lg font-semibold transition-colors"
                >
                  {creating ? '⏳ Creating...' : '✅ Create Team'}
                </button>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="px-6 bg-slate-200 hover:bg-slate-300 text-slate-900 py-3 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Browse Teams */}
        <TeamBrowse userId={userId} onJoinTeam={(teamId) => window.location.href = `/teams/${teamId}`} />
      </div>
    </div>
  )
}










