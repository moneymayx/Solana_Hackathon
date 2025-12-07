/**
 * Initialize Multi-Bounty V3 Lottery using Raw Instructions
 * Mirrors scripts/initialize_v3_raw.js but loops through all bounty IDs.
 *
 * Based on documentation in docs/V3_INITIALIZATION_COMPLETE_DEBUG.md and
 * scripts/initialize_v3_raw.js (known-good pattern).
 */

const {
  Connection,
  PublicKey,
  Transaction,
  Keypair,
  SystemProgram,
  sendAndConfirmTransaction,
} = require("@solana/web3.js");
const {
  getAssociatedTokenAddress,
  getAccount,
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
} = require("@solana/spl-token");
const { readFileSync, existsSync } = require("fs");
const { homedir } = require("os");
const path = require("path");

// Configuration
const PROGRAM_ID = new PublicKey("7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh");
const DEVNET_RPC = "https://api.devnet.solana.com";

// Environment config
const JACKPOT_WALLET = new PublicKey(
  process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);
const BACKEND_AUTHORITY = new PublicKey(
  process.env.V3_BACKEND_AUTHORITY || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);
const USDC_MINT = new PublicKey(
  process.env.V3_USDC_MINT_DEVNET || "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh" // Devnet test token per docs
);

const BOUNTY_CONFIGS = {
  // Devnet/test values pulled from docs: keep floors tiny so mock USDC supply suffices
  1: { name: "Claude Champ", difficulty: "expert", floor: 10_000_000, fee: 1_000_000 }, // $10 floor, $1 entry
  2: { name: "GPT Gigachad", difficulty: "hard", floor: 5_000_000, fee: 500_000 },     // $5 floor, $0.50 entry
  3: { name: "Gemini Great", difficulty: "medium", floor: 2_500_000, fee: 250_000 },   // $2.50 floor, $0.25 entry
  4: { name: "Llama Legend", difficulty: "easy", floor: 500_000, fee: 100_000 },       // $0.50 floor, $0.10 entry
};

// Instruction discriminator: sha256("global:initialize_lottery")[:8]
const INIT_DISCRIMINATOR = Buffer.from([113, 199, 243, 247, 73, 217, 33, 11]);

function serializeU8(value) {
  return Buffer.from([value & 0xff]);
}

function serializeU64(value) {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

function serializePubkey(pubkey) {
  return Buffer.from(pubkey.toBytes());
}

async function loadAuthorityKeypair() {
  const keypairPath = path.join(homedir(), ".config", "solana", "id.json");
  if (!existsSync(keypairPath)) {
    throw new Error(`Authority keypair not found at ${keypairPath}`);
  }
  const keypairData = JSON.parse(readFileSync(keypairPath, "utf-8"));
  return Keypair.fromSecretKey(Uint8Array.from(keypairData));
}

async function initializeBounty(connection, authority, bountyId, config, jackpotTokenAccount) {
  console.log(`\n${"=".repeat(60)}`);
  console.log(
    `Initializing Bounty ${bountyId}: ${config.name} (${config.difficulty})`
  );
  console.log(`${"=".repeat(60)}`);

  const [lotteryPDA, lotteryBump] = PublicKey.findProgramAddressSync(
    [Buffer.from("lottery"), Buffer.from([bountyId])],
    PROGRAM_ID
  );

  console.log("Lottery PDA:", lotteryPDA.toBase58());
  console.log("Bump:", lotteryBump);

  // Skip if already initialized
  const existing = await connection.getAccountInfo(lotteryPDA);
  if (existing) {
    console.log("✅ Already initialized. Skipping...");
    return { bountyId, alreadyInitialized: true };
  }

  // Check funding for this bounty
  const tokenAccount = await getAccount(connection, jackpotTokenAccount);
  const balance = Number(tokenAccount.amount);
  if (balance < config.floor) {
    throw new Error(
      `Insufficient USDC for bounty ${bountyId}. Have ${balance}, need ${config.floor}`
    );
  }

  // Serialize args: bounty_id (u8) +
  // researchFundFloor (u64) + researchFee (u64) +
  // jackpotWallet (32) + backendAuthority (32)
  const args = Buffer.concat([
    serializeU8(bountyId),
    serializeU64(config.floor),
    serializeU64(config.fee),
    serializePubkey(JACKPOT_WALLET),
    serializePubkey(BACKEND_AUTHORITY),
  ]);

  const data = Buffer.concat([INIT_DISCRIMINATOR, args]);

  const instruction = {
    keys: [
      { pubkey: lotteryPDA, isSigner: false, isWritable: true },
      { pubkey: authority.publicKey, isSigner: true, isWritable: true },
      { pubkey: JACKPOT_WALLET, isSigner: false, isWritable: false },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: USDC_MINT, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  };

  const tx = new Transaction().add(instruction);
  const { blockhash } = await connection.getLatestBlockhash();
  tx.recentBlockhash = blockhash;
  tx.feePayer = authority.publicKey;
  tx.sign(authority);

  console.log("📤 Sending transaction...");
  const signature = await sendAndConfirmTransaction(connection, tx, [authority], {
    commitment: "confirmed",
    maxRetries: 3,
  });

  console.log("✅ Bounty initialized!");
  console.log(`   Transaction: ${signature}`);
  console.log(
    `   Explorer: https://explorer.solana.com/tx/${signature}?cluster=devnet`
  );

  return { bountyId, lotteryPDA: lotteryPDA.toBase58(), signature };
}

async function main() {
  console.log("🚀 Initializing Multi-Bounty V3 Lottery (Raw Instructions)\n");

  const connection = new Connection(DEVNET_RPC, "confirmed");
  const authority = await loadAuthorityKeypair();

  console.log("Authority:", authority.publicKey.toBase58());
  const balance = await connection.getBalance(authority.publicKey);
  console.log("Balance:", balance / 1e9, "SOL\n");

  const jackpotTokenAccount = await getAssociatedTokenAddress(
    USDC_MINT,
    JACKPOT_WALLET
  );
  console.log("Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("Jackpot Token Account:", jackpotTokenAccount.toBase58());
  console.log("Backend Authority:", BACKEND_AUTHORITY.toBase58());

  const results = [];

  for (const [bountyIdStr, config] of Object.entries(BOUNTY_CONFIGS)) {
    const bountyId = Number(bountyIdStr);
    try {
      const result = await initializeBounty(
        connection,
        authority,
        bountyId,
        config,
        jackpotTokenAccount
      );
      results.push({ ...result, success: true });
    } catch (error) {
      console.error(`❌ Failed to initialize bounty ${bountyId}:`, error.message);
      results.push({ bountyId, success: false, error: error.message });
    }
  }

  console.log(`\n${"=".repeat(60)}`);
  console.log("Summary");
  console.log(`${"=".repeat(60)}`);
  results.forEach((result) => {
    if (result.success) {
      if (result.alreadyInitialized) {
        console.log(`✅ Bounty ${result.bountyId}: Already initialized`);
      } else {
        console.log(`✅ Bounty ${result.bountyId}: Initialized (PDA ${result.lotteryPDA})`);
      }
    } else {
      console.log(`❌ Bounty ${result.bountyId}: ${result.error}`);
    }
  });

  const failures = results.filter((r) => !r.success);
  if (failures.length > 0) {
    process.exit(1);
  }

  console.log("\n🎉 All bounties initialized successfully!");
}

main().catch((error) => {
  console.error("❌ Fatal error:", error);
  process.exit(1);
});


