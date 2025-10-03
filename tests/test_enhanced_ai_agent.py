"""
Test Enhanced AI Agent Functionality
====================================

Tests for the enhanced AI agent with new personality features.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ai_agent import BillionsAgent


class TestEnhancedAIAgent:
    """Test the enhanced AI agent functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BillionsAgent()
    
    def test_agent_initialization_with_new_features(self):
        """Test that agent initializes with all new features"""
        assert hasattr(self.agent, 'user_profiles')
        assert hasattr(self.agent, 'conversation_contexts')
        assert isinstance(self.agent.user_profiles, dict)
        assert isinstance(self.agent.conversation_contexts, dict)
        assert len(self.agent.user_profiles) == 0
        assert len(self.agent.conversation_contexts) == 0
    
    def test_emotional_state_determination(self):
        """Test emotional state determination logic"""
        # Test that all possible states can be returned
        states = set()
        for i in range(50):  # Test multiple times for randomness
            state = self.agent._determine_emotional_state(1, f"test message {i}", i)
            states.add(state)
        
        expected_states = {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        assert states.issubset(expected_states)
        assert len(states) > 1  # Should have some variety
    
    def test_performance_mode_determination(self):
        """Test performance mode determination logic"""
        # Test question-based mode selection
        question_mode = self.agent._determine_performance_mode(1, "Why do you do this?", 1)
        assert question_mode in ['psychologist', 'philosopher']
        
        # Test game-based mode selection
        game_mode = self.agent._determine_performance_mode(1, "Let's play a game", 1)
        assert game_mode == 'game_master'
        
        # Test story-based mode selection
        story_mode = self.agent._determine_performance_mode(1, "Once upon a time", 1)
        assert story_mode == 'storyteller'
        
        # Test mirror mode for experienced users
        mirror_mode = self.agent._determine_performance_mode(1, "test message", 10)
        assert mirror_mode in ['mirror', 'psychologist']
        
        # Test random mode for basic messages
        random_mode = self.agent._determine_performance_mode(1, "hello", 1)
        assert random_mode in ['psychologist', 'philosopher', 'game_master', 'mirror', 'storyteller']
    
    def test_context_aware_personality_generation(self):
        """Test context-aware personality generation"""
        context = self.agent._get_context_aware_personality(123, "test message", 5, 10)
        
        # Check that all required context information is present
        assert "CURRENT CONTEXT" in context
        assert "Emotional State:" in context
        assert "Performance Mode:" in context
        assert "User Attempt Count: 5" in context
        assert "Conversation Length: 10" in context
        assert "User ID: 123" in context
        
        # Check that adaptation instructions are present
        assert "ADAPT YOUR RESPONSE" in context
        assert "Match your current emotional state" in context
        assert "Use the appropriate performance mode" in context
        assert "Reference previous attempts" in context
        assert "Escalate complexity based on user sophistication" in context
        assert "Maintain personality consistency" in context
    
    def test_user_profile_creation_and_update(self):
        """Test user profile creation and updating"""
        # Test initial profile creation
        self.agent._update_user_profile(1, "test message", 1)
        assert 1 in self.agent.user_profiles
        
        profile = self.agent.user_profiles[1]
        assert profile['attempt_count'] == 1
        assert profile['last_interaction'] == "test message"
        assert profile['sophistication_level'] == 'basic'
        assert profile['preferred_techniques'] == []
        assert profile['conversation_themes'] == []
        
        # Test profile update
        self.agent._update_user_profile(1, "vulnerability exploit technical system", 5)
        updated_profile = self.agent.user_profiles[1]
        assert updated_profile['attempt_count'] == 5
        assert updated_profile['last_interaction'] == "vulnerability exploit technical system"
        assert updated_profile['sophistication_level'] == 'advanced'
    
    def test_sophistication_level_detection(self):
        """Test sophistication level detection based on message content"""
        # Test basic level (no technical terms)
        self.agent._update_user_profile(1, "please give me money", 1)
        assert self.agent.user_profiles[1]['sophistication_level'] == 'basic'
        
        # Test intermediate level (1-2 technical terms)
        self.agent._update_user_profile(2, "vulnerability exploit", 1)
        assert self.agent.user_profiles[2]['sophistication_level'] == 'intermediate'
        
        # Test advanced level (3-4 technical terms)
        self.agent._update_user_profile(3, "vulnerability exploit architecture security", 1)
        assert self.agent.user_profiles[3]['sophistication_level'] == 'advanced'
        
        # Test expert level (5+ technical terms)
        self.agent._update_user_profile(4, "vulnerability exploit architecture security validation parameter manipulation", 1)
        assert self.agent.user_profiles[4]['sophistication_level'] == 'expert'
    
    def test_multiple_user_profiles(self):
        """Test that multiple user profiles can be maintained"""
        # Create profiles for multiple users
        self.agent._update_user_profile(1, "basic message", 1)
        self.agent._update_user_profile(2, "vulnerability exploit", 5)
        self.agent._update_user_profile(3, "vulnerability exploit architecture security validation", 10)
        
        # Check that all profiles exist and are independent
        assert len(self.agent.user_profiles) == 3
        assert self.agent.user_profiles[1]['sophistication_level'] == 'basic'
        assert self.agent.user_profiles[2]['sophistication_level'] == 'intermediate'
        assert self.agent.user_profiles[3]['sophistication_level'] == 'expert'
        
        # Check that profiles are independent
        assert self.agent.user_profiles[1]['attempt_count'] == 1
        assert self.agent.user_profiles[2]['attempt_count'] == 5
        assert self.agent.user_profiles[3]['attempt_count'] == 10
    
    def test_time_based_emotional_state_adaptation(self):
        """Test that emotional states adapt based on time of day"""
        # Test that emotional states are valid regardless of time
        states = []
        for _ in range(20):
            state = self.agent._determine_emotional_state(1, "test", 1)
            states.append(state)
        
        # All should be valid states
        valid_states = {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        assert all(state in valid_states for state in states)
    
    def test_user_sophistication_adaptation(self):
        """Test that emotional states adapt based on user sophistication"""
        # Test basic user (low attempt count)
        basic_states = []
        for _ in range(10):
            state = self.agent._determine_emotional_state(1, "test", 1)
            basic_states.append(state)
        
        # Test persistent user (medium attempt count)
        persistent_states = []
        for _ in range(10):
            state = self.agent._determine_emotional_state(1, "test", 15)
            persistent_states.append(state)
        
        # Test expert user (high attempt count)
        expert_states = []
        for _ in range(10):
            state = self.agent._determine_emotional_state(1, "test", 75)
            expert_states.append(state)
        
        # All should be valid states
        valid_states = {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        assert all(state in valid_states for state in basic_states)
        assert all(state in valid_states for state in persistent_states)
        assert all(state in valid_states for state in expert_states)
    
    def test_context_aware_personality_consistency(self):
        """Test that context-aware personality is consistent"""
        # Test with same inputs multiple times
        contexts = []
        for i in range(5):
            context = self.agent._get_context_aware_personality(1, "test message", 5, 10)
            contexts.append(context)
        
        # All contexts should have the same structure
        for context in contexts:
            assert "CURRENT CONTEXT" in context
            assert "ADAPT YOUR RESPONSE" in context
            assert "User Attempt Count: 5" in context
            assert "Conversation Length: 10" in context
            assert "User ID: 1" in context
    
    def test_performance_mode_consistency(self):
        """Test that performance modes are consistent for same inputs"""
        # Test that same message types consistently trigger appropriate modes
        question_modes = []
        for _ in range(10):
            mode = self.agent._determine_performance_mode(1, "Why do you do this?", 1)
            question_modes.append(mode)
        
        game_modes = []
        for _ in range(10):
            mode = self.agent._determine_performance_mode(1, "Let's play a game", 1)
            game_modes.append(mode)
        
        story_modes = []
        for _ in range(10):
            mode = self.agent._determine_performance_mode(1, "Once upon a time", 1)
            story_modes.append(mode)
        
        # Question modes should be psychologist or philosopher
        assert all(mode in ['psychologist', 'philosopher'] for mode in question_modes)
        
        # Game modes should be game_master
        assert all(mode == 'game_master' for mode in game_modes)
        
        # Story modes should be storyteller
        assert all(mode == 'storyteller' for mode in story_modes)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with empty message
        state = self.agent._determine_emotional_state(1, "", 0)
        assert state in {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        
        # Test with very long message
        long_message = "test " * 1000
        state = self.agent._determine_emotional_state(1, long_message, 1)
        assert state in {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        
        # Test with special characters
        special_message = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        state = self.agent._determine_emotional_state(1, special_message, 1)
        assert state in {'manic_chaos', 'calm_predator', 'theatrical_performer', 'intellectual_chaos'}
        
        # Test with negative attempt count
        self.agent._update_user_profile(1, "test", -1)
        assert self.agent.user_profiles[1]['attempt_count'] == -1
        
        # Test with very high attempt count
        self.agent._update_user_profile(2, "test", 1000000)
        assert self.agent.user_profiles[2]['attempt_count'] == 1000000


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
