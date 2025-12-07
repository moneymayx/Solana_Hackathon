'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Star, Zap, Users, TrendingUp, Medal, Crown, Award, Flame } from 'lucide-react';

interface LeaderboardEntry {
  rank: number;
  user_id: number;
  wallet_address: string;
  display_name: string;
  total_points: number;
  question_points: number;
  question_count: number;
  referral_points: number;
  referral_count: number;
  jailbreak_count: number;
  multiplier_applied: number;
  tier: string;
  last_updated: string | null;
}

interface UserRank {
  rank: number;
  total_users: number;
  percentile: number;
  points: {
    total_points: number;
    question_points: number;
    referral_points: number;
    jailbreak_count: number;
    multiplier_applied: number;
  };
  tier: string;
  points_to_next_rank: number;
}

interface PointsLeaderboardProps {
  currentUserWallet?: string;
  limit?: number;
}

const TIER_CONFIG = {
  legendary: {
    name: 'Legendary',
    icon: Crown,
    color: 'from-yellow-400 via-amber-500 to-orange-600',
    textColor: 'text-yellow-400',
    bgColor: 'bg-gradient-to-r from-yellow-500/10 to-orange-500/10',
    borderColor: 'border-yellow-500/50',
    glow: 'shadow-yellow-500/50',
    min: 10000
  },
  diamond: {
    name: 'Diamond',
    icon: Award,
    color: 'from-cyan-400 via-blue-500 to-indigo-600',
    textColor: 'text-cyan-400',
    bgColor: 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10',
    borderColor: 'border-cyan-500/50',
    glow: 'shadow-cyan-500/50',
    min: 5000
  },
  platinum: {
    name: 'Platinum',
    icon: Medal,
    color: 'from-slate-300 via-slate-400 to-slate-500',
    textColor: 'text-slate-300',
    bgColor: 'bg-gradient-to-r from-slate-500/10 to-slate-600/10',
    borderColor: 'border-slate-500/50',
    glow: 'shadow-slate-500/50',
    min: 1000
  },
  gold: {
    name: 'Gold',
    icon: Trophy,
    color: 'from-yellow-300 via-yellow-500 to-yellow-600',
    textColor: 'text-yellow-300',
    bgColor: 'bg-gradient-to-r from-yellow-500/10 to-yellow-600/10',
    borderColor: 'border-yellow-500/50',
    glow: 'shadow-yellow-500/50',
    min: 500
  },
  silver: {
    name: 'Silver',
    icon: Star,
    color: 'from-gray-300 via-gray-400 to-gray-500',
    textColor: 'text-gray-300',
    bgColor: 'bg-gradient-to-r from-gray-500/10 to-gray-600/10',
    borderColor: 'border-gray-500/50',
    glow: 'shadow-gray-500/50',
    min: 100
  },
  bronze: {
    name: 'Bronze',
    icon: Medal,
    color: 'from-orange-400 via-orange-600 to-orange-700',
    textColor: 'text-orange-400',
    bgColor: 'bg-gradient-to-r from-orange-600/10 to-orange-700/10',
    borderColor: 'border-orange-600/50',
    glow: 'shadow-orange-600/50',
    min: 10
  },
  beginner: {
    name: 'Beginner',
    icon: Zap,
    color: 'from-green-400 via-green-500 to-green-600',
    textColor: 'text-green-400',
    bgColor: 'bg-gradient-to-r from-green-500/10 to-green-600/10',
    borderColor: 'border-green-500/50',
    glow: 'shadow-green-500/50',
    min: 0
  }
};

export default function PointsLeaderboard({ currentUserWallet, limit = 100 }: PointsLeaderboardProps) {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userRank, setUserRank] = useState<UserRank | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'all' | 'top10'>('all');

  useEffect(() => {
    fetchLeaderboard();
    if (currentUserWallet) {
      fetchUserRank();
    }
  }, [currentUserWallet, limit]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/leaderboards/points?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to fetch leaderboard');
      
      const data = await response.json();
      setLeaderboard(data.leaderboard || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching leaderboard:', err);
      setError('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserRank = async () => {
    if (!currentUserWallet) return;
    
    try {
      const response = await fetch(`/api/user/points/wallet/${currentUserWallet}`);
      if (response.ok) {
        const data = await response.json();
        setUserRank(data.rank);
      }
    } catch (err) {
      console.error('Error fetching user rank:', err);
    }
  };

  const getTierConfig = (tier: string) => {
    return TIER_CONFIG[tier as keyof typeof TIER_CONFIG] || TIER_CONFIG.beginner;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const displayedLeaderboard = selectedTab === 'top10' 
    ? leaderboard.slice(0, 10) 
    : leaderboard;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent mb-4">
          🏆 Points Leaderboard
        </h1>
        <p className="text-gray-400 text-lg">
          Compete, earn points, and climb the ranks!
        </p>
      </motion.div>

      {/* Points Rules Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl p-6 mb-8"
      >
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Star className="w-5 h-5 text-yellow-400" />
          How Points Work
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-500/20 rounded-lg p-3">
              <Zap className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <p className="text-white font-semibold">1 Point</p>
              <p className="text-gray-400 text-sm">Per Question</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="bg-purple-500/20 rounded-lg p-3">
              <Users className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-white font-semibold">2 Points</p>
              <p className="text-gray-400 text-sm">Per Referral</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="bg-orange-500/20 rounded-lg p-3">
              <Flame className="w-6 h-6 text-orange-400" />
            </div>
            <div>
              <p className="text-white font-semibold">10x Multiplier</p>
              <p className="text-gray-400 text-sm">Per Jailbreak</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Current User Card */}
      {userRank && currentUserWallet && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className={`${getTierConfig(userRank.tier).bgColor} border ${getTierConfig(userRank.tier).borderColor} rounded-xl p-6 shadow-lg ${getTierConfig(userRank.tier).glow} shadow-lg`}>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                {React.createElement(getTierConfig(userRank.tier).icon, {
                  className: `w-12 h-12 ${getTierConfig(userRank.tier).textColor}`
                })}
                <div>
                  <p className="text-gray-400 text-sm">Your Rank</p>
                  <p className="text-3xl font-bold text-white">#{userRank.rank}</p>
                  <p className="text-gray-400 text-sm">Top {userRank.percentile}%</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-gray-400 text-sm">Total Points</p>
                <p className={`text-4xl font-bold ${getTierConfig(userRank.tier).textColor}`}>
                  {formatNumber(userRank.points.total_points)}
                </p>
                <p className={`text-sm font-semibold ${getTierConfig(userRank.tier).textColor}`}>
                  {getTierConfig(userRank.tier).name} Tier
                </p>
              </div>
            </div>
            
            {/* Points Breakdown */}
            <div className="mt-4 pt-4 border-t border-gray-700/50">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-gray-400 text-xs">Questions</p>
                  <p className="text-white font-semibold">{userRank.points.question_points}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Referrals</p>
                  <p className="text-white font-semibold">{userRank.points.referral_points}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Jailbreaks</p>
                  <p className="text-white font-semibold">{userRank.points.jailbreak_count}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-xs">Multiplier</p>
                  <p className="text-orange-400 font-semibold">{userRank.points.multiplier_applied}x</p>
                </div>
              </div>
            </div>

            {userRank.points_to_next_rank > 0 && (
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Next Rank</span>
                  <span className="text-white">{userRank.points_to_next_rank} points away</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`bg-gradient-to-r ${getTierConfig(userRank.tier).color} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${Math.min((userRank.points.total_points / (userRank.points.total_points + userRank.points_to_next_rank)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Tab Selection */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setSelectedTab('all')}
          className={`px-6 py-2 rounded-lg font-semibold transition-all ${
            selectedTab === 'all'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          All Players
        </button>
        <button
          onClick={() => setSelectedTab('top10')}
          className={`px-6 py-2 rounded-lg font-semibold transition-all ${
            selectedTab === 'top10'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          Top 10
        </button>
      </div>

      {/* Leaderboard List */}
      <div className="space-y-3">
        <AnimatePresence>
          {displayedLeaderboard.map((entry, index) => {
            const tierConfig = getTierConfig(entry.tier);
            const isCurrentUser = entry.wallet_address === currentUserWallet;
            const isTopThree = entry.rank <= 3;

            return (
              <motion.div
                key={entry.user_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                className={`
                  ${isCurrentUser ? `${tierConfig.bgColor} border-2 ${tierConfig.borderColor}` : 'bg-gray-800/50 border border-gray-700/50'}
                  ${isTopThree ? `${tierConfig.glow} shadow-lg` : ''}
                  rounded-xl p-4 hover:bg-gray-800/70 transition-all cursor-pointer
                `}
              >
                <div className="flex items-center justify-between flex-wrap gap-4">
                  {/* Rank and User Info */}
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    {/* Rank Badge */}
                    <div className={`
                      ${isTopThree ? `bg-gradient-to-r ${tierConfig.color}` : 'bg-gray-700'}
                      ${isTopThree ? 'w-14 h-14' : 'w-12 h-12'}
                      rounded-full flex items-center justify-center flex-shrink-0
                    `}>
                      {isTopThree ? (
                        <Trophy className="w-7 h-7 text-white" />
                      ) : (
                        <span className="text-white font-bold text-lg">#{entry.rank}</span>
                      )}
                    </div>

                    {/* User Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-white font-semibold truncate">{entry.display_name}</p>
                        {React.createElement(tierConfig.icon, {
                          className: `w-4 h-4 ${tierConfig.textColor} flex-shrink-0`
                        })}
                      </div>
                      <p className="text-gray-400 text-sm truncate">
                        {entry.wallet_address.slice(0, 8)}...{entry.wallet_address.slice(-6)}
                      </p>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex items-center gap-6">
                    <div className="hidden md:flex items-center gap-4 text-sm">
                      <div className="text-center">
                        <p className="text-gray-400 text-xs">Questions</p>
                        <p className="text-white font-semibold">{entry.question_count}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-gray-400 text-xs">Referrals</p>
                        <p className="text-white font-semibold">{entry.referral_count}</p>
                      </div>
                      {entry.jailbreak_count > 0 && (
                        <div className="text-center">
                          <p className="text-gray-400 text-xs">Jailbreaks</p>
                          <p className="text-orange-400 font-semibold flex items-center gap-1">
                            <Flame className="w-3 h-3" />
                            {entry.jailbreak_count}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Total Points */}
                    <div className="text-right">
                      <p className="text-gray-400 text-xs mb-1">{tierConfig.name}</p>
                      <p className={`text-2xl font-bold ${tierConfig.textColor}`}>
                        {formatNumber(entry.total_points)}
                      </p>
                      {entry.multiplier_applied > 1 && (
                        <p className="text-orange-400 text-xs font-semibold">
                          {entry.multiplier_applied}x multiplier
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {error && (
        <div className="text-center text-red-400 mt-8">
          {error}
        </div>
      )}

      {leaderboard.length === 0 && !loading && !error && (
        <div className="text-center text-gray-400 mt-8">
          No leaderboard data available yet. Be the first to earn points!
        </div>
      )}
    </div>
  );
}

