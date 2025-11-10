/**
 * Initialize V3 Lottery - EXACT test pattern (CommonJS)
 * Uses require() like tests do
 */

const anchor = require("@coral-xyz/anchor");
const { PublicKey, Keypair, SystemProgram, Connection } = require("@solana/web3.js");
const { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } = require("@solana/spl-token");
const { readFileSync, existsSync } = require("fs");
const { homedir } = require("os");
const path = require("path");

const PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");
const DEVNET_RPC = "https://api.devnet.solana.com";

const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");
const RESEARCH_FUND_FLOOR = Number(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
const RESEARCH_FEE = Number(process.env.V3_RESEARCH_FEE || 10_000_000);

async function main() {
  console.log("🚀 Initializing V3 Lottery (Exact Test Pattern)\n");

  // Load IDL exactly like tests: using require()
  const idlPath = path.join(__dirname, "..", "programs", "billions-bounty-v3", "target", "idl", "billions_bounty_v3.json");
  if (!existsSync(idlPath)) {
    console.error("❌ IDL not found");
    process.exit(1);
  }

  const idl = require(idlPath); // Use require like tests
  console.log("✅ IDL loaded via require()");

  // Load authority
  const keypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(keypairPath)) {
    console.error("❌ No keypair found");
    process.exit(1);
  }

  const keypairData = JSON.parse(readFileSync(keypairPath, "utf-8"));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log("✅ Authority:", authority.publicKey.toBase58());

  // Create provider
  const connection = new Connection(DEVNET_RPC, "confirmed");
  const balance = await connection.getBalance(authority.publicKey);
  console.log("   Balance:", balance / 1e9, "SOL\n");

  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });
  anchor.setProvider(provider);

  // Create program exactly like tests
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  console.log("Creating Program...");
  
  let program;
  try {
    program = new anchor.Program(idl, programId, provider);
    console.log("✅ Program created!");
  } catch (error) {
    console.error("❌ Failed to create Program:", error.message);
    throw error;
  }

  // Derive PDA
  const [lotteryPDA] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    PROGRAM_ID
  );

  console.log("\n📋 Configuration:");
  console.log("   Lottery PDA:", lotteryPDA.toBase58());
  console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("   Research Fund Floor:", RESEARCH_FUND_FLOOR / 1e6, "USDC\n");

  // Check if initialized
  const existing = await connection.getAccountInfo(lotteryPDA);
  if (existing) {
    console.log("✅ Already initialized!");
    return;
  }

  // Get token account
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log("Jackpot Token Account:", jackpotTokenAccount.toBase58());

  const tokenAccount = await getAccount(connection, jackpotTokenAccount);
  const balanceUSDC = Number(tokenAccount.amount) / 1e6;
  console.log("Balance:", balanceUSDC, "USDC");
  
  if (balanceUSDC < RESEARCH_FUND_FLOOR / 1e6) {
    console.error("❌ Insufficient balance");
    process.exit(1);
  }
  console.log("✅ Sufficient balance\n");

  // Initialize
  console.log("📝 Initializing...");
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

    console.log("\n✅ Lottery initialized!");
    console.log("Transaction:", tx);
    console.log("Explorer:", `https://explorer.solana.com/tx/${tx}?cluster=devnet`);
    console.log("\n🎉 V3 lottery is ready!");
  } catch (error) {
    console.error("\n❌ Failed:", error.message);
    if (error.logs) {
      console.error("Logs:");
      error.logs.forEach(log => console.error("  ", log));
    }
    throw error;
  }
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});

