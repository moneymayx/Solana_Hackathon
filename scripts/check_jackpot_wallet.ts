#!/usr/bin/env ts-node
/**
 * Check Jackpot Wallet Balance for V3 Initialization
 */

import { Connection, PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddress, getAccount } from '@solana/spl-token';

const DEVNET_RPC = 'https://api.devnet.solana.com';

// Configuration
const JACKPOT_WALLET = new PublicKey('CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF');
const USDC_MINT_OPTIONS = [
  { name: 'Mainnet USDC', address: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v' },
  { name: 'V2 Devnet Test', address: 'JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh' },
  { name: 'V1 Devnet Test', address: 'Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr' },
];

async function checkWallet() {
  console.log('🔍 Checking Jackpot Wallet Status\n');
  console.log('Jackpot Wallet:', JACKPOT_WALLET.toBase58());
  console.log('');
  
  const connection = new Connection(DEVNET_RPC, 'confirmed');
  
  // Check SOL balance
  const solBalance = await connection.getBalance(JACKPOT_WALLET);
  console.log('SOL Balance:', solBalance / 1e9, 'SOL');
  console.log('');
  
  // Check USDC balances for each mint
  console.log('📊 Checking USDC Token Balances:\n');
  
  for (const mint of USDC_MINT_OPTIONS) {
    try {
      const mintPubkey = new PublicKey(mint.address);
      const tokenAccount = await getAssociatedTokenAddress(mintPubkey, JACKPOT_WALLET);
      
      try {
        const account = await getAccount(connection, tokenAccount);
        const balance = Number(account.amount) / 1e6; // USDC has 6 decimals
        console.log(`${mint.name}:`);
        console.log(`  Mint: ${mint.address}`);
        console.log(`  Token Account: ${tokenAccount.toBase58()}`);
        console.log(`  Balance: ${balance} USDC`);
        if (balance >= 1000) {
          console.log(`  ✅ Sufficient for initialization (need 1000 USDC)`);
        } else {
          console.log(`  ⚠️  Insufficient (need 1000 USDC, have ${balance})`);
        }
        console.log('');
      } catch (e: any) {
        if (e.message?.includes('TokenAccountNotFoundError')) {
          console.log(`${mint.name}:`);
          console.log(`  Mint: ${mint.address}`);
          console.log(`  ❌ Token account does not exist`);
          console.log('');
        } else {
          throw e;
        }
      }
    } catch (error: any) {
      console.log(`${mint.name}:`);
      console.log(`  ❌ Error: ${error.message}`);
      console.log('');
    }
  }
  
  console.log('📋 Summary:');
  console.log('   To initialize V3 lottery, the jackpot wallet needs:');
  console.log('   - At least 1000 USDC in one of the token accounts above');
  console.log('   - Or you can mint test USDC if you have mint authority');
  console.log('');
}

checkWallet().catch(console.error);

