'use client'

import { useWallet } from '@solana/wallet-adapter-react'
import { WalletMultiButton, useWalletModal } from '@solana/wallet-adapter-react-ui'
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
 * by properly deselecting the wallet adapter and clearing state on disconnect.
 * Also handles keeping the modal open during connection flow.
 */
export default function WalletButton() {
  const { connected, connecting, wallet, select, disconnect } = useWallet()
  const { setVisible, visible } = useWalletModal()
  const wasConnected = useRef(false)
  const lastWalletName = useRef<string | null>(null)
  const lastWallet = useRef<any>(null)
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const previousWalletRef = useRef<any>(null)
  const keepModalOpenRef = useRef(false)

  // Handle wallet selection - keep modal open during connection
  useEffect(() => {
    const currentWalletName = wallet?.adapter?.name || null
    
    // If a wallet was just selected (not previously selected) and not connected yet
    const walletJustSelected = wallet && wallet !== previousWalletRef.current && !connected
    
    if (walletJustSelected) {
      console.log(`💼 Wallet selected: ${currentWalletName} - keeping modal open during connection...`)
      // Mark that we should keep the modal open
      keepModalOpenRef.current = true
      // Ensure modal stays open
      if (!visible) {
        setVisible(true)
      }
    }
    
    previousWalletRef.current = wallet
    
    // If wallet changed, log it
    if (currentWalletName !== lastWalletName.current) {
      if (currentWalletName) {
        console.log(`💼 Wallet selected: ${currentWalletName}`)
      }
      lastWalletName.current = currentWalletName
    }
    
    // Close modal when successfully connected
    if (connected && wallet && keepModalOpenRef.current) {
      console.log(`✅ Wallet connected: ${currentWalletName} - closing modal`)
      keepModalOpenRef.current = false
      setVisible(false)
    }
    
    // If connection failed or was cancelled, keep modal open if user just selected wallet
    // The modal will remain visible so user can try again or cancel
    
    // Keep modal open while connecting
    if (connecting && wallet && !connected) {
      keepModalOpenRef.current = true
      if (!visible) {
        setVisible(true)
      }
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
  }, [connected, connecting, wallet, select, disconnect, visible, setVisible])
  
  // Separate effect to keep modal open during connection
  // This ensures if the modal closes prematurely, we reopen it
  useEffect(() => {
    // If we have a wallet selected but not connected yet, ensure modal stays open
    // Check both the flag and the connecting state to catch all cases
    if (wallet && !connected && (keepModalOpenRef.current || connecting)) {
      // If modal is closed but we're still connecting, reopen it
      if (!visible) {
        console.log('🔄 Reopening modal - connection in progress')
        // Use a small delay to ensure this runs after any modal close events from WalletMultiButton
        const timeoutId = setTimeout(() => {
          setVisible(true)
        }, 100)
        
        return () => clearTimeout(timeoutId)
      }
    }
    
    // Reset the flag if we're connected or no wallet is selected
    if (connected || !wallet) {
      keepModalOpenRef.current = false
    }
  }, [wallet, connected, connecting, visible, setVisible])

  // Just render the button - let it work normally
  // The cleanup happens automatically in the effect above
  return <WalletMultiButton />
}

