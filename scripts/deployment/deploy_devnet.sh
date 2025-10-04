#!/bin/bash
# Deployment script for Billions Bounty smart contract to Solana Devnet
# This script automates the deployment process outlined in SMART_CONTRACT_DEPLOYMENT.md

set -e  # Exit on any error

echo "=========================================="
echo "Billions Bounty - Devnet Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROGRAM_ID="4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK"
PROGRAM_KEYPAIR="target/deploy/billions_bounty-keypair.json"
PROGRAM_SO="programs/billions-bounty/target/deploy/billions_bounty.so"
NETWORK="devnet"

# Check if running from correct directory
if [ ! -f "Anchor.toml" ]; then
    echo -e "${RED}Error: Must be run from Billions_Bounty directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking Solana CLI configuration...${NC}"
solana config get

echo ""
echo -e "${YELLOW}Current network:${NC}"
CURRENT_NETWORK=$(solana config get | grep "RPC URL" | awk '{print $3}')
echo "$CURRENT_NETWORK"

# Ask user to confirm or switch to devnet
if [[ "$CURRENT_NETWORK" != *"devnet"* ]]; then
    echo -e "${RED}WARNING: You are not on devnet!${NC}"
    read -p "Switch to devnet? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Switching to devnet...${NC}"
        solana config set --url https://api.devnet.solana.com
    else
        echo -e "${RED}Deployment cancelled.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}Step 2: Checking wallet balance...${NC}"
BALANCE=$(solana balance)
echo "Balance: $BALANCE"

# Check if balance is sufficient (need at least 5 SOL for deployment)
BALANCE_NUM=$(echo $BALANCE | awk '{print $1}')
if (( $(echo "$BALANCE_NUM < 5" | bc -l) )); then
    echo -e "${RED}Insufficient balance! Need at least 5 SOL for deployment.${NC}"
    echo -e "${YELLOW}Get devnet SOL from: https://faucet.solana.com${NC}"
    read -p "Press enter after adding SOL to continue, or Ctrl+C to cancel..."
fi

echo ""
echo -e "${YELLOW}Step 3: Building smart contract...${NC}"
cd programs/billions-bounty
cargo build-sbf
cd ../..

# Verify build output
if [ ! -f "$PROGRAM_SO" ]; then
    echo -e "${RED}Error: Program binary not found at $PROGRAM_SO${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build successful${NC}"
ls -lh "$PROGRAM_SO"

echo ""
echo -e "${YELLOW}Step 4: Deploying program to devnet...${NC}"
echo "Program ID: $PROGRAM_ID"

solana program deploy \
    --program-id "$PROGRAM_KEYPAIR" \
    "$PROGRAM_SO" \
    --url https://api.devnet.solana.com

echo ""
echo -e "${GREEN}✓ Program deployed successfully!${NC}"

echo ""
echo -e "${YELLOW}Step 5: Verifying deployment...${NC}"
solana program show "$PROGRAM_ID" --url https://api.devnet.solana.com

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Program ID: $PROGRAM_ID"
echo "Network: Devnet"
echo "Explorer: https://explorer.solana.com/address/$PROGRAM_ID?cluster=devnet"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Initialize the lottery using: anchor run initialize"
echo "2. Update smart_contract_service.py with the deployed program ID"
echo "3. Test entry payments on devnet"
echo "4. Monitor contract state with: ./monitor_contract.sh"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "- Store AUTHORITY_PRIVATE_KEY securely (never commit to git)"
echo "- The authority wallet controls emergency recovery"
echo "- Test thoroughly on devnet before mainnet deployment"
echo ""
