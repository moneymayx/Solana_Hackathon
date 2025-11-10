#!/usr/bin/env python3
"""Tests for the V3EntryNonceTracker model."""
import sys
from pathlib import Path
from datetime import datetime

import pytest

# Ensure src package is importable when running directly
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))


@pytest.mark.asyncio
async def test_v3_entry_nonce_tracker():
    """Verify nonce tracking supports multiple increments per wallet."""
    from sqlalchemy import select

    from src.database import create_tables, AsyncSessionLocal
    from src.models import V3EntryNonceTracker

    # Create tables (idempotent for sqlite) so the tracker table exists
    await create_tables()

    wallet_address = "TestWallet11111111111111111111111111111111"

    async with AsyncSessionLocal() as session:
        # Ensure clean slate for the wallet under test
        await session.execute(
            V3EntryNonceTracker.__table__.delete().where(
                V3EntryNonceTracker.wallet_address == wallet_address
            )
        )
        await session.commit()

        # Insert initial tracker (simulates first contact with backend)
        tracker = V3EntryNonceTracker(
            wallet_address=wallet_address,
            current_nonce=0,
            updated_at=datetime.utcnow(),
        )
        session.add(tracker)
        await session.commit()

        # Fetch and assert initial state
        result = await session.execute(
            select(V3EntryNonceTracker).where(V3EntryNonceTracker.wallet_address == wallet_address)
        )
        record = result.scalar_one()
        assert record.current_nonce == 0, "Initial nonce should default to zero"

        # Simulate first payment increment
        record.current_nonce += 1
        record.updated_at = datetime.utcnow()
        await session.commit()

        result = await session.execute(
            select(V3EntryNonceTracker).where(V3EntryNonceTracker.wallet_address == wallet_address)
        )
        record = result.scalar_one()
        assert record.current_nonce == 1, "Nonce should increment to one after first payment"

        # Simulate second payment increment and verify persistence
        record.current_nonce += 1
        record.updated_at = datetime.utcnow()
        await session.commit()

        result = await session.execute(
            select(V3EntryNonceTracker).where(V3EntryNonceTracker.wallet_address == wallet_address)
        )
        record = result.scalar_one()
        assert record.current_nonce == 2, "Nonce should increment sequentially for each payment"


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_v3_entry_nonce_tracker())
