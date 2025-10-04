# Escape Plan Countdown Feature

## Overview

The Escape Plan Countdown is a real-time display component that shows users when the last question was asked and tracks the 24-hour timeout period for the escape plan distribution.

## Features

### 🕐 **Real-time Countdown**
- Updates every second to show current status
- Displays time since last question was asked
- Shows countdown to escape plan trigger (24 hours)

### 👤 **Last Participant Tracking**
- Shows who asked the last question
- Displays user's display name, wallet address, or user ID
- Handles cases where no questions have been asked yet

### 📊 **Visual Progress Indicator**
- Color-coded status (orange for counting down, red for ready)
- Progress bar showing elapsed time out of 24 hours
- Clear visual hierarchy with icons and styling

### 🎯 **Escape Plan Information**
- Explains the 80/20 distribution rule
- Shows which user will receive the 20% bonus
- Updates in real-time as the situation changes

## Component Structure

### `EscapePlanCountdown.tsx`
- **Location**: `frontend/src/components/EscapePlanCountdown.tsx`
- **Purpose**: Main countdown display component
- **Updates**: Every 1 second via `setInterval`

### API Integration
- **Endpoint**: `GET /api/bounty/escape-plan/status`
- **Response**: Includes escape plan status and last participant data
- **Frequency**: Fetches data every second for real-time updates

## Visual States

### 🟠 **Counting Down State**
- Orange background and border
- Shows time remaining until escape plan triggers
- Progress bar fills as time approaches 24 hours
- Message: "Escape plan in Xh Ym if no questions"

### 🔴 **Ready State**
- Red background and border
- Shows escape plan is ready to trigger
- Message: "🚨 ESCAPE PLAN READY! No questions for 24+ hours"

### ⚪ **Inactive State**
- Component is hidden when no questions have been asked
- Only shows when there's been at least one question

## User Experience

### **Main Screen Display**
- Always visible at the top of the main content area
- Appears on all tabs when age verification is complete
- Provides constant awareness of escape plan status

### **Information Displayed**
1. **Last Question By**: Shows who asked the most recent question
2. **Time Since Last Question**: How long it's been since last activity
3. **Time Until Escape**: Countdown to 24-hour trigger (if applicable)
4. **Progress Bar**: Visual representation of elapsed time
5. **Escape Plan Rules**: Clear explanation of distribution rules

## Technical Implementation

### **State Management**
```typescript
interface EscapePlanData {
  is_active: boolean
  time_since_last_question?: string
  time_until_escape?: string
  message: string
  should_trigger?: boolean
  last_participant_id?: number
  last_question_at?: string
}
```

### **User Data Integration**
- Fetches user details for last participant
- Handles display name, wallet address, or user ID
- Gracefully handles missing user data

### **Real-time Updates**
- 1-second interval for countdown updates
- Automatic API calls to get latest status
- Smooth progress bar animations

## Integration Points

### **Backend Services**
- `bounty_service.py`: Tracks last participant and question timing
- `main.py`: Provides escape plan status API endpoint
- Database: Stores last participant and timing information

### **Frontend Integration**
- `page.tsx`: Main page includes countdown component
- `BountyDisplay.tsx`: Detailed escape plan information in research tab
- Real-time updates across all components

## Benefits

1. **Transparency**: Users always know the current escape plan status
2. **Engagement**: Creates urgency and encourages participation
3. **Fairness**: Clear visibility of who will benefit from escape plan
4. **Real-time**: Live updates keep information current
5. **User-friendly**: Clear visual design and intuitive information display

## Future Enhancements

- Sound notifications when escape plan is ready
- Push notifications for mobile users
- Historical data showing past escape plan triggers
- More detailed participant statistics
- Integration with wallet notifications
