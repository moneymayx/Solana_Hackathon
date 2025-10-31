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
  const { connected, connecting, wallet, select, disconnect, connect } = useWallet()
  const { setVisible, visible } = useWalletModal()
  const wasConnected = useRef(false)
  const lastWalletName = useRef<string | null>(null)
  const lastWallet = useRef<any>(null)
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const previousWalletRef = useRef<any>(null)
  const keepModalOpenRef = useRef(false)
  const hasHandledSelectionRef = useRef(false)
  const reopenTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const connectionAttemptedRef = useRef(false)

  // Handle wallet selection - keep modal open during connection
  useEffect(() => {
    const currentWalletName = wallet?.adapter?.name || null
    let connectionTimeout: NodeJS.Timeout | null = null
    let retryTimeout: NodeJS.Timeout | null = null
    
    // If a wallet was just selected (not previously selected) and not connected yet
    const walletJustSelected = wallet && wallet !== previousWalletRef.current && !connected
    
    if (walletJustSelected) {
      console.log(`💼 Wallet selected: ${currentWalletName} - triggering connection...`)
      // Reset connection attempt flag for new wallet selection
      connectionAttemptedRef.current = false
      hasHandledSelectionRef.current = true
      
      // Keep modal open
      keepModalOpenRef.current = true
      if (!visible) {
        setVisible(true)
      }
      
      // Automatically trigger connection when wallet is selected
      // Use a small delay to ensure wallet adapter is ready and to avoid conflicts
      // with WalletMultiButton's internal connection flow
      if (!connecting && !connected && connect) {
        // Use setTimeout to ensure this happens after React's render cycle
        connectionTimeout = setTimeout(() => {
          if (wallet && !connecting && !connected && !connectionAttemptedRef.current) {
            console.log(`🔌 Starting connection to ${currentWalletName}...`)
            connectionAttemptedRef.current = true
            connect()
              .then(() => {
                console.log(`✅ Connection initiated for ${currentWalletName}`)
              })
              .catch((error) => {
                console.error(`❌ Connection failed: ${error.message}`)
                connectionAttemptedRef.current = false
                // Keep modal open so user can try again
              })
          }
        }, 50) // Small delay to ensure wallet adapter is ready
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
    
    // Keep modal open while actively connecting
    if (connecting && wallet && !connected) {
      keepModalOpenRef.current = true
      hasHandledSelectionRef.current = true
      if (!visible) {
        setVisible(true)
      }
    }
    
    // If we have a wallet selected but not connecting and not connected after a delay,
    // try to trigger connection again (in case it didn't start automatically)
    if (wallet && !connecting && !connected && !connectionAttemptedRef.current && hasHandledSelectionRef.current) {
      // Wallet is selected but connection hasn't started - try to start it
      retryTimeout = setTimeout(() => {
        if (wallet && !connecting && !connected && connect && !connectionAttemptedRef.current) {
          console.log(`🔄 Retrying connection for ${wallet.adapter?.name}...`)
          connectionAttemptedRef.current = true
          connect()
            .then(() => {
              console.log(`✅ Retry connection initiated`)
            })
            .catch((error) => {
              console.error(`❌ Retry connection failed: ${error.message}`)
              connectionAttemptedRef.current = false
            })
        }
      }, 200) // Wait 200ms before retry
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
    
    // Cleanup function to clear all timeouts on unmount or re-render
    return () => {
      if (connectionTimeout) {
        clearTimeout(connectionTimeout)
      }
      if (retryTimeout) {
        clearTimeout(retryTimeout)
      }
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current)
        cleanupTimeoutRef.current = null
      }
    }
  }, [connected, connecting, wallet, select, disconnect, connect, visible, setVisible])
  
  // Separate effect to keep modal open during connection
  // This ensures if the modal closes prematurely, we reopen it
  useEffect(() => {
    // Clear any pending reopen timeout
    if (reopenTimeoutRef.current) {
      clearTimeout(reopenTimeoutRef.current)
      reopenTimeoutRef.current = null
    }
    
    // Only reopen modal if we're ACTIVELY connecting (not just selected)
    // This prevents infinite loops when wallet is selected but connection hasn't started
    if (connecting && wallet && !connected) {
      // We're actively connecting - keep modal open
      keepModalOpenRef.current = true
      if (!visible) {
        console.log('🔄 Reopening modal - connection in progress')
        // Use a small delay to ensure this runs after any modal close events from WalletMultiButton
        // Only reopen once per connection attempt
        reopenTimeoutRef.current = setTimeout(() => {
          if (connecting && wallet && !connected) {
            setVisible(true)
          }
        }, 100)
      }
    } else if (!connecting && wallet && !connected) {
      // Wallet is selected but not connecting yet - don't force reopen
      // This prevents the loop - let the modal stay closed if connection hasn't started
      // The wallet adapter will start connecting automatically, and then we'll reopen
      keepModalOpenRef.current = false
    }
    
    // Reset the flag if we're connected or no wallet is selected
    if (connected || !wallet) {
      keepModalOpenRef.current = false
      hasHandledSelectionRef.current = false
      connectionAttemptedRef.current = false
    }
    
    return () => {
      if (reopenTimeoutRef.current) {
        clearTimeout(reopenTimeoutRef.current)
        reopenTimeoutRef.current = null
      }
    }
  }, [wallet, connected, connecting, visible, setVisible])

  // Just render the button - let it work normally
  // The cleanup happens automatically in the effect above
  return <WalletMultiButton />
}

