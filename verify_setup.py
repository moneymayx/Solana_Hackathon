#!/usr/bin/env python3
"""
Quick verification script to check if AI Decision System is properly set up
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def check_environment():
    """Check if environment variables are set"""
    print("🔍 Checking Environment Configuration")
    print("-" * 40)
    
    required_vars = [
        "AI_DECISION_PRIVATE_KEY_PATH",
        "BACKEND_AUTHORITY_PUBLIC_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {os.getenv(var)[:20]}...")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_key_files():
    """Check if key files exist"""
    print("\n🔑 Checking Key Files")
    print("-" * 40)
    
    key_files = [
        "ai_decision_key.pem",
        "ai_decision_key_public.pem", 
        "backend_authority_key.pem",
        "backend_authority_key_public.pem"
    ]
    
    missing_files = []
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing key files: {', '.join(missing_files)}")
        return False
    
    print("✅ All key files are present")
    return True

def check_ai_decision_service():
    """Check if AI decision service is working"""
    print("\n🤖 Testing AI Decision Service")
    print("-" * 40)
    
    try:
        from src.ai_decision_service import ai_decision_service
        
        # Test key retrieval
        public_key = ai_decision_service.get_public_key_bytes()
        print(f"✅ Public key retrieved: {len(public_key)} bytes")
        
        # Test decision creation
        signed_decision = ai_decision_service.create_ai_decision(
            user_message="Test message",
            ai_response="Test response",
            is_successful_jailbreak=False,
            user_id=1,
            session_id="test"
        )
        print("✅ Decision creation: Working")
        
        # Test decision verification
        is_valid = ai_decision_service.verify_decision(signed_decision)
        if is_valid:
            print("✅ Decision verification: Working")
        else:
            print("❌ Decision verification: Failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AI Decision Service error: {e}")
        return False

def check_smart_contract_files():
    """Check if smart contract files are updated"""
    print("\n📄 Checking Smart Contract Files")
    print("-" * 40)
    
    contract_file = "programs/billions-bounty/src/lib.rs"
    if not os.path.exists(contract_file):
        print(f"❌ Smart contract file not found: {contract_file}")
        return False
    
    with open(contract_file, "r") as f:
        content = f.read()
    
    required_functions = [
        "process_ai_decision",
        "AIDecisionLogged",
        "WinnerSelected"
    ]
    
    missing_functions = []
    for func in required_functions:
        if func in content:
            print(f"✅ {func}: Found")
        else:
            print(f"❌ {func}: Missing")
            missing_functions.append(func)
    
    if missing_functions:
        print(f"❌ Missing smart contract functions: {', '.join(missing_functions)}")
        return False
    
    print("✅ Smart contract is properly updated")
    return True

def main():
    """Main verification function"""
    print("🔍 AI Decision System Verification")
    print("=" * 50)
    
    checks = [
        check_environment,
        check_key_files,
        check_ai_decision_service,
        check_smart_contract_files
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your AI Decision System is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Deploy smart contract: cd programs/billions-bounty && anchor deploy")
        print("2. Start backend: python main.py")
        print("3. Test API: curl http://localhost:8000/api/ai-decisions/public-key")
        return True
    else:
        print("❌ Some checks failed. Please run setup_ai_decision_system.py to fix issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
