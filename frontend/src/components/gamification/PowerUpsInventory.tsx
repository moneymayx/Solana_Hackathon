'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Zap, Clock, CheckCircle, Gift } from 'lucide-react';

interface PowerUp {
  id: number;
  power_up_type: string;
  name: string;
  description: string;
  multiplier: number;
  source: string;
  is_active: boolean;
  is_used: boolean;
  expires_at: string | null;
  time_remaining: number | null;
  created_at: string;
}

interface PowerUpsInventoryProps {
  walletAddress: string;
  className?: string;
}

export default function PowerUpsInventory({ walletAddress, className = '' }: PowerUpsInventoryProps) {
  const [powerUps, setPowerUps] = useState<{ active: PowerUp[]; inactive: PowerUp[]; total: number }>({
    active: [],
    inactive: [],
    total: 0
  });
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState<number | null>(null);

  useEffect(() => {
    if (!walletAddress) return;

    const fetchPowerUps = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/user/power-ups/${walletAddress}?include_used=false`);
        if (!response.ok) throw new Error('Failed to fetch power-ups');
        
        const data = await response.json();
        setPowerUps(data);
      } catch (err) {
        console.error('Error fetching power-ups:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPowerUps();
    // Refresh every 10 seconds to update timers
    const interval = setInterval(fetchPowerUps, 10000);
    return () => clearInterval(interval);
  }, [walletAddress]);

  const handleActivate = async (powerUpId: number) => {
    try {
      setActivating(powerUpId);
      const response = await fetch(`/api/user/power-ups/activate/${powerUpId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ wallet_address: walletAddress }),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(error.detail || 'Failed to activate power-up');
        return;
      }

      // Refresh power-ups
      const refreshResponse = await fetch(`/api/user/power-ups/${walletAddress}?include_used=false`);
      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        setPowerUps(data);
      }
    } catch (err) {
      console.error('Error activating power-up:', err);
      alert('Failed to activate power-up');
    } finally {
      setActivating(null);
    }
  };

  const formatTimeRemaining = (seconds: number | null) => {
    if (!seconds) return null;
    if (seconds < 60) return `${Math.floor(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    return `${minutes}m`;
  };

  if (loading) {
    return (
      <div className={`space-y-3 ${className}`}>
        {[1, 2].map(i => (
          <div key={i} className="bg-gray-800/50 rounded-xl p-4 animate-pulse">
            <div className="h-20 bg-gray-700 rounded"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Active Power-Ups */}
      {powerUps.active.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Active Power-Ups
          </h3>
          <div className="space-y-3">
            {powerUps.active.map((powerUp) => (
              <motion.div
                key={powerUp.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 border border-yellow-500/30 rounded-xl p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center">
                      <Zap className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{powerUp.name}</p>
                      <p className="text-sm text-gray-300">{powerUp.description}</p>
                      {powerUp.time_remaining && (
                        <div className="flex items-center gap-1 mt-1">
                          <Clock className="w-3 h-3 text-yellow-400" />
                          <span className="text-xs text-yellow-400">
                            {formatTimeRemaining(powerUp.time_remaining)} remaining
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-yellow-400 font-bold text-lg">
                      {powerUp.multiplier}x
                    </p>
                    <p className="text-xs text-gray-400">Multiplier</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Inactive Power-Ups */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <Gift className="w-5 h-5 text-purple-400" />
          Available Power-Ups ({powerUps.inactive.length})
        </h3>
        {powerUps.inactive.length === 0 ? (
          <div className="text-center text-gray-400 py-8 bg-gray-800/30 rounded-xl">
            <Gift className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No power-ups available</p>
            <p className="text-sm mt-2">Complete challenges to earn power-ups!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {powerUps.inactive.map((powerUp) => (
              <motion.div
                key={powerUp.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4 hover:border-purple-500/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                      <Zap className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-white">{powerUp.name}</p>
                      <p className="text-xs text-gray-400">{powerUp.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-purple-400 font-bold">
                      {powerUp.multiplier}x
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleActivate(powerUp.id)}
                  disabled={activating === powerUp.id}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-2 px-4 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {activating === powerUp.id ? 'Activating...' : 'Activate'}
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

