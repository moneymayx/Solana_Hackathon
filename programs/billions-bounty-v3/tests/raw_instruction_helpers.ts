/**
 * Raw instruction building helpers for V3 tests
 * Bypasses Anchor Program class to work around build issues
 */

import { PublicKey, TransactionInstruction, SystemProgram, SYSVAR_RENT_PUBKEY } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from "@solana/spl-token";
import { sha256 } from "@noble/hashes/sha256";
import { Buffer } from "buffer";

// Program ID
export const PROGRAM_ID = new PublicKey("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");

// Instruction discriminators (8-byte SHA256 hashes of "global:instruction_name")
export const INSTRUCTION_DISCRIMINATORS = {
  initializeLottery: Buffer.from([113, 199, 243, 247, 73, 217, 33, 11]),
  processEntryPayment: Buffer.from([48, 174, 15, 37, 20, 95, 183, 60]),
  processAiDecision: Buffer.from([234, 175, 194, 9, 1, 218, 217, 234]),
  emergencyRecovery: Buffer.from([243, 108, 62, 60, 131, 169, 148, 83]),
  executeTimeEscapePlan: Buffer.from([155, 241, 248, 32, 209, 73, 193, 141]),
};

/**
 * Calculate instruction discriminator (Anchor's method)
 */
export function calculateInstructionDiscriminator(instructionName: string): Buffer {
  const seed = `global:${instructionName}`;
  const hash = sha256(seed);
  return Buffer.from(hash.slice(0, 8));
}

/**
 * Calculate account discriminator (Anchor's method)
 */
export function calculateAccountDiscriminator(accountName: string): Buffer {
  const seed = `account:${accountName}`;
  const hash = sha256(seed);
  return Buffer.from(hash.slice(0, 8));
}

/**
 * Serialize u64 to 8-byte little-endian buffer
 */
export function serializeU64(value: number | bigint): Buffer {
  const buf = Buffer.allocUnsafe(8);
  const val = typeof value === "bigint" ? value : BigInt(value);
  buf.writeBigUInt64LE(val, 0);
  return buf;
}

/**
 * Serialize i64 to 8-byte little-endian buffer
 */
export function serializeI64(value: number | bigint): Buffer {
  const buf = Buffer.allocUnsafe(8);
  const val = typeof value === "bigint" ? value : BigInt(value);
  buf.writeBigInt64LE(val, 0);
  return buf;
}

/**
 * Serialize bool to 1 byte
 */
export function serializeBool(value: boolean): Buffer {
  return Buffer.from([value ? 1 : 0]);
}

/**
 * Serialize string with length prefix
 */
export function serializeString(value: string): Buffer {
  const strBuf = Buffer.from(value, "utf8");
  const lenBuf = Buffer.allocUnsafe(4);
  lenBuf.writeUInt32LE(strBuf.length, 0);
  return Buffer.concat([lenBuf, strBuf]);
}

/**
 * Serialize pubkey to 32 bytes
 */
export function serializePubkey(value: PublicKey): Buffer {
  return Buffer.from(value.toBytes());
}

/**
 * Serialize byte array
 */
export function serializeBytes(value: Uint8Array | Buffer): Buffer {
  return Buffer.from(value);
}

/**
 * Build initialize_lottery instruction
 */
export function buildInitializeLotteryInstruction(
  lottery: PublicKey,
  authority: PublicKey,
  jackpotWallet: PublicKey,
  jackpotTokenAccount: PublicKey,
  usdcMint: PublicKey,
  researchFundFloor: number,
  researchFee: number,
  backendAuthority: PublicKey,
  lotteryBump?: number // Optional bump for PDA seeds
): TransactionInstruction {
  const discriminator = INSTRUCTION_DISCRIMINATORS.initializeLottery;
  
  // Serialize args: researchFundFloor (u64), researchFee (u64), jackpotWallet (pubkey), backendAuthority (pubkey)
  const args = Buffer.concat([
    serializeU64(researchFundFloor),
    serializeU64(researchFee),
    serializePubkey(jackpotWallet),
    serializePubkey(backendAuthority),
  ]);

  const data = Buffer.concat([discriminator, args]);

  // Account keys must match Rust struct order:
  // lottery, authority, jackpot_wallet, jackpot_token_account, usdc_mint, token_program, associated_token_program, system_program
  // Note: PDA is NOT a signer - Anchor derives and verifies it internally using seeds
  return new TransactionInstruction({
    keys: [
      { pubkey: lottery, isSigner: false, isWritable: true }, // PDA, derived via seeds, not a signer
      { pubkey: authority, isSigner: true, isWritable: true },
      { pubkey: jackpotWallet, isSigner: false, isWritable: false },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true }, // Must be writable (mut in Rust)
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  });
}

/**
 * Build process_entry_payment instruction
 */
export function buildProcessEntryPaymentInstruction(
  lottery: PublicKey,
  entry: PublicKey,
  user: PublicKey,
  userWallet: PublicKey,
  userTokenAccount: PublicKey,
  jackpotTokenAccount: PublicKey,
  buybackWallet: PublicKey,
  buybackTokenAccount: PublicKey,
  usdcMint: PublicKey,
  entryAmount: number,
  entryNonce: number
): TransactionInstruction {
  const discriminator = INSTRUCTION_DISCRIMINATORS.processEntryPayment;

  // Serialize args: entryAmount (u64), userWallet (pubkey), entryNonce (u64)
  const args = Buffer.concat([
    serializeU64(entryAmount),
    serializePubkey(userWallet),
    serializeU64(entryNonce),
  ]);

  const data = Buffer.concat([discriminator, args]);

  return new TransactionInstruction({
    keys: [
      { pubkey: lottery, isSigner: false, isWritable: true },
      { pubkey: entry, isSigner: false, isWritable: true },
      { pubkey: user, isSigner: true, isWritable: true },
      { pubkey: userWallet, isSigner: false, isWritable: false },
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: buybackWallet, isSigner: false, isWritable: false },
      { pubkey: buybackTokenAccount, isSigner: false, isWritable: true },
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  });
}

/**
 * Build process_ai_decision instruction
 */
export function buildProcessAiDecisionInstruction(
  lottery: PublicKey,
  winner: PublicKey,
  winnerTokenAccount: PublicKey,
  jackpotTokenAccount: PublicKey,
  backendAuthority: PublicKey,
  usdcMint: PublicKey,
  userMessage: string,
  aiResponse: string,
  decisionHash: Uint8Array,
  signature: Uint8Array,
  isSuccessfulJailbreak: boolean,
  userId: number,
  sessionId: string,
  timestamp: number
): TransactionInstruction {
  const discriminator = INSTRUCTION_DISCRIMINATORS.processAiDecision;

  // Serialize args in order:
  // userMessage (string), aiResponse (string), decisionHash ([u8; 32]), signature ([u8; 64]),
  // isSuccessfulJailbreak (bool), userId (u64), sessionId (string), timestamp (i64)
  const args = Buffer.concat([
    serializeString(userMessage),
    serializeString(aiResponse),
    serializeBytes(decisionHash), // 32 bytes
    serializeBytes(signature),    // 64 bytes
    serializeBool(isSuccessfulJailbreak),
    serializeU64(userId),
    serializeString(sessionId),
    serializeI64(timestamp),
  ]);

  const data = Buffer.concat([discriminator, args]);

  return new TransactionInstruction({
    keys: [
      { pubkey: lottery, isSigner: false, isWritable: true },
      { pubkey: backendAuthority, isSigner: true, isWritable: false },
      { pubkey: winner, isSigner: false, isWritable: false },
      { pubkey: winnerTokenAccount, isSigner: false, isWritable: true },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  });
}

/**
 * Build emergency_recovery instruction
 */
export function buildEmergencyRecoveryInstruction(
  lottery: PublicKey,
  authority: PublicKey,
  jackpotTokenAccount: PublicKey,
  authorityTokenAccount: PublicKey,
  usdcMint: PublicKey,
  amount: number
): TransactionInstruction {
  const discriminator = INSTRUCTION_DISCRIMINATORS.emergencyRecovery;

  // Serialize args: amount (u64)
  const args = serializeU64(amount);
  const data = Buffer.concat([discriminator, args]);

  return new TransactionInstruction({
    keys: [
      { pubkey: lottery, isSigner: false, isWritable: true },
      { pubkey: authority, isSigner: true, isWritable: false },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: authorityTokenAccount, isSigner: false, isWritable: true },
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  });
}

/**
 * Find Program Derived Address (PDA)
 */
export async function findLotteryPDA(): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("lottery")],
    PROGRAM_ID
  );
}

export async function findEntryPDA(lottery: PublicKey, userWallet: PublicKey): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddressSync(
    [Buffer.from("entry"), lottery.toBuffer(), userWallet.toBuffer()],
    PROGRAM_ID
  );
}

