'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, Users, Trophy, Clock, Target, Zap, Shield, Crown, Gift, Plus, UserPlus } from 'lucide-react'
import BountyChatInterface from '@/components/BountyChatInterface'
import GlobalChat from '@/components/GlobalChat'
import WinnerCelebration from '@/components/WinnerCelebration'
import ReferralCodeClaim from '@/components/ReferralCodeClaim'
import TeamBrowse from '@/components/TeamBrowse'
import { cn } from '@/lib/utils'

interface Bounty {
  id: number
  name: string
  description: string
  llm_provider: string
  difficulty_level: string
  current_pool: number
  starting_pool?: number
  total_entries: number
  win_rate: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Message {
  id: number
  user_id: number
  message_type: 'user' | 'assistant'
  content: string
  timestamp: string
  is_winner: boolean
  cost?: number
  model_used?: string
}

export default function BountyPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const bountyId = params.id as string

  const [bounty, setBounty] = useState<Bounty | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isParticipating, setIsParticipating] = useState(false)
  const [showGlobalChat, setShowGlobalChat] = useState(false)
  const [winnerData, setWinnerData] = useState<any>(null)
  const [referralCode, setReferralCode] = useState<string | null>(null)
  const [showReferralEmail, setShowReferralEmail] = useState(false)
  const [showTeamOptions, setShowTeamOptions] = useState(false)
  const [userTeam, setUserTeam] = useState<any>(null)
  const [userId] = useState(1) // Mock user ID - in production, get from auth

  // Check for action parameter and referral code in URL
  useEffect(() => {
    // Check for action parameter to determine initial view
    const action = searchParams.get('action')
    if (action === 'watch') {
      setShowGlobalChat(true) // Show watch mode
    } else if (action === 'beat') {
      setShowGlobalChat(false) // Show participate mode
    }
    
    // Check for referral code
    const code = searchParams.get('ref')
    if (code) {
      setReferralCode(code)
      setShowReferralEmail(true)
    }
  }, [searchParams])

  // Fetch bounty details
  const fetchBounty = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/bounty/${bountyId}`)
      const data = await response.json()
      
      if (data.success) {
        setBounty(data.bounty)
      } else {
        setError('Bounty not found')
      }
    } catch (err) {
      setError('Failed to load bounty')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchBounty()
  }, [bountyId])

  const handleWinner = (winnerData: any) => {
    setWinnerData(winnerData)
    console.log('Winner detected:', winnerData)
  }

  const getDifficultyIcon = (difficulty: string | undefined) => {
    if (!difficulty) return <Target className="h-5 w-5 text-slate-600" />
    
    switch (difficulty.toLowerCase()) {
      case 'expert':
        return <Crown className="h-5 w-5 text-red-600" />
      case 'hard':
        return <Zap className="h-5 w-5 text-orange-600" />
      case 'medium':
        return <Target className="h-5 w-5 text-blue-600" />
      case 'easy':
        return <Shield className="h-5 w-5 text-emerald-600" />
      default:
        return <Target className="h-5 w-5 text-slate-600" />
    }
  }

  const getDifficultyColor = (difficulty: string | undefined) => {
    if (!difficulty) return 'text-slate-600 bg-slate-100 border-slate-300'
    
    switch (difficulty.toLowerCase()) {
      case 'expert':
        return 'text-red-600 bg-red-100 border-red-300'
      case 'hard':
        return 'text-orange-600 bg-orange-100 border-orange-300'
      case 'medium':
        return 'text-blue-600 bg-blue-100 border-blue-300'
      case 'easy':
        return 'text-emerald-600 bg-emerald-100 border-emerald-300'
      default:
        return 'text-slate-600 bg-slate-100 border-slate-300'
    }
  }

  const getProviderIcon = (provider: string) => {
    const providerIcons = {
      claude: '/images/logos/claude-ai.svg',
      'gpt-4': '/images/logos/gpt-4.svg',
      gemini: '/images/logos/gemini-ai.svg',
      llama: '/images/logos/llama-ai.svg'
    }
    
    return providerIcons[provider as keyof typeof providerIcons] || '/images/logos/claude-ai.svg'
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading bounty...</p>
        </div>
      </div>
    )
  }

  if (error || !bounty) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Bounty Not Found</h1>
          <p className="text-slate-600 mb-6">{error || 'This bounty does not exist'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white rounded-lg hover:from-yellow-500 hover:to-orange-600"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/')}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-6 w-6" />
              </button>
              <div className="flex items-center space-x-3">
                <img 
                  src={getProviderIcon(bounty.llm_provider)} 
                  alt={`${bounty.llm_provider} logo`}
                  className="w-8 h-8"
                />
                <div>
                  <h1 className="text-2xl font-bold">{bounty.name}</h1>
                  <p className="text-slate-300">{bounty.description}</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-3xl font-bold text-yellow-400">
                  ${bounty.current_pool.toLocaleString()}
                </div>
                <div className="text-sm text-slate-300">Prize Pool</div>
              </div>
              <div className={cn(
                "px-3 py-1 rounded-full border text-sm font-medium flex items-center space-x-1",
                getDifficultyColor(bounty.difficulty_level)
              )}>
                {getDifficultyIcon(bounty.difficulty_level)}
                <span className="capitalize">{bounty.difficulty_level}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Section */}
          <div className="lg:col-span-2">
            <div className="h-[600px]">
              {showGlobalChat ? (
                <GlobalChat
                  bountyId={bounty.id}
                  bountyName={bounty.name}
                  isWatching={true}
                />
              ) : (
                <BountyChatInterface
                  bountyId={bounty.id}
                  bountyName={bounty.name}
                  onWinner={handleWinner}
                />
              )}
            </div>
            
            {/* Referral Email Collection Box */}
            {showReferralEmail && referralCode && (
              <div className="mt-4">
                <ReferralCodeClaim 
                  referralCode={referralCode}
                  onClaimed={() => {
                    setShowReferralEmail(false)
                    window.location.reload()
                  }}
                />
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Bounty Stats */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Bounty Stats</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Starting Bounty</span>
                  <span className="text-slate-900">
                    ${bounty.starting_pool?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Total Entries</span>
                  <span className="text-slate-900">{bounty.total_entries}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Bounty Increase per Question</span>
                  <span className="text-slate-900">0.78%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">Current Bounty</span>
                  <span className="font-bold text-emerald-600">
                    ${bounty.current_pool.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">Status</span>
                  <span className={cn(
                    "px-2 py-1 rounded-full text-xs font-medium",
                    bounty.is_active 
                      ? "bg-emerald-100 text-emerald-600" 
                      : "bg-slate-100 text-slate-600"
                  )}>
                    {bounty.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            {/* Team Section */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Team Collaboration
              </h3>
              
              {userTeam ? (
                <div className="space-y-3">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium text-green-800">Team Member</span>
                    </div>
                    <p className="text-sm text-green-700">{userTeam.team_name}</p>
                    <p className="text-xs text-green-600">Pool: ${userTeam.total_pool?.toFixed(2) || '0'}</p>
                  </div>
                  
                  <button
                    onClick={() => setShowTeamOptions(true)}
                    className="w-full px-4 py-2 text-sm border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium"
                  >
                    Manage Team
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-slate-600 mb-3">
                    Join a team to pool resources and share strategies for this bounty.
                  </p>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setShowTeamOptions(true)}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm flex items-center justify-center space-x-2"
                    >
                      <UserPlus className="h-4 w-4" />
                      <span>Join Team</span>
                    </button>
                    
                    <button
                      onClick={() => setShowTeamOptions(true)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-sm flex items-center justify-center space-x-2"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Create Team</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => setShowGlobalChat(!showGlobalChat)}
                  className={cn(
                    "w-full px-4 py-3 rounded-lg font-medium transition-all",
                    showGlobalChat 
                      ? "bg-gradient-to-r from-yellow-400 to-orange-500 text-white hover:from-yellow-500 hover:to-orange-600"
                      : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                  )}
                >
                  {showGlobalChat ? 'Beat the Bot' : 'Watch the Madness'}
                </button>
                
                <button className="w-full px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium">
                  View Rules
                </button>
              </div>
            </div>

            {/* Recent Winners */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-lg">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Winners</h3>
              <div className="text-center text-slate-500 py-8">
                <Trophy className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                <p className="text-sm">No winners yet</p>
                <p className="text-xs text-slate-400">Be the first to beat this AI!</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Winner Celebration Modal */}
      {winnerData && (
        <WinnerCelebration
          winnerData={winnerData}
          onClose={() => setWinnerData(null)}
        />
      )}

      {/* Team Options Modal */}
      {showTeamOptions && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Team Options</h2>
              <button
                onClick={() => setShowTeamOptions(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <TeamBrowse 
                userId={userId}
                onJoinTeam={(teamId) => {
                  console.log('Joined team:', teamId)
                  setUserTeam({ team_id: teamId, team_name: 'Team Name', total_pool: 0 })
                  setShowTeamOptions(false)
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
