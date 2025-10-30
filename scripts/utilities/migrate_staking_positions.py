"""Utility to align the staking_positions table with the current ORM model.

This script upgrades legacy staking tables so the backend can serve the
mock lottery staking API without hitting missing-column errors. Older builds
only tracked a few staking fields; the refreshed schema stores wallet context,
reward projections, and timestamp metadata that mirrors the 60/20/10/10 lottery
split used by the on-chain program. Run this script once per database whenever
the staking schema drifts out of sync (e.g., after restoring a backup).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone
from typing import Dict, Iterable, Set

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncConnection


def _load_environment() -> None:
    """Load environment variables before importing the shared engine."""

    # Allow .env overrides so local runs pick up the intended database.
    load_dotenv()


_load_environment()

# Import after the environment is available so engine points at the right DB.
from src.database import engine  # noqa: E402


def _dialect_name(conn: AsyncConnection) -> str:
    """Return the SQL dialect we're connected to (sqlite or postgresql)."""

    return conn.dialect.name


async def _existing_columns(conn: AsyncConnection, table: str) -> Set[str]:
    """Fetch existing column names for the given table."""

    dialect = _dialect_name(conn)
    if dialect == "sqlite":
        result = await conn.execute(text(f"PRAGMA table_info('{table}')"))
        return {row[1] for row in result}

    result = await conn.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table
              AND table_schema = current_schema()
            """
        ),
        {"table": table},
    )
    return {row[0] for row in result}


async def _ensure_column(
    conn: AsyncConnection,
    table: str,
    column: str,
    type_map: Dict[str, str],
) -> None:
    """Add the column if it does not exist."""

    dialect = _dialect_name(conn)
    definition = type_map.get(dialect)
    if definition is None:
        raise ValueError(f"Unsupported dialect '{dialect}' for column {column}")

    sql = text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    await conn.execute(sql)


async def _rename_column(
    conn: AsyncConnection,
    table: str,
    old_name: str,
    new_name: str,
) -> None:
    """Rename a column when both names differ across schema versions."""

    sql = text(f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}")
    await conn.execute(sql)


async def _backfill_columns(conn: AsyncConnection, available_columns: Iterable[str]) -> None:
    """Populate newly added staking columns using legacy data where possible."""

    columns = set(available_columns)

    # Preserve historical reward projections so the lottery dashboard stays deterministic.
    if {"claimable_rewards", "estimated_rewards"}.issubset(columns):
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET claimable_rewards = estimated_rewards
                WHERE claimable_rewards IS NULL AND estimated_rewards IS NOT NULL
                """
            )
        )

    # Carry forward historical withdrawals into the new unstaked_at field.
    if {"unstaked_at", "withdrawn_at"}.issubset(columns):
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET unstaked_at = withdrawn_at
                WHERE unstaked_at IS NULL AND withdrawn_at IS NOT NULL
                """
            )
        )

    # Tie on-chain transaction signatures to the refreshed column name.
    if {"stake_tx_signature", "transaction_signature"}.issubset(columns):
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET stake_tx_signature = transaction_signature
                WHERE stake_tx_signature IS NULL AND transaction_signature IS NOT NULL
                """
            )
        )

    # Align tier allocation percentages with the 30/60/90 day lottery split.
    if "tier_allocation_percentage" in columns:
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET tier_allocation_percentage = 20.0
                WHERE tier_allocation_percentage IS NULL
                  AND staking_period_days = 30
                """
            )
        )
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET tier_allocation_percentage = 30.0
                WHERE tier_allocation_percentage IS NULL
                  AND staking_period_days = 60
                """
            )
        )
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET tier_allocation_percentage = 50.0
                WHERE tier_allocation_percentage IS NULL
                  AND staking_period_days = 90
                """
            )
        )

    # Default status labels so clients can show active vs. unstaked stakes.
    if "status" in columns:
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET status = CASE
                    WHEN COALESCE(is_active, FALSE) THEN 'active'
                    ELSE 'inactive'
                END
                WHERE status IS NULL
                """
            )
        )

    # Mirror claimed totals into the new cumulative rewards field.
    if {"total_rewards_earned", "claimed_rewards"}.issubset(columns):
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET total_rewards_earned = claimed_rewards
                WHERE total_rewards_earned IS NULL AND claimed_rewards IS NOT NULL
                """
            )
        )

    # Ensure the timestamp columns have sensible defaults for auditing.
    now_iso = datetime.now(timezone.utc).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()
    if "created_at" in columns:
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET created_at = COALESCE(created_at, staked_at, :now)
                """
            ),
            {"now": now_iso},
        )
    if "updated_at" in columns:
        await conn.execute(
            text(
                """
                UPDATE staking_positions
                SET updated_at = COALESCE(updated_at, created_at, :now)
                """
            ),
            {"now": now_iso},
        )


async def _ensure_unique_index(conn: AsyncConnection) -> None:
    """Create a unique index for stake_tx_signature if it does not exist."""

    dialect = _dialect_name(conn)
    if dialect == "sqlite":
        sql = text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_staking_positions_stake_tx_signature
            ON staking_positions(stake_tx_signature)
            """
        )
    else:
        sql = text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_staking_positions_stake_tx_signature
            ON staking_positions(stake_tx_signature)
            """
        )

    await conn.execute(sql)


async def migrate_staking_positions() -> None:
    """Entry point for upgrading the staking schema."""

    column_definitions: Dict[str, Dict[str, str]] = {
        # Wallet context ensures we can attribute lottery payouts to Solana addresses.
        "wallet_address": {"sqlite": "TEXT", "postgresql": "VARCHAR(255)"},
        # Store the on-chain signature used to fund the staking vault.
        "stake_tx_signature": {"sqlite": "TEXT", "postgresql": "VARCHAR(255)"},
        # Percentage of the vault allocated to the stake's lock duration (20/30/50).
        "tier_allocation_percentage": {"sqlite": "REAL", "postgresql": "DOUBLE PRECISION"},
        # Textual lifecycle status keeps the UI aligned with the smart contract flow.
        "status": {"sqlite": "TEXT", "postgresql": "VARCHAR(50)"},
        # Snapshot of rewards still claimable for the current epoch.
        "claimable_rewards": {"sqlite": "REAL", "postgresql": "DOUBLE PRECISION"},
        # Running total of rewards paid out across epochs.
        "total_rewards_earned": {"sqlite": "REAL", "postgresql": "DOUBLE PRECISION"},
        # Optional Solana address where rewards should be sent.
        "reward_wallet_address": {"sqlite": "TEXT", "postgresql": "VARCHAR(255)"},
        # Timestamp bookkeeping so we match blockchain vesting windows.
        "last_reward_calculated_at": {"sqlite": "TIMESTAMP", "postgresql": "TIMESTAMP"},
        "unstaked_at": {"sqlite": "TIMESTAMP", "postgresql": "TIMESTAMP"},
        "created_at": {"sqlite": "TIMESTAMP", "postgresql": "TIMESTAMP"},
        "updated_at": {"sqlite": "TIMESTAMP", "postgresql": "TIMESTAMP"},
        # JSON blob capturing projected rewards used by the lottery dashboard.
        "extra_metadata": {"sqlite": "TEXT", "postgresql": "JSONB"},
    }

    async with engine.begin() as conn:
        try:
            existing = await _existing_columns(conn, "staking_positions")

            # Legacy builds used different column names; migrate them before adding new ones.
            if "transaction_signature" in existing and "stake_tx_signature" not in existing:
                try:
                    await _rename_column(conn, "staking_positions", "transaction_signature", "stake_tx_signature")
                    existing.add("stake_tx_signature")
                    existing.discard("transaction_signature")
                except SQLAlchemyError:
                    # Fall back to adding a new column if the rename is not supported.
                    pass

            if "withdrawn_at" in existing and "unstaked_at" not in existing:
                try:
                    await _rename_column(conn, "staking_positions", "withdrawn_at", "unstaked_at")
                    existing.add("unstaked_at")
                    existing.discard("withdrawn_at")
                except SQLAlchemyError:
                    pass

            if "estimated_rewards" in existing and "claimable_rewards" not in existing:
                # Keep estimated_rewards around for comparison but still add the new column.
                pass

            for column, type_map in column_definitions.items():
                if column in existing:
                    continue
                await _ensure_column(conn, "staking_positions", column, type_map)

            updated_columns = await _existing_columns(conn, "staking_positions")

            await _backfill_columns(conn, updated_columns)
            await _ensure_unique_index(conn)
        except SQLAlchemyError as exc:
            raise RuntimeError(f"Failed to migrate staking_positions: {exc}") from exc


def main() -> None:
    """CLI entry point."""

    asyncio.run(migrate_staking_positions())


if __name__ == "__main__":
    main()


