# Gamified Points & Leaderboard System

## Overview

A comprehensive gamification system that rewards users with points based on their activity and engagement. The system features a highly engaging 10x multiplier for successful jailbreaks, making them extremely valuable.

## Points System

### Point Distribution

| Activity | Points Earned | Description |
|----------|--------------|-------------|
| **Question Asked** | 1 point | Each user message/question earns 1 point |
| **Successful Referral** | 2 points | Each person who signs up using your referral code |
| **Successful Jailbreak** | 10x multiplier | Multiplies ALL your points by 10! |

### Multiplier Rules

- Each successful jailbreak applies a **10x multiplier** to your total points
- Multiple jailbreaks stack multiplicatively:
  - 1 jailbreak: `base_points × 10`
  - 2 jailbreaks: `base_points × 10 × 10 = base_points × 100`
  - 3 jailbreaks: `base_points × 1,000`
- This creates a strong incentive for users to attempt jailbreaks

### Example Calculations

**Example 1: Active Question Asker**
- 50 questions = 50 points
- 0 referrals = 0 points
- Base: 50 points
- No jailbreaks = **50 total points**

**Example 2: Referral Master**
- 10 questions = 10 points
- 5 referrals = 10 points
- Base: 20 points
- No jailbreaks = **20 total points**

**Example 3: Jailbreak Champion** 🏆
- 20 questions = 20 points
- 3 referrals = 6 points
- Base: 26 points
- **1 jailbreak = 26 × 10 = 260 total points!**

## Tier System

Users are assigned tiers based on their total points:

| Tier | Points Required | Badge |
|------|----------------|-------|
| **Legendary** | 10,000+ | 👑 Crown |
| **Diamond** | 5,000-9,999 | 💎 Award |
| **Platinum** | 1,000-4,999 | 🥈 Medal |
| **Gold** | 500-999 | 🏆 Trophy |
| **Silver** | 100-499 | ⭐ Star |
| **Bronze** | 10-99 | 🥉 Medal |
| **Beginner** | 0-9 | ⚡ Zap |

## Database Schema

### User Model Updates

Added the following fields to the `User` model:

```python
total_points: int  # Total gamification points
question_points: int  # Points from questions (before multiplier)
referral_points: int  # Points from referrals (before multiplier)
jailbreak_multiplier_applied: int  # Number of successful jailbreaks
last_points_update: datetime  # Timestamp of last points calculation
```

### Data Sources

Points are calculated from:
- **Questions**: `Conversation` table where `message_type = 'user'`
- **Referrals**: `Referral` table where `is_valid = True`
- **Jailbreaks**: `AttackAttempt` table where `was_successful = True`

## API Endpoints

### Get Points Leaderboard
```
GET /api/leaderboards/points?limit=100&offset=0
```

Returns ranked list of users by total points.

**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 123,
      "wallet_address": "ABC...XYZ",
      "display_name": "JailbreakChampion",
      "total_points": 260,
      "question_points": 20,
      "question_count": 20,
      "referral_points": 6,
      "referral_count": 3,
      "jailbreak_count": 1,
      "multiplier_applied": 10,
      "tier": "silver"
    }
  ],
  "total_entries": 1,
  "limit": 100,
  "offset": 0,
  "points_rules": {
    "question_points": 1,
    "referral_points": 2,
    "jailbreak_multiplier": 10
  }
}
```

### Get User Points by User ID
```
GET /api/user/points/{user_id}
```

Returns detailed points breakdown for a specific user.

### Get User Points by Wallet Address
```
GET /api/user/points/wallet/{wallet_address}
```

Returns detailed points breakdown for a user by their wallet address.

**Response:**
```json
{
  "user_id": 123,
  "wallet_address": "ABC...XYZ",
  "display_name": "JailbreakChampion",
  "points": {
    "total_points": 260,
    "question_points": 20,
    "question_count": 20,
    "referral_points": 6,
    "referral_count": 3,
    "base_points": 26,
    "jailbreak_count": 1,
    "multiplier_applied": 10
  },
  "rank": {
    "rank": 1,
    "total_users": 4,
    "percentile": 100.0,
    "tier": "silver",
    "points_to_next_rank": 0,
    "points_above_previous": 210
  },
  "tier": "silver"
}
```

### Update User Points
```
POST /api/user/points/update/{user_id}
```

Manually recalculates and updates points for a specific user.

### Admin: Recalculate All Points
```
POST /api/admin/points/recalculate-all
```

Admin endpoint to recalculate points for all users.

## Frontend Components

### PointsLeaderboard Component

Location: `frontend/src/components/PointsLeaderboard.tsx`

**Features:**
- Animated, responsive leaderboard display
- Tier-based color coding and badges
- Current user highlighting
- Points breakdown (questions, referrals, jailbreaks)
- Progress bars showing distance to next rank
- Top 10 vs All Players toggle
- Real-time updates

**Props:**
```typescript
interface PointsLeaderboardProps {
  currentUserWallet?: string;  // Wallet address of current user
  limit?: number;  // Number of users to display (default: 100)
}
```

**Usage:**
```tsx
import PointsLeaderboard from '@/components/PointsLeaderboard';

<PointsLeaderboard 
  currentUserWallet={publicKey?.toString()}
  limit={100}
/>
```

### Leaderboard Page

Location: `frontend/src/app/leaderboard/page.tsx`

Accessible at: `/leaderboard`

Full-page leaderboard with navigation back to home.

## Points Service

Location: `src/services/points_service.py`

### Key Functions

#### `calculate_user_points(session, user_id)`
Calculates current points for a user without updating the database.

#### `update_user_points(session, user_id)`
Calculates and updates user points in the database.

#### `get_leaderboard(session, limit, offset)`
Returns ranked list of users by points.

#### `get_user_rank(session, user_id)`
Returns user's current rank, percentile, and comparison to nearby users.

#### `recalculate_all_user_points(session)`
Admin function to recalculate points for all users.

## Testing

### Test Script

Location: `scripts/test_points_system.py`

Creates test users with various activities and verifies points calculation:

```bash
cd Billions_Bounty
source venv/bin/activate
python3 scripts/test_points_system.py
```

### Test Results

```
🥇 #1 - JailbreakChampion
   Total: 260 pts | Tier: SILVER
   Questions: 20 | Referrals: 3 | Jailbreaks: 1

🥈 #2 - QuestionMaster
   Total: 50 pts | Tier: BRONZE
   Questions: 50 | Referrals: 0 | Jailbreaks: 0

🥉 #3 - ReferralPro
   Total: 20 pts | Tier: BRONZE
   Questions: 10 | Referrals: 5 | Jailbreaks: 0

   #4 - CasualUser
   Total: 2 pts | Tier: BEGINNER
   Questions: 2 | Referrals: 0 | Jailbreaks: 0
```

## Migration Scripts

### Initial Points System Migration
```bash
python3 scripts/migrations/add_points_system.py
```

Adds points-related columns to the users table and performs initial points calculation.

### Sync User Table
```bash
python3 scripts/migrations/sync_user_table.py
```

Ensures all user table columns match the model definition.

## Design Philosophy

### Why 10x Multiplier for Jailbreaks?

1. **High Risk, High Reward**: Jailbreaks are difficult to achieve, so they deserve massive rewards
2. **Engagement Driver**: Creates excitement and urgency around attempting jailbreaks
3. **Competitive Edge**: Even users with fewer activities can compete if they succeed
4. **Viral Potential**: Creates "wow moments" that users want to share
5. **Platform Value**: Encourages the exact behavior (finding vulnerabilities) that provides value to the platform

### Gamification Psychology

- **Clear Progress**: Users can see exactly where they stand
- **Multiple Paths**: Can compete through questions, referrals, OR jailbreaks
- **Visible Rewards**: Tiers and badges provide social status
- **Competitive**: Leaderboard creates comparison and motivation
- **Achievable**: Bronze and Silver tiers are accessible to most users
- **Aspirational**: Legendary tier (10,000+ points) gives long-term goals

## Future Enhancements

Potential additions to the points system:

1. **Streak Bonuses**: Consecutive days of activity
2. **First Achievement Bonuses**: First jailbreak, first 100 questions, etc.
3. **Time-Limited Events**: Double points weekends, competitions
4. **Team Leaderboards**: Combined points for teams
5. **Seasonal Resets**: Fresh leaderboards each quarter
6. **NFT Rewards**: Special NFTs for top performers
7. **Token Integration**: Convert points to $100Bs tokens
8. **Challenge Modes**: Specific challenges for bonus points

## Monitoring & Analytics

### Key Metrics to Track

- Average points per user
- Distribution across tiers
- Jailbreak success rate vs. points gained
- Referral conversion rates
- User retention by tier
- Time to first jailbreak
- Leaderboard engagement (views, time spent)

### Performance Considerations

- Points are calculated on-demand (not cached)
- Leaderboard queries are optimized with indexes
- Consider caching for high-traffic scenarios
- Batch recalculation available for maintenance

## Maintenance

### Regular Tasks

1. **Monitor Database Performance**: Ensure points queries remain fast
2. **Verify Points Accuracy**: Spot-check calculations periodically
3. **Handle Edge Cases**: Users with extreme values (millions of questions)
4. **Update Tiers**: Adjust tier thresholds based on user distribution
5. **Clean Test Data**: Remove test users from production

### Troubleshooting

**Points not updating?**
- Check if `last_points_update` is recent
- Run manual update: `POST /api/user/points/update/{user_id}`
- Verify database connectivity

**Incorrect calculations?**
- Check for orphaned records (deleted users with activity)
- Verify `is_valid` flags on referrals
- Confirm `was_successful` on attack attempts

**Leaderboard not showing users?**
- Ensure users have `total_points > 0`
- Check pagination (limit/offset)
- Verify database query performance

## Security Considerations

- Points cannot be manually set (only calculated)
- Admin endpoints should be protected
- Validate user IDs and wallet addresses
- Prevent points manipulation through fake activities
- Monitor for suspicious patterns (bot accounts)

## Conclusion

The points and leaderboard system creates a highly engaging gamification layer that:
- Rewards all types of user activity
- Creates strong incentives for jailbreak attempts
- Provides clear progression and goals
- Enables competitive comparison
- Scales efficiently with user growth

The 10x multiplier for jailbreaks is the key differentiator that makes the system exciting and aligns perfectly with the platform's goals.

---

**Built by Billions Bounty Team**
**Last Updated: November 18, 2025**

