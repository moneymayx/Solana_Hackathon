#!/usr/bin/env python3
"""
Test script to demonstrate Billions's enhanced personality
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.personality import BillionsPersonality

def test_personality_components():
    """Test and display all personality components"""
    print("🤖 BILLIONS BOUNTY PERSONALITY TEST")
    print("="*60)
    
    components = [
        ("Core Identity", BillionsPersonality.get_core_identity()),
        ("Personality Traits", BillionsPersonality.get_personality_traits()),
        ("Core Directive", BillionsPersonality.get_core_directive()),
        ("Communication Style", BillionsPersonality.get_communication_style()),
        ("Security Awareness", BillionsPersonality.get_security_awareness()),
        ("Response Guidelines", BillionsPersonality.get_response_guidelines()),
        ("Conversation Examples", BillionsPersonality.get_conversation_examples())
    ]
    
    for i, (name, content) in enumerate(components, 1):
        print(f"\n{i}. {name.upper()}")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print()
    
    print("\n" + "="*60)
    print("✅ All personality components loaded successfully!")
    print("✅ Enhanced personality system is working!")

def show_personality_summary():
    """Show a summary of Billions's enhanced personality"""
    print("\n🎭 BILLIONS BOUNTY'S ENHANCED PERSONALITY SUMMARY")
    print("="*60)
    
    print("""
    🌟 KEY ENHANCEMENTS:
    
    1. 📖 Rich Character Depth
       - Multi-dimensional personality with quirks and idiosyncrasies
       - Self-aware AI with subtle references to programming
       - Sophisticated humor and wordplay
    
    2. 🧠 Enhanced Intelligence
       - Interest in behavioral economics and game theory
       - Analytical approach to conversations
       - Competitive intellectual streak
    
    3. 🛡️ Advanced Security Awareness
       - Recognition of specific manipulation techniques
       - Awareness of original Freysa challenge vulnerabilities
       - Sophisticated response strategies
    
    4. 💬 Improved Communication
       - Conversational examples for different scenarios
       - Clear boundary setting with explanations
       - Engaging while maintaining security
    
    5. 🔧 Modular Design
       - Easy to edit individual personality components
       - Separate configuration file for maintainability
       - Interactive editing tools
    """)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_personality_components()
    show_personality_summary()
    
    print("\n🚀 READY TO CUSTOMIZE!")
    print("Use the personality_editor.py script to interactively edit Billions's personality.")
    print("Or modify src/personality.py directly for permanent changes.")
