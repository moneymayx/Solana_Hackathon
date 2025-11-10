#!/bin/bash
# Build V3 using the same method that successfully built V2
# Based on V2_COMPLETE_STATUS.md: "Solved by using Solana's Rust toolchain (`rustup run solana cargo`)"

set -e

cd "$(dirname "$0")/.."

echo "🔧 Building V3 using V2's successful method"
echo "============================================"
echo ""
echo "Method: rustup run solana cargo (as documented in V2_COMPLETE_STATUS.md)"
echo ""

# Check if Solana toolchain is available
if ! rustup toolchain list | grep -q "solana"; then
    echo "❌ Solana Rust toolchain not found!"
    echo "   Run: rustup toolchain link solana ~/.local/share/solana/install/active_release/bin"
    exit 1
fi

echo "✅ Solana Rust toolchain found"
echo ""

# Navigate to V3 program directory
cd programs/billions-bounty-v3

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf target

# Use rustup run solana cargo to generate lockfile and build
# This uses Solana's Rust 1.75.0 which creates v3 lockfiles
echo "🔨 Building with 'rustup run solana cargo build-sbf --release'..."
echo "   (This method successfully built V2 per V2_COMPLETE_STATUS.md)"
echo ""

if rustup run solana cargo build-sbf -- --release 2>&1 | tee /tmp/v3_build_v2_method.log | tail -60; then
    echo ""
    echo "✅ Build completed!"
    
    # Find the built binary
    BINARY=$(find target/sbf-solana-solana/release -name "*.so" 2>/dev/null | head -1)
    if [ -n "$BINARY" ]; then
        echo "✅ Binary found: $BINARY"
        
        # Copy to deploy directory (standard location)
        mkdir -p target/deploy
        cp "$BINARY" target/deploy/billions_bounty_v3.so
        
        # Verify program ID in binary
        echo ""
        echo "🔍 Verifying program ID in binary..."
        if strings target/deploy/billions_bounty_v3.so | grep -q "ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"; then
            echo "✅ Correct program ID found in binary!"
        else
            echo "⚠️  Warning: Program ID not found in binary strings (may be embedded differently)"
        fi
        
        echo ""
        echo "✅ Build complete: target/deploy/billions_bounty_v3.so"
        ls -lh target/deploy/billions_bounty_v3.so
    else
        echo "❌ Binary not found"
        echo "Check /tmp/v3_build_v2_method.log for details"
        exit 1
    fi
else
    echo ""
    echo "❌ Build failed"
    echo "Check /tmp/v3_build_v2_method.log for details"
    exit 1
fi

