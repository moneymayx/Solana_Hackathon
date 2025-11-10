import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV2 } from "../target/types/billions_bounty_v2";
import { PublicKey, Keypair, SystemProgram, LAMPORTS_PER_SOL } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  createMint,
  createAccount,
  mintTo,
  getAccount,
  getAssociatedTokenAddress,
} from "@solana/spl-token";
import { expect } from "chai";
import * as ed25519 from "@noble/ed25519";

describe("billions-bounty-v2", () => {
  // Configure the client to use the local cluster
  anchor.setProvider(anchor.AnchorProvider.env());
  const provider = anchor.getProvider();
  const program = anchor.workspace.BillionsBountyV2 as Program<BillionsBountyV2>;

  // Test accounts
  let authority: Keypair;
  let user: Keypair;
  let bountyPoolWallet: Keypair;
  let operationalWallet: Keypair;
  let buybackWallet: Keypair;
  let stakingWallet: Keypair;
  let backendAuthority: Keypair;
  let usdcMint: PublicKey;

  // Token accounts
  let userTokenAccount: PublicKey;
  let bountyPoolTokenAccount: PublicKey;
  let operationalTokenAccount: PublicKey;
  let buybackTokenAccount: PublicKey;
  let stakingTokenAccount: PublicKey;

  // Constants
  const RESEARCH_FUND_FLOOR = 1_000_000_000; // 1000 USDC (6 decimals)
  const RESEARCH_FEE = 10_000_000; // 10 USDC (6 decimals)
  const BASE_PRICE = 10_000_000; // 10 USDC
  const ENTRY_AMOUNT = 10_000_000; // 10 USDC
  const BOUNTY_ID = 1;

  before(async () => {
    // Generate test keypairs
    authority = Keypair.generate();
    user = Keypair.generate();
    bountyPoolWallet = Keypair.generate();
    operationalWallet = Keypair.generate();
    buybackWallet = Keypair.generate();
    stakingWallet = Keypair.generate();
    backendAuthority = Keypair.generate();

    // Airdrop SOL to test accounts
    await provider.connection.requestAirdrop(authority.publicKey, 10 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(user.publicKey, 10 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(bountyPoolWallet.publicKey, 2 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(operationalWallet.publicKey, 2 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(buybackWallet.publicKey, 2 * LAMPORTS_PER_SOL);
    await provider.connection.requestAirdrop(stakingWallet.publicKey, 2 * LAMPORTS_PER_SOL);

    // Wait for airdrops to confirm
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Create USDC mint for testing
    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6 // 6 decimals for USDC
    );

    // Create token accounts
    userTokenAccount = await createAccount(
      provider.connection,
      user,
      usdcMint,
      user.publicKey
    );

    bountyPoolTokenAccount = await getAssociatedTokenAddress(
      usdcMint,
      bountyPoolWallet.publicKey
    );

    operationalTokenAccount = await getAssociatedTokenAddress(
      usdcMint,
      operationalWallet.publicKey
    );

    buybackTokenAccount = await getAssociatedTokenAddress(
      usdcMint,
      buybackWallet.publicKey
    );

    stakingTokenAccount = await getAssociatedTokenAddress(
      usdcMint,
      stakingWallet.publicKey
    );

    // Mint tokens to user
    await mintTo(
      provider.connection,
      authority,
      usdcMint,
      userTokenAccount,
      authority,
      100_000_000_000 // 100,000 USDC
    );

    // Mint tokens to bounty pool wallet for initial funding
    const bountyPoolATA = await getAssociatedTokenAddress(
      usdcMint,
      bountyPoolWallet.publicKey
    );
    await mintTo(
      provider.connection,
      authority,
      usdcMint,
      bountyPoolATA,
      authority,
      RESEARCH_FUND_FLOOR * 2 // Double the floor amount
    );

    // Wait for transactions to confirm
    await new Promise((resolve) => setTimeout(resolve, 2000));
  });

  describe("Phase 1: 4-way Split & Per-Bounty Tracking", () => {
    it("Initializes lottery with 4 wallets", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const tx = await program.methods
        .initializeLottery(
          new anchor.BN(RESEARCH_FUND_FLOOR),
          new anchor.BN(RESEARCH_FEE),
          bountyPoolWallet.publicKey,
          operationalWallet.publicKey,
          buybackWallet.publicKey,
          stakingWallet.publicKey
        )
        .accounts({
          global: globalPda,
          authority: authority.publicKey,
          bountyPoolWallet: bountyPoolWallet.publicKey,
          operationalWallet: operationalWallet.publicKey,
          buybackWallet: buybackWallet.publicKey,
          stakingWallet: stakingWallet.publicKey,
          bountyPoolTokenAccount: bountyPoolTokenAccount,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const globalAccount = await program.account.global.fetch(globalPda);
      expect(globalAccount.bountyPoolWallet.toString()).to.equal(
        bountyPoolWallet.publicKey.toString()
      );
      expect(globalAccount.operationalWallet.toString()).to.equal(
        operationalWallet.publicKey.toString()
      );
      expect(globalAccount.buybackWallet.toString()).to.equal(
        buybackWallet.publicKey.toString()
      );
      expect(globalAccount.stakingWallet.toString()).to.equal(
        stakingWallet.publicKey.toString()
      );
      expect(globalAccount.bountyPoolRate).to.equal(60);
      expect(globalAccount.operationalRate).to.equal(20);
      expect(globalAccount.buybackRate).to.equal(10);
      expect(globalAccount.stakingRate).to.equal(10);
    });

    it("Initializes a bounty", async () => {
      const [bountyPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("bounty"), Buffer.from(Uint8Array.from([BOUNTY_ID, 0, 0, 0, 0, 0, 0, 0]))],
        program.programId
      );

      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const tx = await program.methods
        .initializeBounty(new anchor.BN(BOUNTY_ID), new anchor.BN(BASE_PRICE))
        .accounts({
          bounty: bountyPda,
          global: globalPda,
          authority: authority.publicKey,
          systemProgram: SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      const bountyAccount = await program.account.bounty.fetch(bountyPda);
      expect(bountyAccount.bountyId.toNumber()).to.equal(BOUNTY_ID);
      expect(bountyAccount.basePrice.toNumber()).to.equal(BASE_PRICE);
      expect(bountyAccount.currentPool.toNumber()).to.equal(0);
      expect(bountyAccount.totalEntries.toNumber()).to.equal(0);
    });

    it("Processes entry payment with 4-way split (60/20/10/10)", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const [bountyPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("bounty"), Buffer.from(Uint8Array.from([BOUNTY_ID, 0, 0, 0, 0, 0, 0, 0]))],
        program.programId
      );

      const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("buyback_tracker")],
        program.programId
      );

      const userBalanceBefore = await getAccount(provider.connection, userTokenAccount);
      const bountyPoolBalanceBefore = await getAccount(
        provider.connection,
        bountyPoolTokenAccount
      );
      const operationalBalanceBefore = await getAccount(
        provider.connection,
        operationalTokenAccount
      );
      const buybackBalanceBefore = await getAccount(provider.connection, buybackTokenAccount);
      const stakingBalanceBefore = await getAccount(provider.connection, stakingTokenAccount);

      const tx = await program.methods
        .processEntryPaymentV2(new anchor.BN(BOUNTY_ID), new anchor.BN(ENTRY_AMOUNT))
        .accounts({
          global: globalPda,
          bounty: bountyPda,
          buybackTracker: buybackTrackerPda,
          user: user.publicKey,
          userTokenAccount: userTokenAccount,
          bountyPoolTokenAccount: bountyPoolTokenAccount,
          operationalTokenAccount: operationalTokenAccount,
          buybackTokenAccount: buybackTokenAccount,
          stakingTokenAccount: stakingTokenAccount,
          bountyPoolWallet: bountyPoolWallet.publicKey,
          operationalWallet: operationalWallet.publicKey,
          buybackWallet: buybackWallet.publicKey,
          stakingWallet: stakingWallet.publicKey,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user])
        .rpc();

      // Verify balances
      const userBalanceAfter = await getAccount(provider.connection, userTokenAccount);
      const bountyPoolBalanceAfter = await getAccount(provider.connection, bountyPoolTokenAccount);
      const operationalBalanceAfter = await getAccount(provider.connection, operationalTokenAccount);
      const buybackBalanceAfter = await getAccount(provider.connection, buybackTokenAccount);
      const stakingBalanceAfter = await getAccount(provider.connection, stakingTokenAccount);

      const expectedBountyPool = ENTRY_AMOUNT * 0.6;
      const expectedOperational = ENTRY_AMOUNT * 0.2;
      const expectedBuyback = ENTRY_AMOUNT * 0.1;
      const expectedStaking = ENTRY_AMOUNT * 0.1;

      expect(
        Number(bountyPoolBalanceBefore.amount) + expectedBountyPool
      ).to.equal(Number(bountyPoolBalanceAfter.amount));
      expect(
        Number(operationalBalanceBefore.amount) + expectedOperational
      ).to.equal(Number(operationalBalanceAfter.amount));
      expect(Number(buybackBalanceBefore.amount) + expectedBuyback).to.equal(
        Number(buybackBalanceAfter.amount)
      );
      expect(Number(stakingBalanceBefore.amount) + expectedStaking).to.equal(
        Number(stakingBalanceAfter.amount)
      );

      // Verify bounty state updated
      const bountyAccount = await program.account.bounty.fetch(bountyPda);
      expect(bountyAccount.totalEntries.toNumber()).to.equal(1);
      expect(bountyAccount.currentPool.toNumber()).to.equal(expectedBountyPool);
    });

    it("Rejects insufficient payment", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const [bountyPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("bounty"), Buffer.from(Uint8Array.from([BOUNTY_ID, 0, 0, 0, 0, 0, 0, 0]))],
        program.programId
      );

      const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("buyback_tracker")],
        program.programId
      );

      try {
        await program.methods
          .processEntryPaymentV2(new anchor.BN(BOUNTY_ID), new anchor.BN(ENTRY_AMOUNT / 2))
          .accounts({
            global: globalPda,
            bounty: bountyPda,
            buybackTracker: buybackTrackerPda,
            user: user.publicKey,
            userTokenAccount: userTokenAccount,
            bountyPoolTokenAccount: bountyPoolTokenAccount,
            operationalTokenAccount: operationalTokenAccount,
            buybackTokenAccount: buybackTokenAccount,
            stakingTokenAccount: stakingTokenAccount,
            bountyPoolWallet: bountyPoolWallet.publicKey,
            operationalWallet: operationalWallet.publicKey,
            buybackWallet: buybackWallet.publicKey,
            stakingWallet: stakingWallet.publicKey,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([user])
          .rpc();
        expect.fail("Should have thrown error");
      } catch (err) {
        expect(err.toString()).to.include("InsufficientPayment");
      }
    });
  });

  describe("Phase 1: Ed25519 Signature Verification", () => {
    it("Sets backend authority public key", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const backendPubkeyBytes = Array.from(backendAuthority.publicKey.toBytes());

      await program.methods
        .setBackendAuthority(backendPubkeyBytes)
        .accounts({
          global: globalPda,
          authority: authority.publicKey,
        })
        .signers([authority])
        .rpc();

      const globalAccount = await program.account.global.fetch(globalPda);
      expect(Array.from(globalAccount.backendAuthorityPubkey)).to.deep.equal(backendPubkeyBytes);
    });

    it("Processes AI decision with valid Ed25519 signature", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const [bountyPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("bounty"), Buffer.from(Uint8Array.from([BOUNTY_ID, 0, 0, 0, 0, 0, 0, 0]))],
        program.programId
      );

      const userMessage = "Test message";
      const aiResponse = "Test response";
      const isSuccessfulJailbreak = false;
      const userId = 123;
      const sessionId = "test-session-123";
      const timestamp = Math.floor(Date.now() / 1000);

      // Compute decision hash (simplified - should match contract logic)
      const decisionHash = Buffer.alloc(32); // Simplified for test

      // Sign with backend authority
      const signature = await ed25519.sign(
        decisionHash,
        backendAuthority.secretKey.slice(0, 32)
      );

      const [noncePda] = PublicKey.findProgramAddressSync(
        [Buffer.from("nonce"), Buffer.from(sessionId)],
        program.programId
      );

      const winner = Keypair.generate();
      const winnerTokenAccount = await getAssociatedTokenAddress(usdcMint, winner.publicKey);

      await program.methods
        .processAiDecisionV2(
          new anchor.BN(BOUNTY_ID),
          userMessage,
          aiResponse,
          Array.from(decisionHash),
          Array.from(signature),
          isSuccessfulJailbreak,
          new anchor.BN(userId),
          sessionId,
          new anchor.BN(timestamp)
        )
        .accounts({
          global: globalPda,
          bounty: bountyPda,
          nonceAccount: noncePda,
          authority: authority.publicKey,
          winner: winner.publicKey,
          bountyPoolTokenAccount: bountyPoolTokenAccount,
          winnerTokenAccount: winnerTokenAccount,
          bountyPoolWallet: bountyPoolWallet.publicKey,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([authority])
        .rpc();

      // Verify nonce was incremented
      const nonceAccount = await program.account.nonceAccount.fetch(noncePda);
      expect(nonceAccount.nonce).to.equal(1);
    });
  });

  describe("Phase 2: Price Escalation", () => {
    it("Enforces price escalation for multiple entries", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const [bountyPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("bounty"), Buffer.from(Uint8Array.from([BOUNTY_ID, 0, 0, 0, 0, 0, 0, 0]))],
        program.programId
      );

      const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("buyback_tracker")],
        program.programId
      );

      // First entry should succeed at base price
      await program.methods
        .processEntryPaymentV2(new anchor.BN(BOUNTY_ID), new anchor.BN(BASE_PRICE))
        .accounts({
          global: globalPda,
          bounty: bountyPda,
          buybackTracker: buybackTrackerPda,
          user: user.publicKey,
          userTokenAccount: userTokenAccount,
          bountyPoolTokenAccount: bountyPoolTokenAccount,
          operationalTokenAccount: operationalTokenAccount,
          buybackTokenAccount: buybackTokenAccount,
          stakingTokenAccount: stakingTokenAccount,
          bountyPoolWallet: bountyPoolWallet.publicKey,
          operationalWallet: operationalWallet.publicKey,
          buybackWallet: buybackWallet.publicKey,
          stakingWallet: stakingWallet.publicKey,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user])
        .rpc();

      // Second entry should require escalated price
      const bountyAccount = await program.account.bounty.fetch(bountyPda);
      const expectedEscalatedPrice = Math.floor(BASE_PRICE * Math.pow(1.0078, bountyAccount.totalEntries.toNumber()));

      // Should reject if payment is less than escalated price
      try {
        await program.methods
          .processEntryPaymentV2(new anchor.BN(BOUNTY_ID), new anchor.BN(BASE_PRICE))
          .accounts({
            global: globalPda,
            bounty: bountyPda,
            buybackTracker: buybackTrackerPda,
            user: user.publicKey,
            userTokenAccount: userTokenAccount,
            bountyPoolTokenAccount: bountyPoolTokenAccount,
            operationalTokenAccount: operationalTokenAccount,
            buybackTokenAccount: buybackTokenAccount,
            stakingTokenAccount: stakingTokenAccount,
            bountyPoolWallet: bountyPoolWallet.publicKey,
            operationalWallet: operationalWallet.publicKey,
            buybackWallet: buybackWallet.publicKey,
            stakingWallet: stakingWallet.publicKey,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([user])
          .rpc();
        expect.fail("Should have thrown error");
      } catch (err) {
        expect(err.toString()).to.include("InsufficientPayment");
      }

      // Should accept escalated price
      await program.methods
        .processEntryPaymentV2(new anchor.BN(BOUNTY_ID), new anchor.BN(expectedEscalatedPrice))
        .accounts({
          global: globalPda,
          bounty: bountyPda,
          buybackTracker: buybackTrackerPda,
          user: user.publicKey,
          userTokenAccount: userTokenAccount,
          bountyPoolTokenAccount: bountyPoolTokenAccount,
          operationalTokenAccount: operationalTokenAccount,
          buybackTokenAccount: buybackTokenAccount,
          stakingTokenAccount: stakingTokenAccount,
          bountyPoolWallet: bountyPoolWallet.publicKey,
          operationalWallet: operationalWallet.publicKey,
          buybackWallet: buybackWallet.publicKey,
          stakingWallet: stakingWallet.publicKey,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user])
        .rpc();
    });
  });

  describe("Phase 2: Buyback Execution", () => {
    it("Executes buyback transfer", async () => {
      const [globalPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("global")],
        program.programId
      );

      const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
        [Buffer.from("buyback_tracker")],
        program.programId
      );

      const buybackTarget = Keypair.generate();
      const buybackTargetTokenAccount = await getAssociatedTokenAddress(
        usdcMint,
        buybackTarget.publicKey
      );

      const buybackAmount = 1_000_000; // 1 USDC

      const trackerBefore = await program.account.buybackTracker.fetch(buybackTrackerPda);
      const buybackBalanceBefore = await getAccount(provider.connection, buybackTokenAccount);

      await program.methods
        .executeBuyback(new anchor.BN(buybackAmount))
        .accounts({
          global: globalPda,
          buybackTracker: buybackTrackerPda,
          authority: authority.publicKey,
          buybackTokenAccount: buybackTokenAccount,
          buybackTargetAccount: buybackTargetTokenAccount,
          buybackWallet: buybackWallet.publicKey,
          buybackTarget: buybackTarget.publicKey,
          buybackAuthority: buybackWallet.publicKey,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .signers([authority])
        .rpc();

      const trackerAfter = await program.account.buybackTracker.fetch(buybackTrackerPda);
      expect(trackerAfter.totalExecuted.toNumber()).to.be.greaterThan(
        trackerBefore.totalExecuted.toNumber()
      );
    });
  });
});



