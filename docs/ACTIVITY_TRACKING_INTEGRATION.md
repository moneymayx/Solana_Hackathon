# Activity Tracking Integration - Frontend & Mobile

## Overview
This document describes the integration of activity tracking for gamification features (streaks, challenges, achievements, power-ups, milestones) across both the web frontend (Next.js) and mobile app (Android/Kotlin).

## Frontend Integration

### Changes Made

#### 1. Updated `useActivityTracking` Hook
**File**: `frontend/src/hooks/useActivityTracking.ts`
- Updated to use `getBackendUrl()` for proper API endpoint resolution
- Calls `/api/user/activity` endpoint to track user activities for streak system

#### 2. Integrated Activity Tracking in Chat Interface
**File**: `frontend/src/components/BountyChatInterface.tsx`
- Added `useActivityTracking` hook import and usage
- Tracks question activity: Every question sent calls `recordActivity()`
- Tracks jailbreak success: When `is_winner` is true, calls `recordActivity()` (triggers 10x multiplier)
- Maintains existing `addActivity()` calls for UI display (localStorage-based ActivityTracker component)

#### 3. Integrated Activity Tracking in Referral Flows
**File**: `frontend/src/components/ReferralCodeClaim.tsx`
- Added `useActivityTracking` hook
- Tracks referral activity when a referral code is successfully claimed
- Awards 2 points per referral

### Activity Tracking Points

1. **Questions**: 1 point per question
   - Tracked in `BountyChatInterface.tsx` after successful message send
   - Also tracked when jailbreak is successful (separate call for 10x multiplier)

2. **Referrals**: 2 points per referral
   - Tracked in `ReferralCodeClaim.tsx` when referral code is successfully used

3. **Jailbreaks**: 10x multiplier on total points
   - Tracked in `BountyChatInterface.tsx` when `is_winner` is true
   - Backend automatically applies the multiplier

## Mobile App Integration

### Changes Made

#### 1. Added Gamification API Endpoints
**File**: `mobile-app/app/src/main/java/com/billionsbounty/mobile/data/api/ApiClient.kt`
- Added all gamification endpoints:
  - `POST /api/user/activity` - Record activity
  - `GET /api/user/streak/{walletAddress}` - Get streak info
  - `GET /api/challenges` - Get active challenges
  - `GET /api/user/challenges/{walletAddress}` - Get user challenges
  - `GET /api/user/achievements/{walletAddress}` - Get achievements
  - `POST /api/user/achievements/check/{walletAddress}` - Check achievements
  - `GET /api/user/power-ups/{walletAddress}` - Get power-ups
  - `POST /api/user/power-ups/activate/{powerUpId}` - Activate power-up
  - `GET /api/user/milestones/{walletAddress}` - Get milestones
  - `POST /api/user/milestones/{milestoneId}/mark-shown` - Mark milestone shown
  - `GET /api/leaderboards/points` - Get leaderboard
  - `GET /api/user/points/wallet/{walletAddress}` - Get user points

- Added all corresponding request/response data classes

#### 2. Added Gamification Methods to Repository
**File**: `mobile-app/app/src/main/java/com/billionsbounty/mobile/data/repository/ApiRepository.kt`
- Added wrapper methods for all gamification endpoints
- All methods return `Result<T>` for proper error handling
- Methods follow the same pattern as existing repository methods

#### 3. Integrated Activity Tracking in Chat ViewModel
**File**: `mobile-app/app/src/main/java/com/billionsbounty/mobile/ui/viewmodel/ChatViewModel.kt`
- Added activity tracking in `sendBountyMessage()`:
  - Tracks question activity after successful message send
  - Tracks jailbreak success when `is_winner` is true (10x multiplier)
  - Also tracks activity using `ActivityHelper` for UI display (similar to frontend's localStorage)

### Activity Tracking Points (Mobile)

Same as frontend:
1. **Questions**: 1 point per question
2. **Referrals**: 2 points per referral (to be added in referral screens)
3. **Jailbreaks**: 10x multiplier on total points

## Testing Checklist

### Frontend Testing
- [ ] Test question tracking: Send a question and verify activity is recorded
- [ ] Test jailbreak tracking: Trigger a successful jailbreak and verify activity is recorded
- [ ] Test referral tracking: Claim a referral code and verify activity is recorded
- [ ] Verify streak updates: Check that daily streaks are maintained
- [ ] Verify points calculation: Check that points are correctly calculated (1 per question, 2 per referral, 10x multiplier for jailbreaks)

### Mobile Testing
- [ ] Test question tracking: Send a question from mobile app and verify activity is recorded
- [ ] Test jailbreak tracking: Trigger a successful jailbreak from mobile and verify activity is recorded
- [ ] Test API connectivity: Verify all gamification endpoints are accessible from mobile
- [ ] Test error handling: Verify graceful error handling when backend is unavailable
- [ ] Test offline behavior: Verify app doesn't crash when offline

## Next Steps

### Mobile UI Components (Pending)
The following mobile UI components should be created to match the frontend gamification features:

1. **StreakDisplay.kt** - Display user's daily streak
2. **ChallengesList.kt** - Display active challenges and progress
3. **AchievementsGallery.kt** - Display unlocked achievements
4. **PowerUpsInventory.kt** - Display and activate power-ups
5. **MilestoneCelebration.kt** - Show milestone celebrations with animations
6. **GamificationDashboardScreen.kt** - Main gamification dashboard screen

### Referral Tracking in Mobile
- Add activity tracking to mobile referral screens (similar to frontend)
- Track when referral codes are successfully used

## API Endpoints Reference

All endpoints use the base URL from `getBackendUrl()` (frontend) or configured API base URL (mobile).

### Activity Tracking
```
POST /api/user/activity
Body: { "wallet_address": "..." }
Response: {
  "success": true,
  "current_streak": 5,
  "longest_streak": 10,
  "bonus_earned": 0,
  "bonus_name": null
}
```

### Streak Information
```
GET /api/user/streak/{walletAddress}
Response: {
  "success": true,
  "current_streak": 5,
  "longest_streak": 10,
  "last_activity_date": "2024-01-15T10:30:00",
  "streak_bonus_points": 25
}
```

### Points Information
```
GET /api/user/points/wallet/{walletAddress}
Response: {
  "success": true,
  "wallet_address": "...",
  "total_points": 150,
  "question_points": 10,
  "referral_points": 4,
  "jailbreak_multiplier_applied": 1,
  "tier": "intermediate",
  "rank": 42
}
```

## Notes

- Activity tracking is non-blocking: failures are logged but don't interrupt user flow
- Both frontend and mobile use the same backend API endpoints
- Frontend uses React hooks, mobile uses Kotlin coroutines
- Activity tracking happens automatically when users perform actions (questions, referrals, jailbreaks)
- The backend handles all point calculations, streak updates, and achievement unlocks

