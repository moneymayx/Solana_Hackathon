# Activity Tracker Feature - Testing Guide

## Overview
This document outlines all tests needed to verify the activity tracker feature works correctly.

## Automated Tests

### Frontend Tests
Run: `npm test` in the `frontend` directory

Test files created:
- `src/__tests__/components/ActivityTracker.test.tsx` - Tests for ActivityTracker component
- `src/__tests__/components/UsernamePrompt.test.tsx` - Tests for UsernamePrompt component

### Backend Tests
The backend endpoint `/api/user/set-profile` should be tested manually or added to backend test suite.

## Manual Testing Checklist

### 1. Feature Flag Behavior

#### Test: Feature Disabled (Default)
- [ ] Set `NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER=false` or omit from .env
- [ ] Start frontend application
- [ ] Navigate to bounty page
- [ ] Verify: No username prompt appears when clicking action buttons
- [ ] Verify: No activity tracker appears at bottom of bounty cards
- [ ] Verify: All existing functionality works normally (buttons work without prompts)

#### Test: Feature Enabled
- [ ] Set `NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER=true` in .env.local
- [ ] Restart frontend application
- [ ] Navigate to bounty page
- [ ] Verify: Activity tracker appears at bottom of bounty cards (if activities exist)
- [ ] Verify: Username prompt appears when clicking action buttons (if username not set)

### 2. Username Collection

#### Test: Username Prompt Modal
- [ ] Enable feature flag
- [ ] Connect wallet that doesn't have username set
- [ ] Click "Start Participating" button
- [ ] Verify: UsernamePrompt modal appears
- [ ] Verify: Username field has red asterisk (*)
- [ ] Verify: Email field shows "(optional)" text
- [ ] Verify: Submit button is disabled when username < 3 characters
- [ ] Verify: Submit button enables when username >= 3 characters

#### Test: Username Validation
- [ ] Try submitting with username "ab" (too short)
- [ ] Verify: Error message "Username must be at least 3 characters" appears
- [ ] Try submitting with username "validuser"
- [ ] Verify: API call is made with correct payload
- [ ] Verify: Modal closes on success
- [ ] Verify: Action continues after username is set

#### Test: Email Optional
- [ ] Submit username without email
- [ ] Verify: API is called with `email: undefined`
- [ ] Verify: Backend accepts and saves username only
- [ ] Submit username with email
- [ ] Verify: Both username and email are saved

#### Test: Username Persistence
- [ ] Set username for a wallet
- [ ] Disconnect and reconnect wallet
- [ ] Verify: Username is remembered (no prompt appears)
- [ ] Click action buttons
- [ ] Verify: No username prompt, actions proceed directly

### 3. Activity Tracker Component

#### Test: Activity Display
- [ ] Enable feature flag
- [ ] Perform an action (ask question, redeem NFT, refer friend)
- [ ] Verify: Activity appears at bottom of bounty card
- [ ] Verify: Activity shows correct username and message
- [ ] Verify: Green bubble styling is applied
- [ ] Verify: Activity is only visible on the correct bounty card (per-bounty filtering)

#### Test: Auto-Cycling
- [ ] Create multiple activities (at least 2)
- [ ] Verify: First activity appears
- [ ] Wait 4 seconds
- [ ] Verify: Activity automatically cycles to next one
- [ ] Verify: No manual scroll controls are visible
- [ ] Verify: Activities cycle in correct order

#### Test: Time Filtering (24 Hours)
- [ ] Manually add an old activity to localStorage (25+ hours old)
- [ ] Refresh page
- [ ] Verify: Old activity does not appear
- [ ] Create a new activity
- [ ] Verify: Only new activity appears

#### Test: Per-Bounty Filtering
- [ ] Create activity for Bounty 1
- [ ] Create activity for Bounty 2
- [ ] View Bounty 1 card
- [ ] Verify: Only Bounty 1 activity appears
- [ ] View Bounty 2 card
- [ ] Verify: Only Bounty 2 activity appears

#### Test: Auto-Refresh
- [ ] View bounty card with activities
- [ ] In another tab/browser, perform an action (add activity)
- [ ] Wait 3-4 seconds
- [ ] Verify: New activity appears in the tracker (auto-refresh working)

### 4. Activity Creation

#### Test: Question Activity
- [ ] Set username
- [ ] Ask a question in the chat
- [ ] Verify: Activity "username just asked [bounty name]" is created
- [ ] Verify: Activity appears in localStorage
- [ ] Verify: Activity appears in activity tracker

#### Test: First Question Activity
- [ ] Set username
- [ ] Ask your first question (no previous questions)
- [ ] Verify: Activity shows "username just asked their first question"
- [ ] Ask second question
- [ ] Verify: Activity shows "username just asked [bounty name]" (not first question)

#### Test: NFT Redeem Activity
- [ ] Set username
- [ ] Click "Solana Seekers" button
- [ ] Complete NFT verification
- [ ] Verify: Activity "username redeemed their NFT" is created
- [ ] Verify: Activity appears in tracker

#### Test: Referral Activity
- [ ] Set username
- [ ] Click "Refer Someone" button
- [ ] Complete referral flow
- [ ] Verify: Activity "username referred a new friend" is created
- [ ] Verify: Activity appears in tracker

### 5. Backend Integration

#### Test: Set Profile Endpoint
- [ ] Use API client (Postman/curl) or frontend
- [ ] POST to `/api/user/set-profile` with:
  ```json
  {
    "wallet_address": "test-address",
    "username": "testuser",
    "email": "test@example.com"
  }
  ```
- [ ] Verify: Returns `{ "success": true, "username": "testuser", ... }`
- [ ] Verify: User is created in database if doesn't exist
- [ ] Verify: User's display_name is updated
- [ ] Verify: Email is saved if provided

#### Test: Get Profile Endpoint
- [ ] Set username via `/api/user/set-profile`
- [ ] GET `/api/user/profile/{wallet_address}`
- [ ] Verify: Returns user profile with display_name
- [ ] Verify: Frontend can read username from this endpoint

### 6. Edge Cases

#### Test: localStorage Limits
- [ ] Create 101+ activities
- [ ] Verify: Only last 100 activities are kept
- [ ] Verify: Oldest activities are removed

#### Test: Multiple Browsers/Tabs
- [ ] Open same app in two browser tabs
- [ ] Perform action in tab 1
- [ ] Verify: Activity appears in tab 2 within 3-4 seconds (localStorage sync)

#### Test: Wallet Disconnect
- [ ] Connect wallet and set username
- [ ] Perform actions (create activities)
- [ ] Disconnect wallet
- [ ] Verify: Activity tracker still shows activities (localStorage persists)
- [ ] Verify: Username prompt appears again if new wallet connects

#### Test: Network Errors
- [ ] Disable network
- [ ] Try to submit username
- [ ] Verify: Error message is displayed
- [ ] Verify: Modal doesn't close
- [ ] Re-enable network and retry
- [ ] Verify: Success flow works

### 7. UI/UX Verification

#### Test: Styling
- [ ] Verify: Green bubble matches Phantom app style
- [ ] Verify: Activity text is readable
- [ ] Verify: Component doesn't break card layout
- [ ] Verify: Component is responsive on mobile

#### Test: Performance
- [ ] Create 100 activities
- [ ] Verify: Component doesn't lag
- [ ] Verify: Auto-cycling works smoothly
- [ ] Verify: Page load time not significantly impacted

## Integration Testing Scenarios

### Full Flow Test 1: New User Journey
1. [ ] Enable feature flag
2. [ ] Connect new wallet (no username)
3. [ ] Click "Start Participating"
4. [ ] Enter username (required) and email (optional)
5. [ ] Submit
6. [ ] Verify: Modal closes, chat input appears
7. [ ] Ask a question
8. [ ] Verify: Activity appears on bounty card
9. [ ] Verify: Activity cycles after 4 seconds

### Full Flow Test 2: Returning User
1. [ ] User with existing username connects
2. [ ] Click any action button
3. [ ] Verify: No username prompt (username remembered)
4. [ ] Perform action
5. [ ] Verify: Activity is created and displayed

### Full Flow Test 3: Feature Toggle
1. [ ] Start with feature disabled
2. [ ] Use app normally (verify no prompts/tracker)
3. [ ] Enable feature flag
4. [ ] Refresh page
5. [ ] Verify: Feature now works
6. [ ] Disable feature flag
7. [ ] Refresh page
8. [ ] Verify: Feature disabled again

## Browser Compatibility Testing

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Security Considerations

- [ ] Verify: Username cannot contain XSS payloads
- [ ] Verify: localStorage data is properly sanitized
- [ ] Verify: API endpoints validate input
- [ ] Verify: No sensitive data in localStorage

## Performance Testing

- [ ] Load test with 1000+ activities
- [ ] Verify: localStorage doesn't exceed browser limits
- [ ] Verify: Component renders efficiently
- [ ] Verify: Memory leaks don't occur with long sessions

---

## Quick Smoke Test (5 minutes)

1. Enable feature: `NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER=true`
2. Connect wallet
3. Click "Start Participating" → Set username
4. Ask a question
5. Verify: Activity appears at bottom of bounty card
6. Wait 4 seconds
7. Verify: Activity auto-cycles (if multiple exist)

If all pass, core functionality is working! ✅

