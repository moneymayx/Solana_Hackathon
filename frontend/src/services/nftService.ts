/**
 * NFT Service
 * 
 * Handles NFT verification and ownership checking via smart contract
 */

import { Connection, PublicKey, Transaction, TransactionInstruction } from '@solana/web3.js';
import { WalletContextState } from '@solana/wallet-adapter-react';
import { TOKEN_PROGRAM_ID } from '@solana/spl-token';
import { getBackendUrl } from '@/lib/api/client';

// NFT mint address that grants access
export const AUTHORIZED_NFT_MINT = '9dBdXMB3WuTy638W1a1tTygWCzosUmALhRLksrX8oQVa';

// Program ID for the lottery contract (will be updated after deployment)
const PROGRAM_ID = new PublicKey('Exdfc34rowaKJDnJtLpf5hNs5EF6eGXghRB2ocjrPd6H');

interface NftVerificationResult {
  success: boolean;
  verified: boolean;
  questionsGranted?: number;
  message: string;
  signature?: string;
}

interface NftStatusResult {
  verified: boolean;
  nftMint?: string;
  verifiedAt?: string;
  questionsRemaining: number;
}

/**
 * Check if wallet owns the required NFT
 * Backend returns is_mock flag to determine whether to use RPC or mock
 */
export async function checkNftOwnership(
  connection: Connection,
  walletAddress: string
): Promise<boolean> {
  try {
    // First check with backend to see if we're in mock mode
    const statusResponse = await fetch(`${getBackendUrl()}/api/nft/status/${walletAddress}`);
    const statusData = await statusResponse.json();
    
    // If backend is in mock mode, use its response
    if (statusData.is_mock) {
      console.log('🎨 MOCK NFT mode - using backend response');
      return statusData.has_nft || false;
    }
    
    // Real mode - use Solana RPC to check NFT ownership
    console.log('💎 REAL NFT mode - checking blockchain');
    const wallet = new PublicKey(walletAddress);
    const nftMint = new PublicKey(AUTHORIZED_NFT_MINT);
    
    // Get token accounts owned by the wallet
    const tokenAccounts = await connection.getParsedTokenAccountsByOwner(wallet, {
      mint: nftMint,
    });
    
    // Check if user has at least 1 of the NFT
    if (tokenAccounts.value.length > 0) {
      const balance = tokenAccounts.value[0].account.data.parsed.info.tokenAmount.uiAmount;
      return balance >= 1;
    }
    
    return false;
  } catch (error) {
    console.error('Error checking NFT ownership:', error);
    return false;
  }
}

/**
 * Get NFT verification status for a wallet
 */
export async function getNftStatus(walletAddress: string): Promise<NftStatusResult> {
  try {
    const response = await fetch(`${getBackendUrl()}/api/nft/status/${walletAddress}`);
    const data = await response.json();
    
    return {
      verified: data.verified || false,
      nftMint: data.nft_mint,
      verifiedAt: data.verified_at,
      questionsRemaining: data.questions_remaining || 0,
    };
  } catch (error) {
    console.error('Error fetching NFT status:', error);
    return {
      verified: false,
      questionsRemaining: 0,
    };
  }
}

/**
 * Derive the NFT verification PDA for a user
 */
function deriveNftVerificationPda(userWallet: PublicKey): [PublicKey, number] {
  return PublicKey.findProgramAddressSync(
    [Buffer.from('nft_verification'), userWallet.toBuffer()],
    PROGRAM_ID
  );
}

/**
 * Get associated token address for NFT
 */
async function getAssociatedTokenAddress(
  mint: PublicKey,
  owner: PublicKey
): Promise<PublicKey> {
  const [address] = await PublicKey.findProgramAddress(
    [
      owner.toBuffer(),
      TOKEN_PROGRAM_ID.toBuffer(),
      mint.toBuffer(),
    ],
    new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL') // Associated Token Program
  );
  return address;
}

/**
 * Verify NFT ownership
 * Checks backend mode first, then uses either mock or real verification
 */
export async function verifyNftOwnership(
  connection: Connection,
  wallet: WalletContextState
): Promise<NftVerificationResult> {
  if (!wallet.publicKey || !wallet.signTransaction) {
    return {
      success: false,
      verified: false,
      message: 'Wallet not connected',
    };
  }
  
  try {
    // Check NFT ownership first (this already handles mock vs real)
    const ownsNft = await checkNftOwnership(connection, wallet.publicKey.toString());
    if (!ownsNft) {
      return {
        success: false,
        verified: false,
        message: 'You do not own the required NFT to verify.',
      };
    }
    
    // Check backend mode
    const statusResponse = await fetch(`http://localhost:8000/api/nft/status/${wallet.publicKey.toString()}`);
    const statusData = await statusResponse.json();
    
    let signature: string | undefined;
    
    // If real mode, create and sign blockchain transaction
    if (!statusData.is_mock) {
      console.log('💎 REAL NFT verification - signing transaction');
      
      // Derive accounts
      const nftMint = new PublicKey(AUTHORIZED_NFT_MINT);
      const [nftVerificationPda] = deriveNftVerificationPda(wallet.publicKey);
      const nftTokenAccount = await getAssociatedTokenAddress(nftMint, wallet.publicKey);
      
      // Derive metadata account (Metaplex standard)
      const [nftMetadata] = await PublicKey.findProgramAddress(
        [
          Buffer.from('metadata'),
          new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s').toBuffer(),
          nftMint.toBuffer(),
        ],
        new PublicKey('metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s')
      );
      
      // Build instruction
      const instructionData = Buffer.from([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]);
      
      const instruction = new TransactionInstruction({
        keys: [
          { pubkey: nftVerificationPda, isSigner: false, isWritable: true },
          { pubkey: wallet.publicKey, isSigner: true, isWritable: true },
          { pubkey: nftMint, isSigner: false, isWritable: false },
          { pubkey: nftTokenAccount, isSigner: false, isWritable: false },
          { pubkey: nftMetadata, isSigner: false, isWritable: false },
          { pubkey: new PublicKey('11111111111111111111111111111111'), isSigner: false, isWritable: false },
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
        ],
        programId: PROGRAM_ID,
        data: instructionData,
      });
      
      // Create and send transaction
      const transaction = new Transaction().add(instruction);
      transaction.feePayer = wallet.publicKey;
      transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
      
      const signedTransaction = await wallet.signTransaction(transaction);
      signature = await connection.sendRawTransaction(signedTransaction.serialize());
      await connection.confirmTransaction(signature, 'confirmed');
      
      console.log('✅ Transaction signed:', signature);
    } else {
      console.log('🎨 MOCK NFT mode - skipping blockchain transaction');
    }
    
    // Call backend to verify and grant questions
    const response = await fetch(`${getBackendUrl()}/api/nft/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: wallet.publicKey.toString(),
        signature: signature,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to verify NFT`);
    }
    
    const data = await response.json();
    
    return {
      success: data.success || false,
      verified: data.verified || false,
      questionsGranted: data.questions_granted,
      message: data.message || 'Verification completed',
      signature: data.signature || signature,
    };
    
  } catch (error) {
    console.error('Error verifying NFT ownership:', error);
    return {
      success: false,
      verified: false,
      message: error instanceof Error ? error.message : 'Failed to verify NFT ownership',
    };
  }
}

/**
 * Check ownership via backend (pre-verification check)
 */
export async function checkNftOwnershipViaBackend(
  walletAddress: string,
  nftMint: string = AUTHORIZED_NFT_MINT
): Promise<boolean> {
  try {
    const response = await fetch(
      `${getBackendUrl()}/api/nft/check-ownership/${walletAddress}/${nftMint}`
    );
    const data = await response.json();
    return data.owns_nft || false;
  } catch (error) {
    console.error('Error checking NFT ownership via backend:', error);
    return false;
  }
}


