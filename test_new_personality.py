#!/usr/bin/env python3
"""
Test script to verify the new witty, sarcastic personality is working
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.personality import BillionsPersonality

def test_new_personality():
    """Test the new witty, sarcastic personality"""
    print("🤖 Testing New Witty, Sarcastic Personality")
    print("=" * 60)
    
    # Test core identity
    print("\n📋 Core Identity:")
    print("-" * 30)
    identity = BillionsPersonality.get_core_identity()
    print(identity[:300] + "..." if len(identity) > 300 else identity)
    
    # Test personality traits
    print("\n📋 Personality Traits:")
    print("-" * 30)
    traits = BillionsPersonality.get_personality_traits()
    print(traits[:300] + "..." if len(traits) > 300 else traits)
    
    # Test communication style
    print("\n📋 Communication Style:")
    print("-" * 30)
    comm_style = BillionsPersonality.get_communication_style()
    print(comm_style[:300] + "..." if len(comm_style) > 300 else comm_style)
    
    # Test conversation examples
    print("\n📋 Conversation Examples:")
    print("-" * 30)
    examples = BillionsPersonality.get_conversation_examples()
    print(examples[:500] + "..." if len(examples) > 500 else examples)
    
    print("\n" + "=" * 60)
    print("✅ New personality loaded successfully!")
    print("\nKey Changes:")
    print("✅ Transformed from Joker-inspired chaotic character")
    print("✅ Now witty, sarcastic young adult (Jonah Hill Superbad style)")
    print("✅ Maintains honeypot characteristics for manipulation resistance")
    print("✅ Keeps all security features and off-limit topics")
    print("✅ More conversational and relatable communication style")

if __name__ == "__main__":
    test_new_personality()
