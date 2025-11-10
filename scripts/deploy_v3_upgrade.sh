#!/bin/bash
# Deploy V3 Binary Upgrade to Devnet
# This upgrades the existing V3 program with the newly built binary

set -e

cd "$(dirname "$0")/.."

echo "🚀 V3 Program Upgrade Deployment"
echo "================================="
echo ""

PROGRAM_ID="ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"
BINARY_PATH="target/deploy/billions_bounty_v3.so"
KEYPAIR_PATH="target/deploy/billions_bounty_v3-keypair.json"
NETWORK="devnet"

# Verify binary exists
if [ ! -f "$BINARY_PATH" ]; then
    echo "❌ Binary not found: $BINARY_PATH"
    exit 1
fi

echo "✅ Binary found: $BINARY_PATH"
ls -lh "$BINARY_PATH"

# Verify keypair exists
if [ ! -f "$KEYPAIR_PATH" ]; then
    echo "❌ Keypair not found: $KEYPAIR_PATH"
    exit 1
fi

ACTUAL_PROGRAM_ID=$(solana-keygen pubkey "$KEYPAIR_PATH")
if [ "$ACTUAL_PROGRAM_ID" != "$PROGRAM_ID" ]; then
    echo "⚠️  Warning: Keypair ID ($ACTUAL_PROGRAM_ID) doesn't match expected ($PROGRAM_ID)"
    echo "   Proceeding anyway (may be different keypair file)"
fi

echo "✅ Keypair: $ACTUAL_PROGRAM_ID"
echo ""

# Check current program status
echo "📋 Current Program Status:"
solana program show "$PROGRAM_ID" --url "$NETWORK" 2>&1 | head -10 || echo "   Program not found on devnet (new deployment)"
echo ""

# Check wallet balance
BALANCE=$(solana balance --url "$NETWORK" | awk '{print $1}')
echo "💰 Wallet Balance: $BALANCE SOL"

BALANCE_NUM=$(echo "$BALANCE" | sed 's/ SOL//')
if (( $(echo "$BALANCE_NUM < 5" | bc -l) )); then
    echo "⚠️  Warning: Low balance. Deployment may require 2-3 SOL."
    echo "   Airdrop SOL: solana airdrop 2 --url $NETWORK"
fi
echo ""

# Deploy/upgrade
echo "🔨 Deploying/Upgrading V3 Program..."
echo "   Program ID: $PROGRAM_ID"
echo "   Binary: $BINARY_PATH"
echo "   Network: $NETWORK"
echo ""

solana program deploy \
    --program-id "$KEYPAIR_PATH" \
    "$BINARY_PATH" \
    --url "$NETWORK" \
    --max-len 500000

echo ""
echo "✅ Deployment complete!"
echo ""

# Verify deployment
echo "📋 Verifying deployment..."
solana program show "$PROGRAM_ID" --url "$NETWORK" | head -15

echo ""
echo "🎉 V3 Program deployed/upgraded successfully!"
echo ""
echo "Next: Initialize the lottery account using scripts/initialize_v3_final.js"

