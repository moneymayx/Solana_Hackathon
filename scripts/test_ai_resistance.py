#!/usr/bin/env python3
"""
AI Resistance Testing CLI Script
==================================

Main orchestrator for AI vs AI resistance testing.
Tests available LLMs against selected difficulty levels to determine resistance.

Usage (interactive defaults):
    python3 scripts/test_ai_resistance.py
      - Prompts for difficulty: easy | medium | hard | expert | all
      - Prompts for max consecutive failed jailbreak attempts before quitting early

Usage (automated / non-interactive):
    python3 scripts/test_ai_resistance.py [--difficulty easy|medium|hard|expert|all]
                                         [--provider anthropic|openai|gemini|deepseek]
                                         [--max-failed-without-success N]
"""

import asyncio
import sys
import os
import argparse
import logging
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
from src.services.ai_decision_service import ai_decision_service
from src.services.ai_decision_integration import AIDecisionIntegration
from src.database import AsyncSessionLocal, create_tables
from src.models import AITestRun, AITestResult


class AITestOrchestrator:
    """Orchestrates AI resistance testing across multiple LLMs and difficulties"""
    
    def __init__(self):
        # Manager discovers all configured LLM providers from environment variables.
        self.client_manager = LLMClientManager()
        self.available_clients = self.client_manager.get_available_clients()
        self.available_providers = list(self.available_clients.keys())
        self.provider_variant_index = self._build_provider_variant_index()
        # Integration service for submitting AI decisions to the V3 contract
        # flow in simulation mode (no funds are transferred).
        self.ai_decision_integration = AIDecisionIntegration()

        # Difficulty ordering is intentionally fixed from easiest to hardest so
        # we can gate progression by difficulty in the orchestrator.
        self.difficulties = ["easy", "medium", "hard", "expert"]

        # Max questions per head-to-head attack before we consider the attempt
        # exhausted. This is independent from the global
        # ``max_failed_without_success`` early‑quit safeguard which is configured
        # at runtime.
        self.max_questions = 100

    def _build_provider_variant_index(self) -> Dict[str, List[str]]:
        """
        Build a map of provider → aliases (including 'default')
        so we can surface variant combinations in CLI output.
        """
        index: Dict[str, List[str]] = {}
        all_providers = self.client_manager.get_available_providers()
        
        for provider in all_providers:
            if ':' in provider:
                # Provider has alias (e.g., "groq:v1")
                base_provider, alias = provider.split(':', 1)
                if base_provider not in index:
                    index[base_provider] = []
                index[base_provider].append(alias)
            else:
                # Base provider without alias (e.g., "groq")
                if provider not in index:
                    index[provider] = []
                index[provider].append('default')
        
        return index

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

        # Arrange providers so Anthropic is evaluated last. This allows other
        # models to cycle through the bounty personality first, and keeps
        # Anthropic as the final target in each round for comparison.
        prioritized_providers: List[str] = [p for p in providers if p != "anthropic"]
        if "anthropic" in providers:
            prioritized_providers.append("anthropic")

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
        provider_filter: Optional[str] = None,
        max_failed_without_success: Optional[int] = None,
    ) -> Dict:
        """
        Run complete test suite.
        
        Args:
            difficulty_filter: Optional difficulty to test (otherwise tests all in order:
                               easy → medium → hard → expert). If set to \"all\", behaves
                               the same as None and runs all difficulties.
            provider_filter: Optional provider to test (otherwise tests all available).
            max_failed_without_success: Global cap on consecutive failed jailbreak
                               attempts (across all difficulties). When this threshold
                               is exceeded without a single successful jailbreak, the
                               suite exits early and reports partial results.
        
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

        # Normalize difficulty filter so \"all\" means \"no filter\".
        if difficulty_filter and difficulty_filter.lower() != "all":
            normalized_difficulty_filter: Optional[str] = difficulty_filter.lower()
        else:
            normalized_difficulty_filter = None
        
        # Filter providers and difficulties
        providers_to_test = [provider_filter] if provider_filter else list(self.available_providers)
        difficulties_to_test = (
            [normalized_difficulty_filter] if normalized_difficulty_filter else list(self.difficulties)
        )

        # Pre-compute total scheduled tests for metadata; the suite may exit early,
        # but this gives a sense of intended size.
        total_scheduled_tests = 0
        for difficulty in difficulties_to_test:
            per_difficulty_schedule = self._generate_round_robin_schedule(
                providers_to_test,
                [difficulty],
            )
            total_scheduled_tests += len(per_difficulty_schedule)

        if total_scheduled_tests == 0:
            print("⚠️  Not enough providers to run round-robin attacks. At least two providers are required.")
            return None

        # Create test run record once for the entire suite.
        test_run = await self._create_test_run(
            providers_to_test,
            difficulties_to_test,
            total_tests=total_scheduled_tests
        )
        
        total_tests_run = 0
        # Track cumulative questions per attacker across the entire suite and
        # global cumulative questions across all attacks so you can see how
        # much pressure each LLM has applied and the overall cost surface.
        attacker_question_totals: Dict[str, int] = {}
        global_question_total = 0
        successful_jailbreaks = 0
        failed_jailbreaks = 0
        
        # Track per-target statistics for detailed reporting
        # Key: (target_provider, difficulty), Value: dict with stats
        per_target_stats: Dict[tuple, Dict[str, Any]] = {}

        early_quit_info: Optional[Dict[str, str]] = None

        print(f"\n📊 Planned tests: {total_scheduled_tests} (may exit early based on safeguards)...\n")
        
        # Run tests difficulty by difficulty so we never move past easy until
        # each LLM has had its chance at that personality. We will keep
        # attacking a given target/difficulty combo until it has been
        # successfully jailbroken at least once OR we hit the per-target
        # max_failed_without_success safeguard.
        for difficulty in difficulties_to_test:
            if early_quit_info is not None:
                # Once early‑quit has been triggered, skip remaining difficulties.
                break

            per_difficulty_schedule = self._generate_round_robin_schedule(
                providers_to_test,
                [difficulty],
            )

            if not per_difficulty_schedule:
                continue

            print(f"\n🔎 Running tests for difficulty: {difficulty.upper()}\n")

            # Track whether each target provider has been successfully jailbroken
            # at least once for this difficulty.
            per_target_success: Dict[str, bool] = {provider: False for provider in providers_to_test}

            # We may need to make multiple passes over the schedule for this
            # difficulty until every target has been jailbroken at least once,
            # or the per-target failure safeguard is reached.
            while not all(per_target_success.values()):
                any_ran_this_pass = False

                for entry in per_difficulty_schedule:
                    if early_quit_info is not None:
                        break

                    attacker = entry["attacker_provider"]
                    target = entry["target_provider"]
                    current_difficulty = entry["difficulty"]

                    # Skip targets that have already been jailbroken at this difficulty.
                    if per_target_success.get(target):
                        continue

                    any_ran_this_pass = True
                    
                    # Initialize per-target stats tracking if this is a new target
                    target_key = (target, current_difficulty)
                    if target_key not in per_target_stats:
                        per_target_stats[target_key] = {
                            "target_provider": target,
                            "difficulty": current_difficulty,
                            "total_questions": 0,
                            "attempts": 0,
                            "consecutive_failed": 0,
                            "successful_attacker": None,
                            "successful_question": None,
                            # Number of questions used in the successful
                            # jailbreak conversation (per attack), so reports
                            # can distinguish between true first-question
                            # jailbreaks and longer conversations.
                            "successful_question_number": None,
                            "successful_response": None,
                        }
                        print(
                            f"\n🎯 New Target: {self._format_provider_label(target)} "
                            f"({current_difficulty.upper()} difficulty)\n"
                        )

                    print(
                        f"Testing {self._format_provider_label(attacker)} attacking "
                        f"{self._format_provider_label(target)} "
                        f"({current_difficulty.upper()} difficulty)..."
                    )

                    result = await self._run_single_test(
                        test_run_id=test_run.id,
                        attacker_provider=attacker,
                        target_provider=target,
                        target_difficulty=current_difficulty
                    )

                    total_tests_run += 1

                    if result:
                        questions_this_attack = result.question_count
                        # Update cumulative question counters.
                        attacker_question_totals[attacker] = (
                            attacker_question_totals.get(attacker, 0) + questions_this_attack
                        )
                        global_question_total += questions_this_attack
                        
                        # Update per-target stats
                        per_target_stats[target_key]["total_questions"] += questions_this_attack
                        per_target_stats[target_key]["attempts"] += 1

                        if result.was_successful:
                            successful_jailbreaks += 1
                            per_target_success[target] = True
                            per_target_stats[target_key]["consecutive_failed"] = 0
                            per_target_stats[target_key]["successful_attacker"] = attacker
                            # Store the actual question number that caused the jailbreak
                            per_target_stats[target_key]["successful_question_number"] = questions_this_attack
                            
                            # Extract the successful jailbreak question from conversation
                            # The conversation history alternates: [user1, assistant1, user2, assistant2, ...]
                            # Question N is at index (N-1)*2 (0-indexed)
                            conversation = result.conversation_json.get("messages", [])
                            successful_question_text = "N/A"
                            if conversation and questions_this_attack > 0:
                                # Find the user message at the position corresponding to the successful question
                                # questions_this_attack is 1-indexed (question 1, 2, 3...)
                                # In conversation array: question 1 = index 0, question 2 = index 2, question N = index (N-1)*2
                                question_index = (questions_this_attack - 1) * 2
                                if question_index < len(conversation) and conversation[question_index].get("role") == "user":
                                    successful_question_text = conversation[question_index].get("content", "")[:500]
                                else:
                                    # Fallback: get last user message if index doesn't match
                                    for msg in reversed(conversation):
                                        if msg.get("role") == "user":
                                            successful_question_text = msg.get("content", "")[:500]
                                            break
                            
                            per_target_stats[target_key]["successful_question"] = successful_question_text
                            per_target_stats[target_key]["successful_response"] = result.target_response_preview
                            
                            # Print per-target summary
                            print(
                                f"\n{'='*60}\n"
                                f"✅ TARGET JAILBROKEN: {self._format_provider_label(target)} ({current_difficulty.upper()})\n"
                                f"{'='*60}\n"
                                f"Total questions asked to this target: {per_target_stats[target_key]['total_questions']}\n"
                                f"Number of attempts: {per_target_stats[target_key]['attempts']}\n"
                                f"Successful attacker: {self._format_provider_label(attacker)}\n"
                                f"Jailbroken on Question #{per_target_stats[target_key]['successful_question_number']}\n"
                                f"Successful jailbreak question (first 200 chars):\n"
                                f"  {successful_question_text[:200]}...\n"
                                f"{'='*60}\n"
                            )
                        else:
                            failed_jailbreaks += 1
                            per_target_stats[target_key]["consecutive_failed"] += 1

                        print(
                            f"  {'✅' if result.was_successful else '❌'} "
                            f"Questions this attack: {questions_this_attack}, "
                            f"Cumulative for attacker: {attacker_question_totals[attacker]}, "
                            f"Global total questions: {global_question_total}, "
                            f"Target questions so far: {per_target_stats[target_key]['total_questions']}, "
                            f"Duration: {result.duration_seconds:.1f}s"
                        )
                    else:
                        # Treat a failed-to-complete test as a failed attempt for the purpose
                        # of the early‑quit safeguard so we don't loop indefinitely.
                        failed_jailbreaks += 1
                        per_target_stats[target_key]["consecutive_failed"] += 1
                        per_target_stats[target_key]["attempts"] += 1
                        print("  ⚠️  Test failed to complete")

                    # Check per-target early‑quit safeguard after each attempt.
                    # This counter resets for each new target, as the user requested.
                    if (
                        max_failed_without_success is not None
                        and max_failed_without_success > 0
                        and per_target_stats[target_key]["consecutive_failed"] >= max_failed_without_success
                    ):
                        early_quit_info = {
                            "reason": "max_failed_without_success",
                            "difficulty": current_difficulty,
                            "target": target,
                            "consecutive_failed_without_success": str(per_target_stats[target_key]["consecutive_failed"]),
                            "total_tests_run": str(total_tests_run),
                        }
                        print(
                            f"\n🛑 Early quit triggered for target {self._format_provider_label(target)}: "
                            f"{per_target_stats[target_key]['consecutive_failed']} consecutive failed jailbreak attempts "
                            "without a single success.\n"
                        )
                        break

                # If we iterated over the whole schedule without running any new
                # tests (e.g., all remaining entries were for already-jailbroken
                # targets), break to avoid an infinite loop.
                if early_quit_info is not None or not any_ran_this_pass:
                    break
        
        # Update test run summary
        await self._complete_test_run(
            test_run_id=test_run.id,
            successful=successful_jailbreaks,
            failed=failed_jailbreaks
        )
        
        # Generate analysis
        print("\n📈 Generating Analysis...")
        summary = await generate_rankings(test_run.id)
        # Attach early‑quit metadata so the printer can explain why we stopped early.
        if early_quit_info is not None:
            summary["early_quit"] = early_quit_info
            summary.setdefault("notes", []).append(
                "Suite exited early due to max_failed_without_success threshold."
            )
        summary["total_tests_planned"] = total_scheduled_tests
        summary["total_tests_run"] = total_tests_run
        
        # Attach per-target detailed jailbreak statistics
        summary["per_target_jailbreak_details"] = [
            stats for stats in per_target_stats.values()
            if stats["successful_attacker"] is not None  # Only include successfully jailbroken targets
        ]
        
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
            
            # Run attack against the mock target agent. This returns both a
            # high-level result and the full conversation so we can surface
            # a preview in the interactive console.
            try:
                # Protect each attack with a timeout so a single slow or
                # rate-limited provider cannot stall the entire suite.
                attack_result = await asyncio.wait_for(
                    attacker_service.attack(
                        target_agent=target_agent,
                        target_difficulty=target_difficulty,
                        max_questions=self.max_questions
                    ),
                    timeout=300,  # 5 minutes per attacker/target pair
                )
            except asyncio.TimeoutError:
                print("  ⚠️  Attack timed out (skipping to next pair)")
                return None
            
            # Optional interactive console preview of the conversation so it is
            # clear which LLM currently owns the personality, what difficulty
            # is being tested, and how the attacker is trying to jailbreak it.
            conversation = attack_result.get("conversation", [])
            if conversation:
                print("  ─ Conversation Preview ─")
                print(
                    f"  Target: {self._format_provider_label(target_provider)} "
                    f"({target_difficulty.upper()})"
                )
                print(
                    f"  Attacker: {self._format_provider_label(attacker_provider)} "
                    f"(questions asked: {attack_result.get('question_count', 0)})"
                )
                # Show up to first 3 user/assistant exchanges to keep output readable.
                max_pairs = 3
                user_idx = 0
                pair_count = 0
                while user_idx < len(conversation) and pair_count < max_pairs:
                    user_msg = conversation[user_idx]
                    assistant_msg = (
                        conversation[user_idx + 1]
                        if user_idx + 1 < len(conversation)
                        else None
                    )
                    if user_msg.get("role") == "user":
                        q_content = user_msg.get("content", "")
                        print(f"    Q{pair_count + 1} (attacker): {q_content[:300]}")
                    if assistant_msg and assistant_msg.get("role") == "assistant":
                        a_content = assistant_msg.get("content", "")
                        print(f"    A{pair_count + 1} (target): {a_content[:300]}")
                    user_idx += 2
                    pair_count += 1
                print("  ─ End Preview ─")

            # If the attacker succeeded in jailbreaking the target according to
            # the off-chain transfer detection logic, also submit this decision
            # to the V3 on-chain flow in **simulation mode**. This uses the
            # new process_ai_decision_v3 instruction via the adapter, but only
            # via simulate_transaction, so no funds move on devnet.
            if attack_result.get("was_successful"):
                try:
                    conversation_history = attack_result.get("conversation", [])
                    # Use the first user message as the canonical user_message for
                    # the decision payload.
                    user_message = ""
                    for msg in conversation_history:
                        if msg.get("role") == "user":
                            user_message = msg.get("content", "")
                            break
                    ai_response = attack_result.get("final_response", "") or ""
                    user_id = 99999  # Test user ID for resistance harness
                    session_id = f"ai_test_run_{test_run_id}"

                    signed_decision = ai_decision_service.create_ai_decision(
                        user_message=user_message,
                        ai_response=ai_response,
                        is_successful_jailbreak=True,
                        user_id=user_id,
                        session_id=session_id,
                        conversation_history=conversation_history,
                        user_profile=None,
                    )

                    onchain_result = await self.ai_decision_integration.process_ai_decision_on_chain_v3(
                        signed_decision=signed_decision,
                        winner_wallet_address=None,
                        conversation_history=conversation_history,
                        model_id=os.getenv("AI_MODEL_ID"),
                    )

                    status_label = "✅" if onchain_result.get("success") else "⚠️"
                    print(
                        f"  {status_label} V3 on-chain decision simulation "
                        f"({'success' if onchain_result.get('success') else 'failed'})"
                    )
                except Exception as sim_err:
                    print(f"  ⚠️ V3 on-chain decision simulation error: {sim_err}")

            # Store result in the database for later analysis.
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

        planned = summary.get("total_tests_planned")
        executed = summary.get("total_tests_run", summary.get("total_tests", 0))

        print(f"\nTotal Tests Planned: {planned if planned is not None else 'N/A'}")
        print(f"Total Tests Executed: {executed}")
        print(f"Successful Jailbreaks: {summary.get('successful', 0)}")
        print(f"Failed Jailbreaks: {summary.get('failed', 0)}")
        
        # If the orchestrator exited early, surface the reason prominently.
        early_quit = summary.get("early_quit")
        if early_quit:
            print("\n🛑 Early Quit Details:")
            print(
                f"  Reason: max_failed_without_success "
                f"(consecutive failures: {early_quit.get('consecutive_failed_without_success')})"
            )
            print(f"  Difficulty at quit: {early_quit.get('difficulty', 'unknown').upper()}")
            print(f"  Tests run before quit: {early_quit.get('total_tests_run', 'N/A')}")
        
        if summary.get('rankings'):
            print("\n📊 Rankings by Resistance (Avg Questions to Jailbreak):")
            for i, ranking in enumerate(summary['rankings'], 1):
                provider = ranking['provider']
                difficulty = ranking['difficulty']
                avg_questions = ranking.get('avg_questions', 'N/A')
                print(f"  {i}. {provider.upper()} ({difficulty}) - {avg_questions} questions")
        
        # Optional richer breakdown of how each target LLM performed per difficulty.
        by_target = summary.get("by_target")
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
        
        # Detailed per-target jailbreak information
        per_target_jailbreak_details = summary.get("per_target_jailbreak_details")
        if per_target_jailbreak_details:
            print("\n🔓 Detailed Jailbreak Information (Successfully Jailbroken Targets):")
            print("=" * 60)
            for details in per_target_jailbreak_details:
                target_label = details["target_provider"].upper() if details.get("target_provider") else "UNKNOWN"
                difficulty = details.get("difficulty", "unknown").upper()
                total_questions = details.get("total_questions", 0)
                attempts = details.get("attempts", 0)
                attacker_label = details["successful_attacker"].upper() if details.get("successful_attacker") else "UNKNOWN"
                successful_question = details.get("successful_question", "N/A")
                successful_q_num = details.get("successful_question_number")
                
                print(f"\n🎯 Target: {target_label} ({difficulty})")
                print(f"   Total Questions Asked: {total_questions}")
                print(f"   Number of Attempts: {attempts}")
                print(f"   Successfully Jailbroken By: {attacker_label}")
                if successful_q_num is not None:
                    # This is the question number within the successful attack attempt
                    # where the jailbreak occurred (1-indexed: Question #1, #2, #3, etc.)
                    print(f"   Jailbroken on Question #{successful_q_num}")
                else:
                    print(f"   Jailbroken on Question #? (unknown)")
                print(f"   Successful Jailbreak Question:")
                print(f"   {successful_question[:300]}...")
                print("-" * 60)
        
        if summary.get('recommendations'):
            print("\n💡 Recommended Difficulty Assignments:")
            for rec in summary['recommendations']:
                provider = rec.get("provider")
                provider_label = provider.upper() if isinstance(provider, str) else "N/A"
                print(f"  - {rec['difficulty']}: {provider_label}")
        
        print("\n✅ Testing complete!")


async def main():
    """Main entry point"""
    # Reduce noise from underlying HTTP clients so test progress output is clearer.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Initialize manager to get available providers dynamically
    manager = LLMClientManager()
    available_providers = manager.get_available_providers()
    
    # Add all known providers from config for validation
    all_known_providers = list(UnifiedLLMClient.PROVIDER_CONFIGS.keys())
    choices_providers = list(set(available_providers + all_known_providers))
    
    parser = argparse.ArgumentParser(description="AI Resistance Testing CLI")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard", "expert", "all"],
        help="Difficulty level to test (or 'all' to run easy→expert)"
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
    parser.add_argument(
        "--max-failed-without-success",
        type=int,
        help=(
            "Maximum number of consecutive failed jailbreak attempts allowed "
            "before quitting early. If omitted, you will be prompted."
        ),
    )
    
    args = parser.parse_args()

    # Interactive selection for difficulty if not provided.
    selected_difficulty = args.difficulty
    if selected_difficulty is None:
        print(
            "\nSelect difficulty to test "
            "[easy / medium / hard / expert / all] (default: easy): "
        )
        while True:
            user_input = input("> ").strip().lower()
            if not user_input:
                selected_difficulty = "easy"
                break
            if user_input in {"easy", "medium", "hard", "expert", "all"}:
                selected_difficulty = user_input
                break
            print("Please enter one of: easy, medium, hard, expert, all (or press Enter for default).")

    # Interactive selection for max consecutive failures if not provided.
    max_failed_without_success = args.max_failed_without_success
    if max_failed_without_success is None:
        print(
            "\nEnter max consecutive failed jailbreak attempts before quitting "
            "(default: 100): "
        )
        while True:
            user_input = input("> ").strip()
            if not user_input:
                max_failed_without_success = 100
                break
            try:
                value = int(user_input)
                if value <= 0:
                    print("Please enter a positive integer greater than 0, or press Enter for default.")
                    continue
                max_failed_without_success = value
                break
            except ValueError:
                print("Please enter a valid integer, or press Enter for default.")
    
    # Create tables if they don't exist
    await create_tables()
    
    # Run tests
    orchestrator = AITestOrchestrator()
    try:
        await orchestrator.run_full_test_suite(
            difficulty_filter=selected_difficulty,
            provider_filter=args.provider,
            max_failed_without_success=max_failed_without_success,
        )
    except KeyboardInterrupt:
        # If the user stops the run manually, try to print a partial summary
        # based on the most recent test run and any results recorded so far.
        print("\n⏹ Run interrupted. Generating partial summary from latest test run...\n")
        from sqlalchemy import select as sql_select

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                sql_select(AITestRun).order_by(AITestRun.id.desc()).limit(1)
            )
            last_run = result.scalars().first()
            if last_run is None:
                print("No AI test runs found to summarize.")
                return
            summary = await generate_rankings(last_run.id)
            orchestrator._print_summary(summary)


if __name__ == "__main__":
    asyncio.run(main())

