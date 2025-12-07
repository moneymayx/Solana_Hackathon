'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import PointsLeaderboard from '@/components/PointsLeaderboard';
import MilestoneCelebration from '@/components/gamification/MilestoneCelebration';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function LeaderboardPage() {
  const { publicKey } = useWallet();
  const walletAddress = publicKey?.toString();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-purple-900">
      {/* Milestone Celebrations */}
      {walletAddress && <MilestoneCelebration walletAddress={walletAddress} />}

      {/* Back Button */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <Link 
          href="/"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>
      </div>

      {/* Main Content */}
      <PointsLeaderboard 
        currentUserWallet={walletAddress}
        limit={100}
      />
    </div>
  );
}

