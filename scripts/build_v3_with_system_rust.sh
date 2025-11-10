#!/bin/bash
# Build V3 using System Rust instead of Solana's bundled Rust
# This bypasses Solana's cargo-build-sbf Rust 1.75.0 limitation

set -e

cd "$(dirname "$0")/.."
PROGRAM_DIR="programs/billions-bounty-v3"

echo "🔧 Building V3 with System Rust (1.91.0)"
echo "=========================================="
echo ""

# Check system Rust version
SYSTEM_RUST_VERSION=$(rustc --version | awk '{print $2}')
echo "System Rust: $SYSTEM_RUST_VERSION"

# Install Solana BPF target if not already installed
echo "📦 Installing Solana BPF target..."
rustup target add sbf-solana-solana || true

# Save original PATH
ORIGINAL_PATH="$PATH"

# Remove Solana tools from PATH temporarily
NEW_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v solana | tr '\n' ':')
export PATH="$NEW_PATH"

# Use system cargo instead of Solana's
export CARGO=$(which cargo)
export RUSTC=$(which rustc)

echo "Using Cargo: $CARGO"
echo "Using Rustc: $RUSTC"
echo ""

# Build with system cargo
cd "$PROGRAM_DIR"
rm -rf target

echo "🏗️  Building with system Rust..."
if cargo build --target sbf-solana-solana --release 2>&1 | tee /tmp/v3_build.log; then
    echo "✅ Build successful!"
    
    # Find the built binary
    BINARY=$(find target/sbf-solana-solana/release -name "*.so" 2>/dev/null | head -1)
    if [ -n "$BINARY" ]; then
        echo "✅ Binary found: $BINARY"
        
        # Copy to deploy directory
        mkdir -p target/deploy
        cp "$BINARY" target/deploy/billions_bounty_v3.so
        
        # Verify program ID in binary
        if strings target/deploy/billions_bounty_v3.so | grep -q "ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"; then
            echo "✅ Correct program ID found in binary!"
        else
            echo "⚠️  Warning: Program ID not found in binary strings"
        fi
        
        echo ""
        echo "✅ Build complete: target/deploy/billions_bounty_v3.so"
    else
        echo "❌ Binary not found"
        exit 1
    fi
else
    echo "❌ Build failed - check /tmp/v3_build.log"
    exit 1
fi

# Restore PATH
export PATH="$ORIGINAL_PATH"

