'use client'

import { useMemo } from 'react'
import { ConnectionProvider, WalletProvider as SolanaWalletProvider } from '@solana/wallet-adapter-react'
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base'
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui'
import { SolflareWalletAdapter } from '@solana/wallet-adapter-wallets'
import { clusterApiUrl } from '@solana/web3.js'

// Default styles that can be overridden by your app
import '@solana/wallet-adapter-react-ui/styles.css'

export function WalletProvider({ children }: { children: React.ReactNode }) {
  // The network can be set to 'devnet', 'testnet', or 'mainnet-beta'
  // Default to devnet for testing (change to Mainnet for production)
  // Can be overridden with NEXT_PUBLIC_SOLANA_NETWORK env var
  const networkEnv = process.env.NEXT_PUBLIC_SOLANA_NETWORK?.toLowerCase();
  const network = networkEnv === 'mainnet' || networkEnv === 'mainnet-beta'
    ? WalletAdapterNetwork.Mainnet
    : WalletAdapterNetwork.Devnet; // Default to devnet for testing

  // You can also provide a custom RPC endpoint via env var
  // If NEXT_PUBLIC_SOLANA_RPC_URL is set, use it; otherwise use clusterApiUrl
  const endpoint = useMemo(() => {
    const customRpc = process.env.NEXT_PUBLIC_SOLANA_RPC_URL;
    if (customRpc) {
      console.log(`🔗 Using custom RPC endpoint: ${customRpc}`);
      return customRpc;
    }
    const defaultEndpoint = clusterApiUrl(network);
    console.log(`🔗 Using default ${network} endpoint: ${defaultEndpoint}`);
    return defaultEndpoint;
  }, [network])

  const wallets = useMemo(
    () => [
      // Phantom is already provided through Wallet Standard adapters, so we only instantiate Solflare explicitly.
      new SolflareWalletAdapter(),
    ],
    []
  )

  return (
    <ConnectionProvider endpoint={endpoint}>
      <SolanaWalletProvider wallets={wallets} autoConnect={false}>
        <WalletModalProvider>
          {children}
        </WalletModalProvider>
      </SolanaWalletProvider>
    </ConnectionProvider>
  )
}
