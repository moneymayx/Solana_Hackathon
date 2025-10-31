/**
 * V2 Payment Processor - Frontend implementation using @solana/web3.js
 * Processes entry payments using raw instructions (bypassing Anchor client)
 * Based on test_v2_raw_payment.ts
 */

import {
  Connection,
  PublicKey,
  Transaction,
  TransactionInstruction,
  SystemProgram,
  sendAndConfirmTransaction,
  Keypair,
  Signer,
} from "@solana/web3.js";
import {
  getAssociatedTokenAddress,
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
// Use browser-compatible crypto (Web Crypto API)
const getCrypto = () => {
  if (typeof window !== "undefined" && window.crypto) {
    return window.crypto;
  }
  // Fallback for Node.js (shouldn't be needed in browser code)
  try {
    return require("crypto").webcrypto || require("crypto");
  } catch {
    throw new Error("Crypto not available");
  }
};

// V2 Contract Configuration
const PROGRAM_ID = new PublicKey(
  process.env.NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2 ||
    "HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm"
);

const USDC_MINT = new PublicKey(
  process.env.NEXT_PUBLIC_V2_USDC_MINT ||
    "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"
);

const BOUNTY_POOL = new PublicKey(
  process.env.NEXT_PUBLIC_V2_BOUNTY_POOL_WALLET ||
    "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);

const OPERATIONAL = new PublicKey(
  process.env.NEXT_PUBLIC_V2_OPERATIONAL_WALLET ||
    "46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D"
);

const BUYBACK = new PublicKey(
  process.env.NEXT_PUBLIC_V2_BUYBACK_WALLET ||
    "7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya"
);

const STAKING = new PublicKey(
  process.env.NEXT_PUBLIC_V2_STAKING_WALLET ||
    "Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX"
);

const SYSVAR_RENT = new PublicKey("SysvarRent111111111111111111111111111111111");

interface PaymentResult {
  success: boolean;
  transactionSignature?: string;
  explorerUrl?: string;
  error?: string;
}

/**
 * Convert u64 to little-endian bytes
 */
function u64LE(value: number): Buffer {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

/**
 * Derive instruction discriminator for Anchor instruction
 * Format: sha256("global:instruction_name")[:8]
 */
async function deriveDiscriminator(instructionName: string): Promise<Buffer> {
  const namespace = "global";
  const seed = `${namespace}:${instructionName}`;
  
  // Use Web Crypto API for browser compatibility
  const crypto = getCrypto();
  const encoder = new TextEncoder();
  const data = encoder.encode(seed);
  
  if (crypto.subtle) {
    // Browser Web Crypto API
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    return Buffer.from(hashBuffer).slice(0, 8);
  } else {
    // Node.js fallback (shouldn't be needed in browser)
    const cryptoNode = require("crypto");
    return cryptoNode.createHash("sha256").update(seed).digest().slice(0, 8);
  }
}

/**
 * Derive all required PDAs for payment processing
 */
function derivePDAs(bountyId: number): {
  global: PublicKey;
  bounty: PublicKey;
  buybackTracker: PublicKey;
} {
  const [globalPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("global")],
    PROGRAM_ID
  );

  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), u64LE(bountyId)],
    PROGRAM_ID
  );

  const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("buyback_tracker")],
    PROGRAM_ID
  );

  return {
    global: globalPda,
    bounty: bountyPda,
    buybackTracker: buybackTrackerPda,
  };
}

/**
 * Derive associated token accounts for all wallets
 */
async function deriveTokenAccounts(
  userWallet: PublicKey
): Promise<{
  user: PublicKey;
  bountyPool: PublicKey;
  operational: PublicKey;
  buyback: PublicKey;
  staking: PublicKey;
}> {
  return {
    user: await getAssociatedTokenAddress(USDC_MINT, userWallet),
    bountyPool: await getAssociatedTokenAddress(USDC_MINT, BOUNTY_POOL),
    operational: await getAssociatedTokenAddress(USDC_MINT, OPERATIONAL),
    buyback: await getAssociatedTokenAddress(USDC_MINT, BUYBACK),
    staking: await getAssociatedTokenAddress(USDC_MINT, STAKING),
  };
}

/**
 * Process V2 entry payment
 * 
 * @param connection - Solana connection
 * @param userWallet - User's wallet public key
 * @param signTransaction - Function to sign transaction (from wallet adapter)
 * @param bountyId - Bounty ID (typically 1)
 * @param entryAmount - Payment amount in smallest unit (e.g., 15_000_000 for 15 USDC)
 * @returns Payment result with transaction signature
 */
export async function processV2EntryPayment(
  connection: Connection,
  userWallet: PublicKey,
  signTransaction: (tx: Transaction) => Promise<Transaction>,
  bountyId: number = 1,
  entryAmount: number
): Promise<PaymentResult> {
  try {
    console.log(`🔄 Processing V2 entry payment: Bounty ${bountyId}, Amount ${entryAmount}`);

    // Derive PDAs
    const pdas = derivePDAs(bountyId);
    console.log("Global PDA:", pdas.global.toBase58());
    console.log("Bounty PDA:", pdas.bounty.toBase58());
    console.log("Buyback Tracker PDA:", pdas.buybackTracker.toBase58());

    // Derive token accounts
    const tokenAccounts = await deriveTokenAccounts(userWallet);

    // Build instruction discriminator
    const discriminator = await deriveDiscriminator("process_entry_payment_v2");

    // Build instruction data: discriminator + bounty_id (u64) + entry_amount (u64)
    const instructionData = Buffer.concat([
      discriminator,
      u64LE(bountyId),
      u64LE(entryAmount),
    ]);

    // Build account keys (must match exact order from contract)
    const keys = [
      // PDAs
      { pubkey: pdas.global, isSigner: false, isWritable: true },
      { pubkey: pdas.bounty, isSigner: false, isWritable: true },
      { pubkey: pdas.buybackTracker, isSigner: false, isWritable: true },
      
      // User
      { pubkey: userWallet, isSigner: true, isWritable: true },
      { pubkey: tokenAccounts.user, isSigner: false, isWritable: true },
      
      // Destination token accounts
      { pubkey: tokenAccounts.bountyPool, isSigner: false, isWritable: true },
      { pubkey: tokenAccounts.operational, isSigner: false, isWritable: true },
      { pubkey: tokenAccounts.buyback, isSigner: false, isWritable: true },
      { pubkey: tokenAccounts.staking, isSigner: false, isWritable: true },
      
      // Wallet addresses (read-only)
      { pubkey: BOUNTY_POOL, isSigner: false, isWritable: false },
      { pubkey: OPERATIONAL, isSigner: false, isWritable: false },
      { pubkey: BUYBACK, isSigner: false, isWritable: false },
      { pubkey: STAKING, isSigner: false, isWritable: false },
      
      // Program IDs
      { pubkey: USDC_MINT, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_RENT, isSigner: false, isWritable: false },
    ];

    // Create instruction
    const instruction = new TransactionInstruction({
      programId: PROGRAM_ID,
      keys,
      data: instructionData,
    });

    // Create transaction
    const transaction = new Transaction();
    transaction.add(instruction);
    transaction.feePayer = userWallet;

    // Get recent blockhash
    const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();
    transaction.recentBlockhash = blockhash;

    // Sign transaction (using wallet adapter)
    const signedTransaction = await signTransaction(transaction);

    // Send transaction
    const signature = await connection.sendRawTransaction(
      signedTransaction.serialize(),
      {
        skipPreflight: false,
        maxRetries: 3,
      }
    );

    // Confirm transaction
    await connection.confirmTransaction(
      {
        signature,
        blockhash,
        lastValidBlockHeight,
      },
      "confirmed"
    );

    const cluster = connection.rpcEndpoint.includes("mainnet") ? "mainnet-beta" : "devnet";
    const explorerUrl = `https://explorer.solana.com/tx/${signature}?cluster=${cluster}`;

    console.log("✅ V2 payment processed successfully");
    console.log("Signature:", signature);
    console.log("Explorer:", explorerUrl);

    return {
      success: true,
      transactionSignature: signature,
      explorerUrl,
    };
  } catch (error: any) {
    console.error("❌ Error processing V2 payment:", error);
    return {
      success: false,
      error: error.message || String(error),
    };
  }
}

/**
 * Get current bounty status
 */
export async function getV2BountyStatus(
  connection: Connection,
  bountyId: number = 1
): Promise<{
  success: boolean;
  bountyId: number;
  bountyPda?: string;
  error?: string;
}> {
  try {
    const pdas = derivePDAs(bountyId);

    // Fetch bounty account
    const bountyAccount = await connection.getAccountInfo(pdas.bounty);

    if (!bountyAccount) {
      return {
        success: false,
        bountyId,
        error: "Bounty not found",
      };
    }

    return {
      success: true,
      bountyId,
      bountyPda: pdas.bounty.toBase58(),
    };
  } catch (error: any) {
    return {
      success: false,
      bountyId,
      error: error.message || String(error),
    };
  }
}

/**
 * Helper to convert USDC amount to smallest unit (6 decimals)
 */
export function usdcToSmallestUnit(usdcAmount: number): number {
  return Math.floor(usdcAmount * 1_000_000);
}

/**
 * Helper to convert smallest unit to USDC (6 decimals)
 */
export function smallestUnitToUsdc(amount: number): number {
  return amount / 1_000_000;
}

