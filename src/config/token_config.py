"""Token economics configuration shared by backend services.

This module consolidates all revenue split parameters so our FastAPI backend,
smart-contract integration, and staking services apply the exact same
distribution math. Keeping these constants in one place prevents subtle bugs
where the lottery smart contract (60/40 jackpot/buyback split) would disagree
with the Python allocation logic.

The enum and helpers below are also imported by tests and monitoring scripts to
validate the on-chain staking program. Please update the values here whenever
the revenue split changes so the frontend, mobile app, and smart contracts stay
in sync.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List


class StakingPeriod(Enum):
    """Supported staking lock periods expressed in days.

    These values map directly to the Solana staking program tiers, so do not
    change them without coordinating an on-chain migration.
    """

    THIRTY_DAYS = 30
    SIXTY_DAYS = 60
    NINETY_DAYS = 90


# ---------------------------------------------------------------------------
# Core $100Bs token metadata
# ---------------------------------------------------------------------------

TOKEN_NAME = "100 Billion ETF"
TOKEN_SYMBOL = "$100Bs"
TOKEN_MINT_ADDRESS = "5ic4A4scnqeAT2XkwvWCUYjZoxjVLvoTz4njbmAhbonk"
TOKEN_DECIMALS = 8
TOKEN_TOTAL_SUPPLY = 999_745_347.873
NETWORK = "mainnet-beta"


# ---------------------------------------------------------------------------
# Revenue split configuration (lottery smart contract, 60/40 jackpot/buyback)
# ---------------------------------------------------------------------------

# 60% of each bounty entry feeds the active jackpot pool.
BOUNTY_CONTRIBUTION_RATE: float = 0.60
# 20% previously covered operational expenses; now kept at 0.0 for compatibility.
OPERATIONAL_FEE_RATE: float = 0.0
# 40% funds the $100Bs buyback-and-burn wallet.
BUYBACK_RATE: float = 0.40
# 10% previously routed to the staking rewards vault; now 0.0, funded separately.
_STAKING_REVENUE_PERCENTAGE_DEPRECATED: float = 0.0
# Backwards-compatible alias for legacy imports that still expect this constant.
STAKING_REVENUE_PERCENTAGE: float = _STAKING_REVENUE_PERCENTAGE_DEPRECATED

# Convenience constant leveraged by health checks to make sure nothing exceeds
# 100% of incoming funds.
REVENUE_SPLIT_TOTAL: float = (
    BOUNTY_CONTRIBUTION_RATE
    + BUYBACK_RATE
)


# ---------------------------------------------------------------------------
# Staking tier allocations
# ---------------------------------------------------------------------------

TIER_ALLOCATIONS: Dict[StakingPeriod, float] = {
    StakingPeriod.THIRTY_DAYS: 0.20,  # Flexible tier – lowest rewards
    StakingPeriod.SIXTY_DAYS: 0.30,   # Balanced tier
    StakingPeriod.NINETY_DAYS: 0.50,  # Longest lock, highest share
}


def get_tier_allocation(period_days: int) -> float:
    """Return the percentage of the staking pool assigned to the given lock period."""

    for period, allocation in TIER_ALLOCATIONS.items():
        if period.value == period_days:
            return allocation
    raise ValueError(f"Unsupported staking period: {period_days}")


DEFAULT_STAKING_PERIODS = [period.value for period in StakingPeriod]


# ---------------------------------------------------------------------------
# Token discount tiers (frontend/mobile still consume this data)
# ---------------------------------------------------------------------------

DISCOUNT_TIERS: Dict[int, float] = {
    1_000_000: 0.10,      # 1M tokens = 10% off
    10_000_000: 0.25,     # 10M tokens = 25% off
    100_000_000: 0.50,    # 100M tokens = 50% off
}


def get_discount_for_balance(token_balance: float) -> float:
    """Return the discount percentage a user qualifies for based on holdings."""

    sorted_tiers = sorted(DISCOUNT_TIERS.items(), key=lambda item: item[0], reverse=True)
    for threshold, discount in sorted_tiers:
        if token_balance >= threshold:
            return discount
    return 0.0


def calculate_discounted_price(base_price: float, token_balance: float) -> Dict[str, float]:
    """Calculate the discounted price for a query given a holder's balance."""

    discount_rate = get_discount_for_balance(token_balance)
    discount_amount = base_price * discount_rate
    final_price = base_price - discount_amount

    return {
        "base_price": base_price,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "final_price": final_price,
        "savings": discount_amount,
        "tokens_required": get_next_tier_requirement(token_balance),
    }


def get_next_tier_requirement(current_balance: float) -> float:
    """Return additional tokens needed to reach the next discount tier."""

    for threshold in sorted(DISCOUNT_TIERS):
        if current_balance < threshold:
            return threshold - current_balance
    return 0.0


def get_tier_info() -> List[Dict[str, float]]:
    """Provide human-friendly descriptions of the discount tiers."""

    tiers: List[Dict[str, float]] = []
    for threshold, discount in sorted(DISCOUNT_TIERS.items()):
        tiers.append(
            {
                "tokens_required": threshold,
                "discount_percentage": discount * 100,
                "description": f"{threshold:,.0f} tokens = {discount*100:.0f}% off",
            }
        )
    return tiers


