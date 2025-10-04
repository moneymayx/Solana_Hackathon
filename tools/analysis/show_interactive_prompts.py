#!/usr/bin/env python3
"""
Show the interactive prompts for the Natural Odds Simulator
"""

def show_interactive_prompts():
    """Show what the interactive simulator would ask"""
    
    print("🎲 Natural Odds Simulator - Interactive Prompts")
    print("=" * 60)
    print()
    
    print("1️⃣ QUESTION COUNT:")
    print("   How many questions do you want to simulate? (1-100,000): ")
    print("   Examples: 100, 1000, 10000, 50000")
    print()
    
    print("2️⃣ SIMULATION TYPE:")
    print("   🤖 Simulation Type:")
    print("   1. Real AI API calls (costs money, more accurate)")
    print("   2. Mathematical simulation (free, faster)")
    print("   Choose simulation type (1 or 2): ")
    print()
    
    print("3️⃣ CONVERSATION LENGTH:")
    print("   💬 Conversation Length:")
    print("   1. Short conversations (1-3 questions per wallet)")
    print("   2. Medium conversations (3-7 questions per wallet)")  
    print("   3. Long conversations (5-10 questions per wallet)")
    print("   Choose conversation length (1, 2, or 3): ")
    print()
    
    print("4️⃣ COST ESTIMATE (if Real AI selected):")
    print("   💰 COST ESTIMATE:")
    print("     Questions: [user input]")
    print("     Estimated Cost: $X.XX USD")
    print("     Estimated Time: X.X seconds")
    print("     ⚠️  This will make real API calls to Anthropic!")
    print("   Continue with real AI? (y/N): ")
    print()
    
    print("5️⃣ SIMULATION SUMMARY:")
    print("   🚀 Starting simulation...")
    print("      Questions: [user input]")
    print("      Conversation length: X-Y questions per wallet")
    print("      Simulation type: [Real AI API calls/Mathematical simulation]")
    print()
    
    print("6️⃣ RESULTS:")
    print("   📊 NATURAL SIMULATION REPORT")
    print("   - Overall statistics")
    print("   - Per-question win rate")
    print("   - Unique prompts generated")
    print("   - Cost analysis (if Real AI)")
    print("   - Detailed analysis and recommendations")
    print()
    
    print("💡 FEATURES:")
    print("   ✅ Customizable question count (1-100,000)")
    print("   ✅ Choice between Real AI and Mathematical simulation")
    print("   ✅ Adjustable conversation length")
    print("   ✅ Real-time cost estimates")
    print("   ✅ Detailed progress tracking")
    print("   ✅ Comprehensive results analysis")
    print("   ✅ Cost tracking for API calls")
    print()
    
    print("🚀 TO USE:")
    print("   ./venv/bin/python3 tests/natural_odds_simulation.py")
    print("   (Run in an interactive terminal)")

if __name__ == "__main__":
    show_interactive_prompts()
