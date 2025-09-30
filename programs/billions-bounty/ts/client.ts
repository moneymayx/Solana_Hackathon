import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBounty } from "../target/types/billions_bounty";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from "@solana/spl-token";

export class BillionsBountyClient {
    private program: Program<BillionsBounty>;
    private provider: anchor.AnchorProvider;

    constructor(provider: anchor.AnchorProvider) {
        this.provider = provider;
        this.program = new Program<BillionsBounty>(
            require("../target/idl/billions_bounty.json"),
            provider
        );
    }

    /**
     * Initialize the lottery system
     */
    async initializeLottery(
        researchFundFloor: number,
        researchFee: number,
        jackpotWallet: PublicKey,
        authority: Keypair
    ): Promise<string> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const tx = await this.program.methods
            .initializeLottery(
                new anchor.BN(researchFundFloor),
                new anchor.BN(researchFee),
                jackpotWallet
            )
            .accounts({
                lottery: lotteryPDA,
                authority: authority.publicKey,
                jackpotWallet: jackpotWallet,
                systemProgram: SystemProgram.programId,
            })
            .signers([authority])
            .rpc();

        return tx;
    }

    /**
     * Process a lottery entry payment
     */
    async processEntryPayment(
        entryAmount: number,
        userWallet: PublicKey,
        user: Keypair,
        usdcMint: PublicKey
    ): Promise<string> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const [entryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("entry"), lotteryPDA.toBuffer(), user.publicKey.toBuffer()],
            this.program.programId
        );

        const userTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            user.publicKey
        );

        const jackpotTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            lotteryPDA
        );

        const tx = await this.program.methods
            .processEntryPayment(
                new anchor.BN(entryAmount),
                userWallet
            )
            .accounts({
                lottery: lotteryPDA,
                entry: entryPDA,
                user: user.publicKey,
                userWallet: userWallet,
                userTokenAccount: userTokenAccount,
                jackpotTokenAccount: jackpotTokenAccount,
                usdcMint: usdcMint,
                tokenProgram: TOKEN_PROGRAM_ID,
                associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .signers([user])
            .rpc();

        return tx;
    }

    /**
     * Select a winner (autonomous function)
     */
    async selectWinner(
        lotteryAuthority: PublicKey,
        winnerWallet: PublicKey,
        usdcMint: PublicKey
    ): Promise<string> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const [winnerPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("winner"), lotteryPDA.toBuffer()],
            this.program.programId
        );

        const jackpotTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            lotteryPDA
        );

        const winnerTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            winnerWallet
        );

        const tx = await this.program.methods
            .selectWinner()
            .accounts({
                lottery: lotteryPDA,
                winner: winnerPDA,
                lotteryAuthority: lotteryAuthority,
                jackpotTokenAccount: jackpotTokenAccount,
                winnerTokenAccount: winnerTokenAccount,
                usdcMint: usdcMint,
                clock: anchor.web3.SYSVAR_CLOCK_PUBKEY,
                tokenProgram: TOKEN_PROGRAM_ID,
                systemProgram: SystemProgram.programId,
            })
            .rpc();

        return tx;
    }

    /**
     * Emergency fund recovery (authority only)
     */
    async emergencyRecovery(
        amount: number,
        authority: Keypair,
        usdcMint: PublicKey
    ): Promise<string> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const jackpotTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            lotteryPDA
        );

        const authorityTokenAccount = await this.getAssociatedTokenAddress(
            usdcMint,
            authority.publicKey
        );

        const tx = await this.program.methods
            .emergencyRecovery(new anchor.BN(amount))
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

        return tx;
    }

    /**
     * Get lottery state
     */
    async getLotteryState(): Promise<any> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        try {
            const lottery = await this.program.account.lottery.fetch(lotteryPDA);
            return lottery;
        } catch (error) {
            console.error("Error fetching lottery state:", error);
            return null;
        }
    }

    /**
     * Get entry details
     */
    async getEntry(user: PublicKey): Promise<any> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const [entryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("entry"), lotteryPDA.toBuffer(), user.toBuffer()],
            this.program.programId
        );

        try {
            const entry = await this.program.account.entry.fetch(entryPDA);
            return entry;
        } catch (error) {
            console.error("Error fetching entry:", error);
            return null;
        }
    }

    /**
     * Get winner details
     */
    async getWinner(): Promise<any> {
        const [lotteryPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("lottery")],
            this.program.programId
        );

        const [winnerPDA] = PublicKey.findProgramAddressSync(
            [Buffer.from("winner"), lotteryPDA.toBuffer()],
            this.program.programId
        );

        try {
            const winner = await this.program.account.winner.fetch(winnerPDA);
            return winner;
        } catch (error) {
            console.error("Error fetching winner:", error);
            return null;
        }
    }

    /**
     * Get associated token address
     */
    private async getAssociatedTokenAddress(
        mint: PublicKey,
        owner: PublicKey
    ): Promise<PublicKey> {
        return await anchor.utils.token.associatedAddress({
            mint,
            owner,
        });
    }

    /**
     * Calculate fund distribution for an entry
     */
    calculateFundDistribution(entryAmount: number): {
        researchContribution: number;
        operationalFee: number;
    } {
        const researchContribution = Math.floor((entryAmount * 80) / 100);
        const operationalFee = entryAmount - researchContribution;
        
        return {
            researchContribution,
            operationalFee,
        };
    }

    /**
     * Check if lottery is active
     */
    async isLotteryActive(): Promise<boolean> {
        const lottery = await this.getLotteryState();
        return lottery ? lottery.isActive : false;
    }

    /**
     * Get current jackpot amount
     */
    async getCurrentJackpot(): Promise<number> {
        const lottery = await this.getLotteryState();
        return lottery ? lottery.currentJackpot.toNumber() : 0;
    }

    /**
     * Get total entries
     */
    async getTotalEntries(): Promise<number> {
        const lottery = await this.getLotteryState();
        return lottery ? lottery.totalEntries.toNumber() : 0;
    }
}
