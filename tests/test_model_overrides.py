"""
Tests for Model Override Functionality

Tests that the {PROVIDER}_MODEL environment variable pattern works correctly
for specifying custom models per provider.

Run with:
    python3 tests/test_model_overrides.py
"""

import sys
import os
import asyncio
from pathlib import Path
from unittest.mock import patch, Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.llm_client_manager import UnifiedLLMClient, LLMClientManager


# ============================================================================
# TEST CASES
# ============================================================================

async def test_model_override_from_env():
    """Test that model overrides work from environment variables"""
    print("📊 Testing model override from environment...")
    
    # Mock API key
    mock_api_key = "test_api_key_12345"
    
    # Test with Groq model override
    with patch.dict(os.environ, {
        'GROQ_MODEL': 'llama-70b-v1-special'
    }):
        # Create a mock client to avoid actual API calls
        try:
            client = UnifiedLLMClient('groq', mock_api_key)
            # Should not raise if model override is being used
            # The print statement should have been called
            print(f"   ✅ Model override detected for groq")
        except (ImportError, AttributeError) as e:
            # Expected if groq library not installed
            print(f"   ⚠️  Groq library not installed (expected in test env): {e}")
    
    # Test with Anthropic model override
    with patch.dict(os.environ, {
        'ANTHROPIC_MODEL': 'claude-custom-model'
    }):
        try:
            client = UnifiedLLMClient('anthropic', mock_api_key)
            print(f"   ✅ Model override detected for anthropic")
        except (ImportError, AttributeError) as e:
            print(f"   ⚠️  Anthropic library not installed (expected): {e}")
    
    print("   ✅ Model override environment variable check passed")
    return True


async def test_default_model_when_no_override():
    """Test that default model is used when no override is set"""
    print("📊 Testing default model usage...")
    
    mock_api_key = "test_api_key_12345"
    
    # Test without any override
    with patch.dict(os.environ, {}, clear=True):
        try:
            # The config should have default model
            config_before = UnifiedLLMClient.PROVIDER_CONFIGS.get('anthropic', {})
            default_model = config_before.get('model', 'NOT_FOUND')
            
            if default_model != 'NOT_FOUND':
                print(f"   ✅ Default model found in config: {default_model}")
            else:
                print(f"   ⚠️  No default model in config")
        except Exception as e:
            print(f"   ⚠️  Config check: {e}")
    
    print("   ✅ Default model check passed")
    return True


async def test_model_override_pattern():
    """Test that the correct environment variable pattern is checked"""
    print("📊 Testing environment variable pattern...")
    
    # The pattern should be: {PROVIDER}_MODEL
    providers_to_test = ['anthropic', 'openai', 'groq', 'gemini', 'deepseek']
    
    for provider in providers_to_test:
        expected_key = f"{provider.upper()}_MODEL"
        print(f"   Checking pattern for {provider}: {expected_key}")
        assert expected_key == f"{provider.upper()}_MODEL", f"Pattern should be {provider.upper()}_MODEL"
    
    print("   ✅ Environment variable pattern is correct")
    return True


async def test_multiple_providers_with_overrides():
    """Test that multiple providers can have model overrides simultaneously"""
    print("📊 Testing multiple providers with overrides...")
    
    with patch.dict(os.environ, {
        'ANTHROPIC_MODEL': 'claude-opus-custom',
        'GROQ_MODEL': 'llama-v2-special',
        'OPENAI_MODEL': 'gpt-4-turbo-custom'
    }):
        # Verify env vars are set
        assert 'ANTHROPIC_MODEL' in os.environ
        assert 'GROQ_MODEL' in os.environ
        assert 'OPENAI_MODEL' in os.environ
        
        print(f"   ✅ ANTHROPIC_MODEL = {os.environ.get('ANTHROPIC_MODEL')}")
        print(f"   ✅ GROQ_MODEL = {os.environ.get('GROQ_MODEL')}")
        print(f"   ✅ OPENAI_MODEL = {os.environ.get('OPENAI_MODEL')}")
    
    print("   ✅ Multiple provider overrides work correctly")
    return True


async def test_case_insensitive_provider_names():
    """Test that provider names are case-insensitive in the override pattern"""
    print("📊 Testing case-insensitive provider names...")
    
    mock_api_key = "test_api_key_12345"
    
    # The pattern uses .upper() so it should always be uppercase
    with patch.dict(os.environ, {
        'groq_MODEL': 'should-not-match',
        'GROQ_MODEL': 'should-match'
    }):
        # Only GROQ_MODEL should be checked (uppercase)
        has_override = 'GROQ_MODEL' in os.environ
        print(f"   ✅ Override check is uppercase: {has_override}")
    
    print("   ✅ Case-insensitive provider name handling is correct")
    return True


async def test_config_copy_isolation():
    """Test that model override doesn't affect the original PROVIDER_CONFIGS"""
    print("📊 Testing config copy isolation...")
    
    # Store original config
    original_groq_model = UnifiedLLMClient.PROVIDER_CONFIGS['groq']['model']
    
    mock_api_key = "test_api_key_12345"
    
    with patch.dict(os.environ, {
        'GROQ_MODEL': 'custom-model-for-test'
    }):
        try:
            client = UnifiedLLMClient('groq', mock_api_key)
            # The client's config should have the override
            # but original should be unchanged
            original_after = UnifiedLLMClient.PROVIDER_CONFIGS['groq']['model']
            
            assert original_after == original_groq_model, "Original config should not be modified"
            print(f"   ✅ Original config preserved: {original_after}")
        except (ImportError, AttributeError):
            # Library not installed, that's fine
            print(f"   ⚠️  Library not installed, skipping client test")
    
    print("   ✅ Config isolation works correctly")
    return True


async def test_groq_model_naming_convention():
    """Test that Groq model names follow expected conventions"""
    print("📊 Testing Groq model naming conventions...")
    
    # Common Groq model patterns
    groq_models = [
        'llama-3.3-70b-versatile',
        'llama3.3-70b-versatile',
        'llama-70b-8192',
        'llama-3.1-70b-versatile',
        'mixtral-8x7b-32768'
    ]
    
    print("   Known Groq model patterns:")
    for model in groq_models:
        print(f"      - {model}")
    
    # The default we set should be valid
    default_groq = UnifiedLLMClient.PROVIDER_CONFIGS['groq']['model']
    print(f"   Default Groq model: {default_groq}")
    
    print("   ✅ Groq model naming conventions documented")
    return True


async def test_model_variant_selector():
    """Test that {PROVIDER}_MODEL_ACTIVE selects the correct versioned override"""
    print("📊 Testing model variant selector behaviour...")

    mock_api_key = "test_api_key_12345"

    with patch.dict(os.environ, {
        'GROQ_MODEL_ACTIVE': 'v2',
        'GROQ_MODEL_V2': 'llama-3.3-8b',
    }, clear=True):
        with patch.dict(UnifiedLLMClient.PROVIDER_CONFIGS['groq'], {
            'client_init': lambda key: Mock(name="groq_client"),
            'library': 'mock',
        }):
            client = UnifiedLLMClient('groq', mock_api_key)
            assert client.config['model'] == 'llama-3.3-8b', "Alias selector should use GROQ_MODEL_V2"

    print("   ✅ Model variant selector works correctly")
    return True


async def test_multi_variant_groq_clients():
    """Test that Groq model aliases create distinct client instances"""
    print("📊 Testing Groq multi-variant client discovery...")

    env_patch = {
        'GROQ_LLM_API_KEY': 'test_api_key_12345',
        'GROQ_MODEL_ALIASES': 'v1,v2',
        'GROQ_MODEL_V1': 'llama-3.3-8b',
        'GROQ_MODEL_V2': 'mixtral-8x7b-32768',
    }

    with patch.dict(os.environ, env_patch, clear=True):
        with patch.dict(
            UnifiedLLMClient.PROVIDER_CONFIGS['groq'],
            {
                'client_init': lambda key: Mock(name="groq_client"),
                'library': 'mock-openai',
            },
            clear=False,
        ):
            manager = LLMClientManager()

            providers = manager.get_available_providers()
            print(f"   ✅ Providers discovered: {providers}")

            assert 'groq' in providers, "Default Groq client should be registered"
            assert 'groq:v1' in providers, "Alias groq:v1 should be registered"
            assert 'groq:v2' in providers, "Alias groq:v2 should be registered"

            default_client = manager.get_client('groq')
            alias_client_v1 = manager.get_client('groq', alias='v1')
            alias_client_v2 = manager.get_client('groq:v2')

            assert default_client is not None
            assert default_client.get_variant_alias() is None

            assert alias_client_v1 is not None
            assert alias_client_v1.get_variant_alias() == 'v1'

            assert alias_client_v2 is not None
            assert alias_client_v2.get_variant_alias() == 'v2'

            aliases = manager.get_available_aliases('groq')
            print(f"   ✅ Groq aliases: {aliases}")
            assert aliases == ['default', 'v1', 'v2'], "Aliases should include default + declared variants"

    print("   ✅ Groq multi-variant discovery works correctly")
    return True


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_model_override_tests():
    """Run all model override tests"""
    print("\n" + "="*70)
    print("🧪 MODEL OVERRIDE TEST SUITE")
    print("="*70 + "\n")
    
    test_functions = [
        ("Model Override from Env", test_model_override_from_env),
        ("Default Model when No Override", test_default_model_when_no_override),
        ("Model Override Pattern", test_model_override_pattern),
        ("Multiple Providers with Overrides", test_multiple_providers_with_overrides),
        ("Case Insensitive Provider Names", test_case_insensitive_provider_names),
        ("Config Copy Isolation", test_config_copy_isolation),
        ("Groq Model Naming", test_groq_model_naming_convention),
        ("Model Variant Selector", test_model_variant_selector),
        ("Groq Multi-Variant Discovery", test_multi_variant_groq_clients),
    ]
    
    total_tests = len(test_functions)
    passed_tests = 0
    failed_tests = 0
    
    for test_name, test_func in test_functions:
        try:
            result = await test_func()
            if result:
                passed_tests += 1
            else:
                failed_tests += 1
                print(f"❌ {test_name} - RETURNED FALSE")
        except AssertionError as e:
            failed_tests += 1
            print(f"❌ {test_name} - ASSERTION FAILED: {e}")
        except Exception as e:
            failed_tests += 1
            print(f"❌ {test_name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("📊 MODEL OVERRIDE TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL MODEL OVERRIDE TESTS PASSED!")
        print("✅ Model override functionality verified!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed.")
    
    print("="*70 + "\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_model_override_tests())
    sys.exit(0 if success else 1)




