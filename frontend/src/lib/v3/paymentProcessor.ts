/**
 * V3 Payment Processor - Frontend implementation using @solana/web3.js
 * Processes entry payments using raw instructions (similar to V2 pattern)
 * Based on raw_instruction_helpers.ts from tests
 */

import {
  Connection,
  PublicKey,
  Transaction,
  TransactionInstruction,
  SystemProgram,
  Keypair,
  Signer,
} from "@solana/web3.js";
import {
  getAssociatedTokenAddress,
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import { sha256 } from "@noble/hashes/sha256";
import { Buffer } from "buffer";

// V3 Contract Configuration
const PROGRAM_ID = new PublicKey(
  process.env.NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V3 ||
    "7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh" // V3 Multi-Bounty program ID
);

const USDC_MINT = new PublicKey(
  process.env.NEXT_PUBLIC_V3_USDC_MINT ||
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" // USDC devnet mint
);

interface PaymentResult {
  success: boolean;
  transactionSignature?: string;
  explorerUrl?: string;
  error?: string;
}

/**
 * Convert u64 to little-endian bytes
 */
function serializeU64(value: number): Buffer {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

/**
 * Derive instruction discriminator for Anchor instruction
 * Format: sha256("global:instruction_name")[:8]
 */
function deriveInstructionDiscriminator(instructionName: string): Buffer {
  const namespace = "global";
  const seed = `${namespace}:${instructionName}`;
  const hash = sha256(seed);
  return Buffer.from(hash).slice(0, 8);
}

/**
 * Find Program Derived Address (PDA)
 */
function findPDA(seeds: Buffer[], programId: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(seeds, programId);
}

/**
 * Find lottery PDA
 */
function findLotteryPDA(): [PublicKey, number] {
  return findPDA([Buffer.from("lottery")], PROGRAM_ID);
}

/**
 * Find entry PDA (entry, lottery, user, nonce)
 * Note: Entry PDA includes nonce to allow multiple entries per wallet
 */
function findEntryPDA(
  lotteryPDA: PublicKey,
  userWallet: PublicKey,
  entryNonce: number
): [PublicKey, number] {
  return findPDA(
    [
      Buffer.from("entry"),
      lotteryPDA.toBuffer(),
      userWallet.toBuffer(),
      serializeU64(entryNonce),
    ],
    PROGRAM_ID
  );
}

/**
 * Entry nonce storage helpers (localStorage-based)
 */
function getEntryNonceStorageKey(userWallet: PublicKey): string {
  return `bb_v3_entry_nonce_${userWallet.toBase58()}`;
}

function readStoredEntryNonce(userWallet: PublicKey): number {
  if (typeof window === "undefined") {
    return 0;
  }

  const key = getEntryNonceStorageKey(userWallet);
  const raw = window.localStorage.getItem(key);
  if (!raw) {
    return 0;
  }

  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed) || parsed < 0) {
    return 0;
  }

  return parsed;
}

function persistEntryNonce(userWallet: PublicKey, nonce: number): void {
  if (typeof window === "undefined") {
    return;
  }

  const key = getEntryNonceStorageKey(userWallet);
  window.localStorage.setItem(key, nonce.toString());
}

function computeNextEntryNonce(userWallet: PublicKey): number {
  const currentNonce = readStoredEntryNonce(userWallet);
  return currentNonce + 1;
}

/**
 * Convert USDC amount to smallest unit (6 decimals)
 */
export function usdcToSmallestUnit(amount: number): number {
  return Math.floor(amount * 1_000_000);
}

/**
 * Convert smallest unit back to USDC
 */
export function smallestUnitToUsdc(amount: number): number {
  return amount / 1_000_000;
}

/**
 * Process V3 entry payment
 * 
 * @param connection - Solana connection
 * @param userWallet - User's wallet public key
 * @param signTransaction - Function to sign transaction (from wallet adapter)
 * @param entryAmount - Payment amount in smallest unit (e.g., 10_000_000 for 10 USDC)
 * @param isMock - Optional flag to enable mock payment mode (no real blockchain transaction)
 * @returns Payment result with transaction signature
 */
export async function processV3EntryPayment(
  connection: Connection,
  userWallet: PublicKey,
  signTransaction: (tx: Transaction) => Promise<Transaction>,
  entryAmount: number,
  isMock: boolean = false
): Promise<PaymentResult> {
  try {
    // Check for test contract mode - calls contract via backend using backend's funded wallet
    const paymentMode = process.env.NEXT_PUBLIC_PAYMENT_MODE;
    const nextEntryNonce = computeNextEntryNonce(userWallet);
    
    if (paymentMode === "test_contract") {
      console.log("🧪 TEST CONTRACT MODE - Calling V3 contract via backend (contract WILL execute on devnet)");
      
      try {
        // Call backend API to process V3 payment using backend's funded wallet
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const response = await fetch(`${backendUrl}/api/v3/payment/test`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_wallet: userWallet.toBase58(),
            entry_amount: entryAmount,
            amount_usdc: entryAmount / 1_000_000,
            entry_nonce: nextEntryNonce,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
          throw new Error(errorData.error || `Backend error: ${response.statusText}`);
        }

        const result = await response.json();
        
        if (result.success) {
          console.log("✅ V3 contract executed via backend:", result.transaction_signature);
          if (typeof result.entry_nonce === "number") {
            persistEntryNonce(userWallet, result.entry_nonce);
          } else {
            persistEntryNonce(userWallet, nextEntryNonce);
          }
          const cluster = connection.rpcEndpoint.includes("mainnet") ? "mainnet-beta" : "devnet";
          return {
            success: true,
            transactionSignature: result.transaction_signature,
            explorerUrl: `https://explorer.solana.com/tx/${result.transaction_signature}?cluster=${cluster}`,
          };
        } else {
          throw new Error(result.error || "Backend payment failed");
        }
      } catch (error: any) {
        console.error("❌ Backend test contract call failed:", error);
        return {
          success: false,
          error: error.message || "Failed to call contract via backend",
        };
      }
    }
    
    // Check for mock payment mode (pure UI testing, no contract call)
    if (isMock || paymentMode === "mock") {
      console.log("🧪 MOCK PAYMENT MODE - Simulating V3 transaction (no real funds will be charged, NO contract call)");
      
      // Simulate a delay like a real transaction
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate a mock signature
      const mockSignature = `MOCK_V3_${Date.now()}_${Math.random().toString(36).substring(7)}`;
      const explorerUrl = `https://explorer.solana.com/tx/${mockSignature}?cluster=devnet`;
      
      console.log("✅ Mock V3 transaction complete:", mockSignature);
      
      return {
        success: true,
        transactionSignature: mockSignature,
        explorerUrl,
      };
    }

    console.log(`🔄 Processing V3 entry payment: Amount ${entryAmount} smallest units`);

    // Derive PDAs
    const [lotteryPDA] = findLotteryPDA();
    const [entryPDA] = findEntryPDA(lotteryPDA, userWallet, nextEntryNonce);

    console.log("Lottery PDA:", lotteryPDA.toBase58());
    console.log("Entry PDA:", entryPDA.toBase58());
    console.log("Entry Nonce:", nextEntryNonce);

    // Derive token accounts
    const userTokenAccount = await getAssociatedTokenAddress(
      USDC_MINT,
      userWallet
    );

    // jackpotTokenAccount is the ATA for jackpotWallet stored in lottery account
    // Fetch the lottery account to get jackpotWallet
    const lotteryAccountInfo = await connection.getAccountInfo(lotteryPDA);
    if (!lotteryAccountInfo) {
      const errorMessage = `Lottery not initialized on ${connection.rpcEndpoint.includes('mainnet') ? 'mainnet' : 'devnet'}. 
The V3 contract's lottery account needs to be initialized before processing payments.

Lottery PDA: ${lotteryPDA.toBase58()}
Program ID: ${PROGRAM_ID.toBase58()}

To initialize:
1. Deploy V3 contract to devnet
2. Call initialize_lottery instruction with required parameters
3. Verify lottery account exists before processing payments

See docs/development/V3_INTEGRATION_GUIDE.md for initialization steps.`;
      throw new Error(errorMessage);
    }
    
    // Parse lottery account to get jackpotWallet
    // Format: discriminator (8) + authority (32) + jackpot_wallet (32) + ...
    const jackpotWalletBuffer = lotteryAccountInfo.data.slice(8 + 32, 8 + 32 + 32);
    const jackpotWallet = new PublicKey(jackpotWalletBuffer);
    
    const jackpotTokenAccount = await getAssociatedTokenAddress(
      USDC_MINT,
      jackpotWallet
    );

    // Derive buyback wallet and its USDC ATA from environment.
    // 40% of each entry is routed here to fund 100Bs buy-and-burn.
    const buybackWalletEnv =
      process.env.NEXT_PUBLIC_V3_BUYBACK_WALLET ||
      process.env.NEXT_PUBLIC_BUYBACK_WALLET_ADDRESS;
    if (!buybackWalletEnv) {
      throw new Error(
        "NEXT_PUBLIC_V3_BUYBACK_WALLET (or NEXT_PUBLIC_BUYBACK_WALLET_ADDRESS) is not set. " +
          "This address is required so 40% of each entry can fund the 100Bs buy-and-burn wallet."
      );
    }
    const buybackWallet = new PublicKey(buybackWalletEnv);
    const buybackTokenAccount = await getAssociatedTokenAddress(
      USDC_MINT,
      buybackWallet
    );

    // Build instruction discriminator
    const discriminator = deriveInstructionDiscriminator("process_entry_payment");

    // Build instruction data: discriminator + entryAmount (u64) + userWallet (pubkey)
    const instructionData = Buffer.concat([
      discriminator,
      serializeU64(entryAmount),
      userWallet.toBuffer(),
      serializeU64(nextEntryNonce),
    ]);

    // Build account keys (must match exact order from contract)
    // lottery, entry, user, user_wallet, user_token_account, jackpot_token_account,
    // buyback_wallet, buyback_token_account, usdc_mint, token_program, associated_token_program, system_program
    const keys = [
      { pubkey: lotteryPDA, isSigner: false, isWritable: true },
      { pubkey: entryPDA, isSigner: false, isWritable: true },
      { pubkey: userWallet, isSigner: true, isWritable: true },
      { pubkey: userWallet, isSigner: false, isWritable: false }, // user_wallet (unchecked)
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: buybackWallet, isSigner: false, isWritable: false },
      { pubkey: buybackTokenAccount, isSigner: false, isWritable: true },
      { pubkey: USDC_MINT, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ];

    // Build instruction
    const instruction = new TransactionInstruction({
      keys,
      programId: PROGRAM_ID,
      data: instructionData,
    });

    // Build transaction
    const transaction = new Transaction().add(instruction);

    // Get recent blockhash
    const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();
    transaction.recentBlockhash = blockhash;
    transaction.feePayer = userWallet;

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

    console.log("✅ V3 payment processed successfully");
    console.log("Signature:", signature);
    console.log("Explorer:", explorerUrl);
    persistEntryNonce(userWallet, nextEntryNonce);

    return {
      success: true,
      transactionSignature: signature,
      explorerUrl,
    };
  } catch (error: any) {
    console.error("❌ Error processing V3 payment:", error);
    return {
      success: false,
      error: error.message || String(error),
    };
  }
}

/**
 * Get current lottery status
 */
export async function getV3LotteryStatus(
  connection: Connection
): Promise<{
  success: boolean;
  lotteryPDA?: string;
  error?: string;
}> {
  try {
    const [lotteryPDA] = findLotteryPDA();
    const accountInfo = await connection.getAccountInfo(lotteryPDA);

    if (!accountInfo) {
      return {
        success: false,
        error: "Lottery not initialized",
      };
    }

    return {
      success: true,
      lotteryPDA: lotteryPDA.toBase58(),
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || String(error),
    };
  }
}
