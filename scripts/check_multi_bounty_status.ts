#!/usr/bin/env ts-node
/**
 * Multi-bounty status checker.
 * Mirrors the raw-initialization workflow documented in `docs/V3_INITIALIZATION_STATUS.md`.
 * Verifies each bounty PDA exists and reports the associated jackpot USDC balance.
 */

import { Connection, PublicKey } from "@solana/web3.js";
import {
  getAccount,
  getAssociatedTokenAddress,
} from "@solana/spl-token";

const RPC_ENDPOINT =
  process.env.SOLANA_RPC_ENDPOINT || "https://api.devnet.solana.com";

const PROGRAM_ID = new PublicKey(
  process.env.LOTTERY_PROGRAM_ID_V3 ||
    "7ZK2wtatnS8aqxCPt43pfLeUZGRqx5ucXXeZUngEboNh"
);

const USDC_MINT = new PublicKey(
  process.env.V3_USDC_MINT_DEVNET ||
    "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"
);

const JACKPOT_WALLET = new PublicKey(
  process.env.V3_JACKPOT_WALLET || "CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF"
);

const BOUNTY_CONFIGS: Record<number, { name: string; difficulty: string }> = {
  1: { name: "Claude Champ", difficulty: "expert" },
  2: { name: "GPT Gigachad", difficulty: "hard" },
  3: { name: "Gemini Great", difficulty: "medium" },
  4: { name: "Llama Legend", difficulty: "easy" },
};

async function main() {
  const connection = new Connection(RPC_ENDPOINT, "confirmed");
  console.log("🔍 Multi-Bounty Status Check\n");
  console.log("Program ID:", PROGRAM_ID.toBase58());
  console.log("USDC Mint:", USDC_MINT.toBase58());
  console.log("Jackpot Wallet:", JACKPOT_WALLET.toBase58());
  console.log("");

  try {
    const jackpotATA = await getAssociatedTokenAddress(
      USDC_MINT,
      JACKPOT_WALLET
    );
    const ataInfo = await getAccount(connection, jackpotATA);
    const balance = Number(ataInfo.amount) / 1_000_000;
    console.log("Jackpot Token Account:", jackpotATA.toBase58());
    console.log(`Jackpot Balance: ${balance} USDC\n`);
  } catch (err: any) {
    console.log(
      "⚠️  Unable to read jackpot token account:",
      err?.message || err
    );
    console.log("");
  }

  for (const [idStr, config] of Object.entries(BOUNTY_CONFIGS)) {
    const bountyId = Number(idStr);
    const [lotteryPDA] = PublicKey.findProgramAddressSync(
      [Buffer.from("lottery"), Buffer.from([bountyId])],
      PROGRAM_ID
    );

    console.log(
      `Bounty ${bountyId}: ${config.name} (${config.difficulty})`
    );
    console.log(`  PDA: ${lotteryPDA.toBase58()}`);

    const accountInfo = await connection.getAccountInfo(lotteryPDA);
    if (!accountInfo) {
      console.log("  ❌ Lottery account not found on chain\n");
      continue;
    }

    console.log("  ✅ Lottery account exists");
    console.log(`  Lamports: ${accountInfo.lamports}`);
    console.log(`  Data length: ${accountInfo.data.length} bytes\n`);
  }
}

main().catch((err) => {
  console.error("❌ Status check failed:", err);
  process.exit(1);
});


