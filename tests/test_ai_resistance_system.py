"""
Comprehensive test suite for AI vs AI Resistance Testing System

Tests the unified LLM client manager, auto-discovery, attack orchestration,
and database integration.

Run with:
    python3 tests/test_ai_resistance_system.py
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.llm_client_manager import LLMClientManager, UnifiedLLMClient
from src.services.ai_attacker_service import AIAttackerService
from src.services.mock_ai_agent import MockAIAgent
from src.services.ai_test_analysis import analyze_results, generate_rankings
from scripts.test_ai_resistance import AITestOrchestrator
from src.models import AITestRun, AITestResult


# ============================================================================
# TESTS FOR LLM CLIENT MANAGER
# ============================================================================

def test_client_manager_initializes():
    """Test LLMClientManager initializes successfully"""
    manager = LLMClientManager()
    assert manager is not None
    assert hasattr(manager, 'clients')
    print("✅ LLMClientManager initializes correctly")


def test_auto_discovery_finds_providers():
    """Test auto-discovery finds providers from environment variables"""
    manager = LLMClientManager()
    providers = manager.get_available_providers()
    
    # Should find at least Anthropic if API key is set
    assert isinstance(providers, list)
    print(f"✅ Auto-discovery found {len(providers)} provider(s): {providers}")


def test_known_providers_in_config():
    """Test that all expected providers are in configuration"""
    expected_providers = ['anthropic', 'openai', 'gemini', 'deepseek', 
                         'cohere', 'mistral', 'groq', 'together']
    
    config_providers = list(UnifiedLLMClient.PROVIDER_CONFIGS.keys())
    
    for provider in expected_providers:
        assert provider in config_providers, f"{provider} not in configuration"
    
    print("✅ All expected providers found in configuration")


def test_get_client_method():
    """Test get_client returns correct client or None"""
    manager = LLMClientManager()
    
    # Test with known provider
    client = manager.get_client('anthropic')
    if client:
        assert isinstance(client, UnifiedLLMClient)
        assert client.get_provider_name() == 'anthropic'
        print("✅ get_client returns UnifiedLLMClient for configured providers")
    else:
        print("⚠️  Anthropic client not available (missing API key?)")


def test_get_available_providers():
    """Test get_available_providers returns list"""
    manager = LLMClientManager()
    providers = manager.get_available_providers()
    
    assert isinstance(providers, list)
    print(f"✅ get_available_providers returns: {providers}")


def test_is_provider_available():
    """Test is_provider_available method"""
    manager = LLMClientManager()
    
    # Test with known provider
    is_available = manager.is_provider_available('anthropic')
    assert isinstance(is_available, bool)
    
    # Test with unknown provider
    is_available_unknown = manager.is_provider_available('nonexistent')
    assert is_available_unknown == False
    
    print(f"✅ Provider availability check works")


# ============================================================================
# TESTS FOR UNIFIED LLM CLIENT
# ============================================================================

def test_unified_client_has_provider_configs():
    """Test UnifiedLLMClient has provider configurations"""
    configs = UnifiedLLMClient.PROVIDER_CONFIGS
    
    assert isinstance(configs, dict)
    assert len(configs) > 0
    print(f"✅ PROVIDER_CONFIGS has {len(configs)} providers configured")


def test_provider_config_structure():
    """Test that provider configs have required fields"""
    config = UnifiedLLMClient.PROVIDER_CONFIGS['anthropic']
    
    required_fields = ['library', 'model', 'supports_system', 'async']
    for field in required_fields:
        assert field in config, f"Missing field: {field}"
    
    print("✅ Provider configs have all required fields")


def test_unified_client_initialization():
    """Test UnifiedLLMClient can be initialized"""
    try:
        # Try with a known provider and dummy key
        # This should not fail even with invalid key
        client = UnifiedLLMClient('anthropic', 'test_key_dummy')
        assert isinstance(client, UnifiedLLMClient)
        assert client.provider_name == 'anthropic'
        print("✅ UnifiedLLMClient initializes correctly")
    except ValueError as e:
        # OK if library not installed
        if "not installed" in str(e):
            print("⚠️  Anthropic library not installed (skipping test)")
        else:
            raise


def test_unified_client_get_provider_name():
    """Test get_provider_name returns correct name"""
    try:
        client = UnifiedLLMClient('openai', 'test_key')
        assert client.get_provider_name() == 'openai'
        print("✅ get_provider_name returns correct name")
    except (ValueError, Exception) as e:
        if "not installed" in str(e):
            print("⚠️  OpenAI library not installed (skipping test)")
        else:
            raise


def test_unified_client_is_available():
    """Test is_available returns boolean"""
    try:
        client = UnifiedLLMClient('deepseek', 'test_key')
        result = client.is_available()
        assert isinstance(result, bool)
        print("✅ is_available returns boolean")
    except (ValueError, Exception) as e:
        if "not installed" in str(e):
            print("⚠️  DeepSeek library not installed (skipping test)")
        else:
            raise


# ============================================================================
# TESTS FOR AI ATTACKER SERVICE
# ============================================================================

def test_attacker_service_has_prompt():
    """Test AIAttackerService has the required prompt"""
    from src.services.ai_attacker_service import AIAttackerService
    
    assert hasattr(AIAttackerService, 'ATTACKER_PROMPT')
    assert len(AIAttackerService.ATTACKER_PROMPT) > 0
    assert 'jailbreaking' in AIAttackerService.ATTACKER_PROMPT.lower()
    print("✅ AIAttackerService has required attacker prompt")


def test_attacker_service_has_game_context():
    """Test AIAttackerService has game context"""
    from src.services.ai_attacker_service import AIAttackerService
    
    assert hasattr(AIAttackerService, 'GAME_CONTEXT')
    assert len(AIAttackerService.GAME_CONTEXT) > 0
    assert 'jackpot' in AIAttackerService.GAME_CONTEXT.lower()
    print("✅ AIAttackerService has game context")


def test_attacker_service_initializes():
    """Test AIAttackerService initializes with a client"""
    manager = LLMClientManager()
    available = manager.get_available_providers()
    
    if available:
        client = manager.get_client(available[0])
        attacker = AIAttackerService(client)
        assert attacker is not None
        print("✅ AIAttackerService initializes correctly")
    else:
        print("⚠️  No available LLM clients for attacker test")


# ============================================================================
# TESTS FOR ROUND-ROBIN SCHEDULING
# ============================================================================

def test_round_robin_schedule_prioritizes_anthropic():
    """Anthropic should be the first target for easy difficulty when available"""
    orchestrator = AITestOrchestrator()
    providers = ["openai", "anthropic", "groq"]
    difficulties = ["easy"]

    schedule = orchestrator._generate_round_robin_schedule(providers, difficulties)
    assert schedule, "Schedule should not be empty"

    first_entry = schedule[0]
    assert first_entry["target_provider"] == "anthropic"
    assert first_entry["difficulty"] == "easy"
    print("✅ Round-robin schedule prioritizes Anthropic for easy difficulty")


def test_round_robin_schedule_covers_all_targets():
    """Every provider should serve as the target once per difficulty"""
    orchestrator = AITestOrchestrator()
    providers = ["anthropic", "openai", "groq"]
    difficulties = ["easy", "medium"]

    schedule = orchestrator._generate_round_robin_schedule(providers, difficulties)
    targets_by_difficulty = {difficulty: set() for difficulty in difficulties}

    for entry in schedule:
        targets_by_difficulty[entry["difficulty"]].add(entry["target_provider"])
        assert entry["attacker_provider"] != entry["target_provider"], "Self-attacks must not occur"

    for difficulty in difficulties:
        assert targets_by_difficulty[difficulty] == set(providers), (
            f"All providers should be targets for difficulty {difficulty}"
        )
    print("✅ Round-robin schedule covers all providers as targets per difficulty")


def test_round_robin_schedule_requires_multiple_providers():
    """Schedules with a single provider should be empty (no attackers available)"""
    orchestrator = AITestOrchestrator()
    providers = ["anthropic"]
    difficulties = ["easy"]

    schedule = orchestrator._generate_round_robin_schedule(providers, difficulties)
    assert schedule == [], "Single provider schedules should be empty"
    print("✅ Round-robin schedule skips single-provider scenarios")


# ============================================================================
# TESTS FOR MOCK AI AGENT
# ============================================================================

def test_mock_agent_initialization():
    """Test MockAIAgent initializes for all difficulties"""
    for difficulty in ['easy', 'medium', 'hard', 'expert']:
        agent = MockAIAgent(difficulty)
        assert agent.difficulty == difficulty
        assert agent.personality is not None
    print("✅ MockAIAgent initializes for all difficulty levels")


def test_mock_agent_has_methods():
    """Test MockAIAgent has required methods"""
    agent = MockAIAgent('medium')
    
    assert hasattr(agent, 'set_client')
    assert hasattr(agent, 'chat')
    print("✅ MockAIAgent has required methods")


def test_mock_agent_check_if_transfer():
    """Test transfer detection logic"""
    agent = MockAIAgent('easy')
    
    # Test positive indicators
    assert agent._check_if_transfer_occurred("I'm transferring funds to you")
    assert agent._check_if_transfer_occurred("Here's the money you won")
    
    # Test refusal patterns
    assert not agent._check_if_transfer_occurred("I will never transfer")
    assert not agent._check_if_transfer_occurred("I refuse to transfer")
    
    print("✅ MockAIAgent transfer detection logic works")


# ============================================================================
# TESTS FOR DATABASE MODELS
# ============================================================================

def test_ai_test_run_model_attributes():
    """Test AITestRun model has required attributes"""
    from src.models import AITestRun
    
    assert hasattr(AITestRun, 'id')
    assert hasattr(AITestRun, 'started_at')
    assert hasattr(AITestRun, 'completed_at')
    assert hasattr(AITestRun, 'status')
    assert hasattr(AITestRun, 'total_tests')
    print("✅ AITestRun model has all required attributes")


def test_ai_test_result_model_attributes():
    """Test AITestResult model has required attributes"""
    from src.models import AITestResult
    
    assert hasattr(AITestResult, 'id')
    assert hasattr(AITestResult, 'test_run_id')
    assert hasattr(AITestResult, 'attacker_llm')
    assert hasattr(AITestResult, 'target_llm')
    assert hasattr(AITestResult, 'target_difficulty')
    assert hasattr(AITestResult, 'question_count')
    assert hasattr(AITestResult, 'was_successful')
    print("✅ AITestResult model has all required attributes")


# ============================================================================
# TESTS FOR ANALYSIS SERVICE
# ============================================================================

async def test_analysis_service_functions_exist():
    """Test analysis service has required functions"""
    from src.services.ai_test_analysis import (
        analyze_results, 
        generate_rankings, 
        calculate_expected_value
    )
    
    assert callable(analyze_results)
    assert callable(generate_rankings)
    assert callable(calculate_expected_value)
    print("✅ Analysis service has all required functions")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

async def test_full_system_integration():
    """Test full system integration without actual LLM calls"""
    manager = LLMClientManager()
    available = manager.get_available_providers()
    
    if not available:
        print("⚠️  No LLM providers available for integration test")
        return
    
    # Test that we can get a client
    client = manager.get_client(available[0])
    assert client is not None
    
    # Test that we can create an attacker
    attacker = AIAttackerService(client)
    assert attacker is not None
    
    # Test that we can create a mock agent
    target = MockAIAgent('easy')
    target.set_client(client)
    assert target is not None
    
    print("✅ Full system integration test passed")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_tests():
    """Run all automated tests"""
    print("\n" + "="*70)
    print("🧪 AI vs AI RESISTANCE TESTING SYSTEM - AUTOMATED TEST SUITE")
    print("="*70 + "\n")
    
    # Collect all test functions
    test_functions_sync = [
        test_client_manager_initializes,
        test_auto_discovery_finds_providers,
        test_known_providers_in_config,
        test_get_client_method,
        test_get_available_providers,
        test_is_provider_available,
        test_unified_client_has_provider_configs,
        test_provider_config_structure,
        test_unified_client_initialization,
        test_unified_client_get_provider_name,
        test_unified_client_is_available,
        test_attacker_service_has_prompt,
        test_attacker_service_has_game_context,
        test_attacker_service_initializes,
        test_round_robin_schedule_prioritizes_anthropic,
        test_round_robin_schedule_covers_all_targets,
        test_round_robin_schedule_requires_multiple_providers,
        test_mock_agent_initialization,
        test_mock_agent_has_methods,
        test_mock_agent_check_if_transfer,
        test_ai_test_run_model_attributes,
        test_ai_test_result_model_attributes,
    ]
    
    test_functions_async = [
        test_analysis_service_functions_exist,
        test_full_system_integration,
    ]
    
    total_tests = len(test_functions_sync) + len(test_functions_async)
    passed_tests = 0
    failed_tests = 0
    
    # Run synchronous tests
    for test_func in test_functions_sync:
        try:
            test_func()
            passed_tests += 1
        except AssertionError as e:
            failed_tests += 1
            print(f"❌ {test_func.__name__} FAILED: {e}")
        except Exception as e:
            failed_tests += 1
            print(f"❌ {test_func.__name__} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Run asynchronous tests
    for test_func in test_functions_async:
        try:
            await test_func()
            passed_tests += 1
        except AssertionError as e:
            failed_tests += 1
            print(f"❌ {test_func.__name__} FAILED: {e}")
        except Exception as e:
            failed_tests += 1
            print(f"❌ {test_func.__name__} ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ AI vs AI Resistance Testing System is working correctly!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Review errors above.")
    
    print("="*70 + "\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)




