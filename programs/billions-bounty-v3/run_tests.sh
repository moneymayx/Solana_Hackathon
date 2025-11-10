#!/bin/bash
# Run tests against deployed program on devnet
export ANCHOR_PROVIDER_URL="https://api.devnet.solana.com"
export ANCHOR_WALLET="$HOME/.config/solana/id.json"

# Generate IDL from deployed program
anchor idl init --filepath target/idl/billions_bounty_v3.json ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb --provider.cluster devnet || echo "IDL init failed, continuing..."

# Run tests
yarn run ts-mocha './tests/**/*.ts'
