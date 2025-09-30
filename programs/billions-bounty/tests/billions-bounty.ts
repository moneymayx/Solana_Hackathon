import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBounty } from "../target/types/billions_bounty";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, createMint, createAccount, mintTo, getAccount } from "@solana/spl-token";
import { expect } from "chai";

describe("billions-bounty", () => {
    // Configure the client to use the local cluster.
    anchor.setProvider(anchor.AnchorProvider.env());

    const program = anchor.workspace.BillionsBounty as Program<BillionsBounty>;
    const provider = anchor.getProvider();

    // Test accounts
    let authority: Keypair;
    let user: Keypair;
    let jackpotWallet: Keypair;
    let usdcMint: PublicKey;
    let userTokenAccount: PublicKey;
    let jackpotTokenAccount: PublicKey;

    // Constants
    const RESEARCH_FUND_FLOOR = 10000; // $10,000
    const RESEARCH_FEE = 10; // $10
    const ENTRY_AMOUNT = 10; // $10

    before(async () => {
        // Generate test keypairs
        authority = Keypair.generate();
        user = Keypair.generate();
        jackpotWallet = Keypair.generate();

        // Airdrop SOL to test accounts
        await provider.connection.requestAirdrop(authority.publicKey, 2 * anchor.web3.LAMPORTS_PER_SOL);
        await provider.connection.requestAirdrop(user.publicKey, 2 * anchor.web3.LAMPORTS_PER_SOL);
        await provider.connection.requestAirdrop(jackpotWallet.publicKey, 2 * anchor.web3.LAMPORTS_PER_SOL);

        // Wait for airdrops to confirm
        await new Promise(resolve => setTimeout(resolve, 1000));

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

        jackpotTokenAccount = await createAccount(
            provider.connection,
            authority,
            usdcMint,
            jackpotWallet.publicKey
        );

        // Mint USDC to user for testing
        await mintTo(
            provider.connection,
            authority,
            usdcMint,
            userTokenAccount,
            authority,
            1000 * 10**6 // 1000 USDC
        );
    });

    it("Initializes lottery system", async () => {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            program.programId
        );

        const tx = await program.methods
            .initializeLottery(
                new anchor.BN(RESEARCH_FUND_FLOOR),
                new anchor.BN(RESEARCH_FEE),
                jackpotWallet.publicKey
            )
            .accounts({
                lottery: lotteryPDA,
                authority: authority.publicKey,
                jackpotWallet: jackpotWallet.publicKey,
                systemProgram: SystemProgram.programId,
            })
            .signers([authority])
            .rpc();

        console.log("Initialize lottery transaction signature:", tx);

        // Verify lottery state
        const lottery = await program.account.lottery.fetch(lotteryPDA);
        expect(lottery.authority.toString()).to.equal(authority.publicKey.toString());
        expect(lottery.jackpotWallet.toString()).to.equal(jackpotWallet.publicKey.toString());
        expect(lottery.researchFundFloor.toNumber()).to.equal(RESEARCH_FUND_FLOOR);
        expect(lottery.researchFee.toNumber()).to.equal(RESEARCH_FEE);
        expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR);
        expect(lottery.isActive).to.be.true;
    });

    it("Processes entry payment and locks funds", async () => {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            program.programId
        );

        const [entryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
            program.programId
        );

        // Get initial balances
        const initialUserBalance = await getAccount(provider.connection, userTokenAccount);
        const initialJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

        const tx = await program.methods
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

        console.log("Process entry payment transaction signature:", tx);

        // Verify entry was created
        const entry = await program.account.entry.fetch(entryPDA);
        expect(entry.userWallet.toString()).to.equal(user.publicKey.toString());
        expect(entry.amountPaid.toNumber()).to.equal(ENTRY_AMOUNT);
        expect(entry.researchContribution.toNumber()).to.equal(8); // 80% of $10
        expect(entry.operationalFee.toNumber()).to.equal(2); // 20% of $10

        // Verify funds were transferred
        const finalUserBalance = await getAccount(provider.connection, userTokenAccount);
        const finalJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

        expect(initialUserBalance.amount - finalUserBalance.amount).to.equal(ENTRY_AMOUNT);
        expect(finalJackpotBalance.amount - initialJackpotBalance.amount).to.equal(ENTRY_AMOUNT);

        // Verify lottery state was updated
        const lottery = await program.account.lottery.fetch(lotteryPDA);
        expect(lottery.totalEntries.toNumber()).to.equal(1);
        expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR + 8);
    });

    it("Selects winner and transfers jackpot", async () => {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            program.programId
        );

        const [winnerPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("winner"), lotteryPDA.toBuffer()],
            program.programId
        );

        // Get initial jackpot balance
        const initialJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

        const tx = await program.methods
            .selectWinner()
            .accounts({
                lottery: lotteryPDA,
                winner: winnerPDA,
                lotteryAuthority: authority.publicKey,
                jackpotTokenAccount: jackpotTokenAccount,
                winnerTokenAccount: userTokenAccount, // Winner gets funds in their token account
                usdcMint: usdcMint,
                clock: anchor.web3.SYSVAR_CLOCK_PUBKEY,
                tokenProgram: TOKEN_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        console.log("Select winner transaction signature:", tx);

        // Verify winner was recorded
        const winner = await program.account.winner.fetch(winnerPDA);
        expect(winner.lotteryId.toString()).to.equal(lotteryPDA.toString());
        expect(winner.jackpotAmount.toNumber()).to.be.greaterThan(0);
        expect(winner.isClaimed).to.be.false;

        // Verify jackpot was reset
        const lottery = await program.account.lottery.fetch(lotteryPDA);
        expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR);
        expect(lottery.totalEntries.toNumber()).to.equal(0);
    });

    it("Handles emergency recovery", async () => {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            program.programId
        );

        // First, add some funds to jackpot by processing an entry
        const [entryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
            program.programId
        );

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

        // Get initial balances
        const initialAuthorityBalance = await getAccount(provider.connection, userTokenAccount);
        const initialJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

        const recoveryAmount = 5; // Recover $5

        const tx = await program.methods
            .emergencyRecovery(new anchor.BN(recoveryAmount))
            .accounts({
                lottery: lotteryPDA,
                authority: authority.publicKey,
                jackpotTokenAccount: jackpotTokenAccount,
                authorityTokenAccount: userTokenAccount, // Authority gets funds in their token account
                usdcMint: usdcMint,
                tokenProgram: TOKEN_PROGRAM_ID,
            })
            .signers([authority])
            .rpc();

        console.log("Emergency recovery transaction signature:", tx);

        // Verify funds were recovered
        const finalAuthorityBalance = await getAccount(provider.connection, userTokenAccount);
        const finalJackpotBalance = await getAccount(provider.connection, jackpotTokenAccount);

        expect(finalAuthorityBalance.amount - initialAuthorityBalance.amount).to.equal(recoveryAmount);
        expect(initialJackpotBalance.amount - finalJackpotBalance.amount).to.equal(recoveryAmount);

        // Verify lottery state was updated
        const lottery = await program.account.lottery.fetch(lotteryPDA);
        expect(lottery.currentJackpot.toNumber()).to.equal(RESEARCH_FUND_FLOOR + 8 - recoveryAmount);
    });

    it("Prevents unauthorized access", async () => {
        const unauthorizedUser = Keypair.generate();
        
        // Try to perform emergency recovery with unauthorized user
        try {
            const [lotteryPDA] = PublicKey.findProgramAddressSync(
                [Buffer.from("lottery")],
                program.programId
            );

            await program.methods
                .emergencyRecovery(new anchor.BN(1))
                .accounts({
                    lottery: lotteryPDA,
                    authority: unauthorizedUser.publicKey,
                    jackpotTokenAccount: jackpotTokenAccount,
                    authorityTokenAccount: userTokenAccount,
                    usdcMint: usdcMint,
                    tokenProgram: TOKEN_PROGRAM_ID,
                })
                .signers([unauthorizedUser])
                .rpc();

            expect.fail("Should have thrown an error for unauthorized access");
        } catch (error) {
            expect(error.message).to.include("Unauthorized");
        }
    });

    it("Validates minimum payment amount", async () => {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            program.programId
        );

        const [entryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
            program.programId
        );

        try {
            await program.methods
                .processEntryPayment(
                    new anchor.BN(1), // Less than minimum fee
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

            expect.fail("Should have thrown an error for insufficient payment");
        } catch (error) {
            expect(error.message).to.include("InsufficientPayment");
        }
    });
});
