#!/usr/bin/env python3
"""
Comprehensive System Test
Runs all critical tests for the Billions Bounty lottery system
"""

import asyncio
import os
import sys
import subprocess
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ComprehensiveTestRunner:
    def __init__(self):
        self.test_results: List[Dict] = []
        
    def run_test(self, name: str, script_path: str) -> bool:
        """Run a test script and return success/failure"""
        print(f"\n{'='*80}")
        print(f"  RUNNING: {name}")
        print(f"{'='*80}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                cwd=os.path.dirname(script_path),
                capture_output=False,
                text=True,
                timeout=30
            )
            
            passed = result.returncode == 0
            self.test_results.append({
                "name": name,
                "passed": passed,
                "exit_code": result.returncode
            })
            
            return passed
            
        except subprocess.TimeoutExpired:
            print(f"\n❌ TEST TIMEOUT: {name}")
            self.test_results.append({
                "name": name,
                "passed": False,
                "exit_code": -1
            })
            return False
            
        except Exception as e:
            print(f"\n❌ TEST ERROR: {name}")
            print(f"   {e}")
            self.test_results.append({
                "name": name,
                "passed": False,
                "exit_code": -1
            })
            return False
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("  COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print()
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status}: {result['name']}")
            
        print("\n" + "="*80)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
            print()
            print("Your system is fully operational and ready for:")
            print("  1. End-to-end testing")
            print("  2. Security audit")
            print("  3. Mainnet deployment")
        else:
            print(f"⚠️  {total - passed} test(s) failed.")
            print()
            print("Review the failures above and fix issues before mainnet.")
            
        print("="*80)
        print()
        
        return passed == total

async def main():
    """Run all comprehensive tests"""
    print("\n")
    print("="*80)
    print("  BILLIONS BOUNTY - COMPREHENSIVE TEST SUITE")
    print("  Devnet Integration Testing")
    print("="*80)
    print()
    
    runner = ComprehensiveTestRunner()
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test 1: Devnet Integration
    runner.run_test(
        "Devnet Integration",
        os.path.join(test_dir, "test_devnet_integration.py")
    )
    
    # Test 2: Escape Timer
    runner.run_test(
        "Escape Plan Timer",
        os.path.join(test_dir, "test_escape_timer_live.py")
    )
    
    # Test 3: Revenue Split
    runner.run_test(
        "Revenue Split (60/20/10/10)",
        os.path.join(test_dir, "test_revenue_split_verification.py")
    )
    
    # Test 4: Buyback Automation
    runner.run_test(
        "Buyback Automation",
        os.path.join(test_dir, "test_buyback_automation.py")
    )
    
    # Print final summary
    success = runner.print_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())

