#!/bin/bash
# Update Anchor CLI and rebuild IDL
# Option 1: Rebuild IDL with correct Anchor version

set -e

echo "🔧 Updating Anchor CLI and Rebuilding IDL"
echo ""

# Check current version
echo "Current Anchor version:"
anchor --version 2>&1 || echo "Anchor not found"
echo ""

# Try to install/update Anchor
echo "📦 Installing Anchor CLI 0.31.2..."
echo ""
echo "Option A: Using cargo (if available)"
cargo install --force anchor-cli --locked --version 0.31.2 2>&1 | tail -10 || {
    echo "Cargo install failed or cargo not available"
    echo ""
    echo "Option B: Using npm"
    npm install -g @coral-xyz/anchor-cli@0.31.2 2>&1 | tail -10 || {
        echo "npm install failed"
        echo ""
        echo "Option C: Manual installation"
        echo "Please install Anchor 0.31.2 manually:"
        echo "  - Visit: https://www.anchor-lang.com/docs/installation"
        echo "  - Or use: avm install 0.31.2 && avm use 0.31.2"
    }
}

echo ""
echo "✅ Anchor updated (or manual install required)"
echo ""
echo "Now rebuilding IDL..."
cd programs/billions-bounty-v3
anchor build 2>&1 | tail -20

echo ""
echo "✅ IDL rebuilt. Check target/idl/billions_bounty_v3.json"

