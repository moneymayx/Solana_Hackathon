#!/bin/bash

# Billions Bounty Mobile App Test Runner
# This script runs all automated tests for the mobile app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Billions Bounty Mobile App Test Suite       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print section header
print_section() {
    echo -e "\n${YELLOW}═══════════════════════════════════════${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Parse command line arguments
RUN_UNIT=true
RUN_INSTRUMENTED=false
RUN_COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_UNIT=true
            RUN_INSTRUMENTED=false
            shift
            ;;
        --instrumented-only)
            RUN_UNIT=false
            RUN_INSTRUMENTED=true
            shift
            ;;
        --all)
            RUN_UNIT=true
            RUN_INSTRUMENTED=true
            shift
            ;;
        --coverage)
            RUN_COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit-only           Run only unit tests (default)"
            echo "  --instrumented-only   Run only instrumented tests"
            echo "  --all                 Run all tests (unit + instrumented)"
            echo "  --coverage            Generate code coverage report"
            echo "  --verbose             Show detailed test output"
            echo "  --help                Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if Java is installed and working
if ! java -version > /dev/null 2>&1; then
    print_error "Java is not installed or not working!"
    echo ""
    echo "Android/Kotlin tests require Java to run."
    echo ""
    echo "Quick fix (macOS with Homebrew):"
    echo "  brew install openjdk@17"
    echo "  echo 'export JAVA_HOME=\$(brew --prefix openjdk@17)/libexec/openjdk.jdk/Contents/Home' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo ""
    echo "For detailed instructions, see: JAVA_SETUP_REQUIRED.md"
    exit 1
fi

# Check if gradlew exists
if [ ! -f "./gradlew" ]; then
    print_error "gradlew not found. Are you in the mobile-app directory?"
    exit 1
fi

# Make gradlew executable
chmod +x ./gradlew

# Clean build directory
print_section "Cleaning Build"
./gradlew clean > /dev/null 2>&1
print_success "Build directory cleaned"

# Run unit tests
if [ "$RUN_UNIT" = true ]; then
    print_section "Running Unit Tests"
    
    if [ "$VERBOSE" = true ]; then
        ./gradlew test --info
    else
        ./gradlew test
    fi
    
    if [ $? -eq 0 ]; then
        print_success "All unit tests passed!"
        
        # Count tests
        if [ -d "app/build/test-results/testDebugUnitTest" ]; then
            TEST_COUNT=$(find app/build/test-results/testDebugUnitTest -name "*.xml" -exec grep -o "tests=\"[0-9]*\"" {} \; | grep -o "[0-9]*" | awk '{s+=$1} END {print s}')
            print_success "Total unit tests: $TEST_COUNT"
        fi
    else
        print_error "Unit tests failed!"
        echo ""
        echo "View test report: app/build/reports/tests/testDebugUnitTest/index.html"
        exit 1
    fi
fi

# Run instrumented tests
if [ "$RUN_INSTRUMENTED" = true ]; then
    print_section "Running Instrumented Tests"
    
    # Check if device/emulator is connected
    DEVICE_COUNT=$(adb devices | grep -c "device$")
    
    if [ "$DEVICE_COUNT" -eq 0 ]; then
        print_error "No Android device or emulator connected!"
        echo "Please start an emulator or connect a device, then run again."
        exit 1
    fi
    
    print_success "Found $DEVICE_COUNT connected device(s)"
    
    if [ "$VERBOSE" = true ]; then
        ./gradlew connectedAndroidTest --info
    else
        ./gradlew connectedAndroidTest
    fi
    
    if [ $? -eq 0 ]; then
        print_success "All instrumented tests passed!"
        
        # Count tests
        if [ -d "app/build/outputs/androidTest-results/connected" ]; then
            TEST_COUNT=$(find app/build/outputs/androidTest-results/connected -name "*.xml" -exec grep -o "tests=\"[0-9]*\"" {} \; | grep -o "[0-9]*" | awk '{s+=$1} END {print s}')
            print_success "Total instrumented tests: $TEST_COUNT"
        fi
    else
        print_error "Instrumented tests failed!"
        echo ""
        echo "View test report: app/build/reports/androidTests/connected/index.html"
        exit 1
    fi
fi

# Generate coverage report
if [ "$RUN_COVERAGE" = true ]; then
    print_section "Generating Code Coverage Report"
    
    ./gradlew testDebugUnitTest jacocoTestReport
    
    if [ $? -eq 0 ]; then
        print_success "Coverage report generated!"
        
        # Check if report exists
        if [ -f "app/build/reports/jacoco/jacocoTestReport/html/index.html" ]; then
            COVERAGE_FILE="app/build/reports/jacoco/jacocoTestReport/html/index.html"
            print_success "View coverage: $COVERAGE_FILE"
            
            # Try to open in browser (macOS)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                echo ""
                echo -e "${BLUE}Opening coverage report in browser...${NC}"
                open "$COVERAGE_FILE"
            fi
        fi
    else
        print_error "Coverage report generation failed!"
        exit 1
    fi
fi

# Summary
print_section "Test Summary"

if [ "$RUN_UNIT" = true ]; then
    echo "✓ Unit Tests: PASSED"
fi

if [ "$RUN_INSTRUMENTED" = true ]; then
    echo "✓ Instrumented Tests: PASSED"
fi

if [ "$RUN_COVERAGE" = true ]; then
    echo "✓ Coverage Report: GENERATED"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          All Tests Passed Successfully!        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Test reports location
echo -e "${BLUE}Test Reports:${NC}"
if [ "$RUN_UNIT" = true ]; then
    echo "  Unit Tests:        app/build/reports/tests/testDebugUnitTest/index.html"
fi
if [ "$RUN_INSTRUMENTED" = true ]; then
    echo "  Instrumented:      app/build/reports/androidTests/connected/index.html"
fi
if [ "$RUN_COVERAGE" = true ]; then
    echo "  Coverage:          app/build/reports/jacoco/jacocoTestReport/html/index.html"
fi
echo ""

exit 0

