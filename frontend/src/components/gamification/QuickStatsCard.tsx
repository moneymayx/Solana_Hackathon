'use client';

import React, { useEffect, useState } from 'react';
import { Trophy } from 'lucide-react';

interface QuickStatsCardProps {
  walletAddress: string;
}

export default function QuickStatsCard({ walletAddress }: QuickStatsCardProps) {
  const [stats, setStats] = useState({
    totalPoints: 0,
    achievements: 0,
    challenges: 0,
    loading: true
  });

  useEffect(() => {
    if (!walletAddress) return;

    const fetchStats = async () => {
      try {
        // Fetch points
        const pointsRes = await fetch(`/api/user/points/wallet/${walletAddress}`);
        const pointsData = pointsRes.ok ? await pointsRes.json() : null;

        // Fetch achievements
        const achievementsRes = await fetch(`/api/user/achievements/${walletAddress}`);
        const achievementsData = achievementsRes.ok ? await achievementsRes.json() : null;

        // Fetch challenges
        const challengesRes = await fetch(`/api/user/challenges/${walletAddress}`);
        const challengesData = challengesRes.ok ? await challengesRes.json() : null;

        setStats({
          totalPoints: pointsData?.points?.total_points || 0,
          achievements: achievementsData?.total || 0,
          challenges: challengesData?.total_active || 0,
          loading: false
        });
      } catch (err) {
        console.error('Error fetching stats:', err);
        setStats(prev => ({ ...prev, loading: false }));
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, [walletAddress]);

  return (
    <section className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-500/30 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-yellow-400" />
        Quick Stats
      </h3>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-400">Total Points</span>
          <span className="text-white font-semibold">
            {stats.loading ? '...' : stats.totalPoints.toLocaleString()}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Achievements</span>
          <span className="text-white font-semibold">
            {stats.loading ? '...' : stats.achievements}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Active Challenges</span>
          <span className="text-white font-semibold">
            {stats.loading ? '...' : stats.challenges}
          </span>
        </div>
      </div>
    </section>
  );
}

