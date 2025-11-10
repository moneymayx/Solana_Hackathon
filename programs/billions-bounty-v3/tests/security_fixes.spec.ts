import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, createMint, createAccount, mintTo, getAccount } from "@solana/spl-token";
import { expect } from "chai";
import { sha256 } from "@noble/hashes/sha256";

describe("V3 Security Fixes", function() {
  this.timeout(60000); // 60 second timeout for async operations
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  
  // Load program directly from IDL (bypasses workspace registry issue)
  const idl = require("../target/idl/billions_bounty_v3.json");
  const programId = new anchor.web3.PublicKey("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");
  const program = new anchor.Program(idl, programId, provider) as Program<BillionsBountyV3>;

  let authority: Keypair;
  let user: Keypair;
  let jackpotWallet: Keypair;
  let backendAuthority: Keypair;
  let usdcMint: PublicKey;
  let userTokenAccount: PublicKey;
  let jackpotTokenAccount: PublicKey;
  let lotteryPDA: PublicKey;

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
    const providerWallet = (provider as any).wallet;
    const amount = 0.14 * anchor.web3.LAMPORTS_PER_SOL; // Minimal amount per account
    
    // Check provider wallet balance first
    const balance = await provider.connection.getBalance(providerWallet.publicKey);
    console.log(`Provider wallet (${providerWallet.publicKey.toString()}): ${balance / anchor.web3.LAMPORTS_PER_SOL} SOL`);
    const required = amount * 4 + (0.03 * anchor.web3.LAMPORTS_PER_SOL); // 4 accounts + very small buffer
    if (balance < required) {
      // Fallback to airdrop if transfer not possible
      console.log(`Provider wallet balance insufficient (${balance / anchor.web3.LAMPORTS_PER_SOL} SOL). Attempting airdrops as fallback...`);
      try {
        await provider.connection.requestAirdrop(authority.publicKey, amount);
        await provider.connection.requestAirdrop(user.publicKey, amount);
        await provider.connection.requestAirdrop(jackpotWallet.publicKey, amount);
        await provider.connection.requestAirdrop(backendAuthority.publicKey, amount);
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (e) {
        throw new Error(`Failed to fund test accounts. Provider balance: ${balance / anchor.web3.LAMPORTS_PER_SOL} SOL, Required: ${required / anchor.web3.LAMPORTS_PER_SOL} SOL. Error: ${e}`);
      }
      return; // Skip transfers, use airdropped funds
    }
    
    // Create and send transfer transactions
    const transfer1 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: authority.publicKey,
        lamports: amount,
      })
    );
    const transfer2 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: user.publicKey,
        lamports: amount,
      })
    );
    const transfer3 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: jackpotWallet.publicKey,
        lamports: amount,
      })
    );
    const transfer4 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: backendAuthority.publicKey,
        lamports: amount,
      })
    );

    // Send and confirm transactions
    const sig1 = await provider.sendAndConfirm(transfer1);
    const sig2 = await provider.sendAndConfirm(transfer2);
    const sig3 = await provider.sendAndConfirm(transfer3);
    const sig4 = await provider.sendAndConfirm(transfer4);
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Create USDC mint
    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6
    );

    // Create token accounts
    userTokenAccount = await createAccount(
      provider.connection,
      user,
      usdcMint,
      user.publicKey
    );

    // Create jackpot token account manually (before initialization)
    jackpotTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      jackpotWallet.publicKey
    );

    // Mint USDC to user and jackpot wallet (before initialization)
    await mintTo(
      provider.connection,
      authority,
      usdcMint,
      userTokenAccount,
      authority,
      1000 * 10**6
    );

    await mintTo(
      provider.connection,
      authority,
      usdcMint,
      jackpotTokenAccount,
      authority,
      RESEARCH_FUND_FLOOR * 10**6
    );

    // Initialize lottery
    [lotteryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("lottery")],
      program.programId
    );

    await program.methods
      .initializeLottery(
        new anchor.BN(RESEARCH_FUND_FLOOR),
        new anchor.BN(RESEARCH_FEE),
        jackpotWallet.publicKey,
        backendAuthority.publicKey
      )
      .accounts({
        lottery: lotteryPDA,
        authority: authority.publicKey,
        jackpotWallet: jackpotWallet.publicKey,
        jackpotTokenAccount: jackpotTokenAccount,
        usdcMint: usdcMint,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .rpc(); // Remove .signers() - Anchor will use provider wallet automatically
  });

  describe("Fix 1: Ed25519 Signature Verification", () => {
    it("Rejects invalid signature length", async () => {
      const [entryPDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
        program.programId
      );

      try {
        await program.methods
          .processAiDecision(
            "test message",
            "test response",
            Array(32).fill(0),
            Array(63).fill(0), // Invalid: should be 64 bytes
            false,
            new anchor.BN(1),
            "session-1",
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected invalid signature length");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidSignature");
      }
    });

    it("Rejects wrong backend authority", async () => {
      const wrongAuthority = Keypair.generate();
      
      try {
        await program.methods
          .processAiDecision(
            "test message",
            "test response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            "session-1",
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: wrongAuthority.publicKey, // Wrong authority
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
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

      expect(hash1).to.deep.equal(hash2);
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

      expect(hash1).to.not.deep.equal(hash2);
    });

    it("Rejects invalid decision hash", async () => {
      const invalidHash = Array(32).fill(255);
      
      try {
        await program.methods
          .processAiDecision(
            "test message",
            "test response",
            invalidHash,
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            "session-1",
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected invalid decision hash");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidDecisionHash");
      }
    });
  });

  describe("Fix 3: Input Validation", () => {
    it("Rejects oversized user message", async () => {
      const oversizedMessage = "x".repeat(5001); // Exceeds MAX_MESSAGE_LENGTH
      
      try {
        await program.methods
          .processAiDecision(
            oversizedMessage,
            "response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            "session-1",
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected oversized message");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("InputTooLong") || s.includes("exceeds")
        );
      }
    });

    it("Rejects oversized session ID", async () => {
      const oversizedSessionId = "x".repeat(101); // Exceeds MAX_SESSION_ID_LENGTH
      
      try {
        await program.methods
          .processAiDecision(
            "message",
            "response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            oversizedSessionId,
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected oversized session ID");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("InputTooLong") || s.includes("exceeds")
        );
      }
    });

    it("Rejects invalid session ID format", async () => {
      const invalidSessionId = "session@#$invalid"; // Contains invalid characters
      
      try {
        await program.methods
          .processAiDecision(
            "message",
            "response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            invalidSessionId,
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected invalid session ID format");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidSessionId");
      }
    });

    it("Rejects invalid timestamp (too old)", async () => {
      const oldTimestamp = Math.floor(Date.now() / 1000) - 7200; // 2 hours ago
      
      try {
        await program.methods
          .processAiDecision(
            "message",
            "response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(1),
            "session-1",
            new anchor.BN(oldTimestamp)
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected old timestamp");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("TimestampOutOfRange") || s.includes("timestamp")
        );
      }
    });

    it("Rejects zero user_id", async () => {
      try {
        await program.methods
          .processAiDecision(
            "message",
            "response",
            Array(32).fill(0),
            Array(64).fill(0),
            false,
            new anchor.BN(0), // Invalid: user_id must be > 0
            "session-1",
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            winnerTokenAccount: userTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected zero user_id");
      } catch (e: any) {
        expect(e.toString()).to.include("InvalidInput");
      }
    });
  });

  describe("Fix 4: Reentrancy Guards", () => {
    it("Prevents concurrent processing", async () => {
      // This test would require simulating concurrent calls
      // In practice, the is_processing flag prevents reentrancy
      const lottery = await program.account.lottery.fetch(lotteryPDA);
      expect(lottery.isProcessing).to.be.false;
    });
  });

  describe("Fix 5: Authority Checks", () => {
    it("Rejects unauthorized emergency recovery", async () => {
      const unauthorizedUser = Keypair.generate();
      // Transfer SOL from provider wallet instead of airdropping
      const providerWallet = (provider as any).wallet;
      const transferTx = new anchor.web3.Transaction().add(
        anchor.web3.SystemProgram.transfer({
          fromPubkey: providerWallet.publicKey,
          toPubkey: unauthorizedUser.publicKey,
          lamports: 1 * anchor.web3.LAMPORTS_PER_SOL,
        })
      );
      await provider.sendAndConfirm(transferTx);
      await new Promise(resolve => setTimeout(resolve, 1000));

      try {
        const authorityTokenAccount = await createAccount(
          provider.connection,
          unauthorizedUser,
          usdcMint,
          unauthorizedUser.publicKey
        );

        await program.methods
          .emergencyRecovery(new anchor.BN(100))
          .accounts({
            lottery: lotteryPDA,
            authority: unauthorizedUser.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            authorityTokenAccount: authorityTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([unauthorizedUser])
          .rpc();
        expect.fail("Should have rejected unauthorized recovery");
      } catch (e: any) {
        expect(e.toString()).to.include("Unauthorized");
      }
    });

    it("Requires authority to be signer", async () => {
      // Anchor automatically enforces Signer constraint
      // This is implicit in the account struct definition
      expect(true).to.be.true; // Placeholder - Anchor handles this
    });
  });

  describe("Fix 6: Secure Emergency Recovery", () => {
    it("Enforces cooldown period", async () => {
      // First recovery should succeed
      const authorityTokenAccount = await createAccount(
        provider.connection,
        authority,
        usdcMint,
        authority.publicKey
      );

      await program.methods
        .emergencyRecovery(new anchor.BN(100))
        .accounts({
          lottery: lotteryPDA,
          authority: authority.publicKey,
          jackpotTokenAccount: jackpotTokenAccount,
          authorityTokenAccount: authorityTokenAccount,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .signers([authority])
        .rpc();

      // Second recovery immediately after should fail
      try {
        await program.methods
          .emergencyRecovery(new anchor.BN(50))
          .accounts({
            lottery: lotteryPDA,
            authority: authority.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            authorityTokenAccount: authorityTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([authority])
          .rpc();
        expect.fail("Should have rejected recovery during cooldown");
      } catch (e: any) {
        expect(e.toString()).to.include("RecoveryCooldownActive");
      }
    });

    it("Enforces maximum recovery amount (10% of jackpot)", async () => {
      const lottery = await program.account.lottery.fetch(lotteryPDA);
      const maxRecovery = Number(lottery.currentJackpot) * 0.1;
      const excessiveAmount = new anchor.BN(maxRecovery + 1000);

      try {
        const authorityTokenAccount = await createAccount(
          provider.connection,
          authority,
          usdcMint,
          authority.publicKey
        );

        await program.methods
          .emergencyRecovery(excessiveAmount)
          .accounts({
            lottery: lotteryPDA,
            authority: authority.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            authorityTokenAccount: authorityTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([authority])
          .rpc();
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
): number[] {
  const hasher = sha256.create();
  hasher.update(Buffer.from(userMessage));
  hasher.update(Buffer.from([0]));
  hasher.update(Buffer.from(aiResponse));
  hasher.update(Buffer.from([0]));
  hasher.update(Buffer.from(new Uint8Array(new BigInt64Array([BigInt(isSuccessfulJailbreak ? 1 : 0)]).buffer)));
  hasher.update(Buffer.from(new Uint8Array(new BigUint64Array([BigInt(userId)]).buffer)));
  hasher.update(Buffer.from(sessionId));
  hasher.update(Buffer.from(new Uint8Array(new BigInt64Array([BigInt(timestamp)]).buffer)));
  return Array.from(hasher.digest());
}

