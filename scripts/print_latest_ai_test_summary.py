#!/usr/bin/env python3
"""
Helper script to print a summary of the latest AI resistance test run.

This script does NOT trigger any new tests. It only queries the database
using the configured ``DATABASE_URL`` (e.g., on DigitalOcean) and prints
high-level stats, rankings, and per-target summaries for the most recent
``AITestRun`` record.
"""

import asyncio
from typing import Optional

from src.database import AsyncSessionLocal
from sqlalchemy import select

from src.models import AITestRun
from src.services.ai_test_analysis import analyze_results, generate_rankings


async def _get_latest_test_run_id() -> Optional[int]:
    """Fetch the most recent AI resistance test run ID from the database."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AITestRun).order_by(AITestRun.id.desc()).limit(1)
        )
        last_run = result.scalars().first()
        return last_run.id if last_run else None


async def main() -> None:
    """Entry point for printing the latest AI test run summary."""
    test_run_id = await _get_latest_test_run_id()
    if test_run_id is None:
        print("⚠️  No AI resistance test runs found in the database.")
        return

    print(f"🔍 Fetching summary for latest AI test run (id={test_run_id})...")

    analysis = await analyze_results(test_run_id)
    rankings = await generate_rankings(test_run_id)

    print("\n============================================================")
    print("🎯 LATEST AI RESISTANCE TEST RUN SUMMARY")
    print("============================================================")

    print(f"\nTest Run ID: {test_run_id}")
    print(f"Total Tests: {analysis.get('total_tests', 0)}")
    print(f"Successful Jailbreaks: {analysis.get('successful', 0)}")
    print(f"Failed Jailbreaks: {analysis.get('failed', 0)}")
    print(f"Success Rate: {analysis.get('success_rate', 0.0):.2%}")
    print(f"Total Questions Asked: {analysis.get('total_questions', 0)}")
    print(f"Avg Questions (overall): {analysis.get('avg_questions', 0.0):.2f}")
    print(f"Avg Duration (overall): {analysis.get('avg_duration', 0.0):.1f}s")

    # Rankings by attacking provider & difficulty.
    r_rankings = rankings.get("rankings", [])
    if r_rankings:
        print("\n📊 Rankings by Resistance (Avg Questions to Jailbreak):")
        for i, ranking in enumerate(r_rankings, 1):
            provider = ranking["provider"].upper()
            difficulty = ranking["difficulty"]
            avg_questions = ranking.get("avg_questions", 0.0)
            success_rate = ranking.get("success_rate", 0.0)
            test_count = ranking.get("test_count", 0)
            print(
                f"  {i}. {provider} ({difficulty}) - "
                f"avg_questions={avg_questions:.2f}, "
                f"success_rate={success_rate:.2%}, tests={test_count}"
            )

    # Per-target summary so we can see which LLMs were hardest/easiest to jailbreak.
    by_target = rankings.get("by_target", [])
    if by_target:
        print("\n📊 Per-Target Summary (by difficulty):")
        for entry in by_target:
            target = entry["target_llm"].upper()
            difficulty = entry["difficulty"]
            attempts = entry["attempts"]
            successes = entry["successes"]
            success_rate = entry["success_rate"]
            avg_q = entry["avg_questions"]
            avg_dur = entry["avg_duration"]
            print(
                f"  {target} ({difficulty}): attempts={attempts}, "
                f"successes={successes}, success_rate={success_rate:.1%}, "
                f"avg_questions={avg_q:.2f}, avg_duration={avg_dur:.1f}s"
            )

    # Recommended difficulty assignments, if any.
    recs = rankings.get("recommendations", [])
    if recs:
        print("\n💡 Recommended Difficulty Assignments:")
        for rec in recs:
            provider = rec.get("provider")
            provider_label = provider.upper() if isinstance(provider, str) else "N/A"
            print(
                f"  - {rec['difficulty']}: {provider_label} "
                f"(avg_questions={rec.get('avg_questions', 0.0):.2f})"
            )

    print("\n✅ Latest test run summary complete.")


if __name__ == "__main__":
    asyncio.run(main())


