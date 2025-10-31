import {
  Connection,
  Keypair,
  PublicKey,
  SystemProgram,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
} from "@solana/web3.js";
import {
  getAssociatedTokenAddress,
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import * as crypto from "crypto";
import * as fs from "fs";

const PROGRAM_ID = new PublicKey("HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm");
const USDC_MINT = new PublicKey("JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh");

const BOUNTY_POOL = new PublicKey("CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const OPERATIONAL = new PublicKey("46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D");
const BUYBACK = new PublicKey("7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya");
const STAKING = new PublicKey("Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX");

const SYSVAR_RENT = new PublicKey("SysvarRent111111111111111111111111111111111");

const BOUNTY_ID = 1;
const ENTRY_AMOUNT = 15_000_000; // 15 USDC (6 decimals) - accounts for price escalation

function u64LE(value: number): Buffer {
  const buf = Buffer.alloc(8);
  buf.writeBigUInt64LE(BigInt(value), 0);
  return buf;
}

async function main() {
  const connection = new Connection("https://api.devnet.solana.com", "confirmed");

  const walletPath = process.env.ANCHOR_WALLET || `${process.env.HOME}/.config/solana/id.json`;
  const payer = Keypair.fromSecretKey(new Uint8Array(JSON.parse(fs.readFileSync(walletPath, "utf-8"))));

  console.log("User Wallet:", payer.publicKey.toBase58());

  const [globalPda] = PublicKey.findProgramAddressSync([Buffer.from("global")], PROGRAM_ID);
  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), u64LE(BOUNTY_ID)],
    PROGRAM_ID
  );
  const [buybackTrackerPda] = PublicKey.findProgramAddressSync([Buffer.from("buyback_tracker")], PROGRAM_ID);

  const userTokenAccount = await getAssociatedTokenAddress(USDC_MINT, payer.publicKey);
  const bountyPoolTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BOUNTY_POOL);
  const operationalTokenAccount = await getAssociatedTokenAddress(USDC_MINT, OPERATIONAL);
  const buybackTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BUYBACK);
  const stakingTokenAccount = await getAssociatedTokenAddress(USDC_MINT, STAKING);

  console.log("Global PDA:", globalPda.toBase58());
  console.log("Bounty PDA:", bountyPda.toBase58());
  console.log("Buyback Tracker PDA:", buybackTrackerPda.toBase58());

  const discriminator = crypto
    .createHash("sha256")
    .update("global:process_entry_payment_v2")
    .digest()
    .slice(0, 8);

  const data = Buffer.concat([discriminator, u64LE(BOUNTY_ID), u64LE(ENTRY_AMOUNT)]);

  const ix = new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: globalPda, isSigner: false, isWritable: true },
      { pubkey: bountyPda, isSigner: false, isWritable: true },
      { pubkey: buybackTrackerPda, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: userTokenAccount, isSigner: false, isWritable: true },
      { pubkey: bountyPoolTokenAccount, isSigner: false, isWritable: true },
      { pubkey: operationalTokenAccount, isSigner: false, isWritable: true },
      { pubkey: buybackTokenAccount, isSigner: false, isWritable: true },
      { pubkey: stakingTokenAccount, isSigner: false, isWritable: true },
      { pubkey: BOUNTY_POOL, isSigner: false, isWritable: false },
      { pubkey: OPERATIONAL, isSigner: false, isWritable: false },
      { pubkey: BUYBACK, isSigner: false, isWritable: false },
      { pubkey: STAKING, isSigner: false, isWritable: false },
      { pubkey: USDC_MINT, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: SYSVAR_RENT, isSigner: false, isWritable: false },
    ],
    data,
  });

  const tx = new Transaction().add(ix);
  tx.feePayer = payer.publicKey;
  tx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;

  const signature = await sendAndConfirmTransaction(connection, tx, [payer], {
    commitment: "confirmed",
  });

  console.log("✅ Transaction Signature:", signature);
  console.log(`https://explorer.solana.com/tx/${signature}?cluster=devnet`);

  const fetchBalance = async (label: string, account: PublicKey) => {
    const balance = await connection.getTokenAccountBalance(account);
    console.log(`${label}:`, balance.value.uiAmountString ?? "0");
  };

  console.log("\nBalances after transaction:");
  await fetchBalance("Bounty Pool", bountyPoolTokenAccount);
  await fetchBalance("Operational", operationalTokenAccount);
  await fetchBalance("Buyback", buybackTokenAccount);
  await fetchBalance("Staking", stakingTokenAccount);
}

main().catch((err) => {
  console.error("❌ Error running raw payment test:", err);
  process.exit(1);
});

