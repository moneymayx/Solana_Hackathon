# Mobile App Design Sync

## Overview
This document tracks the synchronization of design changes between the web frontend and mobile app (Android/Kotlin).

## Changes Applied (October 29, 2025)

### 1. Consistent Navigation Header
- **Status**: ✅ Already implemented
- **Details**: Mobile app already uses dark navy header (`Color(0xFF0F172A)`) matching web's `#0f172a`
- **File**: `HomeScreen.kt` - `WebStyleHeader` component

### 2. Color Scheme Updates
- **Status**: ✅ Applied
- **Changes Made**:
  - Updated all Card backgrounds from theme colors to `Color.White`
  - Maintained slate color palette (`Color(0xFF111827)` for text, `Color(0xFF6B7280)` for secondary)
  - Consistent with web's white/slate theme

### 3. Card Elevation (Raised Effect)
- **Status**: ✅ Applied
- **Changes Made**:
  - **Main cards**: Increased elevation from 1dp (default) or 4dp to **12dp**
    - Staking cards (APR, Staked Tokens, Stake/Unstake forms)
    - Team cards (Stats, Team items)
    - Bounty cards
    - FAQ cards
    - Winner showcase cards
    - Feature cards (How It Works section)
  
  - **Nested/Alert cards**: Set elevation to **6dp**
    - Alert/warning cards in staking
    - Nested action cards in team view
  
  - **Rounded corners**: Ensured all cards use `RoundedCornerShape(12.dp)` for main cards, `RoundedCornerShape(8.dp)` for smaller elements

### 4. Files Updated

#### StakingScreen.kt
- APR Card: 12dp elevation, white background
- Staked Tokens Card: 12dp elevation, white background
- StakeTab Card: 12dp elevation, white background
- UnstakeTab Card: 12dp elevation, white background
- AlertCard: 6dp elevation, light yellow background

#### TeamScreen.kt
- TeamStatsCard: 12dp elevation, white background
- TeamCard: 12dp elevation, white/light gray background based on selection
- Nested action card (when team selected): 6dp elevation, very light gray

#### HomeScreen.kt
- BountyCard: 12dp elevation (updated from 4dp)
- FeatureCard (How It Works): 12dp elevation, white background
- Winner showcase cards: 12dp elevation (updated from 4dp)
- FAQItemCard: 12dp elevation

#### Theme.kt
- Already configured with proper light color scheme
- Status bar set to dark navy (`Color(0xFF0F172A)`)

## Elevation Mapping (Web to Mobile)

| Web Shadow Class | Mobile Elevation |
|-----------------|------------------|
| `shadow-2xl shadow-slate-900/10` | 12dp |
| `shadow-lg shadow-slate-900/10` | 8dp |
| `shadow-md shadow-slate-900/5` | 6dp |
| `shadow-sm` | 4dp |

## Color Palette Consistency

### Web → Mobile Mapping

| Web Tailwind | Mobile Compose |
|-------------|----------------|
| `bg-white` | `Color.White` |
| `bg-slate-50` | `Color(0xFFF9FAFB)` |
| `text-slate-900` | `Color(0xFF111827)` |
| `text-slate-600` | `Color(0xFF6B7280)` |
| `border-slate-200` | `Color(0xFFE5E7EB)` |
| Header `#0f172a` | `Color(0xFF0F172A)` |

## Testing Checklist

- [ ] Staking screen displays with elevated white cards
- [ ] Team screen cards have proper elevation and selection states
- [ ] Bounty cards on home screen show strong shadows
- [ ] FAQ accordion cards have elevated appearance
- [ ] Winner showcase cards appear raised
- [ ] Navigation header consistent across all screens
- [ ] Color scheme matches web (white backgrounds, slate text)

## Future Considerations

1. **Shadow Colors**: Android elevation creates automatic shadows. For more precise control matching web's `shadow-slate-900/10`, consider using `Modifier.shadow()` with custom colors.

2. **Hover Effects**: Mobile doesn't support hover. Consider implementing press/ripple effects for interactive feedback.

3. **Animations**: Consider adding subtle scale animations on card press to enhance the raised effect perception.

4. **Dark Mode**: Currently only light theme is implemented. Consider adding dark mode support matching web's future dark theme.

## Notes

- Mobile app uses Jetpack Compose Material 3
- Elevation in Compose is measured in dp (density-independent pixels)
- Default card elevation in Material 3 is 1dp, we've increased to 12dp for main cards to match web's `shadow-2xl`
- The visual effect on mobile will be slightly different due to platform rendering differences, but the intent (pronounced raised cards) is preserved



