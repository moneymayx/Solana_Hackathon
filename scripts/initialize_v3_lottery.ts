#!/usr/bin/env ts-node
/**
 * Initialize V3 Lottery on Devnet
 * 
 * This script initializes the V3 lottery contract with required parameters.
 * Run this after deploying the V3 program to devnet.
 * 
 * Usage:
 *   ts-node scripts/initialize_v3_lottery.ts
 * 
 * Requirements:
 *   - Solana CLI configured with devnet wallet
 *   - Wallet has SOL for transaction fees
 *   - Jackpot wallet has USDC (or test USDC) for initial funding
 */

import { Connection, PublicKey, Transaction, TransactionInstruction, Keypair, SystemProgram } from '@solana/web3.js';
import { 
  getAssociatedTokenAddress, 
  TOKEN_PROGRAM_ID, 
  ASSOCIATED_TOKEN_PROGRAM_ID,
  createAssociatedTokenAccountInstruction,
  getAccount
} from '@solana/spl-token';
import * as anchor from '@coral-xyz/anchor';
import * as fs from 'fs';
import * as path from 'path';
import { sha256 } from '@noble/hashes/sha256';
import { readFileSync, existsSync } from 'fs';
import { homedir } from 'os';

// V3 Configuration
const PROGRAM_ID = new PublicKey('52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov');
const DEVNET_RPC = 'https://api.devnet.solana.com';

// Configuration (update these for your deployment)
const CONFIG = {
  // Authority wallet (the wallet that will own/control the lottery)
  // Can use existing wallet or generate new one
  // Set AUTHORITY_KEYPAIR_PATH or it will use default Solana CLI wallet
  AUTHORITY_KEYPAIR_PATH: process.env.AUTHORITY_KEYPAIR_PATH || undefined,
  
  // Jackpot wallet (where winnings accumulate)
  // Using V2 bounty pool wallet as example - adjust for V3
  JACKPOT_WALLET: new PublicKey('CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF'),
  
  // Backend authority (for signature verification)
  // This should be your backend's public key that signs AI decisions
  BACKEND_AUTHORITY: new PublicKey(process.env.V3_BACKEND_AUTHORITY || 'CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF'),
  
  // USDC Mint (devnet)
  // Options:
  // - EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v (mainnet USDC - can work on devnet)
  // - Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr (V1/V2 devnet test USDC)
  // - JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh (V2 devnet test USDC - has 15 USDC available)
  USDC_MINT: new PublicKey(process.env.V3_USDC_MINT_DEVNET || 'JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh'),
  
  // Lottery parameters
  // Note: research_fund_floor must be <= initial jackpot token account balance
  // For testing, can use lower amounts (e.g., 10 USDC = 10_000_000)
  RESEARCH_FUND_FLOOR: Number(process.env.V3_RESEARCH_FUND_FLOOR || 10_000_000), // Default: 10 USDC for testing (min: 1_000_000 = 1 USDC)
  RESEARCH_FEE: Number(process.env.V3_RESEARCH_FEE || 10_000_000), // 10 USDC per entry (in smallest units: 6 decimals)
};

/**
 * Derive lottery PDA
 */
function findLotteryPDA(): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from('lottery')],
    PROGRAM_ID
  );
}

/**
 * Build initialize_lottery instruction (raw, without Anchor)
 */
function buildInitializeLotteryInstruction(
  lottery: PublicKey,
  authority: PublicKey,
  jackpotWallet: PublicKey,
  jackpotTokenAccount: PublicKey,
  usdcMint: PublicKey,
  researchFundFloor: number,
  researchFee: number,
  backendAuthority: PublicKey
): TransactionInstruction {
  // Instruction discriminator: sha256("global:initialize_lottery")[:8]
  // From raw_instruction_helpers.ts: [113, 199, 243, 247, 73, 217, 33, 11]
  const discriminator = Buffer.from([113, 199, 243, 247, 73, 217, 33, 11]);
  
  // Serialize args: researchFundFloor (u64) + researchFee (u64) + jackpotWallet (32) + backendAuthority (32)
  function serializeU64(value: number): Buffer {
    const buf = Buffer.alloc(8);
    buf.writeBigUInt64LE(BigInt(value), 0);
    return buf;
  }
  
  const args = Buffer.concat([
    serializeU64(researchFundFloor),
    serializeU64(researchFee),
    Buffer.from(jackpotWallet.toBytes()),
    Buffer.from(backendAuthority.toBytes()),
  ]);
  
  const data = Buffer.concat([discriminator, args]);
  
  return new TransactionInstruction({
    keys: [
      { pubkey: lottery, isSigner: false, isWritable: true },
      { pubkey: authority, isSigner: true, isWritable: true },
      { pubkey: jackpotWallet, isSigner: false, isWritable: false },
      { pubkey: jackpotTokenAccount, isSigner: false, isWritable: true },
      { pubkey: usdcMint, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: ASSOCIATED_TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    programId: PROGRAM_ID,
    data,
  });
}

async function main() {
  console.log('🚀 Initializing V3 Lottery on Devnet\n');
  
  const connection = new Connection(DEVNET_RPC, 'confirmed');
  
  // Load authority keypair
  let authority: Keypair;
  if (CONFIG.AUTHORITY_KEYPAIR_PATH) {
    const keypairData = JSON.parse(readFileSync(CONFIG.AUTHORITY_KEYPAIR_PATH, 'utf-8'));
    authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
    console.log('✅ Loaded authority from:', CONFIG.AUTHORITY_KEYPAIR_PATH);
  } else {
    // Try to use Solana CLI default wallet
    const defaultKeypairPath = path.join(homedir(), '.config', 'solana', 'id.json');
    
    if (!existsSync(defaultKeypairPath)) {
      console.error('❌ No authority keypair found!');
      console.error('   Options:');
      console.error('   1. Set AUTHORITY_KEYPAIR_PATH environment variable');
      console.error('   2. Configure Solana CLI default wallet: solana config set --keypair <path>');
      process.exit(1);
    }
    
    const keypairData = JSON.parse(readFileSync(defaultKeypairPath, 'utf-8'));
    authority = Keypair.fromSecretKey(Uint8Array.from(keypairData));
    console.log('✅ Using Solana CLI default wallet as authority');
  }
  
  console.log('   Authority:', authority.publicKey.toBase58());
  
  // Check authority balance
  const authorityBalance = await connection.getBalance(authority.publicKey);
  console.log('   Balance:', authorityBalance / 1e9, 'SOL');
  
  if (authorityBalance < 0.1 * 1e9) {
    console.warn('⚠️  Low balance - may need SOL for transaction fees');
    console.log('   Get devnet SOL: solana airdrop 1', authority.publicKey.toBase58(), '--url devnet');
  }
  
  console.log('');
  
  // Derive lottery PDA
  const [lotteryPDA, lotteryBump] = findLotteryPDA();
  console.log('📋 Configuration:');
  console.log('   Program ID:', PROGRAM_ID.toBase58());
  console.log('   Lottery PDA:', lotteryPDA.toBase58());
  console.log('   Bump:', lotteryBump);
  console.log('   Jackpot Wallet:', CONFIG.JACKPOT_WALLET.toBase58());
  console.log('   Backend Authority:', CONFIG.BACKEND_AUTHORITY.toBase58());
  console.log('   USDC Mint:', CONFIG.USDC_MINT.toBase58());
  console.log('   Research Fund Floor:', CONFIG.RESEARCH_FUND_FLOOR / 1e6, 'USDC');
  console.log('   Research Fee:', CONFIG.RESEARCH_FEE / 1e6, 'USDC');
  console.log('');
  
  // Check if lottery already exists
  console.log('🔍 Checking if lottery is already initialized...');
  const existingLottery = await connection.getAccountInfo(lotteryPDA);
  
  if (existingLottery) {
    console.log('✅ Lottery already initialized!');
    console.log('   Account exists at:', lotteryPDA.toBase58());
    console.log('   Size:', existingLottery.data.length, 'bytes');
    return;
  }
  
  console.log('❌ Lottery not initialized - proceeding with initialization...\n');
  
  // Get jackpot token account (ATA)
  const jackpotTokenAccount = await getAssociatedTokenAddress(
    CONFIG.USDC_MINT,
    CONFIG.JACKPOT_WALLET
  );
  
  console.log('   Jackpot Token Account:', jackpotTokenAccount.toBase58());
  
  // Check if jackpot token account exists and has sufficient balance
  try {
    const tokenAccount = await getAccount(connection, jackpotTokenAccount);
    console.log('   Token Account Balance:', Number(tokenAccount.amount) / 1e6, 'USDC');
    
    if (Number(tokenAccount.amount) < CONFIG.RESEARCH_FUND_FLOOR) {
      console.warn('⚠️  Warning: Jackpot token account has insufficient balance!');
      console.warn(`   Have: ${Number(tokenAccount.amount) / 1e6} USDC`);
      console.warn(`   Need: ${CONFIG.RESEARCH_FUND_FLOOR / 1e6} USDC minimum`);
      console.warn('   Contract requires initial funding to initialize.');
    }
  } catch (e: any) {
    if (e.message?.includes('TokenAccountNotFoundError')) {
      console.error('❌ Jackpot token account does not exist!');
      console.error('   Token Account:', jackpotTokenAccount.toBase58());
      console.error('   You need to create the associated token account first.');
      console.error('   Command: spl-token create-account', CONFIG.USDC_MINT.toBase58(), '--owner', CONFIG.JACKPOT_WALLET.toBase58(), '--url devnet');
      process.exit(1);
    }
    throw e;
  }
  
  // Build initialization instruction
  console.log('\n📝 Building initialization transaction...');
  const initIx = buildInitializeLotteryInstruction(
    lotteryPDA,
    authority.publicKey,
    CONFIG.JACKPOT_WALLET,
    jackpotTokenAccount,
    CONFIG.USDC_MINT,
    CONFIG.RESEARCH_FUND_FLOOR,
    CONFIG.RESEARCH_FEE,
    CONFIG.BACKEND_AUTHORITY
  );
  
  const tx = new Transaction().add(initIx);
  
  // Get recent blockhash
  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();
  tx.recentBlockhash = blockhash;
  tx.feePayer = authority.publicKey;
  
  // Sign transaction
  console.log('✍️  Signing transaction...');
  tx.sign(authority);
  
  // Send transaction
  console.log('📤 Sending transaction to devnet...');
  const signature = await connection.sendRawTransaction(tx.serialize(), {
    skipPreflight: false,
    maxRetries: 3,
  });
  
  console.log('   Signature:', signature);
  
  // Confirm transaction
  console.log('⏳ Confirming transaction...');
  await connection.confirmTransaction(
    {
      signature,
      blockhash,
      lastValidBlockHeight,
    },
    'confirmed'
  );
  
  console.log('\n✅ Lottery initialized successfully!');
  console.log('   Transaction:', signature);
  console.log('   Explorer:', `https://explorer.solana.com/tx/${signature}?cluster=devnet`);
  console.log('\n🎉 V3 lottery is now ready to accept payments!');
}

main().catch((error) => {
  console.error('❌ Error:', error);
  process.exit(1);
});

