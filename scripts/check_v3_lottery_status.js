#!/usr/bin/env node
/**
 * Check V3 Lottery Status on Devnet
 * 
 * Verifies if the V3 lottery account has been initialized on devnet
 */

const { Connection, PublicKey } = require('@solana/web3.js');

// V3 Configuration
const PROGRAM_ID = new PublicKey('52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov');
const DEVNET_RPC = 'https://api.devnet.solana.com';

async function checkLotteryStatus() {
  console.log('🔍 Checking V3 Lottery Status on Devnet...\n');
  
  const connection = new Connection(DEVNET_RPC, 'confirmed');
  
  // Derive lottery PDA
  const [lotteryPDA, bump] = PublicKey.findProgramAddressSync(
    [Buffer.from('lottery')],
    PROGRAM_ID
  );
  
  console.log('Program ID:', PROGRAM_ID.toBase58());
  console.log('Lottery PDA:', lotteryPDA.toBase58());
  console.log('Bump:', bump);
  console.log('');
  
  try {
    // Check if program exists
    console.log('1️⃣ Checking if program is deployed...');
    const programInfo = await connection.getAccountInfo(PROGRAM_ID);
    
    if (!programInfo) {
      console.log('❌ Program not found on devnet!');
      console.log('   The V3 program needs to be deployed first.');
      return;
    }
    
    console.log('✅ Program is deployed');
    console.log('   Owner:', programInfo.owner.toBase58());
    console.log('   Lamports:', programInfo.lamports);
    console.log('');
    
    // Check if lottery account exists
    console.log('2️⃣ Checking if lottery account is initialized...');
    const lotteryAccount = await connection.getAccountInfo(lotteryPDA);
    
    if (!lotteryAccount) {
      console.log('❌ Lottery account NOT initialized');
      console.log('   Lottery PDA:', lotteryPDA.toBase58());
      console.log('');
      console.log('📋 To initialize, you need to:');
      console.log('   1. Call initialize_lottery instruction');
      console.log('   2. Provide required parameters:');
      console.log('      - research_fund_floor (u64)');
      console.log('      - research_fee (u64)');
      console.log('      - jackpot_wallet (Pubkey)');
      console.log('      - backend_authority (Pubkey)');
      console.log('');
      console.log('   See: docs/development/V3_INTEGRATION_GUIDE.md');
      return;
    }
    
    console.log('✅ Lottery account EXISTS!');
    console.log('   Account address:', lotteryPDA.toBase58());
    console.log('   Account size:', lotteryAccount.data.length, 'bytes');
    console.log('   Lamports:', lotteryAccount.lamports);
    console.log('   Owner:', lotteryAccount.owner.toBase58());
    
    // Try to parse account data
    if (lotteryAccount.data.length >= 8 + 32 + 32) {
      // Format: discriminator (8) + authority (32) + jackpot_wallet (32)
      const authorityBuffer = lotteryAccount.data.slice(8, 8 + 32);
      const jackpotWalletBuffer = lotteryAccount.data.slice(8 + 32, 8 + 32 + 32);
      
      try {
        const authority = new PublicKey(authorityBuffer);
        const jackpotWallet = new PublicKey(jackpotWalletBuffer);
        
        console.log('');
        console.log('📊 Lottery Account Data:');
        console.log('   Authority:', authority.toBase58());
        console.log('   Jackpot Wallet:', jackpotWallet.toBase58());
      } catch (e) {
        console.log('   (Could not parse account data structure)');
      }
    }
    
    console.log('');
    console.log('✅ V3 Lottery is INITIALIZED and ready to use!');
    
  } catch (error) {
    console.error('❌ Error checking lottery status:', error.message);
    console.error(error);
  }
}

checkLotteryStatus().catch(console.error);

