'use client'

/**
 * Teams Page
 * 
 * Browse teams and create new ones
 */

import { useState } from 'react'
import TeamBrowse from '@/components/TeamBrowse'
import { teamAPI } from '@/lib/api/enhancements'

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
      )

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
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Teams</h1>
              <p className="text-gray-300">Collaborate and share resources</p>
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
      <div className="container mx-auto px-4 py-8">
        {/* Create Team Form */}
        {showCreateForm && (
          <div className="mb-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4">Create New Team</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-white font-medium mb-2">Team Name *</label>
                <input
                  type="text"
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  placeholder="e.g., Elite Jailbreakers"
                  className="w-full bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500 focus:outline-none"
                  maxLength={100}
                />
              </div>

              <div>
                <label className="block text-white font-medium mb-2">Description (Optional)</label>
                <textarea
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  placeholder="What's your team about?"
                  rows={3}
                  className="w-full bg-gray-700 text-white rounded-lg px-4 py-3 border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
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
                  className="px-6 bg-gray-700 hover:bg-gray-600 text-white py-3 rounded-lg font-medium transition-colors"
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










