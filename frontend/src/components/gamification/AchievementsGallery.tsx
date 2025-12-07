'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Sparkles, Filter } from 'lucide-react';

interface Achievement {
  id: number;
  achievement_id: string;
  name: string;
  description: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  icon: string;
  unlocked_at: string;
}

interface AchievementsGalleryProps {
  walletAddress: string;
  className?: string;
}

const RARITY_COLORS = {
  common: 'from-gray-400 to-gray-600',
  rare: 'from-blue-400 to-blue-600',
  epic: 'from-purple-400 to-purple-600',
  legendary: 'from-yellow-400 via-orange-500 to-red-600'
};

const RARITY_NAMES = {
  common: 'Common',
  rare: 'Rare',
  epic: 'Epic',
  legendary: 'Legendary'
};

export default function AchievementsGallery({ walletAddress, className = '' }: AchievementsGalleryProps) {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [filter, setFilter] = useState<'all' | 'common' | 'rare' | 'epic' | 'legendary'>('all');
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (!walletAddress) return;

    const fetchAchievements = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/user/achievements/${walletAddress}`);
        if (!response.ok) throw new Error('Failed to fetch achievements');
        
        const data = await response.json();
        setAchievements(data.all || []);
        setTotal(data.total || 0);
      } catch (err) {
        console.error('Error fetching achievements:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAchievements();
  }, [walletAddress]);

  const filteredAchievements = filter === 'all' 
    ? achievements 
    : achievements.filter(a => a.rarity === filter);

  if (loading) {
    return (
      <div className={`grid grid-cols-2 md:grid-cols-4 gap-4 ${className}`}>
        {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
          <div key={i} className="bg-gray-800/50 rounded-xl p-4 animate-pulse">
            <div className="w-16 h-16 bg-gray-700 rounded-full mx-auto mb-2"></div>
            <div className="h-3 bg-gray-700 rounded w-3/4 mx-auto"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-white flex items-center gap-2">
            <Trophy className="w-6 h-6 text-yellow-400" />
            Achievements
          </h3>
          <p className="text-gray-400 text-sm mt-1">
            {total} unlocked
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            <option value="all">All</option>
            <option value="common">Common</option>
            <option value="rare">Rare</option>
            <option value="epic">Epic</option>
            <option value="legendary">Legendary</option>
          </select>
        </div>
      </div>

      {/* Achievements Grid */}
      {filteredAchievements.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          <Trophy className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p>No achievements yet</p>
          <p className="text-sm mt-2">Complete challenges to unlock achievements!</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {filteredAchievements.map((achievement, index) => (
            <motion.div
              key={achievement.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className={`
                bg-gradient-to-br ${RARITY_COLORS[achievement.rarity]}
                rounded-xl p-4 cursor-pointer hover:scale-105 transition-transform
                border-2 border-transparent hover:border-white/20
              `}
              title={`${achievement.name}: ${achievement.description}`}
            >
              <div className="text-center">
                <div className="text-4xl mb-2">{achievement.icon}</div>
                <p className="text-white text-xs font-semibold mb-1 truncate">
                  {achievement.name}
                </p>
                <p className={`text-xs ${
                  achievement.rarity === 'legendary' ? 'text-yellow-200' :
                  achievement.rarity === 'epic' ? 'text-purple-200' :
                  achievement.rarity === 'rare' ? 'text-blue-200' :
                  'text-gray-200'
                }`}>
                  {RARITY_NAMES[achievement.rarity]}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Rarity Breakdown */}
      {achievements.length > 0 && (
        <div className="mt-6 grid grid-cols-4 gap-2">
          {(['common', 'rare', 'epic', 'legendary'] as const).map(rarity => {
            const count = achievements.filter(a => a.rarity === rarity).length;
            return (
              <div
                key={rarity}
                className={`bg-gradient-to-r ${RARITY_COLORS[rarity]} rounded-lg p-3 text-center`}
              >
                <p className="text-white font-bold text-lg">{count}</p>
                <p className="text-white/80 text-xs">{RARITY_NAMES[rarity]}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

