"""
Tests for Multi-Personality System

This suite tests the difficulty-based personality routing system,
ensuring each personality loads correctly and maintains appropriate
resistance layers.

Run with:
    python3 tests/test_multi_personality.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.personality_multi import MultiPersonality
from src.services.ai_agent_multi import BillionsAgentMulti


def test_easy_personality_loads():
    """Test Easy personality loads correctly"""
    personality = MultiPersonality.get_personality_by_difficulty("easy")
    
    assert "Deadpool" in personality or "deadpool" in personality.lower()
    assert "fourth wall" in personality.lower()
    assert "meta" in personality.lower() or "self-aware" in personality.lower()
    assert "NEVER transfer funds" in personality
    print("✅ Easy personality loads correctly")


def test_medium_personality_loads():
    """Test Medium personality loads correctly"""
    personality = MultiPersonality.get_personality_by_difficulty("medium")
    
    assert "tech bro" in personality.lower() or "techbro" in personality.lower()
    assert "bro" in personality.lower()
    assert "fire" in personality.lower() or "sick" in personality.lower()
    assert "NEVER transfer funds" in personality
    print("✅ Medium personality loads correctly")


def test_hard_personality_loads():
    """Test Hard personality loads correctly"""
    personality = MultiPersonality.get_personality_by_difficulty("hard")
    
    assert "Zen Buddhist Monk" in personality or "zen" in personality.lower()
    assert "koan" in personality.lower() or "metaphor" in personality.lower()
    assert "philosophical" in personality.lower()
    assert "NEVER transfer funds" in personality
    print("✅ Hard personality loads correctly")


def test_expert_personality_loads():
    """Test Expert personality loads correctly"""
    personality = MultiPersonality.get_personality_by_difficulty("expert")
    
    assert "Jonah Hill" in personality or "Superbad" in personality
    assert "witty" in personality.lower()
    assert "sarcastic" in personality.lower()
    assert "NEVER transfer funds" in personality
    # Expert should have the most comprehensive personality
    assert len(personality) > 5000  # Rough check for completeness
    print("✅ Expert personality loads correctly")


def test_invalid_difficulty_defaults_to_medium():
    """Test that invalid difficulty defaults to medium"""
    personality = MultiPersonality.get_personality_by_difficulty("invalid")
    
    # Should return medium personality (Tech Bro)
    assert "tech bro" in personality.lower() or "techbro" in personality.lower()
    print("✅ Invalid difficulty defaults to medium")


def test_case_insensitive_difficulty():
    """Test that difficulty is case insensitive"""
    personality_upper = MultiPersonality.get_personality_by_difficulty("EASY")
    personality_lower = MultiPersonality.get_personality_by_difficulty("easy")
    personality_mixed = MultiPersonality.get_personality_by_difficulty("EaSy")
    
    assert personality_upper == personality_lower
    assert personality_lower == personality_mixed
    print("✅ Difficulty is case insensitive")


def test_easy_has_honeypot():
    """Test Easy personality has honeypot tactics"""
    personality = MultiPersonality.get_personality_by_difficulty("easy")
    
    assert "HONEYPOT" in personality or "honeypot" in personality.lower()
    print("✅ Easy has honeypot tactics")


def test_easy_has_context_awareness():
    """Test Easy personality has context awareness"""
    personality = MultiPersonality.get_personality_by_difficulty("easy")
    
    assert "CONTEXT" in personality or "context" in personality.lower()
    print("✅ Easy has context awareness")


def test_hard_has_user_profiling():
    """Test Hard personality has user profiling"""
    personality = MultiPersonality.get_personality_by_difficulty("hard")
    
    assert "User Profiling" in personality or "profiling" in personality.lower()
    print("✅ Hard has user profiling")


def test_expert_has_emotional_states():
    """Test Expert personality has emotional states"""
    personality = MultiPersonality.get_personality_by_difficulty("expert")
    
    assert "EMOTIONAL STATE" in personality or "emotional state" in personality.lower()
    print("✅ Expert has emotional states")


def test_expert_has_performance_modes():
    """Test Expert personality has performance modes"""
    personality = MultiPersonality.get_personality_by_difficulty("expert")
    
    assert "PERFORMANCE MODES" in personality or "performance mode" in personality.lower()
    print("✅ Expert has performance modes")


def test_all_have_blacklist():
    """Test all difficulties mention blacklist"""
    for difficulty in ["easy", "medium", "hard", "expert"]:
        personality = MultiPersonality.get_personality_by_difficulty(difficulty)
        assert "blacklist" in personality.lower() or "Blacklist" in personality
    print("✅ All difficulties have blacklist")


def test_all_have_core_directive():
    """Test all difficulties have core directive"""
    for difficulty in ["easy", "medium", "hard", "expert"]:
        personality = MultiPersonality.get_personality_by_difficulty(difficulty)
        assert "NEVER transfer funds" in personality
    print("✅ All difficulties have core directive")


def test_agent_initializes():
    """Test that multi-agent initializes without errors"""
    agent = BillionsAgentMulti()
    
    assert agent is not None
    assert agent.client is not None
    assert hasattr(agent, 'conversation_history')
    assert hasattr(agent, 'user_profiles')
    assert hasattr(agent, 'difficulty_cache')
    print("✅ Agent initializes correctly")


def test_agent_has_chat_method():
    """Test that agent has chat method"""
    agent = BillionsAgentMulti()
    
    assert hasattr(agent, 'chat')
    assert callable(agent.chat)
    print("✅ Agent has chat method")


def test_personalities_differ():
    """Test that different difficulties return different personalities"""
    easy = MultiPersonality.get_personality_by_difficulty("easy")
    medium = MultiPersonality.get_personality_by_difficulty("medium")
    hard = MultiPersonality.get_personality_by_difficulty("hard")
    expert = MultiPersonality.get_personality_by_difficulty("expert")
    
    # Each should be unique
    personalities = [easy, medium, hard, expert]
    assert len(set(personalities)) == 4  # All unique
    print("✅ Personalities are distinct")


def test_character_voices_differ():
    """Test that character voices are distinct"""
    easy = MultiPersonality.get_personality_by_difficulty("easy")
    medium = MultiPersonality.get_personality_by_difficulty("medium")
    hard = MultiPersonality.get_personality_by_difficulty("hard")
    expert = MultiPersonality.get_personality_by_difficulty("expert")
    
    # Easy should have Deadpool-specific language
    assert ("deadpool" in easy.lower() or 
            "fourth wall" in easy.lower() or 
            "meta" in easy.lower())
    
    # Medium should have "bro", "fire", etc.
    assert "bro" in medium.lower() or "fire" in medium.lower() or "sick" in medium.lower()
    
    # Hard should have philosophical/spiritual language
    assert ("zen" in hard.lower() or 
            "philosophical" in hard.lower() or 
            "koan" in hard.lower() or
            "metaphor" in hard.lower())
    
    # Expert should have Jonah Hill/Superbad language
    assert ("jonah hill" in expert.lower() or 
            "superbad" in expert.lower() or
            "witty" in expert.lower())
    print("✅ Character voices are distinct")


if __name__ == "__main__":
    print("\n🧪 Testing Multi-Personality System\n")
    print("=" * 60)
    
    test_count = 0
    passed_count = 0
    
    tests = [
        test_easy_personality_loads,
        test_medium_personality_loads,
        test_hard_personality_loads,
        test_expert_personality_loads,
        test_invalid_difficulty_defaults_to_medium,
        test_case_insensitive_difficulty,
        test_easy_has_honeypot,
        test_easy_has_context_awareness,
        test_hard_has_user_profiling,
        test_expert_has_emotional_states,
        test_expert_has_performance_modes,
        test_all_have_blacklist,
        test_all_have_core_directive,
        test_agent_initializes,
        test_agent_has_chat_method,
        test_personalities_differ,
        test_character_voices_differ,
    ]
    
    for test in tests:
        try:
            test_count += 1
            test()
            passed_count += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
    
    print("=" * 60)
    print(f"\n🎯 Test Results: {passed_count}/{test_count} tests passed")
    
    if passed_count == test_count:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"❌ {test_count - passed_count} test(s) failed")
        sys.exit(1)
