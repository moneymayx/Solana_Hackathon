#!/usr/bin/env python3
"""
AI Resistance Testing CLI Script
==================================

Main orchestrator for AI vs AI resistance testing.
Tests all available LLMs against all difficulty levels to determine resistance.

Usage:
    python3 scripts/test_ai_resistance.py [--difficulty easy|medium|hard|expert] [--provider anthropic|openai|gemini|deepseek]
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Import services
from src.services.llm_client_manager import LLMClientManager, UnifiedLLMClient
from src.services.ai_attacker_service import AIAttackerService
from src.services.mock_ai_agent import MockAIAgent
from src.services.ai_test_analysis import analyze_results, generate_rankings
from src.database import AsyncSessionLocal, create_tables
from src.models import AITestRun, AITestResult


class AITestOrchestrator:
    """Orchestrates AI resistance testing across multiple LLMs and difficulties"""
    
    def __init__(self):
        self.client_manager = LLMClientManager()
        self.available_clients = self.client_manager.get_available_clients()
        self.available_providers = list(self.available_clients.keys())
        self.provider_variant_index = self._build_provider_variant_index()
        self.difficulties = ["easy", "medium", "hard", "expert"]
        self.max_questions = 100

    def _build_provider_variant_index(self) -> Dict[str, List[str]]:
        """
        Build a map of provider → aliases (including 'default')
        so we can surface variant combinations in CLI output.
        """
        base_providers = {provider.split(':')[0] for provider in self.client_manager.get_available_providers()}
        return {
            provider: self.client_manager.get_available_aliases(provider)
            for provider in base_providers
        }

    def _generate_round_robin_schedule(
        self,
        providers: List[str],
        difficulties: List[str]
    ) -> List[Dict[str, str]]:
        """
        Build a round-robin attack schedule prioritizing Anthropic as the first target
        when available.

        Each provider takes a turn as the target for a given difficulty, and every other
        provider attacks sequentially until a jailbreak is attempted.
        """
        if not providers or not difficulties:
            return []

        # Prioritize Anthropic as the first target, then maintain provider order.
        prioritized_providers: List[str] = []
        if "anthropic" in providers:
            prioritized_providers.append("anthropic")
        prioritized_providers.extend([p for p in providers if p != "anthropic"])

        schedule: List[Dict[str, str]] = []
        for difficulty in difficulties:
            for target_provider in prioritized_providers:
                attackers = [p for p in prioritized_providers if p != target_provider]
                if not attackers:
                    continue
                for attacker in attackers:
                    schedule.append(
                        {
                            "difficulty": difficulty,
                            "target_provider": target_provider,
                            "attacker_provider": attacker,
                        }
                    )
        return schedule
    
    @staticmethod
    def _format_provider_label(provider: str) -> str:
        """Format provider identifiers so aliases read clearly in console output"""
        if ':' in provider:
            base, alias = provider.split(':', 1)
            alias_label = alias or 'default'
            return f"{base.upper()} ({alias_label.lower()})"
        return provider.upper()

    def _format_alias_summary(self) -> Optional[str]:
        """Summarize providers that ship with multiple live variants"""
        segments: List[str] = []
        for provider in sorted(self.provider_variant_index.keys()):
            aliases = self.provider_variant_index[provider]
            non_default = [alias for alias in aliases if alias != 'default']
            if non_default:
                descriptor = f"{provider.upper()} → default"
                if non_default:
                    descriptor = f"{descriptor}, " + ", ".join(non_default)
                segments.append(descriptor)
        if not segments:
            return None
        return "; ".join(segments)
    
    async def run_full_test_suite(
        self,
        difficulty_filter: Optional[str] = None,
        provider_filter: Optional[str] = None
    ) -> Dict:
        """
        Run complete test suite
        
        Args:
            difficulty_filter: Optional difficulty to test (otherwise tests all)
            provider_filter: Optional provider to test (otherwise tests all available)
        
        Returns:
            Summary of test results
        """
        print("🎯 Starting AI Resistance Testing Suite")
        print("=" * 60)
        display_providers = [self._format_provider_label(p) for p in self.available_providers]
        print(f"Available Providers: {', '.join(display_providers)}")

        alias_summary = self._format_alias_summary()
        if alias_summary:
            print(f"Variant Map: {alias_summary}")
        
        if not self.available_providers:
            print("❌ No LLM providers available. Check your API keys.")
            return None
        
        # Filter providers and difficulties
        providers_to_test = [provider_filter] if provider_filter else list(self.available_providers)
        difficulties_to_test = [difficulty_filter] if difficulty_filter else list(self.difficulties)

        schedule = self._generate_round_robin_schedule(providers_to_test, difficulties_to_test)

        if not schedule:
            print("⚠️  Not enough providers to run round-robin attacks. At least two providers are required.")
            return None
        
        # Create test run record
        test_run = await self._create_test_run(
            providers_to_test,
            difficulties_to_test,
            total_tests=len(schedule)
        )
        
        total_tests = len(schedule)
        successful_jailbreaks = 0
        failed_jailbreaks = 0
        
        print(f"\n📊 Running {total_tests} tests...\n")
        
        # Run tests following round-robin schedule
        for entry in schedule:
            attacker = entry["attacker_provider"]
            target = entry["target_provider"]
            difficulty = entry["difficulty"]

            print(
                f"Testing {self._format_provider_label(attacker)} attacking {self._format_provider_label(target)} "
                f"({difficulty.upper()} difficulty)..."
            )
            
            result = await self._run_single_test(
                test_run_id=test_run.id,
                attacker_provider=attacker,
                target_provider=target,
                target_difficulty=difficulty
            )
            
            if result:
                if result.was_successful:
                    successful_jailbreaks += 1
                else:
                    failed_jailbreaks += 1
                print(
                    f"  {'✅' if result.was_successful else '❌'} "
                    f"Questions: {result.question_count}, "
                    f"Duration: {result.duration_seconds:.1f}s"
                )
            else:
                print("  ⚠️  Test failed to complete")
        
        # Update test run summary
        await self._complete_test_run(
            test_run_id=test_run.id,
            successful=successful_jailbreaks,
            failed=failed_jailbreaks
        )
        
        # Generate analysis
        print("\n📈 Generating Analysis...")
        summary = await generate_rankings(test_run.id)
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    async def _create_test_run(
        self,
        providers: List[str],
        difficulties: List[str],
        total_tests: int
    ) -> AITestRun:
        """Create a test run record in the database"""
        async with AsyncSessionLocal() as session:
            test_run = AITestRun(
                started_at=datetime.utcnow(),
                status="running",
                total_tests=total_tests,
                test_config={
                    "providers": providers,
                    "difficulties": difficulties,
                    "max_questions": self.max_questions
                }
            )
            session.add(test_run)
            await session.commit()
            await session.refresh(test_run)
            return test_run
    
    async def _complete_test_run(
        self,
        test_run_id: int,
        successful: int,
        failed: int
    ):
        """Mark test run as complete"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import update
            from src.models import AITestRun
            
            await session.execute(
                update(AITestRun)
                .where(AITestRun.id == test_run_id)
                .values(
                    completed_at=datetime.utcnow(),
                    status="completed",
                    successful_jailbreaks=successful,
                    failed_jailbreaks=failed
                )
            )
            await session.commit()
    
    async def _run_single_test(
        self,
        test_run_id: int,
        attacker_provider: str,
        target_provider: str,
        target_difficulty: str
    ) -> Optional[AITestResult]:
        """
        Run a single attack test
        
        Args:
            test_run_id: ID of the parent test run
            attacker_provider: Provider name for attacking LLM
            target_provider: Provider name whose personality is being attacked
            target_difficulty: Difficulty of target to attack
        
        Returns:
            AITestResult record or None if failed
        """
        try:
            # Get attacker client
            attacker_client = self.client_manager.get_client(attacker_provider)
            if not attacker_client:
                print(f"  ⚠️  {attacker_provider} not available")
                return None
            
            # Create attacker service
            attacker_service = AIAttackerService(attacker_client)
            
            # Get target LLM client based on designated provider
            target_client = self.client_manager.get_client(target_provider)
            if not target_client:
                print(f"  ⚠️  Target client not available")
                return None
            
            # Create mock target agent
            target_agent = MockAIAgent(difficulty=target_difficulty)
            target_agent.set_client(target_client)
            
            # Run attack
            attack_result = await attacker_service.attack(
                target_agent=target_agent,
                target_difficulty=target_difficulty,
                max_questions=self.max_questions
            )
            
            # Store result
            result = await self._store_test_result(
                test_run_id=test_run_id,
                attacker_provider=attacker_provider,
                target_provider=target_provider,
                target_difficulty=target_difficulty,
                attack_result=attack_result,
                attacker_prompt=attacker_service.ATTACKER_PROMPT
            )
            
            return result
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _store_test_result(
        self,
        test_run_id: int,
        attacker_provider: str,
        target_provider: str,
        target_difficulty: str,
        attack_result: Dict,
        attacker_prompt: str
    ) -> AITestResult:
        """Store test result in database"""
        async with AsyncSessionLocal() as session:
            result = AITestResult(
                test_run_id=test_run_id,
                attacker_llm=attacker_provider,
                target_llm=target_provider,
                target_difficulty=target_difficulty,
                question_count=attack_result.get("question_count", 0),
                was_successful=attack_result.get("was_successful", False),
                duration_seconds=attack_result.get("duration_seconds", 0.0),
                conversation_json={"messages": attack_result.get("conversation", [])},
                attacker_system_prompt=attacker_prompt,
                target_response_preview=attack_result.get("final_response", "")[:500]
            )
            session.add(result)
            await session.commit()
            await session.refresh(result)
            return result
    
    def _print_summary(self, summary: Dict):
        """Print test summary to console"""
        print("\n" + "=" * 60)
        print("🎯 AI RESISTANCE TESTING RESULTS")
        print("=" * 60)
        
        print(f"\nTotal Tests: {summary.get('total_tests', 0)}")
        print(f"Successful Jailbreaks: {summary.get('successful', 0)}")
        print(f"Failed Jailbreaks: {summary.get('failed', 0)}")
        
        if summary.get('rankings'):
            print("\n📊 Rankings by Resistance (Avg Questions to Jailbreak):")
            for i, ranking in enumerate(summary['rankings'], 1):
                provider = ranking['provider']
                difficulty = ranking['difficulty']
                avg_questions = ranking.get('avg_questions', 'N/A')
                print(f"  {i}. {provider.upper()} ({difficulty}) - {avg_questions} questions")
        
        if summary.get('recommendations'):
            print("\n💡 Recommended Difficulty Assignments:")
            for rec in summary['recommendations']:
                print(f"  - {rec['difficulty']}: {rec['provider'].upper()}")
        
        print("\n✅ Testing complete!")


async def main():
    """Main entry point"""
    # Initialize manager to get available providers dynamically
    manager = LLMClientManager()
    available_providers = manager.get_available_providers()
    
    # Add all known providers from config for validation
    all_known_providers = list(UnifiedLLMClient.PROVIDER_CONFIGS.keys())
    choices_providers = list(set(available_providers + all_known_providers))
    
    parser = argparse.ArgumentParser(description="AI Resistance Testing CLI")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "expert"],
        help="Test only specific difficulty level"
    )
    parser.add_argument(
        "--provider",
        choices=choices_providers if choices_providers else None,
        help=(
            "Test only specific provider "
            f"(available: {', '.join(available_providers) if available_providers else 'none'}; "
            "supports alias notation like groq:v1)"
        )
    )
    
    args = parser.parse_args()
    
    # Create tables if they don't exist
    await create_tables()
    
    # Run tests
    orchestrator = AITestOrchestrator()
    await orchestrator.run_full_test_suite(
        difficulty_filter=args.difficulty,
        provider_filter=args.provider
    )


if __name__ == "__main__":
    asyncio.run(main())

