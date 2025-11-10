#!/usr/bin/env ts-node
/**
 * Initialize V3 Lottery on Devnet using Anchor Program
 * 
 * This script uses Anchor Program class for proper initialization.
 */

import * as anchor from '@coral-xyz/anchor';
import { Connection, PublicKey, Keypair } from '@solana/web3.js';
import { getAssociatedTokenAddress, getAccount } from '@solana/spl-token';
import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import * as path from 'path';
import { fileURLToPath } from 'url';

// V3 Configuration
const PROGRAM_ID = new PublicKey('52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov');
const DEVNET_RPC = 'https://api.devnet.solana.com';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load IDL
const IDL_PATH = path.join(__dirname, '..', 'programs', 'billions-bounty-v3', 'target', 'idl', 'billions_bounty_v3.json');

async function main() {
  console.log('🚀 Initializing V3 Lottery on Devnet (using Anchor)\n');
  
  // Load IDL
  if (!existsSync(IDL_PATH)) {
    console.error('❌ IDL file not found:', IDL_PATH);
    console.error('   Please run: cd programs/billions-bounty-v3 && anchor build');
    process.exit(1);
  }
  
  const idl = JSON.parse(readFileSync(IDL_PATH, 'utf-8'));
  
  const connection = new Connection(DEVNET_RPC, 'confirmed');
  
  // Load authority keypair
  const defaultKeypairPath = path.join(homedir(), '.config', 'solana', 'id.json');
  
  if (!existsSync(defaultKeypairPath)) {
    console.error('❌ No authority keypair found!');
    process.exit(1);
  }
  
  const keypairData = JSON.parse(readFileSync(defaultKeypairPath, 'utf-8'));
  const authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
  console.log('✅ Authority:', authority.publicKey.toBase58());
  console.log('   Balance:', (await connection.getBalance(authority.publicKey)) / 1e9, 'SOL\n');
  
  // Setup Anchor provider and program
  const wallet = new anchor.Wallet(authority);
  const provider = new anchor.AnchorProvider(
    connection,
    wallet,
    { commitment: 'confirmed' }
  );
  anchor.setProvider(provider);
  
  const programId = new anchor.web3.PublicKey(PROGRAM_ID.toBase58());
  const program = new anchor.Program(idl as anchor.Idl, programId, provider);
  
  // Configuration
  const JACKPOT_WALLET = new PublicKey('CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF');
  const BACKEND_AUTHORITY = new PublicKey(process.env.V3_BACKEND_AUTHORITY || 'CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF');
  const USDC_MINT = new PublicKey(process.env.V3_USDC_MINT_DEVNET || 'JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh');
  const RESEARCH_FUND_FLOOR = new anchor.BN(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000);
  const RESEARCH_FEE = new anchor.BN(process.env.V3_RESEARCH_FEE || 10_000_000);
  
  // Derive lottery PDA
  const [lotteryPDA, lotteryBump] = PublicKey.findProgramAddressSync(
    [Buffer.from('lottery')],
    PROGRAM_ID
  );
  
  console.log('📋 Configuration:');
  console.log('   Program ID:', PROGRAM_ID.toBase58());
  console.log('   Lottery PDA:', lotteryPDA.toBase58());
  console.log('   Jackpot Wallet:', JACKPOT_WALLET.toBase58());
  console.log('   Backend Authority:', BACKEND_AUTHORITY.toBase58());
  console.log('   USDC Mint:', USDC_MINT.toBase58());
  console.log('   Research Fund Floor:', RESEARCH_FUND_FLOOR.toNumber() / 1e6, 'USDC');
  console.log('   Research Fee:', RESEARCH_FEE.toNumber() / 1e6, 'USDC\n');
  
  // Check if lottery already exists
  console.log('🔍 Checking if lottery is already initialized...');
  const existingLottery = await connection.getAccountInfo(lotteryPDA);
  
  if (existingLottery) {
    console.log('✅ Lottery already initialized!');
    console.log('   Account:', lotteryPDA.toBase58());
    return;
  }
  
  console.log('❌ Lottery not initialized - proceeding...\n');
  
  // Get jackpot token account
  const jackpotTokenAccount = await getAssociatedTokenAddress(USDC_MINT, JACKPOT_WALLET);
  console.log('   Jackpot Token Account:', jackpotTokenAccount.toBase58());
  
  // Check token account balance
  try {
    const tokenAccount = await getAccount(connection, jackpotTokenAccount);
    const balance = Number(tokenAccount.amount) / 1e6;
    console.log('   Token Account Balance:', balance, 'USDC');
    
    if (balance < RESEARCH_FUND_FLOOR.toNumber() / 1e6) {
      console.error('❌ Insufficient balance!');
      console.error(`   Have: ${balance} USDC`);
      console.error(`   Need: ${RESEARCH_FUND_FLOOR.toNumber() / 1e6} USDC`);
      process.exit(1);
    }
    console.log('   ✅ Sufficient balance\n');
  } catch (e: any) {
    if (e.message?.includes('TokenAccountNotFoundError')) {
      console.error('❌ Token account does not exist!');
      console.error('   Create it first with:');
      console.error(`   spl-token create-account ${USDC_MINT.toBase58()} --owner ${JACKPOT_WALLET.toBase58()} --url devnet`);
      process.exit(1);
    }
    throw e;
  }
  
  // Initialize using Anchor Program
  console.log('📝 Initializing lottery...');
  try {
    const tx = await program.methods
      .initializeLottery(
        RESEARCH_FUND_FLOOR,
        RESEARCH_FEE,
        JACKPOT_WALLET,
        BACKEND_AUTHORITY
      )
      .accounts({
        lottery: lotteryPDA,
        authority: authority.publicKey,
        jackpotWallet: JACKPOT_WALLET,
        jackpotTokenAccount: jackpotTokenAccount,
        usdcMint: USDC_MINT,
        tokenProgram: anchor.utils.token.TOKEN_PROGRAM_ID,
        associatedTokenProgram: anchor.utils.token.ASSOCIATED_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .rpc();
    
    console.log('\n✅ Lottery initialized successfully!');
    console.log('   Transaction:', tx);
    console.log('   Explorer:', `https://explorer.solana.com/tx/${tx}?cluster=devnet`);
    console.log('\n🎉 V3 lottery is now ready to accept payments!');
  } catch (error: any) {
    console.error('\n❌ Initialization failed:', error.message);
    if (error.logs) {
      console.error('\nTransaction logs:');
      error.logs.forEach((log: string) => console.error('  ', log));
    }
    throw error;
  }
}

main().catch((error) => {
  console.error('❌ Error:', error);
  process.exit(1);
});

