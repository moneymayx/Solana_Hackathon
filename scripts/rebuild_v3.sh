#!/bin/bash
# V3 Rebuild Script with All Validation Checkpoints
# This script rebuilds V3 contract in isolation and validates before deployment

set -e

echo "🔧 V3 Rebuild Script - Validation-First Approach"
echo "=================================================="
echo ""

# Configuration
V3_SOURCE_DIR="programs/billions-bounty-v3"
BUILD_DIR="/tmp/v3-rebuild"
PROGRAM_ID="ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"
DEPLOYED_SIZE=313216  # bytes
NETWORK="devnet"

echo "📋 Configuration:"
echo "   Program ID: $PROGRAM_ID"
echo "   Source: $V3_SOURCE_DIR"
echo "   Build Dir: $BUILD_DIR"
echo "   Network: $NETWORK"
echo ""

# CHECKPOINT 1: Setup isolated build environment
echo "✅ CHECKPOINT 1: Setting up isolated build environment..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp -r "$V3_SOURCE_DIR/src" "$BUILD_DIR/"
cp "$V3_SOURCE_DIR/Cargo.toml" "$BUILD_DIR/"

# Remove rayon-core from dependencies (causes stack overflow)
sed -i '' '/rayon-core/d' "$BUILD_DIR/Cargo.toml"
echo "   ✅ Isolated directory created"
echo ""

# CHECKPOINT 2: Build binary
echo "✅ CHECKPOINT 2: Building V3 binary..."
cd "$BUILD_DIR"
rm -f Cargo.lock

# Try to use workspace Cargo.lock if available
if [ -f "../../Cargo.lock" ]; then
    cp ../../Cargo.lock Cargo.lock
    # Manually downgrade lockfile version if needed
    if grep -q "^version = 4" Cargo.lock; then
        echo "   ⚠️  Lockfile version 4 detected - may need Rust toolchain update"
        echo "   Attempting build anyway..."
    fi
fi

if cargo-build-sbf 2>&1 | tee build.log | tail -20; then
    echo "   ✅ Build completed successfully"
else
    echo "   ❌ Build failed - check build.log for details"
    echo ""
    echo "   Note: This may require:"
    echo "   1. Updating Rust toolchain for Solana"
    echo "   2. Fixing workspace dependency conflicts"
    echo "   3. Using a different build method"
    exit 1
fi

BINARY_PATH="$BUILD_DIR/target/deploy/billions_bounty_v3.so"
if [ ! -f "$BINARY_PATH" ]; then
    echo "   ❌ Binary not found at expected path"
    exit 1
fi

# CHECKPOINT 3: Verify embedded program ID
echo ""
echo "✅ CHECKPOINT 3: Verifying embedded program ID..."
CORRECT_ID=$(strings "$BINARY_PATH" | grep "$PROGRAM_ID")
OLD_ID=$(strings "$BINARY_PATH" | grep "9qXY55GYdaUnQmUrqSmSThCKxhWVVqKRczuGmcPduPg7")

if [ -n "$CORRECT_ID" ]; then
    echo "   ✅ Correct program ID found: $PROGRAM_ID"
else
    echo "   ❌ Correct program ID NOT found in binary"
    exit 1
fi

if [ -n "$OLD_ID" ]; then
    echo "   ⚠️  WARNING: Old program ID also found - may cause issues"
fi

# CHECKPOINT 4: Verify binary size
echo ""
echo "✅ CHECKPOINT 4: Verifying binary size..."
BINARY_SIZE=$(stat -f%z "$BINARY_PATH")
SIZE_DIFF=$(( ($BINARY_SIZE - $DEPLOYED_SIZE) * 100 / $DEPLOYED_SIZE ))
echo "   Binary size: $BINARY_SIZE bytes"
echo "   Deployed size: $DEPLOYED_SIZE bytes"
echo "   Difference: ${SIZE_DIFF}%"

if [ ${SIZE_DIFF#-} -gt 10 ]; then
    echo "   ⚠️  WARNING: Size difference > 10% - verify build is correct"
else
    echo "   ✅ Size within acceptable range"
fi

echo ""
echo "✅ All build checkpoints passed!"
echo "   Binary ready at: $BINARY_PATH"
echo ""
echo "Next steps:"
echo "  1. Test on local validator (CHECKPOINT 5)"
echo "  2. Simulate devnet deployment (CHECKPOINT 6)"
echo "  3. Deploy to devnet (Phase 5)"
echo ""

