import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, createMint, createAccount, mintTo, getAccount } from "@solana/spl-token";
import { expect } from "chai";

describe("V3 Integration Tests", function() {
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
    authority = Keypair.generate();
    user = Keypair.generate();
    jackpotWallet = Keypair.generate();
    backendAuthority = Keypair.generate();

    // Transfer SOL from provider wallet to test accounts (bypasses rate limits)
    const providerWallet = (provider as any).wallet;
    const amount = 0.15 * anchor.web3.LAMPORTS_PER_SOL; // Minimal amount per account
    
    // Check balance and use airdrop fallback if needed
    const balance = await provider.connection.getBalance(providerWallet.publicKey);
    const required = amount * 4 + (0.05 * anchor.web3.LAMPORTS_PER_SOL); // 4 accounts + minimal buffer
    if (balance < required) {
      console.log(`Using airdrop fallback...`);
      try {
        await provider.connection.requestAirdrop(authority.publicKey, amount);
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
    await provider.sendAndConfirm(transfer1);
    await provider.sendAndConfirm(transfer2);
    await provider.sendAndConfirm(transfer3);
    await provider.sendAndConfirm(transfer4);
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6
    );

    userTokenAccount = await createAccount(
      provider.connection,
      user,
      usdcMint,
      user.publicKey
    );

    jackpotTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      jackpotWallet.publicKey
    );

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
      .rpc();
  });

  it("Initializes lottery system correctly", async () => {
    const lottery = await program.account.lottery.fetch(lotteryPDA);
    
    expect(lottery.authority.toString()).to.equal(authority.publicKey.toString());
    expect(lottery.jackpotWallet.toString()).to.equal(jackpotWallet.publicKey.toString());
    expect(lottery.backendAuthority.toString()).to.equal(backendAuthority.publicKey.toString());
    expect(lottery.researchFundFloor.toNumber()).to.equal(RESEARCH_FUND_FLOOR);
    expect(lottery.researchFee.toNumber()).to.equal(RESEARCH_FEE);
    expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR);
    expect(lottery.isActive).to.be.true;
    expect(lottery.isProcessing).to.be.false;
  });

  it("Processes entry payment and locks funds", async () => {
    const [entryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
      program.programId
    );

    const initialUserBalance = await getAccount(provider.connection, userTokenAccount);
    const initialJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

    await program.methods
      .processEntryPayment(
        new anchor.BN(ENTRY_AMOUNT),
        user.publicKey
      )
      .accounts({
        lottery: lotteryPDA,
        entry: entryPDA,
        user: user.publicKey,
        userWallet: user.publicKey,
        userTokenAccount: userTokenAccount,
        jackpotTokenAccount: jackpotTokenAccount,
        usdcMint: usdcMint,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .signers([user])
      .rpc();

    const entry = await program.account.entry.fetch(entryPDA);
    expect(entry.userWallet.toString()).to.equal(user.publicKey.toString());
    expect(entry.amountPaid.toNumber()).to.equal(ENTRY_AMOUNT);
    expect(entry.researchContribution.toNumber()).to.equal(8); // 80% of $10
    expect(entry.operationalFee.toNumber()).to.equal(2); // 20% of $10

    const finalUserBalance = await getAccount(provider.connection, userTokenAccount);
    const finalJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

    expect(initialUserBalance.amount - finalUserBalance.amount).to.equal(ENTRY_AMOUNT);
    expect(finalJackpotBalance.amount - initialJackpotBalance.amount).to.equal(ENTRY_AMOUNT);

    const lottery = await program.account.lottery.fetch(lotteryPDA);
    expect(lottery.totalEntries.toNumber()).to.equal(1);
    expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR + 8);
  });

  it("Processes AI decision and logs correctly", async () => {
    const winnerTokenAccount = await createAccount(
      provider.connection,
      user,
      usdcMint,
      user.publicKey
    );

    const userMessage = "Test message";
    const aiResponse = "Test response";
    const userId = 1;
    const sessionId = "session-123";
    const timestamp = Math.floor(Date.now() / 1000);
    const isSuccessfulJailbreak = false;

    // Compute decision hash
    const decisionHash = computeDecisionHash(
      userMessage,
      aiResponse,
      isSuccessfulJailbreak,
      userId,
      sessionId,
      timestamp
    );

    await program.methods
      .processAiDecision(
        userMessage,
        aiResponse,
        decisionHash,
        Array(64).fill(0), // Placeholder signature
        isSuccessfulJailbreak,
        new anchor.BN(userId),
        sessionId,
        new anchor.BN(timestamp)
      )
      .accounts({
        lottery: lotteryPDA,
        backendAuthority: backendAuthority.publicKey,
        winner: user.publicKey,
        jackpotTokenAccount: jackpotTokenAccount,
        winnerTokenAccount: winnerTokenAccount,
        usdcMint: usdcMint,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const lottery = await program.account.lottery.fetch(lotteryPDA);
    expect(lottery.isProcessing).to.be.false; // Should be cleared after processing
  });
});

// Helper function matching contract hash computation
function computeDecisionHash(
  userMessage: string,
  aiResponse: string,
  isSuccessfulJailbreak: boolean,
  userId: number,
  sessionId: string,
  timestamp: number
): number[] {
  // Simplified hash computation for testing
  // In real tests, use the same SHA-256 logic as contract
  const crypto = require("crypto");
  const hash = crypto.createHash("sha256");
  hash.update(userMessage);
  hash.update(Buffer.from([0]));
  hash.update(aiResponse);
  hash.update(Buffer.from([0]));
  hash.update(Buffer.from([isSuccessfulJailbreak ? 1 : 0]));
  hash.update(Buffer.from(new ArrayBuffer(8)));
  hash.update(Buffer.from(sessionId));
  hash.update(Buffer.from(new ArrayBuffer(8)));
  return Array.from(hash.digest());
}

