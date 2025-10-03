#!/bin/bash
# Monitoring script for Billions Bounty smart contract
# Displays current lottery state, jackpot balance, and recent activity

set -e

echo "=========================================="
echo "Billions Bounty - Contract Monitor"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROGRAM_ID="DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh"
LOTTERY_PDA=""  # Will be derived from seeds
NETWORK="${1:-devnet}"  # Default to devnet, accept mainnet as arg

# Set RPC URL based on network
if [ "$NETWORK" == "mainnet" ]; then
    RPC_URL="https://api.mainnet-beta.solana.com"
    EXPLORER_BASE="https://explorer.solana.com"
else
    RPC_URL="https://api.devnet.solana.com"
    EXPLORER_BASE="https://explorer.solana.com"
    NETWORK="devnet"
fi

echo -e "${BLUE}Network: ${NETWORK}${NC}"
echo -e "${BLUE}Program ID: ${PROGRAM_ID}${NC}"
echo ""

# Function to get account info
get_account_info() {
    local address=$1
    solana account "$address" --url "$RPC_URL" 2>/dev/null
}

# Function to get program info
get_program_info() {
    solana program show "$PROGRAM_ID" --url "$RPC_URL" 2>/dev/null
}

echo -e "${YELLOW}[1] Program Status${NC}"
echo "-------------------------------------------"
PROGRAM_INFO=$(get_program_info)

if [ -z "$PROGRAM_INFO" ]; then
    echo -e "${RED}✗ Program not deployed or not found${NC}"
    echo ""
    echo "Deploy the program first using: ./deploy_devnet.sh"
    exit 1
else
    echo -e "${GREEN}✓ Program deployed${NC}"
    echo "$PROGRAM_INFO" | head -10
fi

echo ""
echo -e "${YELLOW}[2] Program Account Details${NC}"
echo "-------------------------------------------"
PROGRAM_DATA=$(solana account "$PROGRAM_ID" --url "$RPC_URL" --output json 2>/dev/null)

if [ -n "$PROGRAM_DATA" ]; then
    BALANCE=$(echo "$PROGRAM_DATA" | jq -r '.account.lamports' 2>/dev/null)
    if [ -n "$BALANCE" ]; then
        BALANCE_SOL=$(echo "scale=4; $BALANCE / 1000000000" | bc)
        echo "Balance: ${BALANCE_SOL} SOL (${BALANCE} lamports)"
    fi
    
    OWNER=$(echo "$PROGRAM_DATA" | jq -r '.account.owner' 2>/dev/null)
    echo "Owner: $OWNER"
    
    EXECUTABLE=$(echo "$PROGRAM_DATA" | jq -r '.account.executable' 2>/dev/null)
    echo "Executable: $EXECUTABLE"
fi

echo ""
echo -e "${YELLOW}[3] Lottery State (PDA)${NC}"
echo "-------------------------------------------"
echo "Note: Lottery PDA must be initialized first"
echo "Use: anchor run initialize"
echo ""
echo "To derive lottery PDA address, run:"
echo "  anchor run derive-pda"

echo ""
echo -e "${YELLOW}[4] Recent Transactions${NC}"
echo "-------------------------------------------"
echo "Fetching recent program transactions..."

# Get recent transaction signatures for the program
RECENT_TXS=$(solana transaction-history "$PROGRAM_ID" --url "$RPC_URL" --limit 5 2>/dev/null || echo "")

if [ -z "$RECENT_TXS" ]; then
    echo "No recent transactions found"
else
    echo "$RECENT_TXS"
fi

echo ""
echo -e "${YELLOW}[5] Links${NC}"
echo "-------------------------------------------"
echo "Program Explorer:"
echo "  ${EXPLORER_BASE}/address/${PROGRAM_ID}?cluster=${NETWORK}"
echo ""
echo "Solscan:"
echo "  https://solscan.io/account/${PROGRAM_ID}?cluster=${NETWORK}"

echo ""
echo -e "${YELLOW}[6] Monitoring Options${NC}"
echo "-------------------------------------------"
echo "Watch mode (updates every 10 seconds):"
echo "  watch -n 10 $0"
echo ""
echo "Monitor specific account (lottery PDA):"
echo "  solana account <LOTTERY_PDA> --url $RPC_URL"
echo ""
echo "Monitor logs in real-time:"
echo "  solana logs $PROGRAM_ID --url $RPC_URL"

echo ""
echo -e "${GREEN}=========================================="
echo "Monitoring complete"
echo "==========================================${NC}"
echo ""
echo "Refresh: $0 $NETWORK"
echo ""

