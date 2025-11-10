import * as anchor from "@coral-xyz/anchor";
import { Connection, Keypair, PublicKey, SystemProgram } from "@solana/web3.js";
import { 
  TOKEN_PROGRAM_ID,
  ASSOCIATED_TOKEN_PROGRAM_ID,
  getAssociatedTokenAddress,
  createAssociatedTokenAccountInstruction 
} from "@solana/spl-token";
import * as fs from "fs";

const PROGRAM_ID = new PublicKey("HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm");
const USDC_MINT = new PublicKey("JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"); // Your test token

// Destination wallets
const BOUNTY_POOL = new PublicKey("CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF");
const OPERATIONAL = new PublicKey("46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D");
const BUYBACK = new PublicKey("7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya");
const STAKING = new PublicKey("Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX");

async function testV2Payment() {
  console.log("╔══════════════════════════════════════════════════════════════════╗");
  console.log("║              🧪 V2 SMART CONTRACT PAYMENT TEST 🧪                ║");
  console.log("╚══════════════════════════════════════════════════════════════════╝");
  console.log();
  
  const connection = new Connection("https://api.devnet.solana.com", "confirmed");
  
  // Load your wallet
  const keypairPath = process.env.HOME + "/.config/solana/id.json";
  console.log("Loading wallet from:", keypairPath);
  
  let keypairData;
  try {
    keypairData = JSON.parse(fs.readFileSync(keypairPath, "utf-8"));
  } catch (error) {
    console.log("❌ Error: Could not load wallet keypair");
    console.log("   Make sure ~/.config/solana/id.json exists");
    console.log("   Or set ANCHOR_WALLET environment variable");
    return;
  }
  
  const userKeypair = Keypair.fromSecretKey(new Uint8Array(keypairData));
  
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("WALLET & CONTRACT INFO");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("User Wallet:", userKeypair.publicKey.toString());
  console.log("Program ID:", PROGRAM_ID.toString());
  console.log("USDC Mint:", USDC_MINT.toString());
  console.log();
  
  // Derive PDAs
  const [globalPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("global")],
    PROGRAM_ID
  );
  
  const bountyId = 1; // Use the initialized bounty ID from init script
  const [bountyPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("bounty"), new anchor.BN(bountyId).toArrayLike(Buffer, "le", 8)],
    PROGRAM_ID
  );
  
  const [buybackTrackerPda] = PublicKey.findProgramAddressSync(
    [Buffer.from("buyback_tracker")],
    PROGRAM_ID
  );
  
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("PDAs");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("Global PDA:", globalPda.toString());
  console.log("Bounty PDA:", bountyPda.toString());
  console.log("Buyback Tracker PDA:", buybackTrackerPda.toString());
  console.log();
  
  // Get/create token accounts
  const userTokenAccount = await getAssociatedTokenAddress(USDC_MINT, userKeypair.publicKey);
  const bountyPoolTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BOUNTY_POOL);
  const operationalTokenAccount = await getAssociatedTokenAddress(USDC_MINT, OPERATIONAL);
  const buybackTokenAccount = await getAssociatedTokenAddress(USDC_MINT, BUYBACK);
  const stakingTokenAccount = await getAssociatedTokenAddress(USDC_MINT, STAKING);
  
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("TOKEN ACCOUNTS");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("User:", userTokenAccount.toString());
  console.log("Bounty Pool:", bountyPoolTokenAccount.toString());
  console.log("Operational:", operationalTokenAccount.toString());
  console.log("Buyback:", buybackTokenAccount.toString());
  console.log("Staking:", stakingTokenAccount.toString());
  console.log();
  
  // Check user USDC balance
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("CHECKING BALANCES");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  let userBalance;
  try {
    userBalance = await connection.getTokenAccountBalance(userTokenAccount);
    console.log("User USDC Balance:", userBalance.value.uiAmount);
  } catch (error) {
    console.log("❌ User token account not found");
    console.log("   Create with: spl-token create-account", USDC_MINT.toString(), "--url devnet");
    return;
  }
  
  if (!userBalance.value.uiAmount || userBalance.value.uiAmount < 10) {
    console.log("❌ Insufficient USDC balance. Need at least 10 USDC.");
    console.log("   Current balance:", userBalance.value.uiAmount || 0);
    console.log();
    console.log("To get devnet USDC:");
    console.log("   1. Use a devnet faucet (if available)");
    console.log("   2. Or mint if you have authority:");
    console.log("      spl-token mint", USDC_MINT.toString(), "100", userTokenAccount.toString(), "--url devnet");
    return;
  }
  
  console.log("✅ Sufficient balance for test");
  console.log();
  
  // Load IDL
  const idlPath = __dirname + "/../target/idl/billions_bounty_v2.json";
  console.log("Loading IDL from:", idlPath);
  
  let idl;
  try {
    idl = JSON.parse(fs.readFileSync(idlPath, "utf-8"));
    console.log("✅ IDL loaded");
  } catch (error) {
    console.log("❌ Error: Could not load IDL");
    console.log("   Make sure", idlPath, "exists");
    return;
  }
  console.log();
  
  // Create program instance
  const provider = new anchor.AnchorProvider(
    connection,
    new anchor.Wallet(userKeypair),
    { commitment: "confirmed" }
  );
  const program = new anchor.Program(idl as anchor.Idl, provider);
  
  // Entry amount: 15 USDC (with 6 decimals) - accounts for price escalation
  const entryAmount = new anchor.BN(15_000_000);
  
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("TRANSACTION DETAILS");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("Amount: 15 USDC");
  console.log("Bounty ID:", bountyId);
  console.log();
  console.log("Expected Distribution:");
  console.log("  Bounty Pool (60%): 9 USDC");
  console.log("  Operational (20%): 3 USDC");
  console.log("  Buyback (10%): 1.5 USDC");
  console.log("  Staking (10%): 1.5 USDC");
  console.log();
  
  console.log("🚀 Sending transaction...");
  console.log();
  
  try {
    const tx = await program.methods
      .processEntryPaymentV2(new anchor.BN(bountyId), entryAmount)
      .accounts({
        global: globalPda,
        bounty: bountyPda,
        buybackTracker: buybackTrackerPda,
        user: userKeypair.publicKey,
        userTokenAccount: userTokenAccount,
        bountyPoolWallet: BOUNTY_POOL,
        bountyPoolTokenAccount: bountyPoolTokenAccount,
        operationalWallet: OPERATIONAL,
        operationalTokenAccount: operationalTokenAccount,
        buybackWallet: BUYBACK,
        buybackTokenAccount: buybackTokenAccount,
        stakingWallet: STAKING,
        stakingTokenAccount: stakingTokenAccount,
        usdcMint: USDC_MINT,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
        systemProgram: SystemProgram.programId,
        rent: anchor.web3.SYSVAR_RENT_PUBKEY,
      })
      .rpc();
    
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log("✅ TRANSACTION SUCCESSFUL!");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log();
    console.log("Signature:", tx);
    console.log();
    console.log("View on Solana Explorer:");
    console.log(`https://explorer.solana.com/tx/${tx}?cluster=devnet`);
    console.log();
    
    // Wait a bit for transaction to finalize
    console.log("Waiting for transaction to finalize...");
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Check new balances
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log("📊 VERIFYING 4-WAY SPLIT");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log();
    
    let allSuccess = true;
    
    try {
      const bountyPoolBalance = await connection.getTokenAccountBalance(bountyPoolTokenAccount);
      // After 2 payments: 6 + 9 = 15 USDC
      const expected = 15;
      const actual = bountyPoolBalance.value.uiAmount || 0;
      const match = Math.abs(actual - expected) < 0.1; // Allow small rounding
      console.log(`Bounty Pool: ${actual} USDC ${match ? '✅' : '❌'} (expected ~${expected})`);
      if (!match) allSuccess = false;
    } catch (error) {
      console.log("Bounty Pool: Error reading balance ❌");
      allSuccess = false;
    }
    
    try {
      const operationalBalance = await connection.getTokenAccountBalance(operationalTokenAccount);
      // After 2 payments: 2 + 3 = 5 USDC
      const expected = 5;
      const actual = operationalBalance.value.uiAmount || 0;
      const match = Math.abs(actual - expected) < 0.1;
      console.log(`Operational: ${actual} USDC ${match ? '✅' : '❌'} (expected ~${expected})`);
      if (!match) allSuccess = false;
    } catch (error) {
      console.log("Operational: Error reading balance ❌");
      allSuccess = false;
    }
    
    try {
      const buybackBalance = await connection.getTokenAccountBalance(buybackTokenAccount);
      // After 2 payments: 1 + 1.5 = 2.5 USDC
      const expected = 2.5;
      const actual = buybackBalance.value.uiAmount || 0;
      const match = Math.abs(actual - expected) < 0.1;
      console.log(`Buyback: ${actual} USDC ${match ? '✅' : '❌'} (expected ~${expected})`);
      if (!match) allSuccess = false;
    } catch (error) {
      console.log("Buyback: Error reading balance ❌");
      allSuccess = false;
    }
    
    try {
      const stakingBalance = await connection.getTokenAccountBalance(stakingTokenAccount);
      // After 2 payments: 1 + 1.5 = 2.5 USDC
      const expected = 2.5;
      const actual = stakingBalance.value.uiAmount || 0;
      const match = Math.abs(actual - expected) < 0.1;
      console.log(`Staking: ${actual} USDC ${match ? '✅' : '❌'} (expected ~${expected})`);
      if (!match) allSuccess = false;
    } catch (error) {
      console.log("Staking: Error reading balance ❌");
      allSuccess = false;
    }
    
    console.log();
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    if (allSuccess) {
      console.log("🎉 TEST PASSED! 4-way split verified!");
    } else {
      console.log("⚠️  TEST INCOMPLETE - Some balances don't match");
      console.log("    Check transaction on explorer for details");
    }
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    
  } catch (error: any) {
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log("❌ TRANSACTION FAILED");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log();
    console.log("Error:", error.message || error);
    console.log();
    
    if (error.logs) {
      console.log("Transaction Logs:");
      error.logs.forEach((log: string) => console.log("  ", log));
      console.log();
    }
    
    console.log("Common Issues:");
    console.log("  • Insufficient USDC balance");
    console.log("  • Token accounts not created");
    console.log("  • PDAs not initialized");
    console.log("  • Program ID mismatch");
    console.log();
    console.log("Check the error message above for details.");
  }
}

testV2Payment().catch(console.error);

