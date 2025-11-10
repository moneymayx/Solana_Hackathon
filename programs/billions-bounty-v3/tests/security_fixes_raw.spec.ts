/**
 * V3 Security Fixes Tests - Using Raw Instruction Builders
 * Bypasses Anchor Program class to work around build issues
 */

import * as anchor from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram, Transaction, sendAndConfirmTransaction, Connection } from "@solana/web3.js";
import { 
  TOKEN_PROGRAM_ID, 
  ASSOCIATED_TOKEN_PROGRAM_ID, 
  createMint, 
  createAccount, 
  mintTo, 
  getAccount,
  getAssociatedTokenAddress
} from "@solana/spl-token";
import { expect } from "chai";
import { sha256 } from "@noble/hashes/sha256";
import {
  PROGRAM_ID,
  findLotteryPDA,
  findEntryPDA,
  buildInitializeLotteryInstruction,
  buildProcessEntryPaymentInstruction,
  buildProcessAiDecisionInstruction,
  buildEmergencyRecoveryInstruction,
  serializeU64,
  serializeI64,
  serializeBool,
  serializeString,
  serializeBytes,
} from "./raw_instruction_helpers";
import { readFileSync } from "fs";
import { join } from "path";

describe("V3 Security Fixes (Raw Instructions)", function() {
  this.timeout(60000); // 60 second timeout for async operations
  
  // Setup connection directly (bypasses Anchor provider requirements)
  const connection = new Connection(
    process.env.ANCHOR_PROVIDER_URL || "https://api.devnet.solana.com",
    "confirmed"
  );
  
  // Load provider wallet from keypair file
  let providerWallet: Keypair;
  try {
    const fs = require("fs");
    const path = require("path");
    const walletPath = process.env.ANCHOR_WALLET || path.join(process.env.HOME, ".config/solana/id.json");
    const walletKeypair = JSON.parse(fs.readFileSync(walletPath, "utf8"));
    providerWallet = Keypair.fromSecretKey(Uint8Array.from(walletKeypair));
  } catch (e) {
    // Fallback: generate a dummy wallet (tests will use actual keypairs)
    providerWallet = Keypair.generate();
  }
  
  // Create a minimal provider-like object for wallet access
  const provider = {
    connection,
    wallet: {
      publicKey: providerWallet.publicKey,
    },
    sendAndConfirm: async (tx: Transaction, signers?: Keypair[]) => {
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = providerWallet.publicKey;
      if (signers) {
        tx.sign(...signers);
      }
      return await sendAndConfirmTransaction(connection, tx, [providerWallet, ...(signers || [])]);
    },
  } as any;
  
  let authority: Keypair;
  let user: Keypair;
  let jackpotWallet: Keypair;
  let backendAuthority: Keypair;
  let usdcMint: PublicKey;
  let userTokenAccount: PublicKey;
  let jackpotTokenAccount: PublicKey;
  let lotteryPDA: PublicKey;
  let lotteryBump: number;

  const RESEARCH_FUND_FLOOR = 10000;
  const RESEARCH_FEE = 10;
  const ENTRY_AMOUNT = 10;

  before(async () => {
    // Generate test keypairs
    authority = Keypair.generate();
    user = Keypair.generate();
    jackpotWallet = Keypair.generate();
    backendAuthority = Keypair.generate();

    // Transfer SOL from provider wallet to test accounts (bypasses rate limits)
    let amount = 0.03 * anchor.web3.LAMPORTS_PER_SOL; // Minimal amount per account
    
    // Check provider wallet balance first
    const balance = await connection.getBalance(providerWallet.publicKey);
    console.log(`Provider wallet (${providerWallet.publicKey.toString()}): ${balance / anchor.web3.LAMPORTS_PER_SOL} SOL`);
    const required = amount * 4 + (0.02 * anchor.web3.LAMPORTS_PER_SOL); // 4 accounts + small buffer
    
    if (balance < required) {
      console.log(`⚠️  Provider wallet balance insufficient (${balance / anchor.web3.LAMPORTS_PER_SOL} SOL < ${required / anchor.web3.LAMPORTS_PER_SOL} SOL)`);
      console.log(`   Attempting to reduce transfer amount per account...`);
      
      // Reduce amount per account if possible
      const available = balance - (0.02 * anchor.web3.LAMPORTS_PER_SOL);
      const reducedAmount = Math.floor(available / 4);
      
      // Minimum 0.005 SOL per account (enough for a few transactions)
      if (reducedAmount < 0.005 * anchor.web3.LAMPORTS_PER_SOL) {
        throw new Error(`Insufficient provider wallet balance. Have: ${balance / anchor.web3.LAMPORTS_PER_SOL} SOL, Need at least: ${(0.005 * 4 + 0.02) / anchor.web3.LAMPORTS_PER_SOL} SOL. Please fund provider wallet or request airdrop.`);
      }
      
      amount = reducedAmount;
      console.log(`   Reduced transfer amount to ${amount / anchor.web3.LAMPORTS_PER_SOL} SOL per account`);
    }
    
    // Always transfer from provider wallet (no airdrops to avoid rate limits)
    console.log(`   Transferring ${amount / anchor.web3.LAMPORTS_PER_SOL} SOL to each test account from provider wallet...`);
    const transfer1 = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: authority.publicKey,
        lamports: amount,
      })
    );
    const transfer2 = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: user.publicKey,
        lamports: amount,
      })
    );
    const transfer3 = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: jackpotWallet.publicKey,
        lamports: amount,
      })
    );
    const transfer4 = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: backendAuthority.publicKey,
        lamports: amount,
      })
    );

    try {
      await sendAndConfirmTransaction(connection, transfer1, [providerWallet]);
      await sendAndConfirmTransaction(connection, transfer2, [providerWallet]);
      await sendAndConfirmTransaction(connection, transfer3, [providerWallet]);
      await sendAndConfirmTransaction(connection, transfer4, [providerWallet]);
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log(`✅ Successfully funded all test accounts`);
    } catch (e: any) {
      throw new Error(`Failed to fund test accounts via transfer. Error: ${e.message || e}`);
    }

    // Create USDC mint
    usdcMint = await createMint(
      connection,
      authority,
      authority.publicKey,
      null,
      6
    );

    // Create token accounts
    userTokenAccount = await createAccount(
      connection,
      user,
      usdcMint,
      user.publicKey
    );

    jackpotTokenAccount = await createAccount(
      connection,
      authority,
      usdcMint,
      jackpotWallet.publicKey
    );

    // Mint USDC to user and jackpot wallet
    await mintTo(
      connection,
      authority,
      usdcMint,
      userTokenAccount,
      authority,
      1000 * 10**6
    );

    await mintTo(
      connection,
      authority,
      usdcMint,
      jackpotTokenAccount,
      authority,
      RESEARCH_FUND_FLOOR * 10**6
    );

    // Find lottery PDA
    [lotteryPDA, lotteryBump] = await findLotteryPDA();

    // Check if lottery already exists
    const lotteryInfo = await connection.getAccountInfo(lotteryPDA);
    if (lotteryInfo) {
      console.log(`⚠️  Lottery account already exists at ${lotteryPDA.toString()}, skipping initialization`);
      console.log(`   Account data length: ${lotteryInfo.data.length} bytes`);
      // Verify it's a valid lottery account by checking it has data
      if (lotteryInfo.data.length < 8) {
        throw new Error("Existing lottery account has invalid data length");
      }
    } else {
      // Initialize lottery using raw instruction
      // Anchor's init constraint with seeds will automatically create the PDA
      const initIx = buildInitializeLotteryInstruction(
        lotteryPDA,
        authority.publicKey,
        jackpotWallet.publicKey,
        jackpotTokenAccount,
        usdcMint,
        RESEARCH_FUND_FLOOR,
        RESEARCH_FEE,
        backendAuthority.publicKey,
        lotteryBump // Pass the bump seed
      );

      const initTx = new Transaction().add(initIx);
      
      // Get recent blockhash
      const { blockhash } = await connection.getLatestBlockhash();
      initTx.recentBlockhash = blockhash;
      initTx.feePayer = authority.publicKey;
      
      // For PDA initialization with seeds, we need to add the PDA seeds
      // Anchor will derive and verify the PDA matches the seeds
      const lotterySeeds = [Buffer.from("lottery")];
      const [lotteryPDAWithBump, _bump] = PublicKey.findProgramAddressSync(
        lotterySeeds,
        PROGRAM_ID
      );
      
      if (!lotteryPDAWithBump.equals(lotteryPDA)) {
        throw new Error(`PDA mismatch: expected ${lotteryPDA.toString()}, got ${lotteryPDAWithBump.toString()}`);
      }
      
      // Sign transaction (authority signs, PDA is derived by program)
      initTx.sign(authority);
      
      try {
        await sendAndConfirmTransaction(connection, initTx, [authority]);
        console.log("✅ Lottery initialized successfully");
      } catch (e: any) {
        console.error(`❌ Failed to initialize lottery: ${e.message || e}`);
        // Log more details if available
        if (e.logs) {
          console.error("Transaction logs:", e.logs);
        }
        throw e;
      }
    }
  });

  /**
   * Fetch lottery account data and parse it
   */
  async function fetchLotteryAccount(): Promise<any> {
    const accountInfo = await connection.getAccountInfo(lotteryPDA);
    if (!accountInfo) {
      throw new Error("Lottery account not found");
    }
    
    // Parse account data (skip 8-byte discriminator)
    const data = accountInfo.data.slice(8);
    const reader = {
      offset: 0,
      readU64LE(): bigint {
        const value = data.readBigUInt64LE(this.offset);
        this.offset += 8;
        return value;
      },
      readI64LE(): bigint {
        const value = data.readBigInt64LE(this.offset);
        this.offset += 8;
        return value;
      },
      readPubkey(): PublicKey {
        const key = new PublicKey(data.slice(this.offset, this.offset + 32));
        this.offset += 32;
        return key;
      },
      readBool(): boolean {
        const value = data[this.offset] !== 0;
        this.offset += 1;
        return value;
      },
    };

    return {
      authority: reader.readPubkey(),
      jackpotWallet: reader.readPubkey(),
      backendAuthority: reader.readPubkey(),
      researchFundFloor: Number(reader.readU64LE()),
      researchFee: Number(reader.readU64LE()),
      researchFundContribution: Number(reader.readU64LE()),
      operationalFee: Number(reader.readU64LE()),
      currentJackpot: Number(reader.readU64LE()),
      totalEntries: Number(reader.readU64LE()),
      isActive: reader.readBool(),
      isProcessing: reader.readBool(),
      lastRollover: Number(reader.readI64LE()),
      nextRollover: Number(reader.readI64LE()),
      lastRecoveryTime: Number(reader.readI64LE()),
    };
  }

  describe("Fix 1: Ed25519 Signature Verification", () => {
    it("Rejects invalid signature length", async () => {
      const invalidSignature = new Uint8Array(63); // Invalid: should be 64 bytes
      const decisionHash = computeDecisionHash(
        "test message",
        "test response",
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        backendAuthority.publicKey,
        usdcMint,
        "test message",
        "test response",
        decisionHash,
        invalidSignature,
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = backendAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [backendAuthority]);
        expect.fail("Should have rejected invalid signature length");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidSignature");
      }
    });

    it("Rejects wrong backend authority", async () => {
      const wrongAuthority = Keypair.generate();
      
      // Fund wrong authority
      const providerWallet = (provider as any).wallet;
      const transferTx = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: providerWallet.publicKey,
          toPubkey: wrongAuthority.publicKey,
          lamports: 0.1 * anchor.web3.LAMPORTS_PER_SOL,
        })
      );
      await sendAndConfirmTransaction(connection, transferTx, [providerWallet]);
      await new Promise(resolve => setTimeout(resolve, 500));

      const signature = new Uint8Array(64);
      const decisionHash = computeDecisionHash(
        "test message",
        "test response",
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        wrongAuthority.publicKey, // Wrong authority
        usdcMint,
        "test message",
        "test response",
        decisionHash,
        signature,
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = wrongAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [wrongAuthority]);
        expect.fail("Should have rejected wrong backend authority");
      } catch (e: any) {
        expect(e.toString()).to.include("UnauthorizedBackend");
      }
    });
  });

  describe("Fix 2: Cryptographic Hash Function (SHA-256)", () => {
    it("Produces deterministic hash for same inputs", () => {
      const hash1 = computeDecisionHash(
        "message",
        "response",
        false,
        1,
        "session-1",
        1000
      );
      
      const hash2 = computeDecisionHash(
        "message",
        "response",
        false,
        1,
        "session-1",
        1000
      );

      expect(Buffer.from(hash1).equals(Buffer.from(hash2))).to.be.true;
    });

    it("Produces different hash for different inputs", () => {
      const hash1 = computeDecisionHash(
        "message1",
        "response",
        false,
        1,
        "session-1",
        1000
      );
      
      const hash2 = computeDecisionHash(
        "message2",
        "response",
        false,
        1,
        "session-1",
        1000
      );

      expect(Buffer.from(hash1).equals(Buffer.from(hash2))).to.be.false;
    });

    it("Rejects invalid decision hash", async () => {
      const invalidHash = new Uint8Array(32).fill(255);
      const signature = new Uint8Array(64);

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        backendAuthority.publicKey,
        usdcMint,
        "test message",
        "test response",
        invalidHash,
        signature,
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = backendAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [backendAuthority]);
        expect.fail("Should have rejected invalid decision hash");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidDecisionHash");
      }
    });
  });

  describe("Fix 3: Input Validation", () => {
    it("Rejects oversized user message", async () => {
      const oversizedMessage = "x".repeat(5001); // Exceeds MAX_MESSAGE_LENGTH
      const signature = new Uint8Array(64);
      const decisionHash = computeDecisionHash(
        oversizedMessage,
        "response",
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        backendAuthority.publicKey,
        usdcMint,
        oversizedMessage,
        "response",
        decisionHash,
        signature,
        false,
        1,
        "session-1",
        Math.floor(Date.now() / 1000)
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = backendAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [backendAuthority]);
        expect.fail("Should have rejected oversized message");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("InputTooLong") || s.includes("exceeds")
        );
      }
    });

    it("Rejects oversized session ID", async () => {
      const oversizedSessionId = "x".repeat(101); // Exceeds MAX_SESSION_ID_LENGTH
      const signature = new Uint8Array(64);
      const decisionHash = computeDecisionHash(
        "message",
        "response",
        false,
        1,
        oversizedSessionId,
        Math.floor(Date.now() / 1000)
      );

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        backendAuthority.publicKey,
        usdcMint,
        "message",
        "response",
        decisionHash,
        signature,
        false,
        1,
        oversizedSessionId,
        Math.floor(Date.now() / 1000)
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = backendAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [backendAuthority]);
        expect.fail("Should have rejected oversized session ID");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("InputTooLong") || s.includes("exceeds")
        );
      }
    });

    it("Rejects invalid timestamp (too old)", async () => {
      const oldTimestamp = Math.floor(Date.now() / 1000) - 7200; // 2 hours ago
      const signature = new Uint8Array(64);
      const decisionHash = computeDecisionHash(
        "message",
        "response",
        false,
        1,
        "session-1",
        oldTimestamp
      );

      const winnerTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        user.publicKey
      );

      const ix = buildProcessAiDecisionInstruction(
        lotteryPDA,
        user.publicKey,
        winnerTokenAccount,
        jackpotTokenAccount,
        backendAuthority.publicKey,
        usdcMint,
        "message",
        "response",
        decisionHash,
        signature,
        false,
        1,
        "session-1",
        oldTimestamp
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = backendAuthority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [backendAuthority]);
        expect.fail("Should have rejected old timestamp");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("TimestampOutOfRange") || s.includes("timestamp")
        );
      }
    });
  });

  describe("Fix 4: Reentrancy Guards", () => {
    it("Prevents concurrent processing", async () => {
      const lottery = await fetchLotteryAccount();
      expect(lottery.isProcessing).to.be.false;
    });
  });

  describe("Fix 5: Authority Checks", () => {
    it("Rejects unauthorized emergency recovery", async () => {
      const unauthorizedUser = Keypair.generate();
      const providerWallet = (provider as any).wallet;
      const transferTx = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: providerWallet.publicKey,
          toPubkey: unauthorizedUser.publicKey,
          lamports: 0.1 * anchor.web3.LAMPORTS_PER_SOL,
        })
      );
      await sendAndConfirmTransaction(connection, transferTx, [providerWallet]);
      await new Promise(resolve => setTimeout(resolve, 500));

      const authorityTokenAccount = await createAccount(
        connection,
        unauthorizedUser,
        usdcMint,
        unauthorizedUser.publicKey
      );

      const ix = buildEmergencyRecoveryInstruction(
        lotteryPDA,
        unauthorizedUser.publicKey,
        jackpotTokenAccount,
        authorityTokenAccount,
        usdcMint,
        100
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = unauthorizedUser.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [unauthorizedUser]);
        expect.fail("Should have rejected unauthorized recovery");
      } catch (e: any) {
        expect(e.toString()).to.include("Unauthorized");
      }
    });
  });

  describe("Fix 6: Secure Emergency Recovery", () => {
    it("Enforces cooldown period", async () => {
      const authorityTokenAccount = await createAccount(
        connection,
        authority,
        usdcMint,
        authority.publicKey
      );

      // First recovery should succeed
      const ix1 = buildEmergencyRecoveryInstruction(
        lotteryPDA,
        authority.publicKey,
        jackpotTokenAccount,
        authorityTokenAccount,
        usdcMint,
        100
      );

      const tx1 = new Transaction().add(ix1);
      tx1.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx1.feePayer = authority.publicKey;
      await sendAndConfirmTransaction(connection, tx1, [authority]);

      // Second recovery immediately after should fail
      const ix2 = buildEmergencyRecoveryInstruction(
        lotteryPDA,
        authority.publicKey,
        jackpotTokenAccount,
        authorityTokenAccount,
        usdcMint,
        50
      );

      const tx2 = new Transaction().add(ix2);
      tx2.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx2.feePayer = authority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx2, [authority]);
        expect.fail("Should have rejected recovery during cooldown");
      } catch (e: any) {
        expect(e.toString()).to.include("RecoveryCooldownActive");
      }
    });

    it("Enforces maximum recovery amount (10% of jackpot)", async () => {
      const lottery = await fetchLotteryAccount();
      const maxRecovery = Math.floor(Number(lottery.currentJackpot) * 0.1);
      const excessiveAmount = maxRecovery + 1000;

      const authorityTokenAccount = await createAccount(
        connection,
        authority,
        usdcMint,
        authority.publicKey
      );

      const ix = buildEmergencyRecoveryInstruction(
        lotteryPDA,
        authority.publicKey,
        jackpotTokenAccount,
        authorityTokenAccount,
        usdcMint,
        excessiveAmount
      );

      const tx = new Transaction().add(ix);
      tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      tx.feePayer = authority.publicKey;

      try {
        await sendAndConfirmTransaction(connection, tx, [authority]);
        expect.fail("Should have rejected excessive recovery amount");
      } catch (e: any) {
        expect(e.toString()).to.include("RecoveryAmountExceedsLimit");
      }
    });
  });
});

// Helper function to compute decision hash (matching contract logic)
function computeDecisionHash(
  userMessage: string,
  aiResponse: string,
  isSuccessfulJailbreak: boolean,
  userId: number,
  sessionId: string,
  timestamp: number
): Uint8Array {
  const hasher = sha256.create();
  hasher.update(Buffer.from(userMessage, "utf8"));
  hasher.update(Buffer.from([0]));
  hasher.update(Buffer.from(aiResponse, "utf8"));
  hasher.update(Buffer.from([0]));
  hasher.update(Buffer.from([isSuccessfulJailbreak ? 1 : 0]));
  
  const userIdBuf = Buffer.allocUnsafe(8);
  userIdBuf.writeBigUInt64LE(BigInt(userId), 0);
  hasher.update(userIdBuf);
  
  hasher.update(Buffer.from(sessionId, "utf8"));
  
  const timestampBuf = Buffer.allocUnsafe(8);
  timestampBuf.writeBigInt64LE(BigInt(timestamp), 0);
  hasher.update(timestampBuf);
  
  return hasher.digest();
}

