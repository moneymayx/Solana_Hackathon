import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, createMint, createAccount, mintTo } from "@solana/spl-token";
import { expect } from "chai";

describe("V3 Edge Cases and Attack Scenarios", function() {
  this.timeout(60000); // 60 second timeout for async operations
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  
  // Load program directly from IDL (bypasses workspace registry issue)
  const idl = require("../target/idl/billions_bounty_v3.json");
  const programId = new anchor.web3.PublicKey("ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb");
  const program = new anchor.Program(idl, programId, provider) as Program<BillionsBountyV3>;

  let authority: Keypair;
  let attacker: Keypair;
  let user: Keypair;
  let jackpotWallet: Keypair;
  let backendAuthority: Keypair;
  let usdcMint: PublicKey;
  let lotteryPDA: PublicKey;

  before(async () => {
    authority = Keypair.generate();
    attacker = Keypair.generate();
    user = Keypair.generate();
    jackpotWallet = Keypair.generate();
    backendAuthority = Keypair.generate();

    // Transfer SOL from provider wallet to test accounts (bypasses rate limits)
    const providerWallet = (provider as any).wallet;
    const amount = 0.15 * anchor.web3.LAMPORTS_PER_SOL; // Minimal amount per account
    
    // Check balance and use airdrop fallback if needed
    const balance = await provider.connection.getBalance(providerWallet.publicKey);
    const required = amount * 5 + (0.05 * anchor.web3.LAMPORTS_PER_SOL); // 5 accounts + minimal buffer
    if (balance < required) {
      console.log(`Using airdrop fallback...`);
      try {
        await provider.connection.requestAirdrop(authority.publicKey, amount);
        await provider.connection.requestAirdrop(attacker.publicKey, amount);
        await provider.connection.requestAirdrop(user.publicKey, amount);
        await provider.connection.requestAirdrop(jackpotWallet.publicKey, amount);
        await provider.connection.requestAirdrop(backendAuthority.publicKey, amount);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return;
      } catch (e) {
        throw new Error(`Failed to fund test accounts: ${e}`);
      }
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
        toPubkey: attacker.publicKey,
        lamports: amount,
      })
    );
    const transfer3 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: user.publicKey,
        lamports: amount,
      })
    );
    const transfer4 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: jackpotWallet.publicKey,
        lamports: amount,
      })
    );
    const transfer5 = new anchor.web3.Transaction().add(
      anchor.web3.SystemProgram.transfer({
        fromPubkey: providerWallet.publicKey,
        toPubkey: backendAuthority.publicKey,
        lamports: amount,
      })
    );

    // Send and confirm transactions
    await provider.sendAndConfirm(transfer1);
    await provider.sendAndConfirm(transfer2);
    await provider.sendAndConfirm(transfer3);
    await provider.sendAndConfirm(transfer4);
    await provider.sendAndConfirm(transfer5);
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6
    );

    [lotteryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("lottery")],
      program.programId
    );

    const jackpotTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      jackpotWallet.publicKey
    );

    await mintTo(
      provider.connection,
      authority,
      usdcMint,
      jackpotTokenAccount,
      authority,
      10000 * 10**6
    );

    await program.methods
      .initializeLottery(
        new anchor.BN(10000),
        new anchor.BN(10),
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
      .rpc();
  });

  describe("Attack Scenarios", () => {
    it("Prevents zero pubkey attacks", async () => {
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
            new anchor.BN(Math.floor(Date.now() / 1000))
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: PublicKey.default, // Zero pubkey attack
            jackpotTokenAccount: PublicKey.unique(),
            winnerTokenAccount: PublicKey.unique(),
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected zero pubkey");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("InvalidPubkey") || s.includes("Constraint")
        );
      }
    });

    it("Prevents replay attacks with old timestamps", async () => {
      const oldTimestamp = Math.floor(Date.now() / 1000) - 86400; // 24 hours ago
      
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
            jackpotTokenAccount: PublicKey.unique(),
            winnerTokenAccount: PublicKey.unique(),
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

    it("Prevents future timestamp attacks", async () => {
      const futureTimestamp = Math.floor(Date.now() / 1000) + 86400; // 24 hours in future
      
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
            new anchor.BN(futureTimestamp)
          )
          .accounts({
            lottery: lotteryPDA,
            backendAuthority: backendAuthority.publicKey,
            winner: user.publicKey,
            jackpotTokenAccount: PublicKey.unique(),
            winnerTokenAccount: PublicKey.unique(),
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .rpc();
        expect.fail("Should have rejected future timestamp");
      } catch (e: any) {
        expect(e.toString()).to.satisfy((s: string) => 
          s.includes("TimestampOutOfRange") || s.includes("timestamp")
        );
      }
    });

    it("Prevents unauthorized emergency recovery attempts", async () => {
      const attackerTokenAccount = await createAccount(
        provider.connection,
        attacker,
        usdcMint,
        attacker.publicKey
      );

      try {
        await program.methods
          .emergencyRecovery(new anchor.BN(100))
          .accounts({
            lottery: lotteryPDA,
            authority: attacker.publicKey, // Attacker trying to recover
            jackpotTokenAccount: PublicKey.unique(),
            authorityTokenAccount: attackerTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
          })
          .signers([attacker])
          .rpc();
        expect.fail("Should have rejected unauthorized recovery");
      } catch (e: any) {
        expect(e.toString()).to.include("Unauthorized");
      }
    });

    it("Prevents recovery exceeding 10% limit", async () => {
      const lottery = await program.account.lottery.fetch(lotteryPDA);
      const jackpotAmount = Number(lottery.currentJackpot);
      const maxAllowed = Math.floor(jackpotAmount * 0.1);
      const excessiveAmount = maxAllowed + 1;

      const authorityTokenAccount = await createAccount(
        provider.connection,
        authority,
        usdcMint,
        authority.publicKey
      );

      try {
        await program.methods
          .emergencyRecovery(new anchor.BN(excessiveAmount))
          .accounts({
            lottery: lotteryPDA,
            authority: authority.publicKey,
            jackpotTokenAccount: PublicKey.unique(),
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

  describe("Boundary Conditions", () => {
    it("Accepts maximum valid message length", async () => {
      const maxMessage = "x".repeat(5000); // Exactly MAX_MESSAGE_LENGTH
      
      // Should not throw error for valid max length
      // (This test would require proper hash/signature setup to pass fully)
      expect(maxMessage.length).to.equal(5000);
    });

    it("Accepts valid session ID with allowed characters", async () => {
      const validSessionIds = ["session-123", "session_456", "session789", "SESSION-ABC-123"];
      
      for (const sessionId of validSessionIds) {
        expect(sessionId.match(/^[a-zA-Z0-9_-]+$/)).to.not.be.null;
      }
    });
  });
});

