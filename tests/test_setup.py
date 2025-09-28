#!/usr/bin/env python3
"""
Test script to verify the Billions setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import anthropic
        print("✅ Anthropic package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import uvicorn: {e}")
        return False
    
    try:
        from src.ai_agent import BillionsAgent
        print("✅ BillionsAgent class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BillionsAgent: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "your_claude_api_key_here":
        print("✅ Claude API key is configured")
        return True
    else:
        print("⚠️  Claude API key not configured (set ANTHROPIC_API_KEY in .env)")
        return False

def test_ai_agent():
    """Test AI agent initialization"""
    try:
        from src.ai_agent import BillionsAgent
        agent = BillionsAgent()
        print("✅ BillionsAgent initialized successfully")
        
        # Test personality loading
        if hasattr(agent, 'personality') and agent.personality:
            print("✅ AI personality loaded successfully")
        else:
            print("⚠️  AI personality not loaded")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize BillionsAgent: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Billions Setup")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Config", test_environment),
        ("AI Agent Initialization", test_ai_agent)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Add your Claude API key to .env file")
        print("2. Run: python main.py")
        print("3. Open: http://localhost:8000/chat")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
