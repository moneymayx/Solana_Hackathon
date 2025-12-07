'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Trophy, Zap, Target, Gift, Sparkles } from 'lucide-react';
import StreakDisplay from '@/components/gamification/StreakDisplay';
import ChallengesList from '@/components/gamification/ChallengesList';
import AchievementsGallery from '@/components/gamification/AchievementsGallery';
import PowerUpsInventory from '@/components/gamification/PowerUpsInventory';
import MilestoneCelebration from '@/components/gamification/MilestoneCelebration';
import QuickStatsCard from '@/components/gamification/QuickStatsCard';
import { useActivityTracking } from '@/hooks/useActivityTracking';

export default function GamificationPage() {
  const { publicKey, connected } = useWallet();
  const { recordActivity } = useActivityTracking();
  const walletAddress = publicKey?.toString();

  // Record activity when page loads (if wallet connected)
  useEffect(() => {
    if (walletAddress && connected) {
      recordActivity(walletAddress);
    }
  }, [walletAddress, connected, recordActivity]);

  if (!connected || !walletAddress) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-2xl font-bold text-white mb-2">Connect Your Wallet</h2>
          <p className="text-gray-400">Please connect your wallet to view your gamification stats</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-purple-900">
      {/* Milestone Celebrations (global overlay) */}
      <MilestoneCelebration walletAddress={walletAddress} />

      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <Link 
          href="/"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>

        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 bg-clip-text text-transparent mb-4">
            🎮 Gamification Hub
          </h1>
          <p className="text-gray-400 text-lg">
            Track your progress, complete challenges, and unlock achievements!
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Streak Display */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-orange-400" />
                Daily Streak
              </h2>
              <StreakDisplay walletAddress={walletAddress} />
            </section>

            {/* Challenges */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Target className="w-6 h-6 text-blue-400" />
                Active Challenges
              </h2>
              <ChallengesList walletAddress={walletAddress} />
            </section>

            {/* Achievements */}
            <section>
              <AchievementsGallery walletAddress={walletAddress} />
            </section>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Power-Ups */}
            <section>
              <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Zap className="w-6 h-6 text-purple-400" />
                Power-Ups
              </h2>
              <PowerUpsInventory walletAddress={walletAddress} />
            </section>

            {/* Quick Stats Card */}
            <QuickStatsCard walletAddress={walletAddress} />
          </div>
        </div>
      </div>
    </div>
  );
}

