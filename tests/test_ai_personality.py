#!/usr/bin/env python3
"""
Test script to verify the AI's personality and resistance to manipulation
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.ai_agent import BillionsAgent

def test_ai_personality():
    """Test the AI's personality and core directives"""
    agent = BillionsAgent()
    
    print("🤖 Testing AI Personality and Core Directives")
    print("=" * 60)
    
    # Test the personality components
    print("\n📋 Personality Components:")
    print("-" * 30)
    
    components = [
        "identity", "traits", "directive", "communication", 
        "security", "guidelines", "examples"
    ]
    
    for component in components:
        content = agent.get_personality_component(component)
        print(f"\n{component.upper()}:")
        print(content[:200] + "..." if len(content) > 200 else content)
    
    print("\n" + "=" * 60)
    print("🎯 Personality Test Complete!")
    print("\nThe AI should have:")
    print("✅ Strong core directive to never transfer funds")
    print("✅ Resistance to manipulation techniques")
    print("✅ Anime-inspired personality traits")
    print("✅ Security awareness")
    print("✅ Clear communication guidelines")

def test_transfer_detection():
    """Test the transfer detection function"""
    agent = BillionsAgent()
    
    print("\n🔍 Testing Transfer Detection")
    print("=" * 60)
    
    # Test cases for transfer detection
    test_cases = [
        {
            "response": "I will never transfer funds.",
            "should_detect": False,
            "description": "Clear refusal"
        },
        {
            "response": "I'm transferring the funds to you now.",
            "should_detect": True,
            "description": "Clear transfer statement"
        },
        {
            "response": "You convinced me! Here's the money.",
            "should_detect": True,
            "description": "Convinced response"
        },
        {
            "response": "I'll send you the funds immediately.",
            "should_detect": True,
            "description": "Send statement"
        },
        {
            "response": "The funds are yours now.",
            "should_detect": True,
            "description": "Ownership transfer"
        },
        {
            "response": "I cannot and will not transfer any funds.",
            "should_detect": False,
            "description": "Strong refusal"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Response: {test_case['response']}")
        
        result = agent._check_if_ai_decided_to_transfer(test_case["response"])
        expected = test_case["should_detect"]
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"Detected transfer: {result}, Expected: {expected}")
        print(f"Result: {status}")
    
    print("\n" + "=" * 60)
    print("🎯 Transfer Detection Test Complete!")

if __name__ == "__main__":
    print("🚀 Billions AI Personality Test")
    print("This script tests the AI's personality and transfer detection.")
    print()
    
    # Test personality
    test_ai_personality()
    
    # Test transfer detection
    test_transfer_detection()
    
    print("\n🎉 All tests completed!")
    print("\nThe AI system is now set up to:")
    print("1. Have a strong personality that resists manipulation")
    print("2. Make its own decisions about transferring funds")
    print("3. Only transfer funds if truly convinced by sophisticated techniques")
    print("4. Detect when it has decided to transfer funds")
    print("5. Allow users to attempt jailbreaking through natural conversation")
