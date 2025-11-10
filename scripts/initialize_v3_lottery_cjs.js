/**
 * Initialize V3 Lottery on Devnet
 * CommonJS version - matches test pattern exactly
 */

const anchor = require("@coral-xyz/anchor");
const { PublicKey, Keypair, SystemProgram, Connection } = require("@solana/web3.js");
const { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } = require("@solana/spl-token");
const { readFileSync, existsSync } = require("fs");
const { homedir } = require("os");
const path = require("path");

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

  // Load IDL (CommonJS require)
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

  const idl = require(idlPath);
  
  // Patch IDL: Add size field to accounts (required by Anchor)
  // From Rust: Lottery::LEN = 32 + 32 + 32 + 8 + 8 + 8 + 8 + 8 + 8 + 1 + 1 + 8 + 8 + 8 = 186
  // Discriminator adds 8, so total = 194
  // Entry::LEN = 32 + 8 + 8 + 8 + 8 + 1 = 65, plus discriminator = 73
  if (idl.accounts) {
    const lotteryAccount = idl.accounts.find(a => a.name === "lottery");
    if (lotteryAccount) {
      // Add size directly on account if not present
      if (!lotteryAccount.size) {
        lotteryAccount.size = 194; // 8 (discriminator) + 186 (LEN from Rust)
      }
      // Also ensure type.size exists
      if (lotteryAccount.type && !lotteryAccount.type.size) {
        lotteryAccount.type.size = 194;
      }
    }
    const entryAccount = idl.accounts.find(a => a.name === "entry");
    if (entryAccount) {
      if (!entryAccount.size) {
        entryAccount.size = 73; // 8 (discriminator) + 65 (LEN from Rust)
      }
      if (entryAccount.type && !entryAccount.type.size) {
        entryAccount.type.size = 73;
      }
    }
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

  // Create connection and provider
  const connection = new Connection(DEVNET_RPC, "confirmed");
  const balance = await connection.getBalance(authority.publicKey);
  console.log("   Balance:", balance / 1e9, "SOL\n");

  // Create wallet and provider
  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });
  anchor.setProvider(provider);

  // Load program (matching test pattern exactly)
  // Add size to accounts if missing (workaround for Anchor account client issue)
  if (idl.accounts) {
    idl.accounts.forEach(account => {
      if (account.type && account.type.fields && !account.type.size) {
        // Estimate size from fields (discriminator + fields)
        let estimatedSize = 8; // discriminator
        account.type.fields.forEach(field => {
          if (field.type === 'pubkey') estimatedSize += 32;
          else if (field.type === 'u64') estimatedSize += 8;
          else if (field.type === 'u32') estimatedSize += 4;
          else if (field.type === 'i64') estimatedSize += 8;
          else if (field.type === 'bool') estimatedSize += 1;
          else if (field.type === 'string') estimatedSize += 4 + 100; // rough estimate
        });
        account.type.size = estimatedSize;
      }
    });
  }
  
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  const program = new anchor.Program(idl, programId, provider);

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
  } catch (e) {
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
  } catch (error) {
    console.error("\n❌ Initialization failed:", error.message);
    if (error.logs) {
      console.error("\nTransaction logs:");
      error.logs.forEach((log) => console.error("  ", log));
    }
    if (error.error) {
      console.error("\nError details:", JSON.stringify(error.error, null, 2));
    }
    throw error;
  }
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});

