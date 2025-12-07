'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Flame, Calendar, TrendingUp } from 'lucide-react';

interface StreakInfo {
  current_streak: number;
  longest_streak: number;
  total_bonus_points: number;
  is_active: boolean;
  last_activity_date: string | null;
  next_bonus: {
    points: number;
    name: string;
  } | null;
  days_until_next_bonus: number | null;
}

interface StreakDisplayProps {
  walletAddress: string;
  className?: string;
}

export default function StreakDisplay({ walletAddress, className = '' }: StreakDisplayProps) {
  const [streakInfo, setStreakInfo] = useState<StreakInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!walletAddress) return;

    const fetchStreak = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/user/streak/${walletAddress}`);
        if (!response.ok) throw new Error('Failed to fetch streak');
        
        const data = await response.json();
        setStreakInfo(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching streak:', err);
        setError('Failed to load streak');
      } finally {
        setLoading(false);
      }
    };

    fetchStreak();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStreak, 30000);
    return () => clearInterval(interval);
  }, [walletAddress]);

  if (loading) {
    return (
      <div className={`bg-gray-800/50 rounded-xl p-4 ${className}`}>
        <div className="animate-pulse flex items-center gap-3">
          <div className="w-12 h-12 bg-gray-700 rounded-full"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-700 rounded w-24 mb-2"></div>
            <div className="h-3 bg-gray-700 rounded w-32"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !streakInfo) {
    return null; // Fail silently
  }

  const { current_streak, longest_streak, next_bonus, days_until_next_bonus, is_active } = streakInfo;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-gradient-to-r from-orange-900/30 to-red-900/30 border border-orange-500/30 rounded-xl p-4 ${className}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`relative ${is_active ? 'animate-pulse' : ''}`}>
            <Flame className={`w-10 h-10 ${is_active ? 'text-orange-400' : 'text-gray-500'}`} />
            {is_active && (
              <motion.div
                className="absolute inset-0 bg-orange-400 rounded-full blur-md opacity-50"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            )}
          </div>
          <div>
            <p className="text-gray-400 text-sm">Current Streak</p>
            <p className={`text-2xl font-bold ${is_active ? 'text-orange-400' : 'text-gray-500'}`}>
              {current_streak} {current_streak === 1 ? 'day' : 'days'}
            </p>
            {!is_active && (
              <p className="text-xs text-red-400 mt-1">⚠️ Streak inactive - log in today!</p>
            )}
          </div>
        </div>

        <div className="text-right">
          <p className="text-gray-400 text-xs mb-1">Best Streak</p>
          <p className="text-lg font-semibold text-white">{longest_streak} days</p>
        </div>
      </div>

      {next_bonus && days_until_next_bonus !== null && (
        <div className="mt-4 pt-4 border-t border-orange-500/20">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              <span className="text-gray-300">Next Bonus</span>
            </div>
            <div className="text-right">
              <p className="text-orange-400 font-semibold">{next_bonus.name}</p>
              <p className="text-gray-400 text-xs">
                {days_until_next_bonus} {days_until_next_bonus === 1 ? 'day' : 'days'} away
              </p>
            </div>
          </div>
          <div className="mt-2 w-full bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${((current_streak / (current_streak + days_until_next_bonus)) * 100)}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      )}
    </motion.div>
  );
}

