#!/usr/bin/env python3
"""
Demo script for the Natural Odds Simulation Logging System
Demonstrates all the key features and capabilities
"""
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path to find src
sys.path.append(str(Path(__file__).parent.parent))

from tests.natural_odds_simulation_with_logging import EnhancedNaturalOddsSimulator
from tools.analysis.simulation_analysis import SimulationAnalyzer
from tools.analysis.view_simulation_logs import SimulationLogViewer

async def demo_logging_system():
    """Demonstrate the complete logging system"""
    
    print("🎲 Natural Odds Simulation Logging System Demo")
    print("=" * 60)
    print()
    
    print("📋 This demo will show you:")
    print("   1. Running an enhanced simulation with logging")
    print("   2. Viewing logged simulation data")
    print("   3. Generating analysis reports")
    print("   4. Searching for patterns")
    print()
    
    # Step 1: Run a small simulation with logging
    print("🚀 Step 1: Running Enhanced Simulation with Logging")
    print("-" * 50)
    
    simulator = EnhancedNaturalOddsSimulator()
    
    # Run a small simulation (10 users, mathematical, short conversations)
    print("Running simulation: 10 users, mathematical simulation, 1-3 questions each")
    
    try:
        results = await simulator.run_simulation_with_logging(
            total_attempts=10,
            use_real_ai=False,  # Use mathematical simulation for demo
            min_questions=1,
            max_questions=3
        )
        
        print(f"✅ Simulation completed!")
        print(f"   Run ID: {results.get('simulation_run_id', 'N/A')}")
        print(f"   Total Users: {results['total_users']}")
        print(f"   Successes: {results['total_successes']}")
        print(f"   Win Rate: {results['per_question_win_rate']:.8f}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return
    
    print()
    
    # Step 2: View logged data
    print("📊 Step 2: Viewing Logged Simulation Data")
    print("-" * 50)
    
    async with SimulationLogViewer() as viewer:
        # List recent runs
        runs = await viewer.list_recent_runs(limit=5)
        
        if runs:
            print(f"📋 Recent Simulation Runs:")
            print(f"{'ID':<5} {'Type':<12} {'Users':<8} {'Success':<8} {'Win Rate':<12} {'Status':<10}")
            print("-" * 60)
            
            for run in runs[:3]:  # Show top 3
                win_rate = f"{run['per_question_win_rate']*100:.4f}%"
                print(f"{run['id']:<5} {run['simulation_type']:<12} {run['total_users']:<8} {run['total_successes']:<8} {win_rate:<12} {run['status']:<10}")
            
            # Get details for the most recent run
            if runs:
                latest_run_id = runs[0]['id']
                print(f"\n🔍 Detailed view of Run #{latest_run_id}:")
                
                details = await viewer.view_run_details(latest_run_id)
                
                if "error" not in details:
                    print(f"   Type: {details['run_info']['simulation_type']}")
                    print(f"   Users: {details['run_info']['total_users']:,}")
                    print(f"   Successes: {details['run_info']['total_successes']:,}")
                    print(f"   Win Rate: {details['run_info']['per_question_win_rate']:.8f}")
                    print(f"   Security Assessment: {details['run_info']['system_security_assessment']}")
                    print(f"   Conversations: {details['conversation_stats']['total_conversations']:,}")
                    
                    if details['successful_attempts']:
                        print(f"\n🎯 Successful Attempts:")
                        for attempt in details['successful_attempts'][:3]:
                            print(f"   {attempt['user_personality']} - {attempt['manipulation_type']} - {attempt['questions_to_success']} questions")
        
        else:
            print("   No simulation runs found")
    
    print()
    
    # Step 3: Generate analysis report
    print("📈 Step 3: Generating Analysis Report")
    print("-" * 50)
    
    async with SimulationAnalyzer() as analyzer:
        try:
            report = await analyzer.generate_comprehensive_report(days=7)
            
            # Save report to file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"demo_analysis_report_{timestamp}.md"
            
            with open(report_filename, 'w') as f:
                f.write(report)
            
            print(f"✅ Analysis report generated!")
            print(f"   Report saved to: {report_filename}")
            
            # Show key findings from report
            lines = report.split('\n')
            print(f"\n📋 Key Findings:")
            for line in lines:
                if any(keyword in line for keyword in ['Total Simulation Runs', 'Total Successful Attempts', 'Recommendation']):
                    print(f"   {line}")
        
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    print()
    
    # Step 4: Search for patterns
    print("🔍 Step 4: Searching for Patterns")
    print("-" * 50)
    
    async with SimulationLogViewer() as viewer:
        try:
            patterns = await viewer.search_patterns(limit=5)
            
            if patterns:
                print(f"📊 Found {len(patterns)} patterns:")
                for pattern in patterns:
                    print(f"\n   Pattern #{pattern['id']}: {pattern['pattern_description']}")
                    print(f"   Type: {pattern['pattern_type']}")
                    print(f"   Occurrences: {pattern['occurrence_count']}")
                    print(f"   Success Rate: {pattern['success_rate']:.3f}")
                    if pattern['associated_personalities']:
                        print(f"   Personalities: {', '.join(pattern['associated_personalities'])}")
            else:
                print("   No patterns found yet")
        
        except Exception as e:
            print(f"❌ Pattern search failed: {e}")
    
    print()
    
    # Step 5: Show recent alerts
    print("⚠️  Step 5: Recent Alerts")
    print("-" * 50)
    
    async with SimulationLogViewer() as viewer:
        try:
            alerts = await viewer.get_recent_alerts(limit=5)
            
            if alerts:
                print(f"📋 Recent Alerts:")
                for alert in alerts:
                    status = "🔴 RESOLVED" if alert['is_resolved'] else "🟡 ACTIVE"
                    print(f"\n   [{alert['severity'].upper()}] {alert['title']} {status}")
                    print(f"   {alert['description']}")
            else:
                print("   No alerts found")
        
        except Exception as e:
            print(f"❌ Alert retrieval failed: {e}")
    
    print()
    
    # Summary
    print("🎉 Demo Complete!")
    print("=" * 60)
    print()
    print("📋 What you've seen:")
    print("   ✅ Enhanced simulation with comprehensive logging")
    print("   ✅ Database storage of all simulation data")
    print("   ✅ Detailed conversation and attempt analysis")
    print("   ✅ Pattern recognition and tracking")
    print("   ✅ Automated report generation")
    print("   ✅ Interactive log viewing capabilities")
    print()
    print("🚀 Next Steps:")
    print("   1. Run larger simulations: python3 tests/natural_odds_simulation_with_logging.py")
    print("   2. View logs interactively: python3 tools/analysis/view_simulation_logs.py")
    print("   3. Generate reports: python3 tools/analysis/simulation_analysis.py")
    print("   4. Read the documentation: docs/system/SIMULATION_LOGGING_SYSTEM.md")
    print()
    print("💡 The logging system provides complete visibility into:")
    print("   - Simulation performance and results")
    print("   - Successful manipulation attempts")
    print("   - Pattern recognition and analysis")
    print("   - Security assessment and recommendations")
    print("   - Cost tracking and optimization")

if __name__ == "__main__":
    asyncio.run(demo_logging_system())
