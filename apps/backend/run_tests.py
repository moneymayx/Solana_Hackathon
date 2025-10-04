#!/usr/bin/env python3
"""
Comprehensive test runner for Billions Bounty web interface
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print(f"Directory: {cwd or os.getcwd()}")
    print()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=True,
            capture_output=False
        )
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    python_deps = [
        "pytest",
        "httpx",
        "fastapi",
        "uvicorn"
    ]
    
    missing_python_deps = []
    for dep in python_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_python_deps.append(dep)
    
    if missing_python_deps:
        print(f"❌ Missing Python dependencies: {', '.join(missing_python_deps)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    # Check Node.js dependencies
    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        try:
            result = subprocess.run(
                "npm list --depth=0",
                cwd=frontend_dir,
                shell=True,
                capture_output=True,
                check=True
            )
            print("✅ Node.js dependencies - OK")
        except subprocess.CalledProcessError:
            print("❌ Node.js dependencies - Missing")
            print("Install with: cd frontend && npm install")
            return False
    
    print("✅ All dependencies - OK")
    return True

def run_backend_tests():
    """Run backend API tests"""
    backend_dir = Path(__file__).parent
    tests_dir = backend_dir / "tests"
    
    # Run existing backend tests
    existing_tests = [
        "test_setup.py",
        "test_ai_personality.py",
        "test_ai_responses.py",
        "test_difficulty.py",
        "test_freysa_protection.py",
        "test_near_miss_system.py",
        "test_personality.py",
        "test_progressive_difficulty.py",
        "test_real_difficulty.py"
    ]
    
    success = True
    for test_file in existing_tests:
        test_path = tests_dir / test_file
        if test_path.exists():
            if not run_command(f"../venv/bin/python {test_file}", cwd=tests_dir, description=f"Backend Test: {test_file}"):
                success = False
    
    # Run new web API tests
    if (tests_dir / "test_web_api.py").exists():
        if not run_command("../venv/bin/python test_web_api.py", cwd=tests_dir, description="Web API Tests"):
            success = False
    
    # Run integration tests
    if (tests_dir / "test_integration.py").exists():
        if not run_command("../venv/bin/python test_integration.py", cwd=tests_dir, description="Integration Tests"):
            success = False
    
    return success

def run_frontend_tests():
    """Run frontend component tests"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Run Jest tests
    if not run_command("npm test -- --watchAll=false", cwd=frontend_dir, description="Frontend Component Tests"):
        return False
    
    return True

def run_e2e_tests():
    """Run end-to-end tests"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Playwright browsers if needed
    run_command("npx playwright install", cwd=frontend_dir, description="Installing Playwright browsers")
    
    # Run E2E tests
    if not run_command("npm run test:e2e", cwd=frontend_dir, description="End-to-End Tests"):
        return False
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🚀 Running All Tests for Billions Bounty Web Interface")
    print("=" * 70)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing dependencies.")
        return False
    
    # Run tests
    results = {
        "backend": run_backend_tests(),
        "frontend": run_frontend_tests(),
        "e2e": run_e2e_tests()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for test_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_type.upper():<15} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your web interface is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run tests for Billions Bounty web interface")
    parser.add_argument("--type", choices=["backend", "frontend", "e2e", "all"], default="all",
                       help="Type of tests to run")
    parser.add_argument("--check-deps", action="store_true",
                       help="Only check dependencies")
    
    args = parser.parse_args()
    
    if args.check_deps:
        success = check_dependencies()
        sys.exit(0 if success else 1)
    
    if args.type == "backend":
        success = run_backend_tests()
    elif args.type == "frontend":
        success = run_frontend_tests()
    elif args.type == "e2e":
        success = run_e2e_tests()
    else:  # all
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
