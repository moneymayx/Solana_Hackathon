/**
 * Initialize Lottery on Devnet
 * Minimal test to initialize V3 lottery using Anchor test framework
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } from "@solana/spl-token";
import { expect } from "chai";

describe("Initialize Lottery on Devnet", function () {
  this.timeout(120000); // 2 minute timeout
  
  // Use environment provider (reads from ANCHOR_PROVIDER_URL and ANCHOR_WALLET)
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  // Load program directly from IDL
  const idl = require("../target/idl/billions_bounty_v3.json");
  const programId = new anchor.web3.PublicKey("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");
  const program = new anchor.Program(idl, programId, provider) as Program<BillionsBountyV3>;

  // Configuration - use existing wallets
  const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
  const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
  const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");
  const RESEARCH_FUND_FLOOR = new anchor.BN(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
  const RESEARCH_FEE = new anchor.BN(process.env.V3_RESEARCH_FEE || 10_000_000);

  it("Initializes lottery on devnet", async () => {
    console.log("\n🚀 Initializing V3 Lottery on Devnet\n");

    // Get authority from provider
    const authority = provider.wallet as anchor.Wallet;
    console.log("✅ Authority:", authority.publicKey.toBase58());
    
    const balance = await provider.connection.getBalance(authority.publicKey);
    console.log("   Balance:", balance / 1e9, "SOL\n");

    // Derive lottery PDA
    const [lotteryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("lottery")],
      program.programId
    );

    console.log("📋 Configuration:");
    console.log("   Program ID:", program.programId.toBase58());
    console.log("   Lottery PDA:", lotteryPDA.toBase58());
    console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
    console.log("   Backend Authority:", BACKEND_AUTHORITY.toBase58());
    console.log("   USDC Mint:", USDC_MINT.toBase58());
    console.log("   Research Fund Floor:", RESEARCH_FUND_FLOOR.toNumber() / 1e6, "USDC");
    console.log("   Research Fee:", RESEARCH_FEE.toNumber() / 1e6, "USDC\n");

    // Check if already initialized
    console.log("🔍 Checking if lottery is already initialized...");
    const existingLottery = await provider.connection.getAccountInfo(lotteryPDA);
    if (existingLottery) {
      console.log("✅ Lottery already initialized!");
      console.log("   Account:", lotteryPDA.toBase58());
      expect(existingLottery).to.not.be.null;
      return;
    }
    console.log("❌ Lottery not initialized - proceeding...\n");

    // Get jackpot token account
    const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
    console.log("   Jackpot Token Account:", jackpotTokenAccount.toBase58());

    // Check balance
    try {
      const tokenAccount = await getAccount(provider.connection, jackpotTokenAccount);
      const balanceUSDC = Number(tokenAccount.amount) / 1e6;
      console.log("   Balance:", balanceUSDC, "USDC");

      if (balanceUSDC < RESEARCH_FUND_FLOOR.toNumber() / 1e6) {
        throw new Error(`Insufficient balance: ${balanceUSDC} USDC < ${RESEARCH_FUND_FLOOR.toNumber() / 1e6} USDC`);
      }
      console.log("   ✅ Sufficient balance\n");
    } catch (e: any) {
      if (e.message?.includes("TokenAccountNotFoundError")) {
        throw new Error("Jackpot token account does not exist! Create it first.");
      }
      throw e;
    }

    // Initialize lottery
    console.log("📝 Initializing lottery...");
    try {
      const tx = await program.methods
        .initializeLottery(
          RESEARCH_FUND_FLOOR,
          RESEARCH_FEE,
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

      // Verify initialization
      const lotteryAccount = await program.account.lottery.fetch(lotteryPDA);
      expect(lotteryAccount.authority.toBase58()).to.equal(authority.publicKey.toBase58());
      expect(lotteryAccount.jackpotWallet.toBase58()).to.equal(JACKPOT_WALLET.toBase58());
      console.log("\n✅ Verification passed!");
    } catch (error: any) {
      console.error("\n❌ Initialization failed:", error.message);
      if (error.logs) {
        console.error("\nTransaction logs:");
        error.logs.forEach((log: string) => console.error("  ", log));
      }
      throw error;
    }
  });
});

