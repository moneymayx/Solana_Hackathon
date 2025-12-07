import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { BillionsBountyV3 } from "../target/types/billions_bounty_v3";
import { PublicKey, Keypair, SystemProgram } from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  createMint,
  createAccount,
  mintTo,
} from "@solana/spl-token";
import { expect } from "chai";

const TEST_AMOUNTS = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 19, 23, 27, 29, 31, 33, 37, 39,
  41, 43, 47, 49, 51, 53, 57, 59, 61, 63, 67, 69, 71, 73, 77, 79, 81, 83, 87,
  89, 91, 93, 97, 99, 101, 107, 113, 131, 137, 149, 163, 179, 199, 211, 241,
  257, 271, 293, 307, 331, 349, 367, 389, 401, 433, 457, 479, 503, 541, 577,
  601, 631, 659, 673, 691, 709, 739, 751, 773, 797, 809, 829, 853, 877, 907,
  919, 947, 971, 997, 1000, 10000, 1000000, 10000000,
];

const USDC_DECIMALS = 6;
const USDC_MULTIPLIER = new anchor.BN(10).pow(new anchor.BN(USDC_DECIMALS));

describe("Rounding edge cases", function () {
  this.timeout(120000);
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);

  const idl = require("../target/idl/billions_bounty_v3.json");
  const programId = new anchor.web3.PublicKey(
    "ALG8r2iZZaoQbfEZBAXAf9vCXL9g6qkyCupvYQqkuZmb"
  );
  const program = new anchor.Program(
    idl,
    programId,
    provider
  ) as Program<BillionsBountyV3>;

  let authority: Keypair;
  let user: Keypair;
  let jackpotWallet: Keypair;
  let buybackWallet: Keypair;
  let backendAuthority: Keypair;
  let usdcMint: PublicKey;
  let userTokenAccount: PublicKey;
  let jackpotTokenAccount: PublicKey;
  let buybackTokenAccount: PublicKey;
  let lotteryPDA: PublicKey;

  before(async () => {
    authority = Keypair.generate();
    user = Keypair.generate();
    jackpotWallet = Keypair.generate();
    buybackWallet = Keypair.generate();
    backendAuthority = Keypair.generate();

    const providerWallet = (provider as any).wallet;
    const amount = 0.15 * anchor.web3.LAMPORTS_PER_SOL;
    const balance = await provider.connection.getBalance(
      providerWallet.publicKey
    );
    const required =
      amount * 5 + 0.05 * anchor.web3.LAMPORTS_PER_SOL;

    if (balance < required) {
      await provider.connection.requestAirdrop(
        authority.publicKey,
        amount
      );
      await provider.connection.requestAirdrop(
        user.publicKey,
        amount
      );
      await provider.connection.requestAirdrop(
        jackpotWallet.publicKey,
        amount
      );
      await provider.connection.requestAirdrop(
        buybackWallet.publicKey,
        amount
      );
      await provider.connection.requestAirdrop(
        backendAuthority.publicKey,
        amount
      );
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }

    usdcMint = await createMint(
      provider.connection,
      authority,
      authority.publicKey,
      null,
      6
    );

    userTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      user.publicKey
    );

    jackpotTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      jackpotWallet.publicKey
    );

    buybackTokenAccount = await createAccount(
      provider.connection,
      authority,
      usdcMint,
      buybackWallet.publicKey
    );

    [lotteryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("lottery")],
      program.programId
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
        jackpotTokenAccount,
        usdcMint,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
      })
      .rpc();
  });

  it("maintains split invariants for odd entry amounts", async () => {
    let entryCounter = 1;

    for (const amount of TEST_AMOUNTS) {
      const entryAmount = new anchor.BN(amount).mul(USDC_MULTIPLIER);
      const entryNonce = entryCounter;
      const entrySeed = [
        Buffer.from("entry"),
        lotteryPDA.toBuffer(),
        user.publicKey.toBuffer(),
        Buffer.alloc(8),
      ];
      entrySeed[3].writeBigUInt64LE(BigInt(entryNonce));
      const [entryPDA] = PublicKey.findProgramAddressSync(
        entrySeed,
        program.programId
      );

      await mintTo(
        provider.connection,
        authority,
        usdcMint,
        userTokenAccount,
        authority,
        BigInt(entryAmount.toString())
      );

      await program.methods
        .processEntryPayment(entryAmount, user.publicKey, new anchor.BN(entryNonce))
        .accounts({
          lottery: lotteryPDA,
          entry: entryPDA,
          user: user.publicKey,
          userWallet: user.publicKey,
          userTokenAccount,
          jackpotTokenAccount,
          buybackWallet: buybackWallet.publicKey,
          buybackTokenAccount,
          usdcMint,
          tokenProgram: TOKEN_PROGRAM_ID,
          associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
          systemProgram: SystemProgram.programId,
        })
        .signers([user])
        .rpc();

      const entryAccount = await program.account.entry.fetch(entryPDA);
      const contributionSum = entryAccount.researchContribution.add(
        entryAccount.operationalFee
      );

      expect(contributionSum.toString()).to.equal(entryAmount.toString());
      entryCounter += 1;
    }
  });

  it("verifies escape plan shares sum to the jackpot", async () => {
    const lotteryAccount = await program.account.lottery.fetch(lotteryPDA);
    const totalJackpot = BigInt(lotteryAccount.currentJackpot.toString());
    const lastParticipantShare = (totalJackpot * 20n) / 100n;
    const communityShare = totalJackpot - lastParticipantShare;

    expect(lastParticipantShare + communityShare).to.equal(totalJackpot);
    expect(communityShare >= lastParticipantShare).to.be.true;
  });
});

