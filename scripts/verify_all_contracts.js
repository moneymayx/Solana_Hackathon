/**
 * Verify All Contracts Initialization Status
 * Checks V1, V2, and V3 lottery/global accounts on devnet
 */

const { Connection, PublicKey } = require("@solana/web3.js");

const DEVNET_RPC = "https://api.devnet.solana.com";

// Contract Program IDs
const V1_PROGRAM_ID = new PublicKey("4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK");
const V2_PROGRAM_ID = new PublicKey("HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm");
const V3_PROGRAM_ID = new PublicKey("52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov");

// Derive PDAs
const [v1LotteryPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from("lottery")],
  V1_PROGRAM_ID
);

const [v2GlobalPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from("global")],
  V2_PROGRAM_ID
);

const [v3LotteryPDA] = PublicKey.findProgramAddressSync(
  [Buffer.from("lottery")],
  V3_PROGRAM_ID
);

async function main() {
  console.log("🔍 Verifying All Contracts on Devnet\n");
  console.log("=".repeat(60));

  const connection = new Connection(DEVNET_RPC, "confirmed");

  // Check V1
  console.log("\n📋 V1 Contract:");
  console.log("   Program ID:", V1_PROGRAM_ID.toBase58());
  console.log("   Lottery PDA:", v1LotteryPDA.toBase58());
  try {
    const program = await connection.getAccountInfo(V1_PROGRAM_ID);
    const lottery = await connection.getAccountInfo(v1LotteryPDA);
    console.log("   Program Deployed:", program ? "✅ Yes" : "❌ No");
    console.log("   Lottery Initialized:", lottery ? "✅ Yes" : "❌ No");
    if (lottery) {
      console.log("   Account Size:", lottery.data.length, "bytes");
    }
  } catch (error) {
    console.log("   Error:", error.message);
  }

  // Check V2
  console.log("\n📋 V2 Contract:");
  console.log("   Program ID:", V2_PROGRAM_ID.toBase58());
  console.log("   Global PDA:", v2GlobalPDA.toBase58());
  try {
    const program = await connection.getAccountInfo(V2_PROGRAM_ID);
    const global = await connection.getAccountInfo(v2GlobalPDA);
    console.log("   Program Deployed:", program ? "✅ Yes" : "❌ No");
    console.log("   Global Initialized:", global ? "✅ Yes" : "❌ No");
    if (global) {
      console.log("   Account Size:", global.data.length, "bytes");
    }
  } catch (error) {
    console.log("   Error:", error.message);
  }

  // Check V3
  console.log("\n📋 V3 Contract:");
  console.log("   Program ID:", V3_PROGRAM_ID.toBase58());
  console.log("   Lottery PDA:", v3LotteryPDA.toBase58());
  try {
    const program = await connection.getAccountInfo(V3_PROGRAM_ID);
    const lottery = await connection.getAccountInfo(v3LotteryPDA);
    console.log("   Program Deployed:", program ? "✅ Yes" : "❌ No");
    if (program) {
      console.log("   Program Size:", program.data.length, "bytes");
      console.log("   Balance:", program.lamports / 1e9, "SOL");
    }
    console.log("   Lottery Initialized:", lottery ? "✅ Yes" : "❌ No");
    if (lottery) {
      console.log("   Account Size:", lottery.data.length, "bytes");
    } else {
      console.log("   ⚠️  V3 lottery needs initialization");
    }
  } catch (error) {
    console.log("   Error:", error.message);
  }

  console.log("\n" + "=".repeat(60));
  console.log("\n✅ Verification complete!");
}

main().catch((error) => {
  console.error("\n❌ Error:", error);
  process.exit(1);
});

