"""
Prepare initialization transactions for v2 global and a sample bounty.
This script ONLY builds the instruction payloads and prints them; it does not send.
Run manually with your wallet if desired.
"""
from __future__ import annotations
from solders.pubkey import Pubkey
from typing import Dict
import json

PROGRAM_ID = Pubkey.from_string("4ChHkYCu5Q8KpBh1pPEx5KgKTQGySikhvzhi3KYrUMuW")

def main() -> None:
    payload: Dict[str, object] = {
        "program_id": str(PROGRAM_ID),
        "instructions": [
            {
                "name": "initialize_lottery",
                "args": {
                    "research_fund_floor": 1_000_000_000,
                    "research_fee": 10_000_000,
                    "bounty_pool_wallet": "<SET>",
                    "operational_wallet": "<SET>",
                    "buyback_wallet": "<SET>",
                    "staking_wallet": "<SET>"
                }
            },
            {
                "name": "initialize_bounty",
                "args": {
                    "bounty_id": 1,
                    "base_price": 10_000_000
                }
            }
        ]
    }
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
