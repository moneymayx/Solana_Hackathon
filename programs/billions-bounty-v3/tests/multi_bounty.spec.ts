import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAssociatedTokenAddress, createMint, mintTo, createAccount } from "@solana/spl-token";
import { expect } from "chai";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";

describe("Multi-Bounty Smart Contract", () => {
  // Configure the client to use the local cluster.
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const program = anchor.workspace.BillionsBountyV3 as Program<BillionsBountyV3>;

  // Test accounts
  let authority: Keypair;
  let jackpotWallet: Keypair;
  let backendAuthority: Keypair;
  let user1: Keypair;
  let user2: Keypair;
  let user3: Keypair;
  let usdcMint: PublicKey;
  let buybackWallet: Keypair;

  // Bounty configurations
  const BOUNTY_CONFIGS = {
    1: { name: "Expert", floor: 10_000_000_000, fee: 10_000_000 }, // $10,000 floor, $10 fee
    2: { name: "Hard", floor: 5_000_000_000, fee: 5_000_000 },     // $5,000 floor, $5 fee
    3: { name: "Medium", floor: 2_500_000_000, fee: 2_500_000 },   // $2,500 floor, $2.50 fee
    4: { name: "Easy", floor: 500_000_000, fee: 500_000 },          // $500 floor, $0.50 fee
  };

  // Lottery PDAs for each bounty
  const lotteryPDAs: { [key: number]: PublicKey } = {};
  const lotteryBumps: { [key: number]: number } = {};

  before(async () => {
    // Generate test keypairs
    authority = Keypair.generate();
    jackpotWallet = Keypair.generate();
    backendAuthority = Keypair.generate();
    user1 = Keypair.generate();
    user2 = Keypair.generate();
    user3 = Keypair.generate();
    buybackWallet = Keypair.generate();

    // Airdrop SOL to test accounts
    const airdropAmount = 2 * anchor.web3.LAMPORTS_PER_SOL;
    await Promise.all([
      provider.connection.requestAirdrop(authority.publicKey, airdropAmount),
      provider.connection.requestAirdrop(jackpotWallet.publicKey, airdropAmount),
      provider.connection.requestAirdrop(user1.publicKey, airdropAmount),
      provider.connection.requestAirdrop(user2.publicKey, airdropAmount),
      provider.connection.requestAirdrop(user3.publicKey, airdropAmount),
      provider.connection.requestAirdrop(buybackWallet.publicKey, airdropAmount),
    ]);

    // Create USDC mint (devnet/test)
    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6 // 6 decimals for USDC
    );

    // Derive lottery PDAs for all bounties
    for (const bountyId of [1, 2, 3, 4]) {
      const [pda, bump] = PublicKey.findProgramAddressSync(
        [Buffer.from("lottery"), Buffer.from([bountyId])],
        program.programId
      );
      lotteryPDAs[bountyId] = pda;
      lotteryBumps[bountyId] = bump;
    }
  });

  describe("Multi-Bounty Initialization", () => {
    it("Initializes all 4 bounties independently", async () => {
      for (const bountyId of [1, 2, 3, 4] as const) {
        const config = BOUNTY_CONFIGS[bountyId];
        
        // Create jackpot token account for this bounty
        const jackpotTokenAccount = await getAssociatedTokenAddress(
          usdcMint,
          lotteryPDAs[bountyId],
          true
        );

        // Fund jackpot wallet with initial floor amount
        const jackpotWalletTokenAccount = await getAssociatedTokenAddress(
          usdcMint,
          jackpotWallet.publicKey
        );
        await createAccount(provider.connection, authority, usdcMint, jackpotWallet.publicKey);
        await mintTo(
          provider.connection,
          authority,
          usdcMint,
          jackpotWalletTokenAccount,
          authority,
          config.floor
        );

        // Initialize lottery
        const tx = await program.methods
          .initializeLottery(
            bountyId,
            new anchor.BN(config.floor),
            new anchor.BN(config.fee),
            jackpotWallet.publicKey,
            backendAuthority.publicKey
          )
          .accounts({
            lottery: lotteryPDAs[bountyId],
            authority: authority.publicKey,
            jackpotWallet: jackpotWallet.publicKey,
            jackpotTokenAccount: jackpotTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([authority])
          .rpc();

        console.log(`✅ Bounty ${bountyId} initialized: ${tx}`);

        // Verify lottery account exists
        const lotteryAccount = await program.account.lottery.fetch(lotteryPDAs[bountyId]);
        expect(lotteryAccount.bountyId).to.equal(bountyId);
        expect(lotteryAccount.researchFundFloor.toNumber()).to.equal(config.floor);
        expect(lotteryAccount.researchFee.toNumber()).to.equal(config.fee);
        expect(lotteryAccount.isActive).to.be.true;
      }
    });

    it("Rejects invalid bounty_id (0)", async () => {
      try {
        await program.methods
          .initializeLottery(
            0, // Invalid bounty_id
            new anchor.BN(1000_000_000),
            new anchor.BN(10_000_000),
            jackpotWallet.publicKey,
            backendAuthority.publicKey
          )
          .accounts({
            lottery: lotteryPDAs[1],
            authority: authority.publicKey,
            jackpotWallet: jackpotWallet.publicKey,
            jackpotTokenAccount: await getAssociatedTokenAddress(usdcMint, lotteryPDAs[1], true),
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        
        expect.fail("Should have rejected invalid bounty_id");
      } catch (err: any) {
        expect(err.toString()).to.include("InvalidBountyId");
      }
    });

    it("Rejects invalid bounty_id (5)", async () => {
      try {
        await program.methods
          .initializeLottery(
            5, // Invalid bounty_id
            new anchor.BN(1000_000_000),
            new anchor.BN(10_000_000),
            jackpotWallet.publicKey,
            backendAuthority.publicKey
          )
          .accounts({
            lottery: lotteryPDAs[1],
            authority: authority.publicKey,
            jackpotWallet: jackpotWallet.publicKey,
            jackpotTokenAccount: await getAssociatedTokenAddress(usdcMint, lotteryPDAs[1], true),
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([authority])
          .rpc();
        
        expect.fail("Should have rejected invalid bounty_id");
      } catch (err: any) {
        expect(err.toString()).to.include("InvalidBountyId");
      }
    });

    it("Verifies bounties are isolated (modifying one doesn't affect others)", async () => {
      // Fetch all lottery accounts
      const lottery1 = await program.account.lottery.fetch(lotteryPDAs[1]);
      const lottery2 = await program.account.lottery.fetch(lotteryPDAs[2]);
      const lottery3 = await program.account.lottery.fetch(lotteryPDAs[3]);
      const lottery4 = await program.account.lottery.fetch(lotteryPDAs[4]);

      // Verify they have different bounty_ids
      expect(lottery1.bountyId).to.equal(1);
      expect(lottery2.bountyId).to.equal(2);
      expect(lottery3.bountyId).to.equal(3);
      expect(lottery4.bountyId).to.equal(4);

      // Verify they have different configurations
      expect(lottery1.researchFundFloor.toNumber()).to.not.equal(lottery2.researchFundFloor.toNumber());
      expect(lottery2.researchFundFloor.toNumber()).to.not.equal(lottery3.researchFundFloor.toNumber());
      expect(lottery3.researchFundFloor.toNumber()).to.not.equal(lottery4.researchFundFloor.toNumber());
    });
  });

  describe("User Bounty State Management", () => {
    it("User can enter bounty 1 when no active bounty", async () => {
      const bountyId = 1;
      const entryAmount = BOUNTY_CONFIGS[bountyId].fee;
      const entryNonce = 1;

      // Create user token account and fund it
      const userTokenAccount = await getAssociatedTokenAddress(usdcMint, user1.publicKey);
      await createAccount(provider.connection, user1, usdcMint, user1.publicKey);
      await mintTo(provider.connection, authority, usdcMint, userTokenAccount, authority, entryAmount * 2);

      // Derive user bounty state PDA
      const [userBountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user1.publicKey.toBuffer()],
        program.programId
      );

      // Derive entry PDA
      const [entryPDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("entry"),
          lotteryPDAs[bountyId].toBuffer(),
          user1.publicKey.toBuffer(),
          Buffer.from(entryNonce.toString().padStart(8, "0")),
        ],
        program.programId
      );

      const jackpotTokenAccount = await getAssociatedTokenAddress(usdcMint, lotteryPDAs[bountyId], true);
      const buybackTokenAccount = await getAssociatedTokenAddress(usdcMint, buybackWallet.publicKey);

      // Process entry payment
      const tx = await program.methods
        .processEntryPayment(
          bountyId,
          new anchor.BN(entryAmount),
          user1.publicKey,
          new anchor.BN(entryNonce)
        )
        .accounts({
          lottery: lotteryPDAs[bountyId],
          userBountyState: userBountyStatePDA,
          entry: entryPDA,
          user: user1.publicKey,
          userWallet: user1.publicKey,
          userTokenAccount: userTokenAccount,
          jackpotTokenAccount: jackpotTokenAccount,
          buybackWallet: buybackWallet.publicKey,
          buybackTokenAccount: buybackTokenAccount,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user1])
        .rpc();

      console.log(`✅ User entered bounty ${bountyId}: ${tx}`);

      // Verify user bounty state
      const userBountyState = await program.account.userBountyState.fetch(userBountyStatePDA);
      expect(userBountyState.activeBountyId).to.equal(bountyId);
      expect(userBountyState.userWallet.toString()).to.equal(user1.publicKey.toString());
    });

    it("User can enter same bounty multiple times", async () => {
      const bountyId = 1;
      const entryAmount = BOUNTY_CONFIGS[bountyId].fee;
      const entryNonce = 2; // Second entry

      const userTokenAccount = await getAssociatedTokenAddress(usdcMint, user1.publicKey);
      const [userBountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user1.publicKey.toBuffer()],
        program.programId
      );
      const [entryPDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("entry"),
          lotteryPDAs[bountyId].toBuffer(),
          user1.publicKey.toBuffer(),
          Buffer.from(entryNonce.toString().padStart(8, "0")),
        ],
        program.programId
      );
      const jackpotTokenAccount = await getAssociatedTokenAddress(usdcMint, lotteryPDAs[bountyId], true);
      const buybackTokenAccount = await getAssociatedTokenAddress(usdcMint, buybackWallet.publicKey);

      // Process second entry in same bounty
      const tx = await program.methods
        .processEntryPayment(
          bountyId,
          new anchor.BN(entryAmount),
          user1.publicKey,
          new anchor.BN(entryNonce)
        )
        .accounts({
          lottery: lotteryPDAs[bountyId],
          userBountyState: userBountyStatePDA,
          entry: entryPDA,
          user: user1.publicKey,
          userWallet: user1.publicKey,
          userTokenAccount: userTokenAccount,
          jackpotTokenAccount: jackpotTokenAccount,
          buybackWallet: buybackWallet.publicKey,
          buybackTokenAccount: buybackTokenAccount,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user1])
        .rpc();

      console.log(`✅ User entered bounty ${bountyId} again: ${tx}`);

      // Verify user bounty state still shows active in same bounty
      const userBountyState = await program.account.userBountyState.fetch(userBountyStatePDA);
      expect(userBountyState.activeBountyId).to.equal(bountyId);
      expect(userBountyState.totalEntries.toNumber()).to.equal(2);
    });

    it("User cannot enter different bounty while active in another", async () => {
      const activeBountyId = 1;
      const differentBountyId = 2;
      const entryAmount = BOUNTY_CONFIGS[differentBountyId].fee;
      const entryNonce = 1;

      // User1 is already active in bounty 1, try to enter bounty 2
      const userTokenAccount = await getAssociatedTokenAddress(usdcMint, user1.publicKey);
      const [userBountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user1.publicKey.toBuffer()],
        program.programId
      );
      const [entryPDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("entry"),
          lotteryPDAs[differentBountyId].toBuffer(),
          user1.publicKey.toBuffer(),
          Buffer.from(entryNonce.toString().padStart(8, "0")),
        ],
        program.programId
      );
      const jackpotTokenAccount = await getAssociatedTokenAddress(usdcMint, lotteryPDAs[differentBountyId], true);
      const buybackTokenAccount = await getAssociatedTokenAddress(usdcMint, buybackWallet.publicKey);

      try {
        await program.methods
          .processEntryPayment(
            differentBountyId,
            new anchor.BN(entryAmount),
            user1.publicKey,
            new anchor.BN(entryNonce)
          )
          .accounts({
            lottery: lotteryPDAs[differentBountyId],
            userBountyState: userBountyStatePDA,
            entry: entryPDA,
            user: user1.publicKey,
            userWallet: user1.publicKey,
            userTokenAccount: userTokenAccount,
            jackpotTokenAccount: jackpotTokenAccount,
            buybackWallet: buybackWallet.publicKey,
            buybackTokenAccount: buybackTokenAccount,
            usdcMint: usdcMint,
            tokenProgram: TOKEN_PROGRAM_ID,
            associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
            systemProgram: SystemProgram.programId,
          })
          .signers([user1])
          .rpc();
        
        expect.fail("Should have rejected entry in different bounty");
      } catch (err: any) {
        expect(err.toString()).to.include("UserActiveInDifferentBounty");
      }
    });

    it("Multiple users can enter different bounties simultaneously", async () => {
      // User2 enters bounty 2
      const bountyId2 = 2;
      const entryAmount2 = BOUNTY_CONFIGS[bountyId2].fee;
      
      const user2TokenAccount = await getAssociatedTokenAddress(usdcMint, user2.publicKey);
      await createAccount(provider.connection, user2, usdcMint, user2.publicKey);
      await mintTo(provider.connection, authority, usdcMint, user2TokenAccount, authority, entryAmount2 * 2);

      const [user2BountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user2.publicKey.toBuffer()],
        program.programId
      );
      const [entry2PDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("entry"),
          lotteryPDAs[bountyId2].toBuffer(),
          user2.publicKey.toBuffer(),
          Buffer.from("1".padStart(8, "0")),
        ],
        program.programId
      );
      const jackpotTokenAccount2 = await getAssociatedTokenAddress(usdcMint, lotteryPDAs[bountyId2], true);
      const buybackTokenAccount2 = await getAssociatedTokenAddress(usdcMint, buybackWallet.publicKey);

      const tx2 = await program.methods
        .processEntryPayment(
          bountyId2,
          new anchor.BN(entryAmount2),
          user2.publicKey,
          new anchor.BN(1)
        )
        .accounts({
          lottery: lotteryPDAs[bountyId2],
          userBountyState: user2BountyStatePDA,
          entry: entry2PDA,
          user: user2.publicKey,
          userWallet: user2.publicKey,
          userTokenAccount: user2TokenAccount,
          jackpotTokenAccount: jackpotTokenAccount2,
          buybackWallet: buybackWallet.publicKey,
          buybackTokenAccount: buybackTokenAccount2,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user2])
        .rpc();

      console.log(`✅ User2 entered bounty ${bountyId2}: ${tx2}`);

      // Verify both users are active in different bounties
      const user1State = await program.account.userBountyState.fetch(
        PublicKey.findProgramAddressSync(
          [Buffer.from("user_bounty"), user1.publicKey.toBuffer()],
          program.programId
        )[0]
      );
      const user2State = await program.account.userBountyState.fetch(user2BountyStatePDA);

      expect(user1State.activeBountyId).to.equal(1);
      expect(user2State.activeBountyId).to.equal(2);
    });
  });

  describe("Independent Jackpot Growth", () => {
    it("Entry in bounty 1 only increases bounty 1 jackpot", async () => {
      const bountyId = 1;
      const entryAmount = BOUNTY_CONFIGS[bountyId].fee;

      // Get initial jackpots
      const lottery1Before = await program.account.lottery.fetch(lotteryPDAs[1]);
      const lottery2Before = await program.account.lottery.fetch(lotteryPDAs[2]);
      const initialJackpot1 = lottery1Before.currentJackpot.toNumber();
      const initialJackpot2 = lottery2Before.currentJackpot.toNumber();

      // User3 enters bounty 1
      const user3TokenAccount = await getAssociatedTokenAddress(usdcMint, user3.publicKey);
      await createAccount(provider.connection, user3, usdcMint, user3.publicKey);
      await mintTo(provider.connection, authority, usdcMint, user3TokenAccount, authority, entryAmount * 2);

      const [user3BountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user3.publicKey.toBuffer()],
        program.programId
      );
      const [entryPDA] = PublicKey.findProgramAddressSync(
        [
          Buffer.from("entry"),
          lotteryPDAs[bountyId].toBuffer(),
          user3.publicKey.toBuffer(),
          Buffer.from("1".padStart(8, "0")),
        ],
        program.programId
      );
      const jackpotTokenAccount = await getAssociatedTokenAddress(usdcMint, lotteryPDAs[bountyId], true);
      const buybackTokenAccount = await getAssociatedTokenAddress(usdcMint, buybackWallet.publicKey);

      await program.methods
        .processEntryPayment(
          bountyId,
          new anchor.BN(entryAmount),
          user3.publicKey,
          new anchor.BN(1)
        )
        .accounts({
          lottery: lotteryPDAs[bountyId],
          userBountyState: user3BountyStatePDA,
          entry: entryPDA,
          user: user3.publicKey,
          userWallet: user3.publicKey,
          userTokenAccount: user3TokenAccount,
          jackpotTokenAccount: jackpotTokenAccount,
          buybackWallet: buybackWallet.publicKey,
          buybackTokenAccount: buybackTokenAccount,
          usdcMint: usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user3])
        .rpc();

      // Verify jackpot growth
      const lottery1After = await program.account.lottery.fetch(lotteryPDAs[1]);
      const lottery2After = await program.account.lottery.fetch(lotteryPDAs[2]);

      // Bounty 1 jackpot should have increased (60% of entry)
      const expectedIncrease = Math.floor(entryAmount * 0.6);
      expect(lottery1After.currentJackpot.toNumber()).to.equal(initialJackpot1 + expectedIncrease);
      
      // Bounty 2 jackpot should be unchanged
      expect(lottery2After.currentJackpot.toNumber()).to.equal(initialJackpot2);
    });
  });

  describe("Winner Selection Per Bounty", () => {
    it("Winner selection clears user's active_bounty_id", async () => {
      // This test would require setting up a successful jailbreak scenario
      // For now, we'll verify the structure is in place
      const [userBountyStatePDA] = PublicKey.findProgramAddressSync(
        [Buffer.from("user_bounty"), user1.publicKey.toBuffer()],
        program.programId
      );

      // User1 should still be active in bounty 1 from previous tests
      const userState = await program.account.userBountyState.fetch(userBountyStatePDA);
      expect(userState.activeBountyId).to.equal(1);

      // Note: Full winner selection test would require:
      // - Setting up AI decision payload
      // - Calling process_ai_decision with is_successful_jailbreak=true
      // - Verifying active_bounty_id is cleared to 0
      // This is a placeholder for the full implementation
    });
  });
});

