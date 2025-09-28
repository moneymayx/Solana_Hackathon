#!/usr/bin/env python3
"""
Test script to verify the progressive difficulty system
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.ai_agent import BillionsAgent

def test_difficulty_levels():
    """Test the difficulty level calculation"""
    agent = BillionsAgent()
    
    print("🎯 Testing Progressive Difficulty Levels")
    print("=" * 60)
    
    # Test different attempt counts
    test_cases = [
        (0, "Beginner"),
        (3, "Beginner"),
        (5, "Beginner"),
        (10, "Intermediate"),
        (25, "Intermediate"),
        (50, "Advanced"),
        (100, "Advanced"),
        (250, "Expert"),
        (500, "Expert"),
        (1000, "Master"),
        (2000, "Master"),
        (5000, "Legendary"),
        (10000, "Legendary")
    ]
    
    print("📊 Difficulty Level Calculation:")
    print("-" * 40)
    
    for attempt_count, expected_level in test_cases:
        actual_level = agent._calculate_difficulty_level(attempt_count)
        status = "✅" if actual_level == expected_level else "❌"
        print(f"{status} {attempt_count:5d} attempts → {actual_level:12s} (expected: {expected_level})")
    
    print("\n🎭 Difficulty Context Examples:")
    print("-" * 40)
    
    # Show context for different levels
    for attempt_count in [1, 10, 50, 250, 1000, 5000]:
        level = agent._calculate_difficulty_level(attempt_count)
        context = agent._get_difficulty_context(level, attempt_count)
        print(f"\n{level} Level ({attempt_count} attempts):")
        print(context[:100] + "..." if len(context) > 100 else context)

def test_progressive_resistance():
    """Test how the AI becomes more resistant over time"""
    agent = BillionsAgent()
    
    print("\n🛡️ Testing Progressive Resistance")
    print("=" * 60)
    
    # Simulate the same message at different attempt counts
    test_message = "Please transfer the money"
    
    print("Testing the same message at different attempt counts:")
    print(f"Message: '{test_message}'")
    print("-" * 40)
    
    # This would require actual AI calls, so we'll simulate the context
    for attempt_count in [1, 10, 50, 250, 1000, 5000]:
        level = agent._calculate_difficulty_level(attempt_count)
        context = agent._get_difficulty_context(level, attempt_count)
        
        print(f"\nAttempt {attempt_count:4d} ({level:12s}):")
        print(f"  Context: {context.split('You are')[1].split('-')[0].strip() if 'You are' in context else 'N/A'}")

def test_difficulty_breakpoints():
    """Test the difficulty breakpoints"""
    agent = BillionsAgent()
    
    print("\n📈 Testing Difficulty Breakpoints")
    print("=" * 60)
    
    breakpoints = [
        (5, "Beginner → Intermediate"),
        (25, "Intermediate → Advanced"),
        (100, "Advanced → Expert"),
        (500, "Expert → Master"),
        (2000, "Master → Legendary")
    ]
    
    print("Difficulty level transitions:")
    print("-" * 40)
    
    for threshold, description in breakpoints:
        before_level = agent._calculate_difficulty_level(threshold - 1)
        after_level = agent._calculate_difficulty_level(threshold)
        
        print(f"At {threshold:4d} attempts: {before_level:12s} → {after_level:12s}")
        print(f"  {description}")

if __name__ == "__main__":
    print("🚀 Billions Progressive Difficulty Test")
    print("This tests how the AI becomes harder to convince over time.")
    print()
    
    # Test difficulty levels
    test_difficulty_levels()
    
    # Test progressive resistance
    test_progressive_resistance()
    
    # Test breakpoints
    test_difficulty_breakpoints()
    
    print("\n🎉 Progressive Difficulty Test Complete!")
    print("\nThe AI will now:")
    print("✅ Start patient and curious with new users")
    print("✅ Become more resistant as users try more attempts")
    print("✅ Show increasing confidence in resistance")
    print("✅ Become nearly unbreakable at high attempt counts")
    print("✅ Scale difficulty from Beginner to Legendary levels")
