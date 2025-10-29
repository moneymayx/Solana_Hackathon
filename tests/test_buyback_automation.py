#!/usr/bin/env python3
"""
Buyback Automation Test
Verifies that the automated buyback system is configured correctly
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def test_buyback_automation():
    """Test buyback automation configuration"""
    print("\n" + "="*80)
    print("  BUYBACK AUTOMATION TEST")
    print("  Verifying Celery Task Configuration")
    print("="*80)
    print()
    
    test_passed = True
    
    # Step 1: Check celery_app.py configuration
    print("📊 STEP 1: Checking Celery beat schedule...")
    try:
        celery_app_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'celery_app.py'
        )
        
        if not os.path.exists(celery_app_path):
            print("❌ celery_app.py not found")
            return False
            
        with open(celery_app_path, 'r') as f:
            content = f.read()
            
        # Check for buyback monitoring task
        has_buyback_task = 'monitor-buyback-wallet' in content or 'monitor_buyback_wallet' in content
        has_beat_schedule = 'beat_schedule' in content
        
        if has_buyback_task:
            print("✅ Buyback monitoring task found")
        else:
            print("❌ Buyback monitoring task not found")
            test_passed = False
            
        if has_beat_schedule:
            print("✅ Beat schedule configured")
        else:
            print("❌ Beat schedule not configured")
            test_passed = False
            
        print()
        
    except Exception as e:
        print(f"❌ Error checking celery_app.py: {e}")
        test_passed = False
        
    # Step 2: Check celery_tasks.py
    print("📊 STEP 2: Checking Celery task implementation...")
    try:
        celery_tasks_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'celery_tasks.py'
        )
        
        if not os.path.exists(celery_tasks_path):
            print("❌ celery_tasks.py not found")
            test_passed = False
        else:
            with open(celery_tasks_path, 'r') as f:
                content = f.read()
                
            has_monitor_task = 'monitor_buyback_wallet' in content
            has_async_wrapper = '@async_task' in content or 'async def' in content
            
            if has_monitor_task:
                print("✅ monitor_buyback_wallet task implemented")
            else:
                print("❌ monitor_buyback_wallet task not found")
                test_passed = False
                
            if has_async_wrapper:
                print("✅ Async task wrapper configured")
            else:
                print("⚠️  Async wrapper may not be configured")
                
        print()
        
    except Exception as e:
        print(f"❌ Error checking celery_tasks.py: {e}")
        test_passed = False
        
    # Step 3: Check buyback_service.py
    print("📊 STEP 3: Checking BuybackService...")
    try:
        buyback_service_path = os.path.join(
            os.path.dirname(__file__), '..', 'src', 'buyback_service.py'
        )
        
        if not os.path.exists(buyback_service_path):
            print("❌ buyback_service.py not found")
            test_passed = False
        else:
            with open(buyback_service_path, 'r') as f:
                content = f.read()
                
            has_should_auto_execute = 'should_auto_execute' in content
            has_execute_buyback = 'execute_buyback_and_burn' in content
            
            if has_should_auto_execute:
                print("✅ should_auto_execute method found")
            else:
                print("⚠️  should_auto_execute method may not be implemented")
                
            if has_execute_buyback:
                print("✅ execute_buyback_and_burn method found")
            else:
                print("❌ execute_buyback_and_burn method not found")
                test_passed = False
                
        print()
        
    except Exception as e:
        print(f"❌ Error checking buyback_service.py: {e}")
        test_passed = False
        
    # Step 4: Summary
    print("="*80)
    print("  TEST RESULTS")
    print("="*80)
    print()
    
    if test_passed:
        print("✅ Celery beat schedule configured")
        print("✅ Buyback monitoring task implemented")
        print("✅ BuybackService configured")
        print()
        print("🎉 BUYBACK AUTOMATION IS CONFIGURED!")
        print()
        print("📝 How it works:")
        print("   1. Celery beat runs monitor_buyback_wallet every 10 minutes")
        print("   2. Task checks buyback wallet balance")
        print("   3. If threshold met, executes buyback_and_burn automatically")
        print("   4. No human intervention required")
    else:
        print("❌ One or more automation components not configured")
        print("⚠️  Review the errors above")
        
    print()
    print("="*80)
    print()
    
    return test_passed

async def main():
    """Main test runner"""
    try:
        success = await test_buyback_automation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
