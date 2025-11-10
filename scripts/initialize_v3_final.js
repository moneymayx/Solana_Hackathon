/**
 * V3 Lottery Initialization - Final Version
 * Uses raw Solana Web3.js instructions (bypasses Anchor Program class)
 * Includes transaction simulation before sending
 */

const {
  Connection,
  PublicKey,
  Keypair,
  Transaction,
  SystemProgram,
  sendAndConfirmTransaction,
} = require("@solana/web3.js");
const {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAccount,
  getAssociatedTokenAddress,
} = require("@solana/spl-token");
const { readFileSync, existsSync } = require("fs");
const { homedir } = require("os");
const path = require("path");

const PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");
const DEVNET_RPC = "https://api.devnet.solana.com";

// Configuration from environment
const JACKPOT_WALLET = new PublicKey(
  process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);
const BACKEND_AUTHORITY = new PublicKey(
  process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);
const USDC_MINT = new PublicKey(
  process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"
);
const RESEARCH_FUND_FLOOR = BigInt(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
const RESEARCH_FEE = BigInt(process.env.V3_RESEARCH_FEE || 10_000_000);

// Instruction discriminator for initializeLottery
// Calculated as: sha256("global:initialize_lottery")[:8]
const INIT_DISCRIMINATOR = Buffer.from([113, 199, 243, 247, 73, 217, 33, 11]);

function serializeU64(value) {
  const buffer = Buffer.allocUnsafe(8);
  buffer.writeBigUInt64LE(BigInt(value), 0);
  return buffer;
}

function serializePubkey(pubkey) {
  return pubkey.toBuffer();
}

function buildInitializeLotteryInstruction(
  lotteryPDA,
  authority,
  jackpotWallet,
  jackpotTokenAccount,
  usdcMint
) {
  // Serialize arguments
  const args = Buffer.concat([
    serializeU64(RESEARCH_FUND_FLOOR),
    serializeU64(RESEARCH_FEE),
    serializePubkey(jackpotWallet),
    serializePubkey(BACKEND_AUTHORITY),
  ]);

  const data = Buffer.concat([INIT_DISCRIMINATOR, args]);

  // Account order matches Rust InitializeLottery struct:
  // lottery, authority, jackpot_wallet, jackpot_token_account, usdc_mint, 
  // token_program, associated_token_program, system_program
  return {
    keys: [
      { pubkey: lotteryPDA, isSigner: false, isWritable: true },
      { pubkey: authority, isSigner: true, isWritable: true },
      { pubkey: jackpotWallet, isSigner: false, isWritable: false },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  };
}

async function main() {
  console.log("🚀 V3 Lottery Initialization (Final Version)\n");

  // Load authority keypair
  const keypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(keypairPath)) {
    console.error("❌ Keypair not found at:", keypairPath);
    process.exit(1);
  }

  const keypairData = JSON.parse(readFileSync(keypairPath, "utf-8"));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log("✅ Authority:", authority.publicKey.toBase58());

  // Connect to devnet
  const connection = new Connection(DEVNET_RPC, "confirmed");
  const balance = await connection.getBalance(authority.publicKey);
  console.log("   Balance:", balance / 1e9, "SOL\n");

  // Derive lottery PDA
  const [lotteryPDA, bump] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    PROGRAM_ID
  );

  console.log("📋 Configuration:");
  console.log("   Program ID:", PROGRAM_ID.toBase58());
  console.log("   Lottery PDA:", lotteryPDA.toBase58());
  console.log("   PDA Bump:", bump);
  console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("   Research Fund Floor:", RESEARCH_FUND_FLOOR.toString() / 1e6, "USDC");
  console.log("");

  // Check if already initialized
  console.log("🔍 Checking if lottery is already initialized...");
  const existingLottery = await connection.getAccountInfo(lotteryPDA);
  if (existingLottery) {
    console.log("✅ Lottery already initialized!");
    console.log("   Account size:", existingLottery.data.length, "bytes");
    return;
  }
  console.log("   Not initialized - proceeding...\n");

  // Get jackpot token account
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log("   Jackpot Token Account:", jackpotTokenAccount.toBase58());

  // Check balance
  try {
    const tokenAccount = await getAccount(connection, jackpotTokenAccount);
    const balanceUSDC = Number(tokenAccount.amount) / 1e6;
    console.log("   Balance:", balanceUSDC, "USDC");

    if (balanceUSDC < Number(RESEARCH_FUND_FLOOR) / 1e6) {
      throw new Error(
        `Insufficient balance: ${balanceUSDC} USDC < ${Number(RESEARCH_FUND_FLOOR) / 1e6} USDC`
      );
    }
    console.log("   ✅ Sufficient balance\n");
  } catch (e) {
    if (e.message?.includes("TokenAccountNotFoundError")) {
      throw new Error("Jackpot token account does not exist! Create it first.");
    }
    throw e;
  }

  // Build instruction
  console.log("📝 Building initialization instruction...");
  const instruction = buildInitializeLotteryInstruction(
    lotteryPDA,
    authority.publicKey,
    JACKPOT_WALLET,
    jackpotTokenAccount,
    USDC_MINT
  );

  // CREATE TRANSACTION FOR SIMULATION
  console.log("🔍 CHECKPOINT 10: Simulating transaction (NO SOL COST)...");
  const transaction = new Transaction().add({
    keys: instruction.keys,
    programId: instruction.programId,
    data: instruction.data,
  });

  const { blockhash } = await connection.getLatestBlockhash();
  transaction.recentBlockhash = blockhash;
  transaction.feePayer = authority.publicKey;
  transaction.sign(authority);

  // SIMULATE
  const simulation = await connection.simulateTransaction(transaction);

  if (simulation.value.err) {
    console.error("❌ STOP - Simulation failed!");
    console.error("Error:", simulation.value.err);
    if (simulation.value.logs) {
      console.error("\nTransaction logs:");
      simulation.value.logs.forEach((log) => console.error("  ", log));
    }
    console.error("\n❌ DO NOT PROCEED - Fix errors before deploying");
    process.exit(1);
  }

  console.log("✅ Simulation successful!");
  console.log("   Compute units:", simulation.value.unitsConsumed);
  if (simulation.value.logs) {
    console.log("\n   Logs preview:");
    simulation.value.logs.slice(0, 10).forEach((log) => console.log("    ", log));
    if (simulation.value.logs.length > 10) {
      console.log(`    ... and ${simulation.value.logs.length - 10} more`);
    }
  }

  // Check for specific errors in logs
  const logsStr = simulation.value.logs.join(" ");
  if (logsStr.includes("DeclaredProgramIdMismatch")) {
    console.error("\n❌ STOP - DeclaredProgramIdMismatch detected!");
    console.error("The deployed binary has wrong program ID embedded.");
    console.error("Must rebuild and redeploy V3 contract first.");
    process.exit(1);
  }

  if (logsStr.includes("AccountNotInitialized") || logsStr.includes("InvalidAccountData")) {
    console.log("\n⚠️  Account creation expected (first initialization)");
  }

  console.log("\n✅ CHECKPOINT 11: Simulation passed - safe to proceed\n");

  // ONLY SEND IF SIMULATION PASSES
  console.log("📤 Sending initialization transaction...");
  try {
    const signature = await sendAndConfirmTransaction(connection, transaction, [authority], {
      commitment: "confirmed",
    });

    console.log("\n✅ Lottery initialized successfully!");
    console.log("   Transaction:", signature);
    console.log(
      "   Explorer:",
      `https://explorer.solana.com/tx/${signature}?cluster=devnet`
    );

    // Verify initialization
    const lotteryAccount = await connection.getAccountInfo(lotteryPDA);
    if (lotteryAccount) {
      console.log("\n✅ Verification: Lottery account exists");
      console.log("   Account size:", lotteryAccount.data.length, "bytes");
    } else {
      console.log("\n⚠️  Warning: Lottery account not found after transaction");
    }

    console.log("\n🎉 V3 lottery is now ready to accept payments!");
  } catch (error) {
    console.error("\n❌ Transaction failed:", error.message);
    if (error.logs) {
      console.error("\nTransaction logs:");
      error.logs.forEach((log) => console.error("  ", log));
    }
    throw error;
  }
}

main().catch((error) => {
  console.error("\n❌ Fatal error:", error);
  process.exit(1);
});

