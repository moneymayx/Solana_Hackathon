'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trophy, Sparkles } from 'lucide-react';

interface Milestone {
  id: number;
  milestone_type: string;
  name: string;
  description: string;
  value: number | null;
  achieved_at: string;
}

interface MilestoneCelebrationProps {
  walletAddress: string;
  onMilestoneShown?: (milestoneId: number) => void;
}

// Confetti particle component
const ConfettiParticle = ({ delay, x, color }: { delay: number; x: number; color: string }) => {
  const height = typeof window !== 'undefined' ? window.innerHeight : 800;
  
  return (
    <motion.div
      className="absolute w-2 h-2 rounded-full"
      style={{ backgroundColor: color, left: `${x}%` }}
      initial={{ y: -20, opacity: 1, rotate: 0 }}
      animate={{
        y: height + 20,
        opacity: [1, 1, 0],
        rotate: 360,
      }}
      transition={{
        duration: 2 + Math.random(),
        delay,
        ease: 'easeOut',
      }}
    />
  );
};

export default function MilestoneCelebration({ walletAddress, onMilestoneShown }: MilestoneCelebrationProps) {
  const [currentMilestone, setCurrentMilestone] = useState<Milestone | null>(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [checkedMilestones, setCheckedMilestones] = useState<Set<number>>(new Set());

  const fetchMilestones = useCallback(async () => {
    if (!walletAddress || checkedMilestones.size > 0) return;

    try {
      const response = await fetch(`/api/user/milestones/${walletAddress}?unshown_only=true`);
      if (!response.ok) return;

      const data = await response.json();
      const milestones = data.milestones || [];

      // Find first unshown milestone
      const unshown = milestones.find((m: Milestone) => !checkedMilestones.has(m.id));
      if (unshown) {
        setCurrentMilestone(unshown);
        setShowConfetti(true);
        setCheckedMilestones(prev => new Set([...prev, unshown.id]));
      }
    } catch (err) {
      console.error('Error fetching milestones:', err);
    }
  }, [walletAddress, checkedMilestones]);

  useEffect(() => {
    fetchMilestones();
    // Check for new milestones every 10 seconds
    const interval = setInterval(fetchMilestones, 10000);
    return () => clearInterval(interval);
  }, [fetchMilestones]);

  const handleClose = async () => {
    if (!currentMilestone) return;

    // Mark milestone as shown
    try {
      await fetch(`/api/user/milestones/${currentMilestone.id}/mark-shown`, {
        method: 'POST',
      });
      
      if (onMilestoneShown) {
        onMilestoneShown(currentMilestone.id);
      }
    } catch (err) {
      console.error('Error marking milestone as shown:', err);
    }

    setShowConfetti(false);
    setTimeout(() => {
      setCurrentMilestone(null);
      // Check for next milestone
      fetchMilestones();
    }, 500);
  };

  // Confetti colors
  const confettiColors = [
    '#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1',
    '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE'
  ];

  return (
    <AnimatePresence>
      {currentMilestone && (
        <>
          {/* Confetti Overlay */}
          {showConfetti && (
            <motion.div
              className="fixed inset-0 pointer-events-none z-50"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {Array.from({ length: 50 }).map((_, i) => (
                <ConfettiParticle
                  key={i}
                  delay={i * 0.02}
                  x={(i * 100) / 50}
                  color={confettiColors[i % confettiColors.length]}
                />
              ))}
            </motion.div>
          )}

          {/* Milestone Modal */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 flex items-center justify-center p-4"
            onClick={handleClose}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0, y: 50 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 50 }}
              transition={{ type: 'spring', damping: 20 }}
              className="bg-gradient-to-br from-yellow-900/90 via-orange-900/90 to-red-900/90 border-2 border-yellow-500/50 rounded-2xl p-8 max-w-md w-full relative overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Sparkle background effect */}
              <div className="absolute inset-0 overflow-hidden">
                {Array.from({ length: 20 }).map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-yellow-400 rounded-full"
                    style={{
                      left: `${Math.random() * 100}%`,
                      top: `${Math.random() * 100}%`,
                    }}
                    animate={{
                      opacity: [0, 1, 0],
                      scale: [0, 1.5, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      delay: Math.random() * 2,
                    }}
                  />
                ))}
              </div>

              {/* Close button */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Content */}
              <div className="relative z-10 text-center">
                {/* Icon */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: 'spring' }}
                  className="mb-4"
                >
                  <div className="w-24 h-24 mx-auto bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl">
                    <Trophy className="w-12 h-12 text-white" />
                  </div>
                </motion.div>

                {/* Title */}
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-3xl font-bold text-white mb-2"
                >
                  🎉 Milestone Achieved! 🎉
                </motion.h2>

                {/* Milestone Name */}
                <motion.h3
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="text-2xl font-bold text-yellow-300 mb-3"
                >
                  {currentMilestone.name}
                </motion.h3>

                {/* Description */}
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-white/90 mb-6"
                >
                  {currentMilestone.description}
                </motion.p>

                {/* Value if available */}
                {currentMilestone.value && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6 }}
                    className="bg-white/20 rounded-lg p-4 mb-6"
                  >
                    <p className="text-4xl font-bold text-yellow-300">
                      {currentMilestone.value.toLocaleString()}
                    </p>
                    <p className="text-white/70 text-sm mt-1">Points</p>
                  </motion.div>
                )}

                {/* Continue button */}
                <motion.button
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  onClick={handleClose}
                  className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold py-3 px-8 rounded-lg transition-all shadow-lg hover:shadow-xl"
                >
                  Awesome! 🚀
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

