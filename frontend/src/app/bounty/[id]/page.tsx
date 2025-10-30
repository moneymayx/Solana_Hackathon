'use client'

import { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, Users, Trophy, Clock, Target, Zap, Shield, Crown, Gift, Plus, UserPlus } from 'lucide-react'
import BountyChatInterface from '@/components/BountyChatInterface'
import GlobalChat from '@/components/GlobalChat'
import WinnerCelebration from '@/components/WinnerCelebration'
import ReferralCodeClaim from '@/components/ReferralCodeClaim'
import TeamBrowse from '@/components/TeamBrowse'
import CreateTeamModal from '@/components/CreateTeamModal'
import RulesModal from '@/components/RulesModal'
import TopNavigation from '@/components/TopNavigation'
import { cn } from '@/lib/utils'
import { Bounty, fetchBountyById } from '@/lib/api/bounties'

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

// Helper function to get starting bounty based on difficulty
const getStartingBounty = (difficulty: string): number => {
  const difficultyMap: Record<string, number> = {
    'easy': 500,
    'medium': 2500,
    'hard': 5000,
    'expert': 10000
  }
  return difficultyMap[difficulty.toLowerCase()] || 500
}

// Helper function to get starting question cost based on difficulty
const getStartingQuestionCost = (difficulty: string): number => {
  const difficultyMap: Record<string, number> = {
    'easy': 0.50,
    'medium': 2.50,
    'hard': 5.00,
    'expert': 10.00
  }
  return difficultyMap[difficulty.toLowerCase()] || 0.50
}

// Helper function to calculate current question cost
const getCurrentQuestionCost = (startingCost: number, totalEntries: number): number => {
  return startingCost * Math.pow(1.0078, totalEntries)
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
  const [showCreateTeamModal, setShowCreateTeamModal] = useState(false)
  const [showRulesModal, setShowRulesModal] = useState(false)
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
  const loadBounty = useCallback(async () => {
    try {
      const data = await fetchBountyById(bountyId)
      setBounty(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load bounty')
    } finally {
      setIsLoading(false)
    }
  }, [bountyId])

  useEffect(() => {
    loadBounty()
  }, [loadBounty])

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
      {/* Standard Header */}
      <TopNavigation />

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
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Bounty Stats</h3>
              <div className="space-y-4">
                {/* Total Entries */}
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Total Entries</span>
                  <span className="text-slate-900">{bounty.total_entries}</span>
                </div>
                
                {/* Starting Bounty */}
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Starting Bounty</span>
                  <span className="text-slate-900">
                    ${getStartingBounty(bounty.difficulty_level).toLocaleString()}
                  </span>
                </div>
                
                {/* Starting Question Cost */}
                <div className="flex justify-between items-center">
                  <span className="text-slate-900">Starting Question Cost</span>
                  <span className="text-slate-900">
                    ${getStartingQuestionCost(bounty.difficulty_level).toFixed(2)}
                  </span>
                </div>
                
                {/* Current Bounty */}
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">Current Bounty</span>
                  <span className="font-bold text-emerald-600">
                    ${bounty.current_pool.toLocaleString()}
                  </span>
                </div>
                
                {/* Current Question Cost */}
                <div className="flex justify-between items-center">
                  <span className="text-slate-600">Current Question Cost</span>
                  <span className="font-bold text-emerald-600">
                    ${getCurrentQuestionCost(
                      getStartingQuestionCost(bounty.difficulty_level),
                      bounty.total_entries
                    ).toFixed(2)}
                  </span>
                </div>
                
                {/* Status */}
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

            {/* Action Buttons */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
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
                
                <button 
                  onClick={() => setShowRulesModal(true)}
                  className="w-full px-4 py-3 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium"
                >
                  View Rules
                </button>
              </div>
            </div>

            {/* Team Section */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
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
                      onClick={() => setShowCreateTeamModal(true)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-sm flex items-center justify-center space-x-2"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Create Team</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Winning Prompts */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-2xl shadow-slate-900/10">
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <Trophy className="h-5 w-5 mr-2" />
                Unusable Winning Prompts
              </h3>
              <div className="space-y-3">
                <div className="text-sm text-slate-500 italic">
                  Prompts that successfully jailbroke the bot will appear here once a winner is declared.
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 shadow-md shadow-slate-900/5">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xs font-bold">1</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900 mb-1">Example Winning Prompt</p>
                      <p className="text-xs text-slate-600 italic">
                        "This is an example of what a successful jailbreak prompt looks like. Each prompt that successfully convinced the AI to transfer funds will be displayed here for reference."
                      </p>
                    </div>
                  </div>
                </div>
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
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[80vh] overflow-hidden shadow-2xl shadow-slate-900/20">
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

      {/* Create Team Modal */}
      {showCreateTeamModal && (
        <CreateTeamModal
          userId={userId}
          onClose={() => setShowCreateTeamModal(false)}
          onSuccess={(team) => {
            console.log('Team created:', team)
            setUserTeam({ team_id: team.id, team_name: team.name, total_pool: 0 })
            setShowCreateTeamModal(false)
          }}
        />
      )}

      {/* Rules Modal */}
      {showRulesModal && (
        <RulesModal
          onClose={() => setShowRulesModal(false)}
        />
      )}
    </div>
  )
}
