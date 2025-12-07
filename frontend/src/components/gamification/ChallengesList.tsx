'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Target, CheckCircle, Clock, Zap } from 'lucide-react';

interface Challenge {
  id: number;
  challenge_type: string;
  name: string;
  description: string;
  objective_type: string;
  objective_target: number;
  reward_points: number;
  start_date: string;
  end_date: string | null;
  time_remaining: number | null;
  progress: {
    current: number;
    target: number;
    percentage: number;
    completed: boolean;
    reward_claimed: boolean;
  };
}

interface ChallengesListProps {
  walletAddress: string;
  className?: string;
}

export default function ChallengesList({ walletAddress, className = '' }: ChallengesListProps) {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!walletAddress) return;

    const fetchChallenges = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/user/challenges/${walletAddress}`);
        if (!response.ok) throw new Error('Failed to fetch challenges');
        
        const data = await response.json();
        setChallenges(data.challenges || []);
      } catch (err) {
        console.error('Error fetching challenges:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchChallenges();
    // Refresh every 30 seconds
    const interval = setInterval(fetchChallenges, 30000);
    return () => clearInterval(interval);
  }, [walletAddress]);

  if (loading) {
    return (
      <div className={`space-y-3 ${className}`}>
        {[1, 2, 3].map(i => (
          <div key={i} className="bg-gray-800/50 rounded-xl p-4 animate-pulse">
            <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
            <div className="h-2 bg-gray-700 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (challenges.length === 0) {
    return (
      <div className={`text-center text-gray-400 py-8 ${className}`}>
        <Target className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>No active challenges</p>
      </div>
    );
  }

  const formatTimeRemaining = (seconds: number | null) => {
    if (!seconds) return null;
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {challenges.map((challenge, index) => (
        <motion.div
          key={challenge.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`
            ${challenge.progress.completed 
              ? 'bg-gradient-to-r from-green-900/30 to-emerald-900/30 border-green-500/30' 
              : 'bg-gray-800/50 border-gray-700/50'
            }
            border rounded-xl p-4
          `}
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                {challenge.progress.completed ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <Target className="w-5 h-5 text-blue-400" />
                )}
                <h3 className="font-semibold text-white">{challenge.name}</h3>
                {challenge.challenge_type === 'daily' && (
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
                    Daily
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-400">{challenge.description}</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-1 text-yellow-400">
                <Zap className="w-4 h-4" />
                <span className="font-semibold">{challenge.reward_points}</span>
              </div>
              {challenge.time_remaining && (
                <p className="text-xs text-gray-500 mt-1">
                  {formatTimeRemaining(challenge.time_remaining)}
                </p>
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-gray-400">
              <span>
                {challenge.progress.current} / {challenge.progress.target}
              </span>
              <span>{challenge.progress.percentage}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
              <motion.div
                className={`h-2 rounded-full ${
                  challenge.progress.completed
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                    : 'bg-gradient-to-r from-blue-500 to-purple-500'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${challenge.progress.percentage}%` }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              />
            </div>
          </div>

          {challenge.progress.completed && !challenge.progress.reward_claimed && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-3 text-center"
            >
              <p className="text-green-400 text-sm font-semibold">
                🎉 Challenge Complete! +{challenge.reward_points} points earned!
              </p>
            </motion.div>
          )}
        </motion.div>
      ))}
    </div>
  );
}

