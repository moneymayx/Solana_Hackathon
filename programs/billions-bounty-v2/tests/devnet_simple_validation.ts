/**
 * Simple Devnet Validation for billions-bounty-v2
 * Validates deployed contract without relying on Anchor Program class
 */

import { Connection, PublicKey } from "@solana/web3.js";
import { getAssociatedTokenAddress } from "@solana/spl-token";

// Devnet deployment addresses
const PROGRAM_ID = new PublicKey("GHvFV9S8XqpR6Pxd3UtZ9vi7AuCd3qLg5kgfAPwcJzJm");
const GLOBAL_PDA = new PublicKey("F4YATUC3tEA3Gb3Tt3v7sZBT9iKRhHXJsZ6s7nBWKDgh");
const BOUNTY_1_PDA = new PublicKey("AJC6D2mvMcktdzpJJQmbYXkTZn9xGpd2C3qm4VAZK83Z");
const IDL_ACCOUNT = new PublicKey("HicBwRnacuFcfYXWGBFSCWofc8ZmJU4v4rKKxtxvXBQr");
const USDC_MINT = new PublicKey("Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr");

const BOUNTY_POOL_WALLET = new PublicKey("CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const OPERATIONAL_WALLET = new PublicKey("46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D");
const BUYBACK_WALLET = new PublicKey("7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya");
const STAKING_WALLET = new PublicKey("Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX");

async function main() {
  console.log("🔍 V2 Contract Devnet Validation (Simple)\n");
  
  const connection = new Connection(
    process.env.ANCHOR_PROVIDER_URL || "https://api.devnet.solana.com",
    "confirmed"
  );

  let passedTests = 0;
  let totalTests = 0;

  // Test 1: Program exists
  totalTests++;
  console.log("Test 1: Program Account");
  try {
    const programAccount = await connection.getAccountInfo(PROGRAM_ID);
    if (programAccount && programAccount.executable) {
      console.log("✅ Program deployed and executable");
      console.log("   Owner:", programAccount.owner.toBase58());
      console.log("   Size:", programAccount.data.length, "bytes");
      passedTests++;
    } else {
      console.log("❌ Program not found or not executable");
    }
  } catch (err) {
    console.log("❌ Error:", err.message);
  }
  console.log();

  // Test 2: IDL Account exists
  totalTests++;
  console.log("Test 2: IDL Account");
  try {
    const idlAccount = await connection.getAccountInfo(IDL_ACCOUNT);
    if (idlAccount) {
      console.log("✅ IDL published");
      console.log("   Size:", idlAccount.data.length, "bytes");
      passedTests++;
    } else {
      console.log("❌ IDL account not found");
    }
  } catch (err) {
    console.log("❌ Error:", err.message);
  }
  console.log();

  // Test 3: Global PDA exists
  totalTests++;
  console.log("Test 3: Global PDA");
  try {
    const globalAccount = await connection.getAccountInfo(GLOBAL_PDA);
    if (globalAccount && globalAccount.owner.equals(PROGRAM_ID)) {
      console.log("✅ Global PDA initialized");
      console.log("   Owner:", globalAccount.owner.toBase58());
      console.log("   Data length:", globalAccount.data.length, "bytes");
      passedTests++;
    } else if (globalAccount) {
      console.log("❌ Global PDA exists but wrong owner");
      console.log("   Expected:", PROGRAM_ID.toBase58());
      console.log("   Got:", globalAccount.owner.toBase58());
    } else {
      console.log("❌ Global PDA not found");
    }
  } catch (err) {
    console.log("❌ Error:", err.message);
  }
  console.log();

  // Test 4: Bounty PDA exists
  totalTests++;
  console.log("Test 4: Bounty[1] PDA");
  try {
    const bountyAccount = await connection.getAccountInfo(BOUNTY_1_PDA);
    if (bountyAccount && bountyAccount.owner.equals(PROGRAM_ID)) {
      console.log("✅ Bounty PDA initialized");
      console.log("   Owner:", bountyAccount.owner.toBase58());
      console.log("   Data length:", bountyAccount.data.length, "bytes");
      passedTests++;
    } else if (bountyAccount) {
      console.log("❌ Bounty PDA exists but wrong owner");
    } else {
      console.log("❌ Bounty PDA not found");
    }
  } catch (err) {
    console.log("❌ Error:", err.message);
  }
  console.log();

  // Test 5: Wallet Token Accounts
  totalTests++;
  console.log("Test 5: Wallet Token Accounts");
  const wallets = [
    { name: "Bounty Pool", key: BOUNTY_POOL_WALLET },
    { name: "Operational", key: OPERATIONAL_WALLET },
    { name: "Buyback", key: BUYBACK_WALLET },
    { name: "Staking", key: STAKING_WALLET },
  ];

  let allATAsExist = true;
  for (const w of wallets) {
    try {
      const ata = await getAssociatedTokenAddress(USDC_MINT, w.key, true);
      const accountInfo = await connection.getAccountInfo(ata);
      if (accountInfo) {
        console.log(`   ✓ ${w.name}: ${ata.toBase58()}`);
      } else {
        console.log(`   ✗ ${w.name}: ATA not found`);
        allATAsExist = false;
      }
    } catch (err) {
      console.log(`   ✗ ${w.name}: Error -`, err.message);
      allATAsExist = false;
    }
  }
  if (allATAsExist) {
    passedTests++;
    console.log("✅ All wallet ATAs exist");
  } else {
    console.log("⚠️  Some wallet ATAs missing");
  }
  console.log();

  // Summary
  console.log("═".repeat(50));
  console.log(`Results: ${passedTests}/${totalTests} tests passed`);
  console.log("═".repeat(50));
  console.log();

  if (passedTests === totalTests) {
    console.log("🎉 All validation tests passed!");
    console.log();
    console.log("Contract Status:");
    console.log("- ✅ Deployed on devnet");
    console.log("- ✅ IDL published and verifiable");
    console.log("- ✅ Global and Bounty PDAs initialized");
    console.log("- ✅ Wallet infrastructure ready");
    console.log();
    console.log("Ready for:");
    console.log("- Backend integration testing");
    console.log("- Staging environment deployment");
    console.log("- End-to-end transaction testing");
  } else {
    console.log("⚠️  Some tests failed. Review above for details.");
  }
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
  });

