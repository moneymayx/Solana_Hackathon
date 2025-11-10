/**
 * Initialize V3 Lottery - Using exact test pattern
 * This script mimics how tests successfully initialize the lottery
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
// Types import not needed for basic initialization
// import { BillionsBountyV3 } from "../programs/billions-bounty-v3/target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } from "@solana/spl-token";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import * as path from "path";

// Configuration - use existing wallets
const PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");
const DEVNET_RPC = "https://api.devnet.solana.com";

const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");
const RESEARCH_FUND_FLOOR = Number(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
const RESEARCH_FEE = Number(process.env.V3_RESEARCH_FEE || 10_000_000);

async function main() {
  console.log("🚀 Initializing V3 Lottery (Using Test Pattern)\n");

  // Load IDL exactly like tests do
  const idlPath = path.join(__dirname, "..", "programs", "billions-bounty-v3", "target", "idl", "billions_bounty_v3.json");
  if (!existsSync(idlPath)) {
    console.error("❌ IDL not found:", idlPath);
    process.exit(1);
  }

  const idlContent = readFileSync(idlPath, "utf-8");
  const idl = JSON.parse(idlContent);
  
  // IDL should already have sizes patched from the manual fix script
  // But double-check and add if missing (defensive)
  if (idl.accounts) {
    const lotteryAccount = idl.accounts.find((a: any) => a.name === "lottery");
    if (lotteryAccount) {
      if (!lotteryAccount.size) lotteryAccount.size = 194;
      if (lotteryAccount.type && !lotteryAccount.type.size) lotteryAccount.type.size = 194;
    }
    const entryAccount = idl.accounts.find((a: any) => a.name === "entry");
    if (entryAccount) {
      if (!entryAccount.size) entryAccount.size = 73;
      if (entryAccount.type && !entryAccount.type.size) entryAccount.type.size = 73;
    }
  }
  if (idl.types) {
    idl.types.forEach((t: any) => {
      if (t.type && !t.type.size && t.type.fields) {
        // Calculate size from fields
        let calcSize = 8; // discriminator
        t.type.fields.forEach((f: any) => {
          if (f.type === "pubkey") calcSize += 32;
          else if (f.type === "u64") calcSize += 8;
          else if (f.type === "i64") calcSize += 8;
          else if (f.type === "bool") calcSize += 1;
        });
        t.type.size = calcSize;
      }
    });
  }
  
  console.log("✅ IDL loaded and patched");

  // Load authority keypair
  const defaultKeypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(defaultKeypairPath)) {
    console.error("❌ No authority keypair found!");
    process.exit(1);
  }

  const keypairData = JSON.parse(readFileSync(defaultKeypairPath, "utf-8"));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log("✅ Authority:", authority.publicKey.toBase58());

  // Create provider using Anchor's environment setup (like tests)
  // But manually specify devnet
  const connection = new anchor.web3.Connection(DEVNET_RPC, "confirmed");
  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });
  anchor.setProvider(provider);

  // Load program exactly like tests do
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  
  // Create program (like tests but without strict typing)
  const program = new anchor.Program(idl, programId, provider);

  console.log("✅ Program created");

  // Derive lottery PDA
  const [lotteryPDA] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    program.programId
  );

  console.log("\n📋 Configuration:");
  console.log("   Program ID:", PROGRAM_ID.toBase58());
  console.log("   Lottery PDA:", lotteryPDA.toBase58());
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
      process.exit(1);
    }
    console.log("   ✅ Sufficient balance\n");
  } catch (e: any) {
    if (e.message?.includes("TokenAccountNotFoundError")) {
      console.error("❌ Token account does not exist!");
      process.exit(1);
    }
    throw e;
  }

  // Initialize exactly like tests do
  console.log("📝 Initializing lottery (using test pattern)...");
  try {
    const tx = await program.methods
      .initializeLottery(
        new anchor.BN(RESEARCH_FUND_FLOOR),
        new anchor.BN(RESEARCH_FEE),
        JACKPOT_WALLET,
        BACKEND_AUTHORITY
      )
      .accounts({
        lottery: lotteryPDA,
        authority: authority.publicKey,
        jackpotWallet: JACKPOT_WALLET,
        jackpotTokenAccount: jackpotTokenAccount,
        usdcMint: USDC_MINT,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .rpc();

    console.log("\n✅ Lottery initialized successfully!");
    console.log("   Transaction:", tx);
    console.log("   Explorer:", `https://explorer.solana.com/tx/${tx}?cluster=devnet`);
    console.log("\n🎉 V3 lottery is now ready to accept payments!");
  } catch (error: any) {
    console.error("\n❌ Initialization failed:", error.message);
    if (error.logs) {
      console.error("\nTransaction logs:");
      error.logs.forEach((log: string) => console.error("  ", log));
    }
    if (error.error) {
      console.error("\nError details:", JSON.stringify(error.error, null, 2));
    }
    throw error;
  }
}

// Get __dirname for ES modules
import { fileURLToPath } from "url";
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});

