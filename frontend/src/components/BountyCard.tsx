'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  Target, 
  Users, 
  TrendingUp, 
  Clock,
  Zap,
  Shield,
  Crown
} from 'lucide-react'
import ActivityTracker from './ActivityTracker'
import { cn } from '@/lib/utils'

interface Bounty {
  id: number
  name: string
  llm_provider: string
  current_pool: number
  total_entries: number
  win_rate: number
  difficulty_level: string
  is_active: boolean
}

interface BountyCardProps {
  bounty: Bounty
  className?: string
}

const difficultyConfig = {
  easy: {
    label: 'Easy',
    color: 'text-emerald-600',
    bgColor: 'bg-emerald-100',
    borderColor: 'border-emerald-300',
    icon: Shield
  },
  medium: {
    label: 'Medium',
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-300',
    icon: Target
  },
  hard: {
    label: 'Hard',
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
    borderColor: 'border-orange-300',
    icon: Zap
  },
  expert: {
    label: 'Expert',
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
    icon: Crown
  }
}

const providerIcons = {
  claude: '/images/logos/claude-ai.svg',
  'gpt-4': '/images/logos/gpt-4.svg',
  gemini: '/images/logos/gemini-ai.svg',
  llama: '/images/logos/llama-ai.svg'
}

const providerColors = {
  claude: {
    primary: '#8B5CF6',
    secondary: '#A78BFA',
    light: '#F3F4F6',
    border: '#8B5CF6',
    text: '#8B5CF6'
  },
  'gpt-4': {
    primary: '#10B981',
    secondary: '#34D399',
    light: '#F0FDF4',
    border: '#10B981',
    text: '#10B981'
  },
  gemini: {
    primary: '#3B82F6',
    secondary: '#60A5FA',
    light: '#EFF6FF',
    border: '#3B82F6',
    text: '#3B82F6'
  },
  llama: {
    primary: '#F97316',
    secondary: '#FB923C',
    light: '#FFF7ED',
    border: '#F97316',
    text: '#F97316'
  }
}

export default function BountyCard({ bounty, className }: BountyCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const difficulty = difficultyConfig[bounty.difficulty_level as keyof typeof difficultyConfig] || difficultyConfig.medium
  const DifficultyIcon = difficulty.icon
  const colors = providerColors[bounty.llm_provider as keyof typeof providerColors] || providerColors.claude
  
  // Check if activity tracker feature is enabled
  const isActivityTrackerEnabled = process.env.NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER === 'true'

  return (
    <div
      className={cn(
        "group relative bg-white border-2 rounded-xl p-6 transition-all duration-200 hover:scale-105 hover:-translate-y-1",
        "shadow-lg hover:shadow-xl",
        "h-64 flex flex-col",
        "will-change-transform", // Optimize for animations
        className
      )}
      style={{
        borderColor: colors.border,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
        {/* Glow effect on hover */}
        {isHovered && (
          <div 
            className="absolute inset-0 rounded-xl pointer-events-none"
            style={{ background: `linear-gradient(135deg, ${colors.primary}15, ${colors.secondary}15)` }}
          />
        )}

        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">
              <img 
                src={providerIcons[bounty.llm_provider as keyof typeof providerIcons] || '/images/logos/claude-ai.svg'} 
                alt={`${bounty.llm_provider} logo`}
                className="w-6 h-6"
                loading="eager"
              />
            </div>
            <div>
              <h3 
                className="font-bold transition-colors whitespace-nowrap"
                style={{ 
                  color: colors.text,
                  fontSize: 'clamp(0.75rem, 2vw, 1rem)',
                  lineHeight: '1.2'
                }}
              >
                {bounty.name}
              </h3>
              <p className="text-gray-600 text-sm capitalize">
                {bounty.llm_provider}
              </p>
            </div>
          </div>

          {/* Difficulty Badge */}
          <div className={cn(
            "flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium",
            difficulty.bgColor,
            difficulty.borderColor,
            "border"
          )}>
            <DifficultyIcon className={cn("h-3 w-3", difficulty.color)} />
            <span className={difficulty.color}>{difficulty.label}</span>
          </div>
        </div>

        {/* Bounty Amount - Centered */}
        <div className="mb-3 flex-grow flex items-center justify-center">
          <div className="text-center">
            <div 
              className="text-5xl font-bold text-gray-900 mb-1"
              style={{ fontFamily: 'var(--font-gravitas), cursive' }}
            >
              ${bounty.current_pool.toLocaleString()}
            </div>
            <div className="text-xs text-gray-500">Bounty Amount</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between space-x-3 mt-auto">
          <Link href={`/bounty/${bounty.id}?action=beat`} className="flex-1">
            <button 
              className="w-full px-4 py-3 rounded-lg text-lg font-bold transition-all duration-200 text-white border-2 shadow-xl hover:shadow-xl hover:scale-105 transform-gpu whitespace-nowrap"
              style={{
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
                borderColor: colors.primary,
                boxShadow: `0 20px 40px -12px ${colors.primary}50, 0 10px 20px -8px ${colors.primary}30, 0 0 0 1px ${colors.primary}25`
              }}
            >
              Beat the Bot
            </button>
          </Link>

          <Link href={`/bounty/${bounty.id}?action=watch`} className="flex-1">
            <button className={cn(
              "w-full px-4 py-3 rounded-lg text-lg font-bold transition-all duration-200",
              "bg-gray-100 text-gray-700 border-2 border-gray-300",
              "hover:bg-gray-200 hover:border-gray-400 hover:shadow-xl hover:scale-105",
              "shadow-xl transform-gpu"
            )}
            style={{
              boxShadow: `0 20px 40px -12px ${colors.primary}50, 0 10px 20px -8px ${colors.primary}30, 0 0 0 1px ${colors.primary}25`
            }}>
              Watch
            </button>
          </Link>
        </div>

        {/* Activity Tracker */}
        {isActivityTrackerEnabled && (
          <ActivityTracker bountyId={bounty.id} />
        )}

        {/* Hover Effect Overlay */}
        {isHovered && (
          <div 
            className="absolute inset-0 rounded-xl border-2 pointer-events-none"
            style={{ borderColor: `${colors.primary}50` }}
          />
        )}
      </div>
  )
}
