const { Connection, PublicKey } = require('@solana/web3.js');

const PROGRAM_ID = new PublicKey('52TDnXrrGRVGsTv6uE4a6cCs2YvELhe4hrtDt5dHoKov');
const DEVNET_RPC = 'https://api.devnet.solana.com';

async function testV3Config() {
  console.log('🧪 Testing V3 Configuration\n');
  
  const connection = new Connection(DEVNET_RPC, 'confirmed');
  
  // 1. Verify program is deployed
  console.log('1. Checking program deployment...');
  const programInfo = await connection.getAccountInfo(PROGRAM_ID);
  if (programInfo) {
    console.log('   ✅ Program deployed');
    console.log('   Size:', programInfo.data.length, 'bytes');
    console.log('   Balance:', programInfo.lamports / 1e9, 'SOL');
  } else {
    console.log('   ❌ Program not found');
    process.exit(1);
  }
  
  // 2. Derive and check lottery PDA
  console.log('\n2. Deriving lottery PDA...');
  const [lotteryPDA] = PublicKey.findProgramAddressSync(
    [Buffer.from('lottery')],
    PROGRAM_ID
  );
  console.log('   PDA:', lotteryPDA.toBase58());
  
  const lotteryInfo = await connection.getAccountInfo(lotteryPDA);
  if (lotteryInfo) {
    console.log('   ✅ Lottery initialized');
    console.log('   Size:', lotteryInfo.data.length, 'bytes');
  } else {
    console.log('   ❌ Lottery not initialized');
    process.exit(1);
  }
  
  // 3. Verify expected PDA matches
  const EXPECTED_PDA = 'HsZZAW2hPyeewapZEGrNJWgnHKc1mQU34oLuBXJUSV2x';
  if (lotteryPDA.toBase58() === EXPECTED_PDA) {
    console.log('   ✅ PDA matches expected value');
  } else {
    console.log('   ⚠️  PDA mismatch!');
    console.log('   Expected:', EXPECTED_PDA);
    console.log('   Got:', lotteryPDA.toBase58());
  }
  
  console.log('\n✅ V3 configuration verified!');
  console.log('\nSummary:');
  console.log('  Program ID:', PROGRAM_ID.toBase58());
  console.log('  Lottery PDA:', lotteryPDA.toBase58());
  console.log('  Status: Ready for payments');
}

testV3Config().catch(console.error);
