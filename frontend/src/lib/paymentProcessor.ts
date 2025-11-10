/**
 * Unified Payment Processor - Automatic V3/V2/V1 Routing
 * 
 * This is the drop-in replacement for processV2EntryPayment/processV3EntryPayment.
 * Just set the environment variable and it automatically uses the right version!
 * 
 * Usage:
 *   import { processEntryPayment } from "@/lib/paymentProcessor";
 *   const result = await processEntryPayment(connection, publicKey, signTransaction, amount);
 * 
 * Environment Variables:
 *   NEXT_PUBLIC_USE_CONTRACT_V3=true  → Uses V3 (secure)
 *   NEXT_PUBLIC_USE_CONTRACT_V2=true  → Uses V2 (parallel)
 *   (neither set)                     → Uses V1 (legacy, via backend API)
 */

import { Connection, PublicKey, Transaction } from "@solana/web3.js";
import { processV3EntryPayment, usdcToSmallestUnit as v3UsdcToSmallestUnit } from "./v3/paymentProcessor";
import { processV2EntryPayment, usdcToSmallestUnit as v2UsdcToSmallestUnit } from "./v2/paymentProcessor";

export interface PaymentResult {
  success: boolean;
  transactionSignature?: string;
  explorerUrl?: string;
  error?: string;
}

/**
 * Process entry payment - automatically routes to V3/V2/V1 based on environment variables
 * 
 * This is the unified entry point. Just set the env var and it works automatically!
 */
export async function processEntryPayment(
  connection: Connection,
  userWallet: PublicKey,
  signTransaction: (tx: Transaction) => Promise<Transaction>,
  entryAmount: number, // Amount in USDC (e.g., 10 for 10 USDC)
  bountyId?: number // Optional, only needed for V2
): Promise<PaymentResult> {
  // Check feature flags in priority order: V3 > V2 > V1
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
  const USE_V2 = process.env.NEXT_PUBLIC_USE_CONTRACT_V2 === "true";

  // Route to V3 if enabled
  if (USE_V3) {
    console.log("🔒 Using V3 payment processor (secure) - AUTOMATIC ROUTING");
    const entryAmountSmallest = v3UsdcToSmallestUnit(entryAmount);
    return await processV3EntryPayment(
      connection,
      userWallet,
      signTransaction,
      entryAmountSmallest
    );
  }

  // Route to V2 if enabled
  if (USE_V2) {
    console.log("🆕 Using V2 payment processor (parallel) - AUTOMATIC ROUTING");
    const entryAmountSmallest = v2UsdcToSmallestUnit(entryAmount);
    return await processV2EntryPayment(
      connection,
      userWallet,
      signTransaction,
      bountyId || 1,
      entryAmountSmallest
    );
  }

  // Fall back to V1 (would need backend API call, but for now log warning)
  console.warn("📌 V1 contract requires backend API - not implemented in frontend");
  return {
    success: false,
    error: "V1 contract must be accessed via backend API. Set NEXT_PUBLIC_USE_CONTRACT_V2=true or NEXT_PUBLIC_USE_CONTRACT_V3=true to use client-side contracts."
  };
}

/**
 * Convert USDC amount to smallest unit (6 decimals)
 */
export function usdcToSmallestUnit(amount: number): number {
  return Math.round(amount * 1_000_000);
}

/**
 * Convert smallest unit back to USDC
 */
export function smallestUnitToUsdc(amount: number): number {
  return amount / 1_000_000;
}

