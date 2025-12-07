'use client';

import { useCallback } from 'react';
import { getBackendUrl } from '@/lib/api/client';

/**
 * Hook for tracking user activity for streak system
 * Call this whenever user performs an action (question, referral, jailbreak)
 */
export function useActivityTracking() {
  const recordActivity = useCallback(async (walletAddress: string) => {
    if (!walletAddress) return;

    try {
      const response = await fetch(`${getBackendUrl()}/api/user/activity`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ wallet_address: walletAddress }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Check if streak bonus was earned
        if (data.bonus_earned > 0) {
          // Could trigger a notification here
          console.log(`🎉 Streak bonus earned: ${data.bonus_name} (+${data.bonus_earned} points)`);
        }
        
        return data;
      }
    } catch (error) {
      console.error('Error recording activity:', error);
    }
  }, []);

  return { recordActivity };
}

