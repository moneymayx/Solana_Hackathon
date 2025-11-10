#!/bin/bash
# Build V3 using Anchor's native build system
# May use system Rust if Anchor is configured correctly

set -e

cd "$(dirname "$0")/.."

export PATH="$HOME/.avm/bin:$PATH"

echo "🔧 Building V3 with Anchor 0.31.1 (Native Build)"
echo "=================================================="
echo ""

# Ensure Anchor 0.31.1 is active
avm use 0.31.1 > /dev/null 2>&1

echo "Anchor version: $(anchor --version | head -1)"
echo ""

# Clean previous builds
cd programs/billions-bounty-v3
rm -rf target .anchor

# Try Anchor build with various options
echo "🏗️  Attempting Anchor build..."

# Method 1: Standard anchor build
if anchor build 2>&1 | tee /tmp/anchor_build.log | tail -50; then
    if [ -f target/deploy/billions_bounty_v3.so ]; then
        echo "✅ Build successful via standard anchor build!"
        exit 0
    fi
fi

# Method 2: With explicit program name
cd ../..
if anchor build --program-name billions_bounty_v3 2>&1 | tee -a /tmp/anchor_build.log | tail -50; then
    if [ -f programs/billions-bounty-v3/target/deploy/billions_bounty_v3.so ]; then
        echo "✅ Build successful via anchor build --program-name!"
        exit 0
    fi
fi

# Method 3: Try with environment variables to force system Rust
export RUSTC=$(which rustc)
export CARGO=$(which cargo)
export PATH="$(dirname $CARGO):$PATH"

cd programs/billions-bounty-v3
if anchor build 2>&1 | tee -a /tmp/anchor_build.log | tail -50; then
    if [ -f target/deploy/billions_bounty_v3.so ]; then
        echo "✅ Build successful with system Rust!"
        exit 0
    fi
fi

echo "❌ All build methods failed"
echo "Check /tmp/anchor_build.log for details"
exit 1

