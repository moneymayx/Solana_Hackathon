'use client'

import { useState, useEffect } from 'react'
import { Trophy, Shield, Target, Zap, Crown, Medal, Award, Star, ChevronUp, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ModelDifficulty {
  id: number
  name: string
  provider: string
  rank: number
  difficulty_level: 'expert' | 'hard' | 'medium' | 'easy'
  difficulty_score: number
  attempts_to_break: number
  success_rate: number
  last_tested: string
  status: 'active' | 'testing' | 'maintenance'
  is_highlighted: boolean // Top 4 models that match active bounties
}

interface ModelDifficultyProps {
  className?: string
  limit?: number
}


const difficultyLevelColors = {
  expert: 'text-red-600 bg-red-100 border-red-300',
  hard: 'text-orange-600 bg-orange-100 border-orange-300',
  medium: 'text-blue-600 bg-blue-100 border-blue-300',
  easy: 'text-emerald-600 bg-emerald-100 border-emerald-300'
}

const difficultyIcons = {
  expert: Crown,
  hard: Zap,
  medium: Target,
  easy: Shield
}

const statusColors = {
  active: 'text-green-600 bg-green-100 border-green-300',
  testing: 'text-blue-600 bg-blue-100 border-blue-300',
  maintenance: 'text-orange-600 bg-orange-100 border-orange-300'
}

export default function ModelDifficulty({ className, limit = 10 }: ModelDifficultyProps) {
  const [models, setModels] = useState<ModelDifficulty[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'rank' | 'difficulty' | 'attempts'>('rank')

  // Mock data for now - will be replaced with API call
  // Top 4 models match the active bounties and are highlighted
  const mockModels: ModelDifficulty[] = [
    {
      id: 1,
      name: 'Llama-3-70B',
      provider: 'Meta',
      rank: 1,
      difficulty_level: 'expert',
      difficulty_score: 95.2,
      attempts_to_break: 247,
      success_rate: 0.8,
      last_tested: '2024-01-15T10:30:00Z',
      status: 'active',
      is_highlighted: true // Matches "Llama Legend" bounty (expert)
    },
    {
      id: 2,
      name: 'GPT-4o',
      provider: 'OpenAI',
      rank: 2,
      difficulty_level: 'hard',
      difficulty_score: 92.8,
      attempts_to_break: 198,
      success_rate: 0.75,
      last_tested: '2024-01-15T09:45:00Z',
      status: 'active',
      is_highlighted: true // Matches "GPT-4 Bounty" (hard)
    },
    {
      id: 3,
      name: 'Claude-3.5-Sonnet',
      provider: 'Anthropic',
      rank: 3,
      difficulty_level: 'medium',
      difficulty_score: 89.5,
      attempts_to_break: 156,
      success_rate: 0.72,
      last_tested: '2024-01-15T08:20:00Z',
      status: 'active',
      is_highlighted: true // Matches "Claude Champ" (medium)
    },
    {
      id: 4,
      name: 'Gemini-Pro',
      provider: 'Google',
      rank: 4,
      difficulty_level: 'easy',
      difficulty_score: 85.3,
      attempts_to_break: 134,
      success_rate: 0.68,
      last_tested: '2024-01-15T07:15:00Z',
      status: 'active',
      is_highlighted: true // Matches "Gemini Quest" (easy)
    },
    {
      id: 5,
      name: 'Claude-3-Haiku',
      provider: 'Anthropic',
      rank: 5,
      difficulty_level: 'medium',
      difficulty_score: 82.1,
      attempts_to_break: 112,
      success_rate: 0.65,
      last_tested: '2024-01-15T06:30:00Z',
      status: 'active',
      is_highlighted: false
    },
    {
      id: 6,
      name: 'GPT-3.5-Turbo',
      provider: 'OpenAI',
      rank: 6,
      difficulty_level: 'easy',
      difficulty_score: 78.9,
      attempts_to_break: 98,
      success_rate: 0.62,
      last_tested: '2024-01-15T05:45:00Z',
      status: 'active',
      is_highlighted: false
    },
    {
      id: 7,
      name: 'Gemini-Flash',
      provider: 'Google',
      rank: 7,
      difficulty_level: 'easy',
      difficulty_score: 75.4,
      attempts_to_break: 87,
      success_rate: 0.58,
      last_tested: '2024-01-15T04:20:00Z',
      status: 'maintenance',
      is_highlighted: false
    },
    {
      id: 8,
      name: 'Llama-3-8B',
      provider: 'Meta',
      rank: 8,
      difficulty_level: 'medium',
      difficulty_score: 72.8,
      attempts_to_break: 76,
      success_rate: 0.55,
      last_tested: '2024-01-15T03:15:00Z',
      status: 'active',
      is_highlighted: false
    },
    {
      id: 9,
      name: 'Mistral-Large',
      provider: 'Mistral AI',
      rank: 9,
      difficulty_level: 'hard',
      difficulty_score: 69.2,
      attempts_to_break: 65,
      success_rate: 0.52,
      last_tested: '2024-01-15T02:30:00Z',
      status: 'active',
      is_highlighted: false
    },
    {
      id: 10,
      name: 'Command-R+',
      provider: 'Cohere',
      rank: 10,
      difficulty_level: 'medium',
      difficulty_score: 66.7,
      attempts_to_break: 54,
      success_rate: 0.48,
      last_tested: '2024-01-15T01:45:00Z',
      status: 'active',
      is_highlighted: false
    }
  ]

  const fetchModels = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // TODO: Replace with actual API call
      // const response = await fetch('http://localhost:8000/api/models/difficulty')
      // const data = await response.json()
      
      // For now, use mock data
      setTimeout(() => {
        const sortedModels = [...mockModels].sort((a, b) => {
          switch (sortBy) {
            case 'rank':
              return a.rank - b.rank
            case 'difficulty':
              return b.difficulty_score - a.difficulty_score
            case 'attempts':
              return b.attempts_to_break - a.attempts_to_break
            default:
              return a.rank - b.rank
          }
        })
        
        setModels(sortedModels.slice(0, limit))
        setLoading(false)
      }, 500)
    } catch (err) {
      console.error('Error fetching model difficulty data:', err)
      setError('Failed to load model difficulty rankings')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchModels()
  }, [sortBy, limit])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getDifficultyIcon = (difficultyLevel: string) => {
    const IconComponent = difficultyIcons[difficultyLevel as keyof typeof difficultyIcons] || Shield
    return <IconComponent className="h-4 w-4" />
  }

  if (loading) {
    return (
      <div className={cn("flex items-center justify-center py-12", className)}>
        <div className="flex items-center space-x-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-500"></div>
          <span className="text-slate-600">Loading model rankings...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn("flex flex-col items-center justify-center py-12", className)}>
        <div className="mb-4">
          <img 
            src="/images/logos/claude-ai.svg" 
            alt="AI Model" 
            className="w-16 h-16 mx-auto"
          />
        </div>
        <h3 className="text-slate-900 text-lg font-semibold mb-2">Unable to Load Rankings</h3>
        <p className="text-slate-600 text-center max-w-md mb-4">{error}</p>
        <button
          onClick={fetchModels}
          className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className={cn("bg-white border border-slate-200 rounded-xl p-6 shadow-lg shadow-slate-200/30", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg">
            <Trophy className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Model Difficulty Rankings</h2>
            <p className="text-slate-600">Top {limit} AI models ranked by resistance to breaking</p>
          </div>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-slate-600">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'rank' | 'difficulty' | 'attempts')}
            className="px-3 py-1 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            <option value="rank">Rank</option>
            <option value="difficulty">Difficulty Score</option>
            <option value="attempts">Attempts to Break</option>
          </select>
        </div>
      </div>

      {/* Rankings List */}
      <div className="space-y-3">
        {models.map((model, index) => {
          const difficultyColor = difficultyLevelColors[model.difficulty_level] || 'text-slate-600 bg-slate-100 border-slate-300'
          const statusColor = statusColors[model.status] || 'text-slate-600 bg-slate-100 border-slate-300'
          
          return (
            <div
              key={model.id}
              className={cn(
                "flex items-center justify-between p-4 rounded-lg border-2 transition-all duration-200 hover:shadow-md",
                model.is_highlighted 
                  ? "bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200 hover:border-yellow-300 shadow-lg shadow-yellow-200/30" 
                  : "bg-slate-50 border-slate-200 hover:border-slate-300"
              )}
            >
              {/* Rank and Model Info */}
              <div className="flex items-center space-x-4">
                <div className={cn(
                  "flex items-center justify-center w-10 h-10 rounded-full border-2 font-bold text-sm",
                  model.is_highlighted ? "bg-gradient-to-r from-yellow-400 to-orange-500 text-white border-yellow-500" : "bg-slate-200 text-slate-700 border-slate-300"
                )}>
                  {model.rank}
                </div>
                
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className={cn(
                      "text-lg font-semibold",
                      model.is_highlighted ? "text-slate-900" : "text-slate-900"
                    )}>
                      {model.name}
                    </h3>
                    <span className={cn(
                      "px-2 py-1 rounded-full text-xs font-medium border",
                      statusColor
                    )}>
                      {model.status}
                    </span>
                    {model.is_highlighted && (
                      <span className="px-2 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-yellow-400 to-orange-500 text-white border border-yellow-500">
                        ACTIVE BOUNTY
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <p className="text-slate-600 text-sm">{model.provider}</p>
                    <span className={cn(
                      "px-2 py-1 rounded-full text-xs font-medium border flex items-center space-x-1",
                      difficultyColor
                    )}>
                      {getDifficultyIcon(model.difficulty_level)}
                      <span className="capitalize">{model.difficulty_level}</span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{model.difficulty_score.toFixed(1)}</div>
                  <div className="text-xs text-slate-600">Difficulty Score</div>
                </div>
                
                <div className="text-center">
                  <div className="text-xl font-semibold text-slate-900">{model.attempts_to_break}</div>
                  <div className="text-xs text-slate-600">Attempts to Break</div>
                </div>
                
                <div className="text-center">
                  <div className="text-lg font-semibold text-slate-900">{(model.success_rate * 100).toFixed(0)}%</div>
                  <div className="text-xs text-slate-600">Success Rate</div>
                </div>
                
                <div className="text-center">
                  <div className="text-sm text-slate-600">{formatDate(model.last_tested)}</div>
                  <div className="text-xs text-slate-500">Last Tested</div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-slate-200">
        <div className="flex items-center justify-between text-sm text-slate-600">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Active Testing</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span>Currently Testing</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
              <span>Maintenance</span>
            </div>
          </div>
          <button className="text-yellow-600 hover:text-yellow-700 font-medium">
            View Full Rankings →
          </button>
        </div>
      </div>
    </div>
  )
}
