#!/bin/bash
# Initialize Lottery Script
# Creates the lottery PDA account and sets initial parameters

set -e

echo "=========================================="
echo "Initialize Billions Bounty Lottery"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROGRAM_ID="DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh"
NETWORK="devnet"
USDC_MINT="Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr"  # Devnet USDC mint

echo -e "${BLUE}Program ID: ${PROGRAM_ID}${NC}"
echo -e "${BLUE}Network: ${NETWORK}${NC}"
echo -e "${BLUE}USDC Mint: ${USDC_MINT}${NC}"
echo ""

echo -e "${YELLOW}Step 1: Deriving Lottery PDA...${NC}"
# The lottery PDA is derived from seeds: ["lottery"]
# We'll use solana-keygen to find the PDA programmatically

# For now, we'll use anchor CLI to interact with the program
echo "Lottery PDA will be derived from seeds: [\"lottery\"]"
echo ""

echo -e "${YELLOW}Step 2: Checking if lottery is already initialized...${NC}"
# Try to fetch lottery account
# This is a placeholder - in production, you'd query the actual PDA

echo -e "${YELLOW}Step 3: Preparing initialization transaction...${NC}"
echo ""
echo "The lottery needs to be initialized with:"
echo "  - Entry fee (e.g., 10 USDC = 10,000,000 tokens)"
echo "  - Research fund floor (minimum jackpot, e.g., 1000 USDC)"
echo "  - Authority (your wallet): $(solana address)"
echo ""

# Since we don't have Anchor client setup yet, let's create a TypeScript initialization script
echo -e "${YELLOW}Creating TypeScript initialization script...${NC}"

cat > /tmp/initialize_lottery.ts << 'EOF'
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from "@solana/spl-token";

// Program ID
const PROGRAM_ID = new PublicKey("DAgzfNPpc3i2EttgxfRtSN4SXQ4CwXQYjStmgrnw3BYh");

// Devnet USDC mint
const USDC_MINT = new PublicKey("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr");

async function initializeLottery() {
    // Set up connection and wallet
    const connection = new anchor.web3.Connection("https://api.devnet.solana.com", "confirmed");
    const wallet = anchor.Wallet.local();
    const provider = new anchor.AnchorProvider(connection, wallet, {});
    
    // Derive lottery PDA
    const [lotteryPda, lotteryBump] = await PublicKey.findProgramAddress(
        [Buffer.from("lottery")],
        PROGRAM_ID
    );
    
    console.log("Lottery PDA:", lotteryPda.toString());
    console.log("Lottery Bump:", lotteryBump);
    
    // Derive jackpot token account (ATA for lottery PDA)
    const jackpotTokenAccount = await anchor.utils.token.associatedAddress({
        mint: USDC_MINT,
        owner: lotteryPda
    });
    
    console.log("Jackpot Token Account:", jackpotTokenAccount.toString());
    
    // Initialize lottery
    const entryFee = new anchor.BN(10_000_000); // 10 USDC
    const researchFundFloor = new anchor.BN(1_000_000_000); // 1000 USDC
    
    console.log("\nInitializing lottery with:");
    console.log("  Entry Fee: 10 USDC");
    console.log("  Research Fund Floor: 1000 USDC");
    console.log("  Authority:", wallet.publicKey.toString());
    
    // Note: You'll need to call the initialize_lottery instruction
    // This requires the actual program IDL to be generated
    
    console.log("\n✓ Lottery configuration prepared");
    console.log("\nTo complete initialization, you need to:");
    console.log("1. Build program with IDL generation");
    console.log("2. Call initialize_lottery instruction with above parameters");
}

initializeLottery().catch(console.error);
EOF

echo -e "${GREEN}✓ TypeScript initialization script created at /tmp/initialize_lottery.ts${NC}"
echo ""

echo -e "${YELLOW}Manual Initialization Steps:${NC}"
echo "-------------------------------------------"
echo "Since the IDL generation failed during build, you have two options:"
echo ""
echo "Option 1: Use Anchor TypeScript Client (requires IDL)"
echo "  1. Generate IDL for the program"
echo "  2. Run: anchor run initialize"
echo ""
echo "Option 2: Manual transaction construction"
echo "  1. Derive lottery PDA: seeds = [\"lottery\"]"
echo "  2. Create and send initialize_lottery instruction"
echo "  3. Parameters:"
echo "     - entry_fee: 10 USDC (10,000,000 tokens)"
echo "     - research_fund_floor: 1000 USDC (1,000,000,000 tokens)"
echo ""
echo "Option 3: Update smart_contract_service.py first"
echo "  - This will allow Python-based initialization"
echo "  - Recommended for integration with your backend"
echo ""

echo -e "${BLUE}=========================================="
echo "Next: Update smart_contract_service.py"
echo "==========================================${NC}"
echo ""

