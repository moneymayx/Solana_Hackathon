import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  TransactionInstruction,
  Transaction,
  sendAndConfirmTransaction,
} from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAssociatedTokenAddress, createAssociatedTokenAccountInstruction } from "@solana/spl-token";
import * as fs from "fs";
import * as crypto from "crypto";

// Program ID for v2 (deployed)
const PROGRAM_ID = new PublicKey("GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm");

// Method discriminators (8-byte Anchor method hash)
const INITIALIZE_LOTTERY_DISCRIMINATOR = Buffer.from(
  crypto.createHash("sha256").update("global:initialize_lottery").digest().slice(0, 8)
);
const INITIALIZE_BOUNTY_DISCRIMINATOR = Buffer.from(
  crypto.createHash("sha256").update("global:initialize_bounty").digest().slice(0, 8)
);

// Helper to serialize u64 as little-endian
function u64LE(n: number): Buffer {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(n), 0);
  return buf;
}

// Helper to serialize public key
function pubkeyBytes(key: PublicKey): Buffer {
  return Buffer.from(key.toBytes());
}

async function main() {
  const connection = new Connection(
    process.env.ANCHOR_PROVIDER_URL || "https://api.devnet.solana.com",
    "confirmed"
  );
  const walletPath = process.env.ANCHOR_WALLET || `${process.env.HOME}/.config/solana/id.json`;
  const payer = Keypair.fromSecretKey(
    new Uint8Array(JSON.parse(fs.readFileSync(walletPath, "utf8")))
  );

  const bountyPoolWallet = new PublicKey(process.env.BOUNTY_POOL_WALLET!);
  const operationalWallet = new PublicKey(process.env.OPERATIONAL_WALLET!);
  const buybackWallet = new PublicKey(process.env.BUYBACK_WALLET!);
  const stakingWallet = new PublicKey(process.env.STAKING_WALLET!);
  // Use a test SPL token mint on devnet (or set USDC_MINT env var)
  // For demo: you can create your own devnet SPL token and set here
  const usdcMint = new PublicKey(
    process.env.USDC_MINT || "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr" // devnet test token
  );

  // Derive PDAs
  const [globalPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("global")],
    PROGRAM_ID
  );
  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), u64LE(1)],
    PROGRAM_ID
  );

  // Derive the bounty pool ATA
  const bountyPoolAta = await getAssociatedTokenAddress(
    usdcMint,
    bountyPoolWallet,
    true
  );

  console.log("Payer:", payer.publicKey.toBase58());
  console.log("Global PDA:", globalPda.toBase58());
  console.log("Bounty PDA:", bountyPda.toBase58());
  console.log("Bounty Pool ATA:", bountyPoolAta.toBase58());

  // Check if bounty pool ATA exists, if not create it
  const ataInfo = await connection.getAccountInfo(bountyPoolAta);
  if (!ataInfo) {
    console.log("\nCreating bounty pool ATA...");
    const createAtaIx = createAssociatedTokenAccountInstruction(
      payer.publicKey,
      bountyPoolAta,
      bountyPoolWallet,
      usdcMint
    );
    const txAta = new Transaction().add(createAtaIx);
    const sigAta = await sendAndConfirmTransaction(connection, txAta, [payer], {
      commitment: "confirmed",
    });
    console.log("✅ Created ATA:", sigAta);
  } else {
    console.log("✅ Bounty pool ATA already exists");
  }

  // Check if global PDA exists
  const globalInfo = await connection.getAccountInfo(globalPda);
  if (!globalInfo) {
    // Instruction 1: initialize_lottery
  // Data: discriminator + research_fund_floor (u64) + research_fee (u64) + 4 pubkeys
  const initLotteryData = Buffer.concat([
    INITIALIZE_LOTTERY_DISCRIMINATOR,
    u64LE(0),                      // research_fund_floor (set to 0 for devnet)
    u64LE(10_000_000),             // research_fee / base_price (10 USDC, 6 decimals)
    pubkeyBytes(bountyPoolWallet),
    pubkeyBytes(operationalWallet),
    pubkeyBytes(buybackWallet),
    pubkeyBytes(stakingWallet),
  ]);

  const initLotteryIx = new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: globalPda, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: bountyPoolWallet, isSigner: false, isWritable: false },
      { pubkey: operationalWallet, isSigner: false, isWritable: false },
      { pubkey: buybackWallet, isSigner: false, isWritable: false },
      { pubkey: stakingWallet, isSigner: false, isWritable: false },
      { pubkey: bountyPoolAta, isSigner: false, isWritable: true }, // bounty_pool_token_account
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data: initLotteryData,
  });

    console.log("\nSending initialize_lottery...");
    const txLottery = new Transaction().add(initLotteryIx);
    const sigLottery = await sendAndConfirmTransaction(connection, txLottery, [payer], {
      commitment: "confirmed",
    });
    console.log("✅ initialize_lottery signature:", sigLottery);
  } else {
    console.log("✅ Global PDA already initialized");
  }

  // Instruction 2: initialize_bounty
  // Data: discriminator + bounty_id (u64) + base_price (u64)
  const initBountyData = Buffer.concat([
    INITIALIZE_BOUNTY_DISCRIMINATOR,
    u64LE(1),           // bounty_id
    u64LE(10_000_000),  // base_price
  ]);

  const initBountyIx = new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: bountyPda, isSigner: false, isWritable: true },
      { pubkey: globalPda, isSigner: false, isWritable: true }, // must be writable per contract constraint
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data: initBountyData,
  });

  console.log("\nSending initialize_bounty...");
  const txBounty = new Transaction().add(initBountyIx);
  const sigBounty = await sendAndConfirmTransaction(connection, txBounty, [payer], {
    commitment: "confirmed",
  });
  console.log("✅ initialize_bounty signature:", sigBounty);

  console.log("\n✅ V2 initialization complete.");
}

main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});

