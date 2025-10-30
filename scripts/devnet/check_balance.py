"""
Check devnet SOL balance and optionally request airdrop.
Usage:
  python3 scripts/devnet/check_balance.py  # read-only
  AIRDROP=1 SOLANA_PUBKEY=<pubkey> python3 scripts/devnet/check_balance.py  # airdrop 2 SOL

Notes:
- Uses default `solana address` to read pubkey if SOLANA_PUBKEY not set
- Does not modify state unless AIRDROP=1
"""
from __future__ import annotations
import os
import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

DEVNET = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")

async def main() -> None:
    from solana.rpc.commitment import Confirmed
    client = AsyncClient(DEVNET, commitment=Confirmed)
    pubkey_str = os.getenv("SOLANA_PUBKEY")
    if not pubkey_str:
        try:
            from subprocess import check_output
            pubkey_str = check_output(["solana", "address"]).decode().strip()
        except Exception as e:
            raise RuntimeError("Set SOLANA_PUBKEY env or install solana CLI to read default address") from e
    pubkey = Pubkey.from_string(pubkey_str)
    resp = await client.get_balance(pubkey)
    lamports = getattr(resp.value, "value", resp.value)
    sol = lamports / 1_000_000_000
    print(f"Devnet balance for {pubkey}: {sol:.6f} SOL")
    if os.getenv("AIRDROP", "0") == "1":
        sig = await client.request_airdrop(pubkey, 2_000_000_000)
        print(f"Requested airdrop: {sig.value}")
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
