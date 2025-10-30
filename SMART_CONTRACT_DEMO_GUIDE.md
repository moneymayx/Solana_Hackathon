# 🎬 How to Show Smart Contract Activity in Your Demo

## Overview

You now have **live smart contract monitoring** built into your platform! This makes it easy to prove that your smart contracts are actually being triggered during demos.

---

## 🚀 Quick Start

### 1. Add the Contract Activity Monitor to Any Page

```tsx
import ContractActivityMonitor from '@/components/ContractActivityMonitor'

// In your component:
<ContractActivityMonitor 
  autoRefresh={true}    // Auto-refresh every 5 seconds
  refreshInterval={5000} // 5 seconds
  maxTransactions={10}   // Show last 10 transactions
/>
```

### 2. Backend Endpoint is Ready

The backend endpoint `/api/contract/activity` is already implemented and returns:
- Lottery entries
- Winner payouts  
- Staking transactions
- Unstaking transactions
- Team contributions

All with clickable Solana Explorer links!

---

## 📍 Where to Add It

### Option 1: Dashboard Page (Recommended)

Add to `/frontend/src/app/dashboard/page.tsx`:

```tsx
import ContractActivityMonitor from '@/components/ContractActivityMonitor'

// Add this section:
<section className="mb-8">
  <ContractActivityMonitor />
</section>
```

### Option 2: Standalone Demo Page

Create `/frontend/src/app/contract-activity/page.tsx`:

```tsx
'use client'

import AppLayout from '@/components/layouts/AppLayout'
import ContractActivityMonitor from '@/components/ContractActivityMonitor'

export default function ContractActivityPage() {
  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Smart Contract Activity</h1>
        <ContractActivityMonitor autoRefresh={true} maxTransactions={20} />
      </div>
    </AppLayout>
  )
}
```

### Option 3: Embed in Existing Components

The monitor can be added anywhere - home page, bounty page, etc.

---

## 🎥 Demo Tips

### During Your Demo:

1. **Show the Contract Activity Monitor**
   - Open it in a side panel or second monitor
   - Point out the "Live" indicator showing it's updating in real-time
   - Click on a transaction to show the Solana Explorer link

2. **Trigger a Transaction**
   - Make a payment (lottery entry)
   - Stake tokens
   - Join a team
   - Watch it appear in the monitor within 5 seconds!

3. **Click Explorer Links**
   - Click "View on Explorer" on any transaction
   - Show the actual Solana transaction details
   - This proves it's real blockchain activity!

4. **Highlight Different Transaction Types**
   - Green = Lottery entries
   - Yellow = Winner payouts
   - Blue = Staking
   - Purple = Team contributions

---

## 🔍 What Gets Displayed

### Transaction Information:
- **Type**: lottery_entry, winner_payout, staking, unstaking, team_contribution
- **Wallet Address**: Shows first 8 and last 8 characters
- **Amount**: Formatted as USD currency
- **Status**: pending (yellow), confirmed (green), failed (red)
- **Transaction Signature**: Full signature with explorer link
- **Timestamp**: Relative time (e.g., "2m ago")

### Visual Indicators:
- ⚡ **Live Badge**: Green pulsing dot when auto-refresh is active
- 🔵 **Status Icons**: 
  - CheckCircle = Confirmed
  - Clock (pulsing) = Pending
  - XCircle = Failed
- 🎯 **Type Icons**:
  - Coins = Lottery entry / Team contribution
  - Trophy = Winner payout
  - Zap = Staking / Unstaking

---

## 🛠️ Customization

### Adjust Refresh Rate:
```tsx
<ContractActivityMonitor 
  autoRefresh={true}
  refreshInterval={3000} // 3 seconds for faster updates
/>
```

### Show More Transactions:
```tsx
<ContractActivityMonitor 
  maxTransactions={20} // Show last 20 transactions
/>
```

### Manual Refresh Only:
```tsx
<ContractActivityMonitor 
  autoRefresh={false} // No auto-refresh, user clicks to refresh
/>
```

---

## 🌐 Explorer Links

All transactions automatically get Solana Explorer links:

- **Devnet**: `https://explorer.solana.com/tx/{signature}?cluster=devnet`
- **Mainnet**: `https://explorer.solana.com/tx/{signature}`

The network is detected from your `SOLANA_NETWORK` environment variable.

---

## 📊 What Transactions Are Tracked

The system tracks these smart contract interactions:

1. **Lottery Entries** (`FundDeposit`)
   - When users pay to enter a lottery
   - Shows amount and wallet address

2. **Winner Payouts** (`Winner`)
   - When smart contract pays out winners
   - Shows prize amount and winner wallet

3. **Staking Deposits** (`StakingDeposit`)
   - When users stake tokens
   - Shows staked amount

4. **Staking Withdrawals** (`StakingWithdrawal`)
   - When users unstake tokens
   - Shows withdrawal amount

5. **Team Contributions** (`TeamContribution`)
   - When users contribute to team funds
   - Shows contribution amount

---

## ✅ Verification Checklist

Before your demo:

- [ ] Backend endpoint `/api/contract/activity` is accessible
- [ ] Component is added to at least one page
- [ ] Test a transaction and verify it appears in the monitor
- [ ] Click an explorer link and verify it opens correctly
- [ ] Check that auto-refresh is working (watch for updates)
- [ ] Verify transactions show correct amounts and addresses

---

## 🎯 Demo Script Snippet

**"Now let me show you the smart contract activity in real-time..."**

1. Open the Contract Activity Monitor
2. Point out: "This is updating automatically every 5 seconds"
3. Show the "Live" indicator
4. **Trigger a transaction** (make a payment, stake, etc.)
5. **Watch it appear** within 5 seconds
6. **Click the explorer link** → "This takes us to the actual Solana transaction"
7. **Show the transaction details** on Solana Explorer
8. **Highlight**: "This proves our smart contracts are actually executing on-chain"

---

## 🔧 Troubleshooting

### No Transactions Showing?
- Check backend logs: `tail -f logs/backend.log`
- Verify endpoint: `curl http://localhost:8000/api/contract/activity`
- Check database has transactions with `transaction_signature` field populated

### Explorer Links Not Working?
- Verify network (devnet vs mainnet)
- Check signature format is correct
- Try manually: `https://explorer.solana.com/tx/{signature}?cluster=devnet`

### Auto-refresh Not Working?
- Check browser console for errors
- Verify `autoRefresh={true}` prop is set
- Check network tab for API calls

---

## 📝 Example Usage in Demo

```tsx
// In your demo page component:
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  {/* Your main content */}
  <div>
    {/* Chat interface, etc */}
  </div>
  
  {/* Contract Activity Sidebar */}
  <div className="sticky top-4">
    <ContractActivityMonitor />
  </div>
</div>
```

---

**Perfect for demos!** Your audience can see blockchain activity happening in real-time! 🚀


