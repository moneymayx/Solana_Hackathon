/**
 * Initialize Multi-Bounty V3 Lottery - Using exact test pattern
 * Initializes all 4 bounties with appropriate parameters for the V3 multi-bounty contract.
 * 
 * Bounty Configuration:
 * - Bounty 1 (Expert): $10,000 floor, $10 entry
 * - Bounty 2 (Hard): $5,000 floor, $5 entry
 * - Bounty 3 (Medium): $2,500 floor, $2.50 entry
 * - Bounty 4 (Easy): $500 floor, $0.50 entry
 * 
 * Based on scripts/initialize_v3_from_test.ts pattern
 */

import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddress } from "@solana/spl-token";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import * as path from "path";
import { fileURLToPath } from "url";

// Get __dirname for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const PROGRAM_ID = new PublicKey("7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh");
const DEVNET_RPC = "https://api.devnet.solana.com";

const JACKPOT_WALLET = new PublicKey(process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");

// Bounty configurations
const BOUNTY_CONFIGS = {
  1: {
    name: "Claude Champ",
    difficulty: "expert",
    researchFundFloor: 10_000_000, // $10 in USDC units (6 decimals)
    researchFee: 1_000_000, // $1
  },
  2: {
    name: "GPT Gigachad",
    difficulty: "hard",
    researchFundFloor: 5_000_000, // $5
    researchFee: 500_000, // $0.50
  },
  3: {
    name: "Gemini Great",
    difficulty: "medium",
    researchFundFloor: 2_500_000, // $2.50
    researchFee: 250_000, // $0.25
  },
  4: {
    name: "Llama Legend",
    difficulty: "easy",
    researchFundFloor: 500_000, // $0.50
    researchFee: 100_000, // $0.10
  },
};

async function main() {
  console.log("🚀 Initializing Multi-Bounty V3 Lottery (Using Test Pattern)\n");

  // Load IDL exactly like tests do
  const idlPath = path.join(__dirname, "..", "target", "idl", "billions_bounty_v3.json");
  if (!existsSync(idlPath)) {
    console.error("❌ IDL not found:", idlPath);
    process.exit(1);
  }

  const idlContent = readFileSync(idlPath, "utf-8");
  const idl = JSON.parse(idlContent);
  
  // IDL should already have sizes patched from the manual fix script
  // But double-check and add if missing (defensive)
  if (idl.accounts) {
    idl.accounts.forEach((account: any) => {
      if (account.name === "lottery") {
        if (!account.size) account.size = 194;
        if (account.type) {
          if (typeof account.type === "object" && !account.type.size) {
            account.type.size = 194;
          }
        }
      } else if (account.name === "entry") {
        if (!account.size) account.size = 73;
        if (account.type) {
          if (typeof account.type === "object" && !account.type.size) {
            account.type.size = 73;
          }
        }
      } else if (account.name === "userBountyState") {
        if (!account.size) account.size = 49; // 32 + 1 + 8 + 8
        if (account.type) {
          if (typeof account.type === "object" && !account.type.size) {
            account.type.size = 49;
          }
        }
      }
    });
  }
  if (idl.types) {
    idl.types.forEach((t: any) => {
      if (t.name === "Lottery" || t.name === "lottery") {
        if (t.type && !t.type.size) {
          t.type.size = 194;
        }
      } else if (t.name === "Entry" || t.name === "entry") {
        if (t.type && !t.type.size) {
          t.type.size = 73;
        }
      } else if (t.name === "UserBountyState" || t.name === "userBountyState") {
        if (t.type && !t.type.size) {
          t.type.size = 49;
        }
      } else if (t.type && !t.type.size && t.type.fields) {
        // Calculate size from fields
        let calcSize = 8; // discriminator
        t.type.fields.forEach((f: any) => {
          if (f.type === "pubkey" || f.type === "publicKey") calcSize += 32;
          else if (f.type === "u64") calcSize += 8;
          else if (f.type === "i64") calcSize += 8;
          else if (f.type === "bool") calcSize += 1;
          else if (f.type === "u8") calcSize += 1;
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
  const connection = new anchor.web3.Connection(DEVNET_RPC, "confirmed");
  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(connection, wallet, {
    commitment: "confirmed",
  });
  anchor.setProvider(provider);

  // Load program exactly like tests do
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  const program = new anchor.Program(idl, programId, provider);

  console.log("✅ Program created");
  console.log("   Program ID:", PROGRAM_ID.toBase58());
  console.log("   Network: devnet\n");

  // Get jackpot token account
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log("   Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("   Jackpot Token Account:", jackpotTokenAccount.toBase58());
  console.log("   Backend Authority:", BACKEND_AUTHORITY.toBase58());
  console.log("   USDC Mint:", USDC_MINT.toBase58());

  // Check balance
  try {
    const tokenAccount = await getAccount(connection, jackpotTokenAccount);
    const balance = Number(tokenAccount.amount) / 1e6;
    console.log("   Balance:", balance, "USDC");
    const minRequired = Math.max(...Object.values(BOUNTY_CONFIGS).map(c => c.researchFundFloor / 1e6));
    if (balance < minRequired) {
      console.error(`❌ Insufficient balance! Need at least ${minRequired} USDC`);
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

  // Initialize all bounties
  interface BountyResult {
    bountyId: number;
    success: boolean;
    lotteryPDA?: string;
    tx?: string;
    error?: string;
  }
  const results: BountyResult[] = [];

  for (const [bountyIdStr, config] of Object.entries(BOUNTY_CONFIGS)) {
    const bountyId = parseInt(bountyIdStr);
    console.log(`\n${"=".repeat(60)}`);
    console.log(`Initializing Bounty ${bountyId}: ${config.name} (${config.difficulty})`);
    console.log(`${"=".repeat(60)}`);
    const floorUsd = (config.researchFundFloor / 1e6).toFixed(2);
    const feeUsd = (config.researchFee / 1e6).toFixed(2);
    console.log(`  Research Fund Floor: $${floorUsd} (${config.researchFundFloor.toLocaleString()} USDC units)`);
    console.log(`  Research Fee: $${feeUsd} (${config.researchFee.toLocaleString()} USDC units)`);

    try {
      // Derive lottery PDA for this bounty (using bounty_id in seeds)
      const [lotteryPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("lottery"), Buffer.from([bountyId])],
        program.programId
      );
      console.log(`  Lottery PDA: ${lotteryPDA.toBase58()}`);

      // Check if already initialized
      const existingLottery = await connection.getAccountInfo(lotteryPDA);
      if (existingLottery) {
        console.log(`  ✅ Bounty ${bountyId} already initialized! Skipping...`);
        results.push({
          bountyId,
          success: true,
          lotteryPDA: lotteryPDA.toBase58(),
        });
        continue;
      }

      // Derive jackpot token account for this bounty's lottery PDA
      const bountyJackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, lotteryPDA);
      console.log(`  Bounty Jackpot Token Account: ${bountyJackpotTokenAccount.toBase58()}`);

      // Initialize exactly like tests do
      console.log(`  📝 Initializing bounty ${bountyId}...`);
      const tx = await program.methods
        .initializeLottery(
          bountyId,
          new anchor.BN(config.researchFundFloor),
          new anchor.BN(config.researchFee),
          JACKPOT_WALLET,
          BACKEND_AUTHORITY
        )
        .accounts({
          lottery: lotteryPDA,
          authority: authority.publicKey,
          jackpotWallet: JACKPOT_WALLET,
          jackpotTokenAccount: bountyJackpotTokenAccount,
          usdcMint: USDC_MINT,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .rpc();

      console.log(`  ✅ Bounty ${bountyId} initialized successfully!`);
      console.log(`     Transaction: ${tx}`);
      console.log(`     Explorer: https://explorer.solana.com/tx/${tx}?cluster=devnet`);

      results.push({
        bountyId,
        success: true,
        lotteryPDA: lotteryPDA.toBase58(),
        tx,
      });

      // Small delay between initializations
      if (bountyId < 4) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    } catch (error: any) {
      console.error(`  ❌ Error initializing bounty ${bountyId}:`, error.message);
      if (error.logs) {
        console.error("  Transaction logs:");
        error.logs.forEach((log: string) => console.error("    ", log));
      }
      results.push({
        bountyId,
        success: false,
        error: error.message,
      });
    }
  }

  // Print summary
  console.log(`\n${"=".repeat(60)}`);
  console.log("Initialization Summary");
  console.log(`${"=".repeat(60)}`);

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  for (const result of results) {
    if (result.success) {
      const config = BOUNTY_CONFIGS[result.bountyId as keyof typeof BOUNTY_CONFIGS];
      console.log(`✅ Bounty ${result.bountyId} (${config.name}): Initialized`);
      if (result.lotteryPDA) {
        console.log(`   PDA: ${result.lotteryPDA}`);
      }
      if (result.tx) {
        console.log(`   TX: ${result.tx}`);
      }
    } else {
      console.log(`❌ Bounty ${result.bountyId}: Failed - ${result.error || "Unknown error"}`);
    }
  }

  console.log(`\nTotal: ${successful.length} successful, ${failed.length} failed`);

  if (failed.length > 0) {
    process.exit(1);
  }

  console.log("\n🎉 All bounties initialized successfully!");
}

main().catch((error) => {
  console.error("❌ Error:", error);
  process.exit(1);
});

