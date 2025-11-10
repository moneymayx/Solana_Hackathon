/**
 * Initialize V3 Lottery on Devnet
 * Based on working test pattern from security_fixes.spec.ts
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } from "@solana/spl-token";
import { Connection } from "@solana/web3.js";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import * as path from "path";

// Configuration
const PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");
const DEVNET_RPC = "https://api.devnet.solana.com";

// Environment-based config
const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");
const RESEARCH_FUND_FLOOR = Number(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
const RESEARCH_FEE = Number(process.env.V3_RESEARCH_FEE || 10_000_000);

async function main() {
  console.log("🚀 Initializing V3 Lottery on Devnet\n");

  // Load IDL using require (CommonJS style, works better than ES modules)
  const idlPath = path.join(
    __dirname,
    "..",
    "programs",
    "billions-bounty-v3",
    "target",
    "idl",
    "billions_bounty_v3.json"
  );

  if (!existsSync(idlPath)) {
    console.error("❌ IDL file not found:", idlPath);
    console.error("   Run: cd programs/billions-bounty-v3 && anchor build");
    process.exit(1);
  }

  // Use eval to load IDL as CommonJS (works around ES module issues)
  const idl = JSON.parse(readFileSync(idlPath, "utf-8"));

  // Load authority keypair
  const defaultKeypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(defaultKeypairPath)) {
    console.error("❌ No authority keypair found!");
    console.error("   Set ANCHOR_WALLET or use Solana CLI default wallet");
    process.exit(1);
  }

  const keypairData = JSON.parse(readFileSync(defaultKeypairPath, "utf-8"));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log("✅ Authority:", authority.publicKey.toBase58());

  // Create connection and provider
  const connection = new Connection(DEVNET_RPC, "confirmed");
  const balance = await connection.getBalance(authority.publicKey);
  console.log("   Balance:", balance / 1e9, "SOL\n");

  // Create wallet and provider manually (like tests do)
  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });
  anchor.setProvider(provider);

  // Load program (matching test pattern exactly)
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  const program = new anchor.Program(idl as anchor.Idl, programId, provider);

  console.log("📋 Configuration:");
  console.log("   Program ID:", PROGRAM_ID.toBase58());
  console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("   Backend Authority:", BACKEND_AUTHORITY.toBase58());
  console.log("   USDC Mint:", USDC_MINT.toBase58());
  console.log("   Research Fund Floor:", RESEARCH_FUND_FLOOR / 1e6, "USDC");
  console.log("   Research Fee:", RESEARCH_FEE / 1e6, "USDC\n");

  // Derive lottery PDA
  const [lotteryPDA, lotteryBump] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    PROGRAM_ID
  );
  console.log("   Lottery PDA:", lotteryPDA.toBase58());
  console.log("   Bump:", lotteryBump, "\n");

  // Check if lottery already exists
  console.log("🔍 Checking if lottery is already initialized...");
  const existingLottery = await connection.getAccountInfo(lotteryPDA);
  if (existingLottery) {
    console.log("✅ Lottery already initialized!");
    console.log("   Account:", lotteryPDA.toBase58());
    return;
  }
  console.log("❌ Lottery not initialized - proceeding...\n");

  // Get jackpot token account (ATA)
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log("   Jackpot Token Account:", jackpotTokenAccount.toBase58());

  // Check token account exists and has sufficient balance
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
  } catch (e: any) {
    if (e.message?.includes("TokenAccountNotFoundError")) {
      console.error("❌ Token account does not exist!");
      console.error("   Create it first:");
      console.error(`   spl-token create-account ${USDC_MINT.toBase58()} --owner ${JACKPOT_WALLET.toBase58()} --url devnet`);
      process.exit(1);
    }
    throw e;
  }

  // Initialize lottery (exactly matching test pattern)
  console.log("📝 Initializing lottery...");
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

