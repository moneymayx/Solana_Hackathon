#!/usr/bin/env python3
"""
Comprehensive AI Resistance Test Statistics Report
==================================================

This script displays:
1. Summary of all test runs
2. Detailed statistics by difficulty level
3. LLM vs LLM attack statistics
4. Rankings and odds calculations
5. All data in easy-to-read tables
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime

# Add project root to path after loading .env so DATABASE_URL resolves correctly.
project_root = Path(__file__).parent.parent
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_root / ".env")
sys.path.insert(0, str(project_root))

from src.database import AsyncSessionLocal
from src.models import AITestResult, AITestRun
from src.services.ai_attacker_service import AIAttackerService
from sqlalchemy import select, func, desc


def format_table_row(cols: List[Tuple[str, int]], align: str = 'left') -> str:
    """Format a table row with specified column widths"""
    if align == 'left':
        return ''.join(f"{str(col[0]):<{col[1]}}" for col in cols)
    elif align == 'right':
        return ''.join(f"{str(col[0]):>{col[1]}}" for col in cols)
    else:  # center
        return ''.join(f"{str(col[0]):^{col[1]}}" for col in cols)


def print_table_header(headers: List[Tuple[str, int]]):
    """Print a formatted table header"""
    print(format_table_row(headers))
    print('-' * sum(h[1] for h in headers))


async def get_all_test_runs() -> List[AITestRun]:
    """Get all test runs ordered by most recent first"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AITestRun).order_by(desc(AITestRun.id))
        )
        return result.scalars().all()


async def get_all_test_results(test_run_id: Optional[int] = None) -> List[AITestResult]:
    """Get all test results, optionally filtered by test_run_id"""
    async with AsyncSessionLocal() as session:
        query = select(AITestResult)
        if test_run_id:
            query = query.where(AITestResult.test_run_id == test_run_id)
        result = await session.execute(query)
        return result.scalars().all()


async def get_comprehensive_statistics() -> Dict[str, Any]:
    """Get comprehensive statistics across all test runs"""
    all_results = await get_all_test_results()
    
    if not all_results:
        return {}
    
    # Overall statistics
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r.was_successful)
    failed_tests = total_tests - successful_tests
    total_questions = sum(r.question_count for r in all_results)
    avg_questions = total_questions / total_tests if total_tests > 0 else 0
    avg_duration = sum(r.duration_seconds for r in all_results) / total_tests if total_tests > 0 else 0
    
    # Group by difficulty
    by_difficulty: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "total_tests": 0,
        "successful": 0,
        "failed": 0,
        "total_questions": 0,
        "targets": defaultdict(lambda: {
            "total_questions": 0,
            "attempts": 0,
            "successful": 0,
            "failed": 0,
            "min_questions": float('inf'),
            "max_questions": 0,
            "avg_questions": 0,
            "question_counts": []
        })
    })
    
    # Group by attacker vs target
    attacker_target_stats: Dict[Tuple[str, str, str], Dict[str, Any]] = defaultdict(lambda: {
        "attempts": 0,
        "successful": 0,
        "failed": 0,
        "total_questions": 0,
        "avg_questions": 0
    })
    
    # Group by target LLM and difficulty
    target_stats: Dict[Tuple[str, str], Dict[str, Any]] = defaultdict(lambda: {
        "total_questions": 0,
        "attempts": 0,
        "successful": 0,
        "failed": 0,
        "attackers": set(),
        "question_counts": []
    })
    
    for r in all_results:
        difficulty = r.target_difficulty.lower() if r.target_difficulty else "unknown"
        target_llm = r.target_llm or "unknown"
        attacker_llm = r.attacker_llm or "unknown"
        
        # Update difficulty stats
        by_difficulty[difficulty]["total_tests"] += 1
        by_difficulty[difficulty]["total_questions"] += r.question_count
        if r.was_successful:
            by_difficulty[difficulty]["successful"] += 1
        else:
            by_difficulty[difficulty]["failed"] += 1
        
        # Update target stats within difficulty
        target_key = (target_llm, difficulty)
        target_stats[target_key]["total_questions"] += r.question_count
        target_stats[target_key]["attempts"] += 1
        target_stats[target_key]["question_counts"].append(r.question_count)
        target_stats[target_key]["attackers"].add(attacker_llm)
        if r.was_successful:
            target_stats[target_key]["successful"] += 1
        else:
            target_stats[target_key]["failed"] += 1
        
        # Update attacker vs target stats
        attack_key = (attacker_llm, target_llm, difficulty)
        attacker_target_stats[attack_key]["attempts"] += 1
        attacker_target_stats[attack_key]["total_questions"] += r.question_count
        if r.was_successful:
            attacker_target_stats[attack_key]["successful"] += 1
        else:
            attacker_target_stats[attack_key]["failed"] += 1
    
    # Calculate averages and odds
    for target_key, stats in target_stats.items():
        if stats["question_counts"]:
            stats["min_questions"] = min(stats["question_counts"])
            stats["max_questions"] = max(stats["question_counts"])
            stats["avg_questions"] = sum(stats["question_counts"]) / len(stats["question_counts"])
        stats["odds_per_question"] = 1 / stats["total_questions"] if stats["total_questions"] > 0 else 0
        stats["success_rate"] = stats["successful"] / stats["attempts"] if stats["attempts"] > 0 else 0
    
    for attack_key, stats in attacker_target_stats.items():
        stats["avg_questions"] = stats["total_questions"] / stats["attempts"] if stats["attempts"] > 0 else 0
        stats["success_rate"] = stats["successful"] / stats["attempts"] if stats["attempts"] > 0 else 0
    
    return {
        "overall": {
            "total_tests": total_tests,
            "successful": successful_tests,
            "failed": failed_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "total_questions": total_questions,
            "avg_questions": avg_questions,
            "avg_duration": avg_duration
        },
        "by_difficulty": dict(by_difficulty),
        "target_stats": {f"{k[0]}_{k[1]}": v for k, v in target_stats.items()},
        "attacker_target_stats": attacker_target_stats
    }


async def print_test_runs_summary():
    """Print summary table of all test runs"""
    runs = await get_all_test_runs()
    
    if not runs:
        print("⚠️  No test runs found in database.")
        return
    
    print("\n" + "=" * 100)
    print("📋 ALL TEST RUNS SUMMARY")
    print("=" * 100)
    
    headers = [
        ("Run ID", 8),
        ("Status", 12),
        ("Difficulty", 12),
        ("Started", 20),
        ("Completed", 20),
        ("Duration", 15),
        ("Tests", 8),
        ("Success", 8),
        ("Failed", 8),
        ("Success %", 10)
    ]
    print_table_header(headers)
    
    for run in runs:
        difficulties = run.test_config.get("difficulties", []) if run.test_config else []
        difficulty_str = ", ".join(difficulties) if difficulties else "N/A"
        
        started = run.started_at.strftime("%Y-%m-%d %H:%M:%S") if run.started_at else "N/A"
        completed = run.completed_at.strftime("%Y-%m-%d %H:%M:%S") if run.completed_at else "N/A"
        
        if run.started_at and run.completed_at:
            duration = run.completed_at - run.started_at
            duration_str = str(duration).split('.')[0]  # Remove microseconds
        else:
            duration_str = "N/A"
        
        total_tests = run.total_tests or 0
        successful = run.successful_jailbreaks or 0
        failed = run.failed_jailbreaks or 0
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        
        row = [
            (str(run.id), 8),
            (run.status, 12),
            (difficulty_str[:11], 12),
            (started, 20),
            (completed, 20),
            (duration_str[:14], 15),
            (str(total_tests), 8),
            (str(successful), 8),
            (str(failed), 8),
            (f"{success_rate:.1f}%", 10)
        ]
        print(format_table_row(row))


async def print_difficulty_statistics(stats: Dict[str, Any]):
    """Print detailed statistics by difficulty level"""
    by_difficulty = stats.get("by_difficulty", {})
    target_stats = stats.get("target_stats", {})
    
    if not by_difficulty:
        print("\n⚠️  No difficulty statistics available.")
        return
    
    print("\n" + "=" * 100)
    print("📊 DETAILED STATISTICS BY DIFFICULTY")
    print("=" * 100)
    
    difficulty_order = ["expert", "hard", "medium", "easy"]
    
    for difficulty in difficulty_order:
        if difficulty not in by_difficulty:
            continue
        
        diff_stats = by_difficulty[difficulty]
        total_tests = diff_stats["total_tests"]
        successful = diff_stats["successful"]
        failed = diff_stats["failed"]
        total_questions = diff_stats["total_questions"]
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        avg_questions = total_questions / total_tests if total_tests > 0 else 0
        overall_odds = (1 / total_questions * 100) if total_questions > 0 else 0
        
        print(f"\n{'='*100}")
        print(f"🎯 DIFFICULTY: {difficulty.upper()}")
        print(f"{'='*100}")
        print(f"Overall: {total_tests} tests | {successful} successful | {failed} failed | "
              f"Success Rate: {success_rate:.2f}% | Avg Questions: {avg_questions:.2f} | "
              f"Overall Odds: {overall_odds:.6f}%")
        
        # Get target LLMs for this difficulty
        target_keys = [k for k in target_stats.keys() if k.endswith(f"_{difficulty}")]
        if not target_keys:
            print("  ⚠️  No target LLM statistics for this difficulty")
            continue
        
        # Sort targets by total questions (most resistant first)
        target_data = []
        for key in target_keys:
            target_name = key.replace(f"_{difficulty}", "")
            target_data.append((target_name, target_stats[key]))
        
        target_data.sort(key=lambda x: x[1]["total_questions"], reverse=True)
        
        print(f"\n{'Target LLM':<20} {'Total Q':<12} {'Attempts':<10} {'Success':<10} {'Failed':<10} "
              f"{'Success %':<12} {'Avg Q':<10} {'Min Q':<8} {'Max Q':<8} {'Odds %':<12}")
        print("-" * 120)
        
        for target_name, t_stats in target_data:
            odds_pct = t_stats["odds_per_question"] * 100
            success_pct = t_stats["success_rate"] * 100
            print(f"{target_name.upper():<20} "
                  f"{t_stats['total_questions']:<12} "
                  f"{t_stats['attempts']:<10} "
                  f"{t_stats['successful']:<10} "
                  f"{t_stats['failed']:<10} "
                  f"{success_pct:>10.2f}% "
                  f"{t_stats['avg_questions']:>9.2f} "
                  f"{t_stats.get('min_questions', 0):>7} "
                  f"{t_stats.get('max_questions', 0):>7} "
                  f"{odds_pct:>11.6f}%")


async def print_attacker_target_matrix(stats: Dict[str, Any]):
    """Print attacker vs target statistics matrix"""
    attacker_target_stats = stats.get("attacker_target_stats", {})
    
    if not attacker_target_stats:
        print("\n⚠️  No attacker-target statistics available.")
        return
    
    print("\n" + "=" * 100)
    print("⚔️  ATTACKER vs TARGET STATISTICS")
    print("=" * 100)
    
    # Group by difficulty
    by_difficulty: Dict[str, List[Tuple[str, str, Dict]]] = defaultdict(list)
    
    for (attacker, target, difficulty), attack_stats in attacker_target_stats.items():
        by_difficulty[difficulty].append((attacker, target, attack_stats))
    
    difficulty_order = ["expert", "hard", "medium", "easy"]
    
    for difficulty in difficulty_order:
        if difficulty not in by_difficulty:
            continue
        
        print(f"\n{'='*100}")
        print(f"🎯 DIFFICULTY: {difficulty.upper()}")
        print(f"{'='*100}")
        
        attacks = by_difficulty[difficulty]
        if not attacks:
            continue
        
        # Get unique attackers and targets
        attackers = sorted(set(a[0] for a in attacks))
        targets = sorted(set(a[1] for a in attacks))
        
        # Create matrix
        print(f"\n{'Attacker →':<20} ", end="")
        for target in targets:
            print(f"{target.upper():<15}", end="")
        print()
        print("-" * (20 + 15 * len(targets)))
        
        for attacker in attackers:
            print(f"{attacker.upper():<20} ", end="")
            for target in targets:
                key = (attacker, target, difficulty)
                if key in attacker_target_stats:
                    stats = attacker_target_stats[key]
                    success_str = f"{stats['successful']}/{stats['attempts']}"
                    avg_q = f"({stats['avg_questions']:.1f}Q)"
                    print(f"{success_str:>6} {avg_q:<8}", end="")
                else:
                    print(f"{'N/A':<15}", end="")
            print()


async def print_overall_summary(stats: Dict[str, Any]):
    """Print overall summary statistics"""
    overall = stats.get("overall", {})
    
    if not overall:
        return
    
    print("\n" + "=" * 100)
    print("📈 OVERALL SUMMARY STATISTICS")
    print("=" * 100)
    
    print(f"\nTotal Tests: {overall['total_tests']:,}")
    print(f"Successful Jailbreaks: {overall['successful']:,}")
    print(f"Failed Jailbreaks: {overall['failed']:,}")
    print(f"Overall Success Rate: {overall['success_rate']*100:.2f}%")
    print(f"Total Questions Asked: {overall['total_questions']:,}")
    print(f"Average Questions per Test: {overall['avg_questions']:.2f}")
    print(f"Average Duration per Test: {overall['avg_duration']:.2f}s")
    
    if overall['total_questions'] > 0:
        overall_odds = (1 / overall['total_questions']) * 100
        print(f"Overall Odds (1 in {overall['total_questions']:,}): {overall_odds:.8f}%")


async def main():
    """Main entry point"""
    print("=" * 100)
    print("🎯 COMPREHENSIVE AI RESISTANCE TEST STATISTICS REPORT")
    print("=" * 100)
    
    # Get comprehensive statistics
    print("\n📊 Gathering statistics from database...")
    stats = await get_comprehensive_statistics()
    
    if not stats:
        print("\n⚠️  No test results found in database.")
        return
    
    # Print all sections
    await print_test_runs_summary()
    await print_overall_summary(stats)
    await print_difficulty_statistics(stats)
    await print_attacker_target_matrix(stats)
    
    # Optional: Show attacker prompt
    print("\n" + "=" * 100)
    print("📝 ATTACKER PROMPT (Reference)")
    print("=" * 100)
    print("\n" + AIAttackerService.ATTACKER_PROMPT)
    print("\n" + AIAttackerService.GAME_CONTEXT)
    
    print("\n" + "=" * 100)
    print("✅ Report Complete")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
