#!/usr/bin/env python3
"""
Test script for winner tracking system
This script tests the winner tracking and wallet blacklisting functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db, create_tables
from src.winner_tracking_service import winner_tracking_service
from src.models import Winner, ConnectedWallet, WalletFundingSource
from sqlalchemy.ext.asyncio import AsyncSession

async def test_winner_tracking():
    """Test the winner tracking system"""
    print("🧪 Testing Winner Tracking System")
    print("=" * 50)
    
    # Create tables
    await create_tables()
    
    # Get database session
    async for session in get_db():
        try:
            # Clear existing data for clean test
            from src.models import Winner, ConnectedWallet, WalletFundingSource
            from sqlalchemy import text
            await session.execute(text("DELETE FROM connected_wallets"))
            await session.execute(text("DELETE FROM wallet_funding_sources")) 
            await session.execute(text("DELETE FROM winners"))
            await session.commit()
            print("   Database cleared for clean test")
            # Test 1: Check if tracking is initially inactive
            print("\n1️⃣ Testing initial state...")
            stats = await winner_tracking_service.get_winner_statistics(session)
            print(f"   Tracking active: {stats['tracking_active']}")
            print(f"   Total winners: {stats['total_winners']}")
            
            # Test 2: Manually activate tracking (for testing)
            print("\n2️⃣ Activating winner tracking...")
            await winner_tracking_service.activate_winner_tracking(session)
            stats = await winner_tracking_service.get_winner_statistics(session)
            print(f"   Tracking active: {stats['tracking_active']}")
            
            # Test 3: Record a test winner
            print("\n3️⃣ Recording test winner...")
            test_winner = await winner_tracking_service.record_winner(
                session=session,
                user_id=1,
                wallet_address="WinnerWallet123456789",
                prize_amount=1000.0,
                token="SOL",
                transaction_hash="test_tx_hash_123"
            )
            print(f"   Winner recorded: {test_winner.wallet_address}")
            print(f"   Prize amount: {test_winner.prize_amount} {test_winner.token}")
            
            # Test 4: Record funding sources
            print("\n4️⃣ Recording wallet funding sources...")
            await winner_tracking_service.record_wallet_funding(
                session, "WinnerWallet123456789", "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM", 500.0  # Binance (known exchange)
            )
            await winner_tracking_service.record_wallet_funding(
                session, "WinnerWallet123456789", "PersonalWallet111222333", 300.0  # Non-exchange
            )
            print("   Funding sources recorded (exchange + non-exchange)")
            
            # Test 5: Check if winner wallet is blacklisted
            print("\n5️⃣ Testing winner wallet blacklist...")
            blacklist_check = await winner_tracking_service.is_wallet_blacklisted(
                session, "WinnerWallet123456789"
            )
            print(f"   Blacklisted: {blacklist_check['blacklisted']}")
            print(f"   Reason: {blacklist_check['reason']}")
            print(f"   Type: {blacklist_check['type']}")
            
            # Test 6: Record a wallet funded by same EXCHANGE (should be allowed)
            print("\n6️⃣ Recording wallet with shared EXCHANGE funding source...")
            await winner_tracking_service.record_wallet_funding(
                session, "NewWallet987654321", "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM", 200.0  # Binance address
            )
            
            # Check if new wallet is blacklisted due to shared exchange funding (should NOT be blacklisted)
            blacklist_check2 = await winner_tracking_service.is_wallet_blacklisted(
                session, "NewWallet987654321"
            )
            print(f"   New wallet blacklisted: {blacklist_check2['blacklisted']}")
            print(f"   Reason: {blacklist_check2['reason']}")
            
            # Test 6b: Record a wallet funded by same NON-EXCHANGE source (should be blacklisted)
            print("\n6️⃣b Recording wallet with shared NON-EXCHANGE funding source...")
            await winner_tracking_service.record_wallet_funding(
                session, "SuspiciousWallet999888777", "PersonalWallet111222333", 100.0  # Non-exchange address
            )
            
            # Check if suspicious wallet is blacklisted due to shared non-exchange funding
            blacklist_check2b = await winner_tracking_service.is_wallet_blacklisted(
                session, "SuspiciousWallet999888777"
            )
            print(f"   Suspicious wallet blacklisted: {blacklist_check2b['blacklisted']}")
            print(f"   Reason: {blacklist_check2b['reason']}")
            
            # Test 7: Record a completely unrelated wallet
            print("\n7️⃣ Testing unrelated wallet...")
            await winner_tracking_service.record_wallet_funding(
                session, "CleanWallet555666777", "DifferentExchange999", 100.0
            )
            
            blacklist_check3 = await winner_tracking_service.is_wallet_blacklisted(
                session, "CleanWallet555666777"
            )
            print(f"   Clean wallet blacklisted: {blacklist_check3['blacklisted']}")
            print(f"   Reason: {blacklist_check3['reason']}")
            
            # Test 8: Get winner statistics
            print("\n8️⃣ Getting final statistics...")
            final_stats = await winner_tracking_service.get_winner_statistics(session)
            print(f"   Total winners: {final_stats['total_winners']}")
            print(f"   Total blacklisted wallets: {final_stats['total_blacklisted_wallets']}")
            print(f"   Total prize money: {final_stats['total_prize_money']}")
            
            # Test 9: Get winner list
            print("\n9️⃣ Getting winner list...")
            winners = await winner_tracking_service.get_winner_list(session)
            print(f"   Winners found: {len(winners)}")
            for winner in winners:
                print(f"   - {winner['wallet_address']}: {winner['prize_amount']} {winner['token']}")
            
            print("\n✅ Winner tracking system test completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        break  # Exit the async generator

async def test_wallet_verification():
    """Test wallet verification before connection"""
    print("\n🔍 Testing Wallet Verification")
    print("=" * 50)
    
    async for session in get_db():
        try:
            # Test wallet verification for different scenarios
            test_wallets = [
                "WinnerWallet123456789",  # Should be blacklisted
                "NewWallet987654321",     # Should be blacklisted (shared funding)
                "CleanWallet555666777",   # Should be allowed
                "FreshWallet111222333"    # Should be allowed
            ]
            
            for wallet in test_wallets:
                print(f"\n   Testing wallet: {wallet}")
                blacklist_status = await winner_tracking_service.is_wallet_blacklisted(session, wallet)
                print(f"   Blacklisted: {blacklist_status['blacklisted']}")
                print(f"   Reason: {blacklist_status['reason']}")
                
                if blacklist_status['blacklisted']:
                    print("   ❌ Wallet would be rejected")
                else:
                    print("   ✅ Wallet would be allowed")
            
            print("\n✅ Wallet verification test completed!")
            
        except Exception as e:
            print(f"\n❌ Wallet verification test failed: {e}")
            import traceback
            traceback.print_exc()
        
        break

if __name__ == "__main__":
    print("🚀 Starting Winner Tracking System Tests")
    print("=" * 60)
    
    # Run the tests
    asyncio.run(test_winner_tracking())
    asyncio.run(test_wallet_verification())
    
    print("\n🎉 All tests completed!")
    print("\nTo test in production:")
    print("1. First jackpot win will automatically activate tracking")
    print("2. All subsequent wallet connections will be verified")
    print("3. Use /api/winners/check-wallet to verify any wallet")
    print("4. Use /api/winners/stats to see tracking statistics")
