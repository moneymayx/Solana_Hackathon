/**
 * Initialize V3 Lottery using Raw Instructions
 * Bypasses Anchor Program class to avoid IDL issues
 */

const { Connection, PublicKey, Transaction, Keypair, SystemProgram } = require("@solana/web3.js");
const { getAssociatedTokenAddress, getAccount, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } = require("@solana/spl-token");
const { sendAndConfirmTransaction } = require("@solana/web3.js");
const { readFileSync, existsSync } = require("fs");
const { homedir } = require("os");
const path = require("path");
const { sha256 } = require("@noble/hashes/sha256");

// Configuration
const PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");
const DEVNET_RPC = "https://api.devnet.solana.com";

// Environment config
const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");
const RESEARCH_FUND_FLOOR = Number(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
const RESEARCH_FEE = Number(process.env.V3_RESEARCH_FEE || 10_000_000);

// Instruction discriminator: sha256("global:initialize_lottery")[:8]
const INIT_DISCRIMINATOR = Buffer.from([113, 199, 243, 247, 73, 217, 33, 11]);

function serializeU64(value) {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

function serializePubkey(pubkey) {
  return Buffer.from(pubkey.toBytes());
}

async function main() {
  console.log("🚀 Initializing V3 Lottery on Devnet (Raw Instructions)\n");

  const connection = new Connection(DEVNET_RPC, "confirmed");

  // Load authority keypair
  const defaultKeypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(defaultKeypairPath)) {
    console.error("❌ No authority keypair found!");
    process.exit(1);
  }

  const keypairData = JSON.parse(readFileSync(defaultKeypairPath, "utf-8"));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log("✅ Authority:", authority.publicKey.toBase58());

  const balance = await connection.getBalance(authority.publicKey);
  console.log("   Balance:", balance / 1e9, "SOL\n");

  // Derive lottery PDA
  const [lotteryPDA, lotteryBump] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    PROGRAM_ID
  );

  console.log("📋 Configuration:");
  console.log("   Program ID:", PROGRAM_ID.toBase58());
  console.log("   Lottery PDA:", lotteryPDA.toBase58());
  console.log("   Bump:", lotteryBump);
  console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("   Backend Authority:", BACKEND_AUTHORITY.toBase58());
  console.log("   USDC Mint:", USDC_MINT.toBase58());
  console.log("   Research Fund Floor:", RESEARCH_FUND_FLOOR / 1e6, "USDC");
  console.log("   Research Fee:", RESEARCH_FEE / 1e6, "USDC\n");

  // Check if already initialized
  console.log("🔍 Checking if lottery is already initialized...");
  const existingLottery = await connection.getAccountInfo(lotteryPDA);
  if (existingLottery) {
    console.log("✅ Lottery already initialized!");
    console.log("   Account:", lotteryPDA.toBase58());
    return;
  }
  console.log("❌ Lottery not initialized - proceeding...\n");

  // Get jackpot token account
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log("   Jackpot Token Account:", jackpotTokenAccount.toBase58());

  // Check balance
  try {
    const tokenAccount = await getAccount(connection, jackpotTokenAccount);
    const balance = Number(tokenAccount.amount) / 1e6;
    console.log("   Balance:", balance, "USDC");

    if (balance < RESEARCH_FUND_FLOOR / 1e6) {
      console.error("❌ Insufficient balance!");
      console.error(`   Have: ${balance} USDC`);
      console.error(`   Need: ${RESEARCH_FUND_FLOOR / 1e6} USDC`);
      process.exit(1);
    }
    console.log("   ✅ Sufficient balance\n");
  } catch (e) {
    if (e.message?.includes("TokenAccountNotFoundError")) {
      console.error("❌ Token account does not exist!");
      process.exit(1);
    }
    throw e;
  }

  // Build raw instruction
  console.log("📝 Building initialization instruction...");
  
  // Serialize args: researchFundFloor (u64) + researchFee (u64) + jackpotWallet (32) + backendAuthority (32)
  const args = Buffer.concat([
    serializeU64(RESEARCH_FUND_FLOOR),
    serializeU64(RESEARCH_FEE),
    serializePubkey(JACKPOT_WALLET),
    serializePubkey(BACKEND_AUTHORITY),
  ]);

  const data = Buffer.concat([INIT_DISCRIMINATOR, args]);

  // Account order MUST match Rust InitializeLottery struct exactly:
  // lottery, authority, jackpot_wallet, jackpot_token_account, usdc_mint, token_program, associated_token_program, system_program
  const instruction = {
    keys: [
      { pubkey: lotteryPDA, isSigner: false, isWritable: true },      // lottery PDA
      { pubkey: authority.publicKey, isSigner: true, isWritable: true }, // authority (signer, mut)
      { pubkey: JACKPOT_WALLET, isSigner: false, isWritable: false },     // jackpot_wallet (not mut in Rust)
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true }, // jackpot_token_account (mut in Rust)
      { pubkey: USDC_MINT, isSigner: false, isWritable: false },          // usdc_mint
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },  // token_program
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }, // associated_token_program
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }, // system_program
    ],
    programId: PROGRAM_ID,
    data,
  };

  // Create and send transaction
  const tx = new Transaction().add(instruction);
  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();
  tx.recentBlockhash = blockhash;
  tx.feePayer = authority.publicKey;

  console.log("✍️  Signing transaction...");
  tx.sign(authority);

  console.log("📤 Sending transaction to devnet...");
  try {
    const signature = await sendAndConfirmTransaction(
      connection,
      tx,
      [authority],
      { commitment: "confirmed", maxRetries: 3 }
    );

    console.log("\n✅ Lottery initialized successfully!");
    console.log("   Transaction:", signature);
    console.log("   Explorer:", `https://explorer.solana.com/tx/${signature}?cluster=devnet`);
    console.log("\n🎉 V3 lottery is now ready to accept payments!");
  } catch (error) {
    console.error("\n❌ Initialization failed:", error.message);
    if (error.logs) {
      console.error("\nTransaction logs:");
      error.logs.forEach((log) => console.error("  ", log));
    }
    throw error;
  }
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});

