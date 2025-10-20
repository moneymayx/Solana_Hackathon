# 🔄 Staking Model Update: Revenue-Based Rewards

## 📋 Change Summary

**Changed from:** Fixed APY staking model  
**Changed to:** Revenue-based tiered reward system  
**Date:** October 19, 2025  
**Reason:** Sustainable, transparent rewards tied to actual platform performance

---

## ❌ Old Model (Fixed APY - REMOVED)

### **Problems:**
- ⚠️ **Unsustainable**: Promised 5-25% APY with no guaranteed revenue
- ⚠️ **Risky**: Could go bankrupt if revenue < promised rewards
- ⚠️ **Misleading**: APY implies guaranteed returns
- ⚠️ **Inflexible**: Can't adjust rewards based on performance

### **What it was:**
```
30 days → 5% APY
60 days → 12% APY
90 days → 25% APY

Example: Stake 1M tokens for 90 days
→ Guaranteed 6,164 tokens reward (regardless of revenue)
```

---

## ✅ New Model (Revenue-Based - CURRENT)

### **Benefits:**
- ✅ **Sustainable**: Rewards only distributed if there's revenue
- ✅ **Transparent**: Users see actual platform performance
- ✅ **Fair**: Everyone shares proportionally
- ✅ **Flexible**: Rewards scale with success
- ✅ **Honest**: No false promises

### **How It Works:**

#### **1. Revenue Allocation**
```
Monthly Revenue: $10,000
├─ 30% → Staking Pool ($3,000)
├─ 5% → Buyback ($500)
├─ 40% → Operations ($4,000)
└─ 25% → Jackpot ($2,500)
```

#### **2. Tier Distribution**
```
Staking Pool: $3,000
├─ 30-day tier: 20% → $600
├─ 60-day tier: 30% → $900
└─ 90-day tier: 50% → $1,500
```

#### **3. User Share Calculation**
```
90-day tier pool: $1,500
Total staked in 90-day tier: 10M tokens

You stake: 1M tokens
Your share: 1M / 10M = 10%
Your reward: $1,500 × 10% = $150/month

Total for 90 days: $150 × 3 months = $450
```

---

## 📊 Comparison Example

**Scenario:** User stakes 1M tokens for 90 days

### **Old Model (Fixed APY):**
- Promise: 25% APY
- Reward: 6,164 tokens (guaranteed)
- Platform risk: Must pay even with $0 revenue
- **Problem:** Unsustainable

### **New Model (Revenue-Based):**
**If $10k monthly revenue:**
- Reward: $450 (3 months × $150)
- Platform risk: Only pays from actual revenue
- **Result:** Sustainable

**If $50k monthly revenue:**
- Staking pool: $15,000/month
- 90-day tier: $7,500/month
- Your reward: $2,250 (3 months)
- **Result:** Everyone wins!

**If $0 revenue:**
- Reward: $0
- Platform risk: No obligation
- **Result:** Honest and fair

---

## 🔧 Technical Changes

### **Files Updated:**

1. **`src/token_config.py`**
   - ✅ Removed `STAKING_APY`
   - ✅ Added `STAKING_REVENUE_PERCENTAGE = 0.30`
   - ✅ Added `TIER_ALLOCATIONS` dict
   - ✅ Changed `calculate_staking_rewards()` → `calculate_staking_share()`

2. **`src/token_economics_service.py`**
   - ✅ Updated `create_staking_position()` to use revenue-based calculation
   - ✅ Added `_get_tier_total_staked()` method
   - ✅ Stores tier allocation in `apy_rate` field (for compatibility)

3. **`src/revenue_distribution_service.py`** (NEW)
   - ✅ `calculate_monthly_distribution()` - Calculate revenue split
   - ✅ `execute_distribution()` - Distribute rewards monthly
   - ✅ `get_user_projected_earnings()` - Show projected earnings
   - ✅ `get_tier_statistics()` - Tier stats for transparency

4. **`src/models.py`**
   - ℹ️ No changes needed (existing `StakingPosition` model works)
   - ℹ️ `apy_rate` field repurposed to store tier allocation %

5. **Documentation**
   - ✅ Updated `PHASE2_COMPLETE.md`
   - ✅ Created `STAKING_MODEL_UPDATE.md` (this file)

---

## 🎯 Configuration

### **Current Settings:**
```python
# src/token_config.py

STAKING_REVENUE_PERCENTAGE = 0.30  # 30% to stakers
BUYBACK_PERCENTAGE = 0.05  # 5% to buyback
# Remaining: 40% operations, 25% jackpot

TIER_ALLOCATIONS = {
    StakingPeriod.THIRTY_DAYS: 0.20,   # 20% of staking pool
    StakingPeriod.SIXTY_DAYS: 0.30,    # 30% of staking pool
    StakingPeriod.NINETY_DAYS: 0.50,   # 50% of staking pool
}
```

### **Adjustable Parameters:**
- `STAKING_REVENUE_PERCENTAGE` - What % of revenue goes to stakers
- `TIER_ALLOCATIONS` - How staking pool is split between tiers
- Both can be tuned based on platform needs

---

## 💡 User Communication

### **What to Tell Users:**

**❌ Don't say:**
- "Earn 25% APY"
- "Guaranteed returns"
- "Fixed interest rate"

**✅ Do say:**
- "Earn from 30% of platform revenue"
- "90-day stakers get 50% of the staking pool"
- "Last month, 90-day stakers earned an average of $150 per 1M tokens"
- "Rewards vary based on platform performance"
- "Lock longer, earn more of the revenue share"

### **Example User-Facing Copy:**
```
🎁 Revenue Share Staking

Lock your $100Bs tokens and earn from platform success!

30 Days: Get 20% of staking rewards pool
60 Days: Get 30% of staking rewards pool  
90 Days: Get 50% of staking rewards pool ⭐

How it works:
• 30% of monthly platform revenue → staking pool
• Longer locks = bigger share of the pool
• Your rewards = (your tokens / tier total) × tier pool

Last month's staking pool: $3,000
Average 90-day staker (1M tokens): $150/month

Rewards based on actual revenue. Past performance doesn't guarantee future results.
```

---

## 📈 Expected Outcomes

### **For Platform:**
- ✅ Sustainable staking program
- ✅ No risk of bankruptcy from fixed obligations
- ✅ Aligned incentives (users want platform to succeed)
- ✅ Flexible rewards adjust with growth

### **For Token Holders:**
- ✅ Transparent revenue sharing
- ✅ Proportional and fair distribution
- ✅ Better rewards if platform grows
- ✅ Honest expectations

### **For $100Bs Token:**
- ✅ Increased utility (staking for revenue)
- ✅ Deflationary pressure (locked supply)
- ✅ Long-term holder incentives
- ✅ Value tied to platform success

---

## 🧪 Testing

### **Test Revenue Distribution:**
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate

# Test calculation
python3 << EOF
from src.revenue_distribution_service import revenue_distribution_service
from src.database import AsyncSessionLocal
import asyncio

async def test():
    async with AsyncSessionLocal() as db:
        # Simulate $10k monthly revenue
        distribution = await revenue_distribution_service.calculate_monthly_distribution(
            db=db,
            monthly_revenue=10000
        )
        
        print(f"Total staking pool: ${distribution['total_staking_pool']:,.2f}")
        print(f"Total stakers: {distribution['total_stakers']}")
        print("\\nTier breakdown:")
        for tier_name, tier_data in distribution['tiers'].items():
            print(f"  {tier_name}: ${tier_data['tier_pool']:,.2f} → {tier_data['staker_count']} stakers")

asyncio.run(test())
EOF
```

---

## ✅ Migration Status

- [x] Code updated
- [x] Database models compatible (no migration needed)
- [x] Documentation updated
- [x] Configuration adjusted
- [x] New service created (RevenueDistributionService)
- [ ] Frontend updated (to be done)
- [ ] User communication drafted
- [ ] Monthly distribution scheduled

---

## 🚀 Next Steps

1. **Test the new model** with current database
2. **Create admin endpoint** to execute monthly distributions
3. **Update frontend** to show:
   - Current tier sizes
   - Projected earnings
   - Last month's distribution
4. **Schedule monthly task** to distribute rewards
5. **Communicate change** to existing stakers (if any)

---

## 📚 Related Files

- `src/token_config.py` - Core configuration
- `src/token_economics_service.py` - Token operations
- `src/revenue_distribution_service.py` - Distribution logic
- `PHASE2_COMPLETE.md` - Phase 2 documentation

---

**This change makes staking sustainable, transparent, and aligned with platform success! 🎉**

