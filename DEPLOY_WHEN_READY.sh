#!/bin/bash
# Deploy V3 when sufficient funds are available
NEW_PROGRAM_ID=$(solana-keygen pubkey target/deploy/billions_bounty_v3-keypair.json)
BALANCE=$(solana balance --url devnet | awk '{print $1}' | sed 's/ SOL//')

echo "🚀 V3 Deployment Script"
echo "Program ID: $NEW_PROGRAM_ID"
echo "Current balance: $BALANCE"
echo ""

BALANCE_NUM=$(echo "$BALANCE" | awk '{print $1}')
if (( $(echo "$BALANCE_NUM >= 4.2" | bc -l 2>/dev/null || echo 0) )); then
    echo "✅ Sufficient balance, deploying..."
    solana program deploy target/deploy/billions_bounty_v3.so \
      --program-id target/deploy/billions_bounty_v3-keypair.json \
      --url devnet --max-len 600000
else
    echo "❌ Insufficient balance: $BALANCE (need ~4.2 SOL)"
    echo "   Request airdrop: solana airdrop 1 --url devnet"
fi
