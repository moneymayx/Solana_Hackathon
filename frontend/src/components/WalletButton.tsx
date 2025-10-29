'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui'
import { useEffect, useRef } from 'react'

/**
 * Clear all wallet-related items from localStorage
 * This ensures users can switch between different wallet providers
 */
function clearWalletStorage() {
  if (typeof window === 'undefined') return
  
  console.log('🧹 Clearing ALL wallet localStorage...')
  
  // Clear the standard keys
  localStorage.removeItem('walletName')
  localStorage.removeItem('billionsBountyWallet')
  
  // Clear any Solana wallet adapter keys - be very aggressive
  const keysToRemove: string[] = []
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key && (
      key.toLowerCase().includes('wallet') || 
      key.toLowerCase().includes('solana') ||
      key.toLowerCase().includes('phantom') ||
      key.toLowerCase().includes('solflare') ||
      key.toLowerCase().includes('adapter')
    )) {
      keysToRemove.push(key)
    }
  }
  
  keysToRemove.forEach(key => {
    console.log('  ❌ Removing:', key)
    localStorage.removeItem(key)
  })
  
  console.log('✅ LocalStorage cleared')
}

/**
 * Disconnect from the wallet adapter (but leave the wallet extension's state alone)
 * This allows the wallet to remember the connection but still lets us switch accounts
 */
async function disconnectWalletAdapter(disconnect: () => Promise<void>) {
  if (typeof window === 'undefined') return
  
  console.log('🔌 Disconnecting wallet adapter...')
  
  try {
    // Only disconnect from the wallet adapter
    // Don't call the wallet extension's disconnect method
    // This allows Phantom/Solflare to remember the connection but lets us clear our app's state
    await disconnect()
    console.log('✅ Wallet adapter disconnected')
  } catch (error) {
    console.error('❌ Error during disconnect:', error)
  }
}

/**
 * Wrapper around WalletMultiButton that ensures proper wallet switching
 * by properly deselecting the wallet adapter and clearing state on disconnect
 */
export default function WalletButton() {
  const { connected, connecting, wallet, select, disconnect } = useWallet()
  const wasConnected = useRef(false)
  const lastWalletName = useRef<string | null>(null)
  const lastWallet = useRef<any>(null)
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Track wallet changes and handle disconnect cleanup
  useEffect(() => {
    const currentWalletName = wallet?.adapter?.name || null
    
    // If wallet changed, log it
    if (currentWalletName !== lastWalletName.current) {
      if (currentWalletName) {
        console.log(`💼 Wallet selected: ${currentWalletName}`)
      }
      lastWalletName.current = currentWalletName
    }
    
    // Clear any pending cleanup if we're connecting or already connected
    if (connected || connecting) {
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current)
        cleanupTimeoutRef.current = null
      }
      // Only mark as "was connected" if we're actually fully connected
      // This prevents false positives during connection attempts
      if (connected) {
        wasConnected.current = true
        lastWallet.current = wallet
      }
    }
    
    // ONLY clean up on intentional disconnect:
    // 1. We WERE fully connected (wasConnected is true)
    // 2. Now we're NOT connected AND not connecting
    // 3. No wallet is selected (user clicked disconnect, not just switching)
    if (wasConnected.current === true && !connected && !connecting && !wallet) {
      // Use a delay to avoid false positives during wallet switching or connection failures
      cleanupTimeoutRef.current = setTimeout(async () => {
        console.log('📴 User disconnected - cleaning up...')
        
        // Disconnect from the wallet adapter only (not the wallet extension itself)
        await disconnectWalletAdapter(disconnect)
        
        // Clear our app's state
        select(null)
        clearWalletStorage()
        
        wasConnected.current = false
        lastWallet.current = null
      }, 500) // Reduced to 500ms for faster cleanup
    }
    
    // Cleanup function to clear timeout on unmount
    return () => {
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current)
      }
    }
  }, [connected, connecting, wallet, select, disconnect])

  // Just render the button - let it work normally
  // The cleanup happens automatically in the effect above
  return <WalletMultiButton />
}

