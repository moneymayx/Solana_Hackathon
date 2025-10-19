"""
$100Bs Token Configuration
Token economics and integration settings for Billions Bounty platform
"""
from typing import Dict, List
from enum import Enum

# Token Details
TOKEN_NAME = "100 Billion ETF"
TOKEN_SYMBOL = "$100Bs"
TOKEN_MINT_ADDRESS = "5ic4A4scnqeAT2XkwvWCUYjZoxjVLvoTz4njbmAhbonk"
TOKEN_DECIMALS = 8
TOKEN_TOTAL_SUPPLY = 999_745_347.873
NETWORK = "mainnet-beta"

# Discount Tiers (amount → discount %)
DISCOUNT_TIERS = {
    1_000_000: 0.10,      # 1M tokens = 10% off
    10_000_000: 0.25,     # 10M tokens = 25% off
    100_000_000: 0.50,    # 100M tokens = 50% off
}

# Staking Configurations
class StakingPeriod(Enum):
    """Staking lock periods"""
    THIRTY_DAYS = 30
    SIXTY_DAYS = 60
    NINETY_DAYS = 90

# Revenue-based staking rewards (no fixed APY)
STAKING_REVENUE_PERCENTAGE = 0.30  # 30% of platform revenue goes to stakers

# Tier allocation - how the staking pool is divided between lock periods
TIER_ALLOCATIONS = {
    StakingPeriod.THIRTY_DAYS: 0.20,   # 30-day tier gets 20% of staking pool
    StakingPeriod.SIXTY_DAYS: 0.30,    # 60-day tier gets 30% of staking pool
    StakingPeriod.NINETY_DAYS: 0.50,   # 90-day tier gets 50% of staking pool
}

# Buyback Configuration
BUYBACK_PERCENTAGE = 0.05  # 5% of platform revenue
BUYBACK_FREQUENCY_DAYS = 30  # Monthly buyback

# Platform Fee Structure
BASE_QUERY_COST = 10.0  # $10 per query (default)
QUERY_COST_CURRENCY = "USD"

# Treasury Configuration
TREASURY_ALLOCATION = {
    "staking_rewards": 0.30,    # 30% to staking rewards pool
    "buyback": 0.05,            # 5% to buyback fund
    "operations": 0.40,         # 40% to operations
    "jackpot": 0.25,           # 25% to jackpot
}

# Token Program IDs
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Standard SPL Token

def get_discount_for_balance(token_balance: float) -> float:
    """
    Calculate discount percentage based on token balance
    
    Args:
        token_balance: Amount of $100Bs tokens held
        
    Returns:
        Discount as decimal (0.0 to 0.5)
    """
    # Sort tiers from highest to lowest
    sorted_tiers = sorted(DISCOUNT_TIERS.items(), key=lambda x: x[0], reverse=True)
    
    for threshold, discount in sorted_tiers:
        if token_balance >= threshold:
            return discount
    
    return 0.0  # No discount if below minimum threshold

def calculate_discounted_price(base_price: float, token_balance: float) -> Dict[str, float]:
    """
    Calculate final price after token holder discount
    
    Args:
        base_price: Original price
        token_balance: Amount of $100Bs tokens held
        
    Returns:
        Dictionary with price breakdown
    """
    discount_rate = get_discount_for_balance(token_balance)
    discount_amount = base_price * discount_rate
    final_price = base_price - discount_amount
    
    return {
        "base_price": base_price,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "savings": discount_amount,
        "tokens_required": get_next_tier_requirement(token_balance)
    }

def get_next_tier_requirement(current_balance: float) -> float:
    """
    Get token amount needed to reach next discount tier
    
    Args:
        current_balance: Current token balance
        
    Returns:
        Tokens needed for next tier, or 0 if at max tier
    """
    sorted_tiers = sorted(DISCOUNT_TIERS.keys())
    
    for threshold in sorted_tiers:
        if current_balance < threshold:
            return threshold - current_balance
    
    return 0.0  # Already at max tier

def calculate_staking_share(
    amount: float,
    period: StakingPeriod,
    tier_total_staked: float,
    monthly_staking_pool: float
) -> Dict[str, float]:
    """
    Calculate staking rewards based on revenue share model
    
    Args:
        amount: Amount of tokens to stake
        period: Staking period (30/60/90 days)
        tier_total_staked: Total tokens staked in this tier
        monthly_staking_pool: Total monthly revenue allocated to staking
        
    Returns:
        Dictionary with reward calculations
    """
    days = period.value
    
    # Get this tier's allocation percentage
    tier_allocation = TIER_ALLOCATIONS[period]
    
    # Calculate this tier's pool amount
    tier_pool = monthly_staking_pool * tier_allocation
    
    # Calculate user's share of the tier
    if tier_total_staked > 0:
        user_share = amount / tier_total_staked
        estimated_monthly_rewards = tier_pool * user_share
    else:
        estimated_monthly_rewards = 0.0
    
    # Estimate for the full lock period
    months_locked = days / 30
    estimated_period_rewards = estimated_monthly_rewards * months_locked
    
    return {
        "staked_amount": amount,
        "staking_days": days,
        "tier_allocation_percentage": tier_allocation * 100,
        "estimated_monthly_rewards": estimated_monthly_rewards,
        "estimated_period_rewards": estimated_period_rewards,
        "total_return": amount + estimated_period_rewards,
        "user_share_of_tier": user_share if tier_total_staked > 0 else 0,
        "note": "Rewards based on actual platform revenue - estimates may vary"
    }

def get_tier_info() -> List[Dict]:
    """
    Get formatted information about all discount tiers
    
    Returns:
        List of tier information dictionaries
    """
    tiers = []
    sorted_tiers = sorted(DISCOUNT_TIERS.items(), key=lambda x: x[0])
    
    for threshold, discount in sorted_tiers:
        tiers.append({
            "tokens_required": threshold,
            "discount_percentage": discount * 100,
            "description": f"{threshold:,.0f} tokens = {discount*100:.0f}% off"
        })
    
    return tiers

# Example usage and testing
if __name__ == "__main__":
    print(f"Token: {TOKEN_NAME} ({TOKEN_SYMBOL})")
    print(f"Mint: {TOKEN_MINT_ADDRESS}")
    print(f"Decimals: {TOKEN_DECIMALS}")
    print(f"Total Supply: {TOKEN_TOTAL_SUPPLY:,.3f}")
    print()
    
    print("Discount Tiers:")
    for tier in get_tier_info():
        print(f"  - {tier['description']}")
    print()
    
    print("Staking Tier Allocations (Revenue-Based):")
    print(f"  Platform allocates {STAKING_REVENUE_PERCENTAGE*100}% of revenue to stakers")
    for period, allocation in TIER_ALLOCATIONS.items():
        print(f"  - {period.value} days: {allocation*100}% of staking pool")
    print()
    
    # Test discount calculation
    test_balances = [500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000]
    print("Example Discount Calculations ($10 base query):")
    for balance in test_balances:
        result = calculate_discounted_price(10.0, balance)
        print(f"  {balance:>12,} tokens → ${result['final_price']:.2f} ({result['discount_rate']*100:.0f}% off)")

