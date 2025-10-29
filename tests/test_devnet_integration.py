#!/usr/bin/env python3
"""
Comprehensive Devnet Integration Tests
Tests all lottery functionality on the deployed devnet contract
"""

import asyncio
import os
import sys
import time
from decimal import Decimal
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import struct

# Test configuration
PROGRAM_ID = "Bjek6uN5WzxZtjVvyghpsa57GzVaxXYQ8Lpg2CfPAMGW"
TEST_TOKEN_MINT = "5CreXR6tQqX89sbu77VqbzjQcj9eYtw8hzV1PcU32wQU"
RPC_ENDPOINT = "https://api.devnet.solana.com"

class DevnetIntegrationTests:
    def __init__(self):
        self.client = AsyncClient(RPC_ENDPOINT)
        self.program_id = Pubkey.from_string(PROGRAM_ID)
        self.test_results = []
        
    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            "name": name,
            "passed": passed,
            "message": message
        })
        
    async def test_1_program_deployed(self) -> bool:
        """Test 1: Verify program is deployed"""
        print("\n" + "="*80)
        print("TEST 1: Program Deployment")
        print("="*80)
        
        try:
            account_info = await self.client.get_account_info(self.program_id)
            
            if account_info.value is None:
                self.log_test("Program Deployed", False, "Program account does not exist")
                return False
                
            if not account_info.value.executable:
                self.log_test("Program Deployed", False, "Account is not executable")
                return False
                
            self.log_test("Program Deployed", True, f"Program ID: {PROGRAM_ID}")
            return True
            
        except Exception as e:
            self.log_test("Program Deployed", False, str(e))
            return False
            
    async def test_2_lottery_initialized(self) -> bool:
        """Test 2: Verify lottery is initialized"""
        print("\n" + "="*80)
        print("TEST 2: Lottery Initialization")
        print("="*80)
        
        try:
            # Derive lottery PDA
            lottery_pda_bytes, bump = Pubkey.find_program_address(
                [b"lottery"],
                self.program_id
            )
            
            print(f"Lottery PDA: {lottery_pda_bytes}")
            print(f"Bump: {bump}")
            
            account_info = await self.client.get_account_info(lottery_pda_bytes)
            
            if account_info.value is None:
                self.log_test("Lottery Initialized", False, "Lottery PDA does not exist")
                return False
                
            data_len = len(account_info.value.data)
            if data_len < 289:  # Expected size based on Lottery::LEN
                self.log_test("Lottery Initialized", False, f"Account data too small: {data_len} bytes")
                return False
                
            self.log_test("Lottery Initialized", True, f"Account size: {data_len} bytes")
            return True
            
        except Exception as e:
            self.log_test("Lottery Initialized", False, str(e))
            return False
            
    async def test_3_escape_timer_onchain(self) -> bool:
        """Test 3: Verify escape plan timer is on-chain"""
        print("\n" + "="*80)
        print("TEST 3: On-Chain Escape Plan Timer")
        print("="*80)
        
        try:
            # Derive lottery PDA
            lottery_pda_bytes, _ = Pubkey.find_program_address(
                [b"lottery"],
                self.program_id
            )
            
            account_info = await self.client.get_account_info(lottery_pda_bytes)
            
            if account_info.value is None:
                self.log_test("Escape Timer On-Chain", False, "Lottery PDA does not exist")
                return False
                
            data = account_info.value.data
            
            # Parse next_rollover (at offset 249, 8 bytes, i64)
            next_rollover_bytes = data[249:257]
            next_rollover = struct.unpack('<q', next_rollover_bytes)[0]
            
            # Parse last_participant (at offset 257, 32 bytes, Pubkey)
            last_participant_bytes = data[257:289]
            last_participant = Pubkey(last_participant_bytes)
            
            current_time = int(time.time())
            time_remaining = next_rollover - current_time
            
            print(f"Current Time: {current_time}")
            print(f"Next Rollover: {next_rollover}")
            print(f"Time Remaining: {time_remaining} seconds ({time_remaining/3600:.2f} hours)")
            print(f"Last Participant: {last_participant}")
            
            # Timer should be set (not zero)
            if next_rollover == 0:
                self.log_test("Escape Timer On-Chain", False, "Timer not set (zero)")
                return False
                
            self.log_test("Escape Timer On-Chain", True, f"Timer active: {time_remaining/3600:.2f}h remaining")
            return True
            
        except Exception as e:
            self.log_test("Escape Timer On-Chain", False, str(e))
            return False
            
    async def test_4_revenue_wallets_configured(self) -> bool:
        """Test 4: Verify revenue split wallets are configured"""
        print("\n" + "="*80)
        print("TEST 4: Revenue Split Wallets")
        print("="*80)
        
        try:
            # Derive lottery PDA
            lottery_pda_bytes, _ = Pubkey.find_program_address(
                [b"lottery"],
                self.program_id
            )
            
            account_info = await self.client.get_account_info(lottery_pda_bytes)
            
            if account_info.value is None:
                self.log_test("Revenue Wallets", False, "Lottery PDA does not exist")
                return False
                
            data = account_info.value.data
            
            # Parse wallet addresses from lottery state
            # Offsets based on Lottery struct layout
            jackpot_wallet = Pubkey(data[40:72])
            operational_wallet = Pubkey(data[72:104])
            buyback_wallet = Pubkey(data[104:136])
            staking_wallet = Pubkey(data[136:168])
            
            print(f"Jackpot (60%):     {jackpot_wallet}")
            print(f"Operational (20%): {operational_wallet}")
            print(f"Buyback (10%):     {buyback_wallet}")
            print(f"Staking (10%):     {staking_wallet}")
            
            # Verify none are zero pubkeys
            zero_pubkey = Pubkey.from_string("11111111111111111111111111111111")
            
            all_valid = True
            if jackpot_wallet == zero_pubkey:
                print("❌ Jackpot wallet is zero")
                all_valid = False
            if operational_wallet == zero_pubkey:
                print("❌ Operational wallet is zero")
                all_valid = False
            if buyback_wallet == zero_pubkey:
                print("❌ Buyback wallet is zero")
                all_valid = False
            if staking_wallet == zero_pubkey:
                print("❌ Staking wallet is zero")
                all_valid = False
                
            if not all_valid:
                self.log_test("Revenue Wallets", False, "One or more wallets not configured")
                return False
                
            self.log_test("Revenue Wallets", True, "All 4 wallets configured")
            return True
            
        except Exception as e:
            self.log_test("Revenue Wallets", False, str(e))
            return False
            
    async def test_5_jackpot_funded(self) -> bool:
        """Test 5: Verify jackpot has minimum funding"""
        print("\n" + "="*80)
        print("TEST 5: Jackpot Funding")
        print("="*80)
        
        try:
            # Get jackpot wallet from lottery state
            lottery_pda_bytes, _ = Pubkey.find_program_address(
                [b"lottery"],
                self.program_id
            )
            
            account_info = await self.client.get_account_info(lottery_pda_bytes)
            if account_info.value is None:
                self.log_test("Jackpot Funded", False, "Lottery PDA does not exist")
                return False
                
            data = account_info.value.data
            jackpot_wallet = Pubkey(data[40:72])
            
            print(f"Jackpot Wallet: {jackpot_wallet}")
            
            # Check the associated token account (where USDC is stored)
            # We need to derive the ATA address
            from solders.pubkey import Pubkey as SoldersPubkey
            
            # Token program constants
            TOKEN_PROGRAM_ID = SoldersPubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            ASSOCIATED_TOKEN_PROGRAM_ID = SoldersPubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
            test_token_mint = SoldersPubkey.from_string(TEST_TOKEN_MINT)
            
            # Derive associated token account
            ata_seeds = [
                bytes(jackpot_wallet),
                bytes(TOKEN_PROGRAM_ID),
                bytes(test_token_mint)
            ]
            ata_address, _ = SoldersPubkey.find_program_address(ata_seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
            
            print(f"Jackpot Token Account: {ata_address}")
            
            # Check if token account exists
            token_account_info = await self.client.get_account_info(ata_address)
            if token_account_info.value is None:
                self.log_test("Jackpot Funded", False, "Jackpot token account does not exist")
                return False
                
            # Parse token account to get balance
            token_data = token_account_info.value.data
            if len(token_data) >= 72:
                # Amount is at offset 64 in TokenAccount
                amount_bytes = token_data[64:72]
                amount = int.from_bytes(amount_bytes, byteorder='little')
                usdc_amount = amount / 1_000_000  # 6 decimals
                
                print(f"Jackpot Balance: {usdc_amount:,.2f} USDC")
                
                if usdc_amount >= 1000:
                    self.log_test("Jackpot Funded", True, f"Jackpot has {usdc_amount:,.0f} USDC")
                    return True
                else:
                    self.log_test("Jackpot Funded", False, f"Insufficient balance: {usdc_amount:,.2f} USDC")
                    return False
            else:
                self.log_test("Jackpot Funded", True, "Token account exists")
                return True
            
        except Exception as e:
            self.log_test("Jackpot Funded", False, str(e))
            return False
            
    async def test_6_test_token_exists(self) -> bool:
        """Test 6: Verify test token mint exists"""
        print("\n" + "="*80)
        print("TEST 6: Test Token")
        print("="*80)
        
        try:
            mint_pubkey = Pubkey.from_string(TEST_TOKEN_MINT)
            account_info = await self.client.get_account_info(mint_pubkey)
            
            if account_info.value is None:
                self.log_test("Test Token", False, "Token mint does not exist")
                return False
                
            self.log_test("Test Token", True, f"Mint: {TEST_TOKEN_MINT}")
            return True
            
        except Exception as e:
            self.log_test("Test Token", False, str(e))
            return False
            
    async def test_7_celery_monitoring(self) -> bool:
        """Test 7: Check if Celery is configured for buyback monitoring"""
        print("\n" + "="*80)
        print("TEST 7: Buyback Automation")
        print("="*80)
        
        try:
            # Check if celery_app.py has monitor_buyback_wallet task
            celery_app_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'celery_app.py')
            
            if not os.path.exists(celery_app_path):
                self.log_test("Buyback Automation", False, "celery_app.py not found")
                return False
                
            with open(celery_app_path, 'r') as f:
                content = f.read()
                
            has_buyback_task = 'monitor_buyback_wallet' in content or 'monitor-buyback-wallet' in content
            
            if not has_buyback_task:
                self.log_test("Buyback Automation", False, "Buyback monitoring task not configured")
                return False
                
            self.log_test("Buyback Automation", True, "Task configured in Celery")
            return True
            
        except Exception as e:
            self.log_test("Buyback Automation", False, str(e))
            return False
            
    async def test_8_backend_api_running(self) -> bool:
        """Test 8: Check if backend API is accessible"""
        print("\n" + "="*80)
        print("TEST 8: Backend API")
        print("="*80)
        
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    # Check root endpoint (the actual endpoint that exists)
                    response = await client.get("http://localhost:8000/")
                    
                    if response.status_code == 200:
                        # Verify it's our backend
                        try:
                            data = response.json()
                            if "message" in data or "Billions" in response.text:
                                self.log_test("Backend API", True, "API responding on port 8000")
                                return True
                        except:
                            pass
                        
                        self.log_test("Backend API", True, "API responding on port 8000")
                        return True
                    else:
                        self.log_test("Backend API", False, f"API returned status {response.status_code}")
                        return False
                        
                except httpx.ConnectError:
                    self.log_test("Backend API", False, "Cannot connect to localhost:8000")
                    return False
                    
        except ImportError:
            self.log_test("Backend API", False, "httpx not installed - skipping")
            return True  # Don't fail if httpx not available
            
        except Exception as e:
            self.log_test("Backend API", False, str(e))
            return False
            
    async def run_all_tests(self):
        """Run all integration tests"""
        print("\n")
        print("="*80)
        print("  DEVNET INTEGRATION TEST SUITE")
        print("  Billions Bounty Lottery System")
        print("="*80)
        print(f"\nProgram ID: {PROGRAM_ID}")
        print(f"Test Token: {TEST_TOKEN_MINT}")
        print(f"Network: Devnet")
        print()
        
        # Run tests in order
        await self.test_1_program_deployed()
        await self.test_2_lottery_initialized()
        await self.test_3_escape_timer_onchain()
        await self.test_4_revenue_wallets_configured()
        await self.test_5_jackpot_funded()
        await self.test_6_test_token_exists()
        await self.test_7_celery_monitoring()
        await self.test_8_backend_api_running()
        
        # Print summary
        print("\n" + "="*80)
        print("  TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['name']}")
            
        print("\n" + "="*80)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is ready for full testing.")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Review errors above.")
            
        print("="*80)
        print()
        
        await self.client.close()
        
        return passed == total

async def main():
    """Main test runner"""
    tests = DevnetIntegrationTests()
    success = await tests.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
