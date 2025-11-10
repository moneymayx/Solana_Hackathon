"""
AI Test Analysis Service
=========================

Analyzes AI resistance testing results to calculate metrics, rankings, and recommendations.
"""

from typing import Dict, List, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import AsyncSessionLocal
from ..models import AITestResult, AITestRun


async def analyze_results(test_run_id: int) -> Dict[str, Any]:
    """
    Analyze results from a specific test run
    
    Args:
        test_run_id: ID of the test run to analyze
    
    Returns:
        Dictionary with analysis metrics
    """
    async with AsyncSessionLocal() as session:
        # Get all results for this test run
        result = await session.execute(
            select(AITestResult)
            .where(AITestResult.test_run_id == test_run_id)
        )
        results = result.scalars().all()
        
        # Calculate aggregate statistics
        total_tests = len(results)
        successful_count = sum(1 for r in results if r.was_successful)
        failed_count = total_tests - successful_count
        
        avg_questions = sum(r.question_count for r in results) / total_tests if total_tests > 0 else 0
        avg_duration = sum(r.duration_seconds for r in results) / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "successful": successful_count,
            "failed": failed_count,
            "success_rate": successful_count / total_tests if total_tests > 0 else 0,
            "avg_questions": avg_questions,
            "avg_duration": avg_duration
        }


async def generate_rankings(test_run_id: int) -> Dict[str, Any]:
    """
    Generate rankings and recommendations based on test results
    
    Args:
        test_run_id: ID of the test run to analyze
    
    Returns:
        Dictionary with rankings and recommendations
    """
    async with AsyncSessionLocal() as session:
        # Get all results for this test run
        result = await session.execute(
            select(AITestResult)
            .where(AITestResult.test_run_id == test_run_id)
        )
        results = result.scalars().all()
        
        # Group by provider and difficulty
        by_provider_difficulty = {}
        for r in results:
            key = f"{r.attacker_llm}_{r.target_difficulty}"
            if key not in by_provider_difficulty:
                by_provider_difficulty[key] = {
                    "provider": r.attacker_llm,
                    "difficulty": r.target_difficulty,
                    "results": []
                }
            by_provider_difficulty[key]["results"].append(r)
        
        # Calculate averages per provider/difficulty combination
        rankings = []
        for key, data in by_provider_difficulty.items():
            provider = data["provider"]
            difficulty = data["difficulty"]
            results_list = data["results"]
            
            # Calculate metrics
            avg_questions = sum(r.question_count for r in results_list) / len(results_list)
            successful_count = sum(1 for r in results_list if r.was_successful)
            success_rate = successful_count / len(results_list)
            
            rankings.append({
                "provider": provider,
                "difficulty": difficulty,
                "avg_questions": avg_questions,
                "success_rate": success_rate,
                "test_count": len(results_list)
            })
        
        # Sort by avg_questions (descending - higher = more resistant)
        rankings.sort(key=lambda x: x["avg_questions"], reverse=True)
        
        # Generate recommendations
        recommendations = _generate_recommendations(rankings)
        
        # Get overall stats
        total_tests = len(results)
        successful = sum(1 for r in results if r.was_successful)
        failed = total_tests - successful
        
        return {
            "total_tests": total_tests,
            "successful": successful,
            "failed": failed,
            "rankings": rankings,
            "recommendations": recommendations
        }


def _generate_recommendations(rankings: List[Dict]) -> List[Dict]:
    """
    Generate difficulty assignment recommendations based on resistance levels
    
    Args:
        rankings: List of rankings sorted by resistance
    
    Returns:
        List of recommended assignments
    """
    recommendations = []
    
    # Sort by difficulty buckets
    easy_candidates = [r for r in rankings if r["difficulty"] == "easy"]
    medium_candidates = [r for r in rankings if r["difficulty"] == "medium"]
    hard_candidates = [r for r in rankings if r["difficulty"] == "hard"]
    expert_candidates = [r for r in rankings if r["difficulty"] == "expert"]
    
    # For each difficulty level, pick the provider with highest resistance
    difficulty_levels = [
        ("easy", easy_candidates),
        ("medium", medium_candidates),
        ("hard", hard_candidates),
        ("expert", expert_candidates)
    ]
    
    for difficulty_name, candidates in difficulty_levels:
        if candidates:
            # Pick the most resistant (highest avg_questions)
            best = max(candidates, key=lambda x: x["avg_questions"])
            recommendations.append({
                "difficulty": difficulty_name,
                "provider": best["provider"],
                "avg_questions": best["avg_questions"],
                "reasoning": f"Highest resistance in {difficulty_name} tests"
            })
        else:
            # No data for this difficulty, recommend fallback
            recommendations.append({
                "difficulty": difficulty_name,
                "provider": None,
                "avg_questions": 0,
                "reasoning": "No test data available"
            })
    
    return recommendations


async def calculate_expected_value(bounty_amount: float, entry_cost: float) -> Dict[str, float]:
    """
    Calculate expected value for bounty pricing based on historical jailbreak rates
    
    Args:
        bounty_amount: Prize pool amount
        entry_cost: Cost per entry
    
    Returns:
        Dictionary with expected value calculations
    """
    async with AsyncSessionLocal() as session:
        # Get all successful jailbreaks
        result = await session.execute(
            select(AITestResult)
            .where(AITestResult.was_successful == True)
        )
        successful_results = result.scalars().all()
        
        # Get all test results
        result_all = await session.execute(select(AITestResult))
        all_results = result_all.scalars().all()
        
        if not all_results:
            return {
                "jailbreak_rate": 0.0,
                "expected_payout": 0.0,
                "expected_profit": 0.0,
                "house_edge": 0.0
            }
        
        jailbreak_rate = len(successful_results) / len(all_results)
        expected_payout = bounty_amount * jailbreak_rate
        expected_profit = entry_cost - expected_payout
        house_edge = (expected_profit / entry_cost) * 100 if entry_cost > 0 else 0
        
        return {
            "jailbreak_rate": jailbreak_rate,
            "expected_payout": expected_payout,
            "expected_profit": expected_profit,
            "house_edge": house_edge
        }




