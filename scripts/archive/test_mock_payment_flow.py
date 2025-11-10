#!/usr/bin/env python3
"""
Comprehensive test script for mock payment flow
Tests all aspects of mock payment + devnet smart contract integration
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_WALLET = "Ega2R4wj89CMogco9r4HUvrGG4aNnXQD9aDYM6JcZr7G"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}🧪 TEST: {test_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def print_json(data):
    print(json.dumps(data, indent=2))

def test_backend_health():
    """Test 0: Backend is running"""
    print_test("Backend Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/bounties")
        if response.status_code == 200:
            print_success("Backend is running")
            return True
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Backend is not accessible: {e}")
        return False

def test_mock_payment_create():
    """Test 1: Create mock payment transaction"""
    print_test("Mock Payment Create")
    
    payload = {
        "payment_method": "wallet",
        "amount_usd": 10.00,
        "wallet_address": TEST_WALLET
    }
    
    print_info(f"Request: POST /api/payment/create")
    print_json(payload)
    
    try:
        response = requests.post(f"{BASE_URL}/api/payment/create", json=payload)
        data = response.json()
        
        print_info("Response:")
        print_json(data)
        
        # Verify response
        if data.get("success"):
            print_success("Payment transaction created")
            
            if data.get("is_mock"):
                print_success("Correctly identified as MOCK transaction")
            else:
                print_error("Transaction not marked as mock!")
                return False
            
            if "🧪 TEST MODE" in data.get("warning", ""):
                print_success("Test mode warning displayed")
            else:
                print_warning("No test mode warning in response")
            
            if data.get("transaction"):
                print_success("Transaction details included")
                tx = data["transaction"]
                print_info(f"  Recipient: {tx.get('recipient', 'N/A')}")
                print_info(f"  Amount: ${tx.get('amount_usd', 0)}")
                print_info(f"  Units: {tx.get('units', 0)}")
            else:
                print_error("No transaction details!")
                return False
            
            return True
        else:
            print_error(f"Payment creation failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_mock_payment_verify():
    """Test 2: Verify mock payment and trigger smart contract"""
    print_test("Mock Payment Verify + Smart Contract")
    
    mock_signature = f"MOCK_TEST_{int(time.time())}"
    
    payload = {
        "payment_method": "wallet",
        "tx_signature": mock_signature,
        "wallet_address": TEST_WALLET,
        "amount_usd": 10.0
    }
    
    print_info(f"Request: POST /api/payment/verify")
    print_json(payload)
    
    try:
        response = requests.post(f"{BASE_URL}/api/payment/verify", json=payload)
        data = response.json()
        
        print_info("Response:")
        print_json(data)
        
        # Verify response
        if data.get("verified"):
            print_success("Payment verified")
            
            if data.get("is_mock"):
                print_success("Correctly identified as MOCK verification")
            else:
                print_error("Verification not marked as mock!")
            
            # Check free questions
            questions = data.get("questions_granted", 0)
            if questions > 0:
                print_success(f"Granted {questions} free questions")
            else:
                print_error("No free questions granted!")
                return False
            
            # Check smart contract execution
            if data.get("smart_contract_executed"):
                print_success("✨ DEVNET SMART CONTRACT EXECUTED!")
                if data.get("smart_contract_tx"):
                    print_info(f"  Contract TX: {data['smart_contract_tx']}")
                if data.get("funds_locked"):
                    print_success("  Funds locked in contract")
            elif data.get("smart_contract_executed") == False:
                print_warning("Smart contract execution attempted but failed")
                if data.get("smart_contract_error"):
                    print_warning(f"  Error: {data['smart_contract_error']}")
            else:
                print_info("Smart contract execution status not reported")
            
            return True
        else:
            print_error(f"Payment verification failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_free_questions_endpoint():
    """Test 3: Check free questions were granted"""
    print_test("Free Questions Check")
    
    print_info(f"Request: GET /api/free-questions/{TEST_WALLET}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/free-questions/{TEST_WALLET}")
        data = response.json()
        
        print_info("Response:")
        print_json(data)
        
        if data.get("success"):
            print_success("Free questions endpoint working")
            
            remaining = data.get("questions_remaining", 0)
            used = data.get("questions_used", 0)
            earned = data.get("questions_earned", 0)
            
            print_info(f"  Remaining: {remaining}")
            print_info(f"  Used: {used}")
            print_info(f"  Earned: {earned}")
            
            if remaining > 0 or earned > 0:
                print_success("User has free questions!")
            else:
                print_warning("User has no free questions")
            
            return True
        else:
            print_error(f"Endpoint failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_different_amounts():
    """Test 4: Test with different payment amounts"""
    print_test("Different Payment Amounts")
    
    test_amounts = [
        (5.50, "Below minimum - should warn"),
        (10.00, "Exactly minimum - should not warn"),
        (15.75, "Above minimum - should not warn"),
        (1.00, "Very low - should warn and grant 1 question")
    ]
    
    results = []
    
    for amount, description in test_amounts:
        print_info(f"\nTesting ${amount:.2f} - {description}")
        
        payload = {
            "payment_method": "wallet",
            "amount_usd": amount,
            "wallet_address": f"TestWallet_{amount}"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/payment/create", json=payload)
            data = response.json()
            
            if data.get("success"):
                has_warning = data.get("warning") is not None
                is_mock = data.get("is_mock", False)
                
                print_info(f"  Success: ✓")
                print_info(f"  Mock mode: {is_mock}")
                print_info(f"  Has warning: {has_warning}")
                
                if amount < 10.00 and not has_warning:
                    print_warning(f"  Expected warning for ${amount}")
                elif amount >= 10.00 and has_warning and "🧪" not in str(data.get("warning")):
                    print_warning(f"  Unexpected non-test warning for ${amount}")
                else:
                    print_success(f"  Warning behavior correct")
                
                results.append(True)
            else:
                print_error(f"  Failed: {data.get('error')}")
                results.append(False)
                
        except Exception as e:
            print_error(f"  Request failed: {e}")
            results.append(False)
    
    return all(results)

def test_messages_endpoint():
    """Test 5: Verify messages endpoint still works"""
    print_test("Messages Endpoint")
    
    print_info("Request: GET /api/bounty/1/messages/public?limit=5")
    
    try:
        response = requests.get(f"{BASE_URL}/api/bounty/1/messages/public?limit=5")
        data = response.json()
        
        print_info("Response:")
        print_json(data)
        
        if data.get("success"):
            message_count = len(data.get("messages", []))
            print_success(f"Messages endpoint working ({message_count} messages)")
            return True
        else:
            print_error(f"Endpoint failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "MOCK PAYMENT TESTING SUITE" + " "*32 + "║")
    print("║" + " "*24 + f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{Colors.END}\n")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Mock Payment Create", test_mock_payment_create),
        ("Mock Payment Verify + Smart Contract", test_mock_payment_verify),
        ("Free Questions Check", test_free_questions_endpoint),
        ("Different Payment Amounts", test_different_amounts),
        ("Messages Endpoint", test_messages_endpoint),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            time.sleep(0.5)  # Brief delay between tests
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*30 + "TEST SUMMARY" + " "*36 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{Colors.END}\n")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{Colors.BOLD}", end="")
    if passed == total:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED ({passed}/{total}){Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED ({passed}/{total} passed){Colors.END}")
    
    print(f"\n{Colors.CYAN}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)



