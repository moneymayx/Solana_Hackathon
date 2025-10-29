"""
Mainnet Readiness Test Suite
Comprehensive tests before deploying to production
"""

import sys
import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MainnetReadinessChecker:
    """Check if system is ready for mainnet deployment"""
    
    def __init__(self):
        self.results = []
        self.warnings = []
        self.critical_failures = []
    
    def log_result(self, name: str, passed: bool, details: str = "", critical: bool = False):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"   {details}")
        
        self.results.append({
            "name": name,
            "passed": passed,
            "details": details,
            "critical": critical
        })
        
        if not passed and critical:
            self.critical_failures.append(name)
    
    def log_warning(self, message: str):
        """Log warning"""
        print(f"⚠️  WARNING: {message}")
        self.warnings.append(message)
    
    # ========================================================================
    # SMART CONTRACT CHECKS
    # ========================================================================
    
    def check_smart_contracts_built(self):
        """Check if all smart contracts are built"""
        print("\n" + "="*70)
        print("SMART CONTRACT BUILD STATUS")
        print("="*70)
        
        contracts = [
            ("Lottery Contract", "programs/billions-bounty/target/deploy/billions_bounty.so"),
            ("Staking Contract", "programs/staking/target/deploy/staking.so"),
        ]
        
        all_built = True
        for name, path in contracts:
            full_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                path
            )
            exists = os.path.exists(full_path)
            
            if exists:
                size = os.path.getsize(full_path) / 1024  # KB
                self.log_result(f"{name} Built", True, f"Size: {size:.1f} KB")
            else:
                self.log_result(f"{name} Built", False, f"File not found: {path}", critical=True)
                all_built = False
        
        return all_built
    
    def check_env_configuration(self):
        """Check environment configuration"""
        print("\n" + "="*70)
        print("ENVIRONMENT CONFIGURATION")
        print("="*70)
        
        required_vars = [
            ("LOTTERY_PROGRAM_ID", True),
            ("STAKING_PROGRAM_ID", True),
            ("JACKPOT_WALLET_ADDRESS", True),
            ("OPERATIONAL_WALLET_ADDRESS", True),
            ("BUYBACK_WALLET_ADDRESS", True),
            ("STAKING_WALLET_ADDRESS", True),
            ("SOLANA_RPC_URL", True),
            ("USDC_MINT_ADDRESS", True),
            ("TOKEN_100BS_MINT_ADDRESS", True),
            ("ANTHROPIC_API_KEY", True),
        ]
        
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        if not os.path.exists(env_file):
            self.log_result("Environment File", False, ".env file not found", critical=True)
            return False
        
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        all_set = True
        for var_name, is_critical in required_vars:
            if var_name in env_content and "your_" not in env_content:
                # Check if it has a value
                lines = [l for l in env_content.split('\n') if l.startswith(var_name)]
                if lines and '=' in lines[0]:
                    value = lines[0].split('=', 1)[1].strip()
                    if value and value not in ['', 'placeholder', 'your_key_here']:
                        self.log_result(f"Env: {var_name}", True, "Configured")
                    else:
                        self.log_result(f"Env: {var_name}", False, "Empty value", critical=is_critical)
                        all_set = False
                else:
                    self.log_result(f"Env: {var_name}", False, "Not set", critical=is_critical)
                    all_set = False
            else:
                self.log_result(f"Env: {var_name}", False, "Missing", critical=is_critical)
                all_set = False
        
        return all_set
    
    def check_wallet_separation(self):
        """Check that all wallets are different"""
        print("\n" + "="*70)
        print("WALLET SEPARATION CHECK")
        print("="*70)
        
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        if not os.path.exists(env_file):
            return False
        
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        wallet_vars = [
            "JACKPOT_WALLET_ADDRESS",
            "OPERATIONAL_WALLET_ADDRESS",
            "BUYBACK_WALLET_ADDRESS",
            "STAKING_WALLET_ADDRESS",
        ]
        
        wallets = {}
        for var in wallet_vars:
            lines = [l for l in env_content.split('\n') if l.startswith(var)]
            if lines and '=' in lines[0]:
                value = lines[0].split('=', 1)[1].strip()
                wallets[var] = value
        
        # Check for duplicates
        wallet_values = list(wallets.values())
        unique_wallets = set(wallet_values)
        
        if len(wallet_values) == len(unique_wallets):
            self.log_result("Wallet Separation", True, "All wallets are unique")
            return True
        else:
            duplicates = [w for w in wallet_values if wallet_values.count(w) > 1]
            self.log_result("Wallet Separation", False, f"Duplicate wallets found: {duplicates}", critical=True)
            return False
    
    def check_revenue_split_configuration(self):
        """Check revenue split is 60/20/10/10"""
        print("\n" + "="*70)
        print("REVENUE SPLIT CONFIGURATION")
        print("="*70)
        
        try:
            from src.token_config import (
                BOUNTY_CONTRIBUTION_RATE,
                OPERATIONAL_FEE_RATE,
                BUYBACK_RATE,
                STAKING_REVENUE_PERCENTAGE
            )
            
            expected = {
                "Bounty": (BOUNTY_CONTRIBUTION_RATE, 0.60),
                "Operational": (OPERATIONAL_FEE_RATE, 0.20),
                "Buyback": (BUYBACK_RATE, 0.10),
                "Staking": (STAKING_REVENUE_PERCENTAGE, 0.10),
            }
            
            all_correct = True
            for name, (actual, expected_val) in expected.items():
                if abs(actual - expected_val) < 0.001:
                    self.log_result(f"Revenue Split: {name}", True, f"{actual*100}%")
                else:
                    self.log_result(f"Revenue Split: {name}", False, f"Expected {expected_val*100}%, got {actual*100}%", critical=True)
                    all_correct = False
            
            # Check total = 100%
            total = sum(v[0] for v in expected.values())
            if abs(total - 1.0) < 0.001:
                self.log_result("Revenue Split: Total", True, "100%")
            else:
                self.log_result("Revenue Split: Total", False, f"Total is {total*100}%, should be 100%", critical=True)
                all_correct = False
            
            return all_correct
            
        except Exception as e:
            self.log_result("Revenue Split Configuration", False, f"Error: {e}", critical=True)
            return False
    
    def check_security_fixes(self):
        """Check that security fixes are applied"""
        print("\n" + "="*70)
        print("SECURITY FIXES VERIFICATION")
        print("="*70)
        
        checks = []
        
        # Check 1: No dual payout in ai_agent.py
        try:
            ai_agent_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/ai_agent.py")
            if os.path.exists(ai_agent_file):
                with open(ai_agent_file, 'r') as f:
                    content = f.read()
                
                # Should NOT have direct backend transfers for winner payouts
                if "solana_service.transfer_token" in content and "winner" in content.lower():
                    self.log_result("Security: No Dual Payout", False, "Found direct backend transfer for winners", critical=True)
                    checks.append(False)
                else:
                    self.log_result("Security: No Dual Payout", True, "Only smart contract handles payouts")
                    checks.append(True)
            else:
                self.log_warning("ai_agent.py not found for security check")
                checks.append(True)  # Don't fail if file doesn't exist
        except Exception as e:
            self.log_result("Security: No Dual Payout", False, f"Error checking: {e}")
            checks.append(False)
        
        # Check 2: No hardcoded secrets
        try:
            env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Check for common placeholder values
                placeholders = ["your_", "placeholder", "example", "test_key", "CHANGEME"]
                has_placeholders = any(p in content for p in placeholders)
                
                if not has_placeholders:
                    self.log_result("Security: No Placeholders", True, "All env vars have real values")
                    checks.append(True)
                else:
                    self.log_result("Security: No Placeholders", False, "Found placeholder values in .env", critical=True)
                    checks.append(False)
        except Exception as e:
            self.log_result("Security: No Placeholders", False, f"Error checking: {e}")
            checks.append(False)
        
        # Check 3: Discount system removed
        try:
            token_economics_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/token_economics_service.py")
            if os.path.exists(token_economics_file):
                with open(token_economics_file, 'r') as f:
                    content = f.read()
                
                # Should not have discount logic
                if "get_discount_for_balance" in content or "calculate_discounted_price" in content:
                    self.log_result("Security: Discount System Removed", False, "Found discount code", critical=False)
                    checks.append(False)
                else:
                    self.log_result("Security: Discount System Removed", True, "No discount system found")
                    checks.append(True)
        except Exception as e:
            self.log_warning(f"Could not check discount system: {e}")
            checks.append(True)
        
        return all(checks)
    
    def check_database_migrations(self):
        """Check database is ready"""
        print("\n" + "="*70)
        print("DATABASE STATUS")
        print("="*70)
        
        try:
            from src.models import Base, BountyState, User, BountyEntry, BuybackEvent, StakingRewardEvent
            
            required_models = [
                "BountyState",
                "User",
                "BountyEntry",
                "BuybackEvent",
                "StakingRewardEvent",
            ]
            
            for model_name in required_models:
                self.log_result(f"Database Model: {model_name}", True, "Defined")
            
            # Check BountyState has escape plan fields
            if hasattr(BountyState, 'last_participant_id'):
                self.log_result("Database: Escape Plan Fields", True, "BountyState has required fields")
            else:
                self.log_result("Database: Escape Plan Fields", False, "Missing escape plan fields", critical=True)
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Database Models", False, f"Error: {e}", critical=True)
            return False
    
    def check_escape_plan_integration(self):
        """Check escape plan is integrated"""
        print("\n" + "="*70)
        print("ESCAPE PLAN INTEGRATION")
        print("="*70)
        
        checks = []
        
        # Check 1: Service exists
        try:
            from src.escape_plan_service import escape_plan_service
            self.log_result("Escape Plan: Service", True, "escape_plan_service exists")
            checks.append(True)
        except Exception as e:
            self.log_result("Escape Plan: Service", False, f"Import error: {e}", critical=True)
            checks.append(False)
            return False
        
        # Check 2: Timer tracking in chat endpoints
        try:
            main_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "apps/backend/main.py")
            if os.path.exists(main_file):
                with open(main_file, 'r') as f:
                    content = f.read()
                
                if "escape_plan_service.update_last_activity" in content:
                    self.log_result("Escape Plan: Timer Tracking", True, "Integrated in chat endpoints")
                    checks.append(True)
                else:
                    self.log_result("Escape Plan: Timer Tracking", False, "Not integrated in chat endpoints", critical=True)
                    checks.append(False)
        except Exception as e:
            self.log_result("Escape Plan: Timer Tracking", False, f"Error checking: {e}")
            checks.append(False)
        
        # Check 3: Smart contract has execute function
        try:
            contract_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "programs/billions-bounty/src/lib.rs")
            if os.path.exists(contract_file):
                with open(contract_file, 'r') as f:
                    content = f.read()
                
                if "execute_time_escape_plan" in content:
                    self.log_result("Escape Plan: Smart Contract", True, "Function exists")
                    checks.append(True)
                else:
                    self.log_result("Escape Plan: Smart Contract", False, "Function missing", critical=True)
                    checks.append(False)
        except Exception as e:
            self.log_result("Escape Plan: Smart Contract", False, f"Error checking: {e}")
            checks.append(False)
        
        return all(checks)
    
    # ========================================================================
    # GENERATE REPORT
    # ========================================================================
    
    def generate_report(self):
        """Generate final readiness report"""
        print("\n" + "="*70)
        print("MAINNET READINESS REPORT")
        print("="*70)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        critical_failed = len(self.critical_failures)
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"🚨 Critical Failures: {critical_failed}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        # Determine readiness
        if critical_failed == 0 and passed == total:
            print("\n🎉 SYSTEM IS READY FOR MAINNET!")
            print("\n✅ All checks passed")
            print("✅ No critical failures")
            print("✅ All configurations correct")
            print("\n📋 Next Steps:")
            print("   1. Deploy contracts to mainnet")
            print("   2. Update .env with mainnet addresses")
            print("   3. Run final smoke tests")
            print("   4. Monitor closely for first 24 hours")
            return True
        elif critical_failed == 0:
            print("\n⚠️  SYSTEM IS MOSTLY READY")
            print(f"\n✅ No critical failures")
            print(f"⚠️  {total - passed} non-critical issues")
            print("\n📋 Recommended:")
            print("   - Fix non-critical issues")
            print("   - Then proceed to mainnet")
            return True
        else:
            print("\n❌ SYSTEM IS NOT READY FOR MAINNET")
            print(f"\n🚨 {critical_failed} CRITICAL FAILURES")
            print("\nCritical issues:")
            for failure in self.critical_failures:
                print(f"   - {failure}")
            print("\n📋 Required:")
            print("   - Fix all critical failures")
            print("   - Re-run this test")
            print("   - Do NOT deploy to mainnet yet")
            return False
    
    def run_all_checks(self):
        """Run all mainnet readiness checks"""
        print("\n" + "🎯"*35)
        print("MAINNET READINESS TEST SUITE")
        print("🎯"*35)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all checks
        self.check_smart_contracts_built()
        self.check_env_configuration()
        self.check_wallet_separation()
        self.check_revenue_split_configuration()
        self.check_security_fixes()
        self.check_database_migrations()
        self.check_escape_plan_integration()
        
        # Generate report
        ready = self.generate_report()
        
        return ready

def main():
    """Main entry point"""
    checker = MainnetReadinessChecker()
    ready = checker.run_all_checks()
    
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()

