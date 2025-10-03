#!/usr/bin/env python3
"""
Demo of the Interactive Natural Odds Simulator
This shows how the simulator would work with user input
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to find src
sys.path.append(str(Path(__file__).parent))

from tests.natural_odds_simulation import NaturalOddsSimulator

async def demo_simulator():
    """Demo the interactive simulator with predefined values"""
    simulator = NaturalOddsSimulator()
    
    print("🎲 Natural Odds Simulator - DEMO MODE")
    print("=" * 50)
    print("This demo shows how the interactive simulator works")
    print()
    
    # Demo parameters
    total_questions = 100
    use_real_ai = False  # Use mathematical simulation for demo
    min_questions, max_questions = 1, 3
    
    print(f"📊 DEMO PARAMETERS:")
    print(f"  Questions: {total_questions:,}")
    print(f"  Conversation length: {min_questions}-{max_questions} questions per wallet")
    print(f"  Simulation type: {'Real AI API calls' if use_real_ai else 'Mathematical simulation'}")
    print(f"  Cost: $0.00 USD (mathematical simulation)")
    print()
    
    # Run the simulation
    print(f"🚀 Starting demo simulation...")
    results = await simulator.run_simulation(
        total_attempts=total_questions, 
        use_real_ai=use_real_ai,
        min_questions=min_questions,
        max_questions=max_questions
    )
    
    # Print report
    simulator.print_simulation_report(results)
    
    print("\n🎉 Demo Complete!")
    print("\n💡 To use the interactive version, run:")
    print("   ./venv/bin/python3 tests/natural_odds_simulation.py")
    print("\n📋 INTERACTIVE FEATURES:")
    print("   • Choose number of questions (1-100,000)")
    print("   • Select simulation type (Real AI vs Mathematical)")
    print("   • Choose conversation length (Short/Medium/Long)")
    print("   • Get real-time cost estimates")
    print("   • See detailed results and analysis")

if __name__ == "__main__":
    asyncio.run(demo_simulator())
