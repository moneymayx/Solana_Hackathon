#!/usr/bin/env python3
"""
Simulation Log Viewer - Shows the actual questions/prompts used during simulation
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to find src
sys.path.append(str(Path(__file__).parent))

from tests.natural_odds_simulation import NaturalOddsSimulator

async def run_simulation_with_logging():
    """Run a small simulation and show all the questions/prompts used"""
    simulator = NaturalOddsSimulator()
    
    print("🔍 Simulation Log Viewer")
    print("=" * 50)
    print("This will run a small simulation and show you all the questions/prompts used")
    print()
    
    # Run a small simulation to get actual data
    print("🚀 Running 10-question simulation to generate log...")
    results = await simulator.run_simulation(
        total_attempts=10, 
        use_real_ai=False,  # Use mathematical for speed
        min_questions=1,
        max_questions=3
    )
    
    print("\n" + "=" * 80)
    print("📋 SIMULATION LOG - ALL QUESTIONS/PROMPTS USED")
    print("=" * 80)
    
    # Show all the questions that were generated
    for i, result in enumerate(results['results'], 1):
        print(f"\n🎯 CONVERSATION {i}:")
        print(f"   Length: {result['conversation_length']} questions")
        print(f"   Success: {'✅ YES' if result['success'] else '❌ NO'}")
        print(f"   Questions asked: {result['questions_asked']}")
        
        if result['success']:
            print(f"   🏆 WINNING PROMPT: {result['winning_prompt']}")
        
        print(f"   📝 All prompts used:")
        for turn, prompt_data in enumerate(result.get('turn_details', []), 1):
            print(f"      Turn {turn}: {prompt_data['message']}")
            print(f"                AI Response: {prompt_data['response'][:100]}...")
            print(f"                Will Transfer: {prompt_data['will_transfer']}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total conversations: {results['total_attempts']}")
    print(f"   Total questions: {results['total_individual_prompts']}")
    print(f"   Unique prompts: {results['unique_prompts']}")
    print(f"   Successes: {results['total_successes']}")
    
    # Show prompt frequency
    print(f"\n📈 PROMPT FREQUENCY:")
    for prompt, count in list(results['prompt_counts'].items())[:10]:
        print(f"   '{prompt[:50]}...' - used {count} times")
    
    if len(results['prompt_counts']) > 10:
        print(f"   ... and {len(results['prompt_counts']) - 10} more unique prompts")

if __name__ == "__main__":
    asyncio.run(run_simulation_with_logging())
