/**
 * V2 Payment Button Component
 * 
 * React component for processing V2 entry payments using raw Solana instructions
 */
"use client";

import { useState } from "react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import {
  processV2EntryPayment,
  usdcToSmallestUnit,
  smallestUnitToUsdc,
} from "@/lib/v2/paymentProcessor";

interface V2PaymentButtonProps {
  bountyId?: number;
  defaultAmount?: number; // Default amount in USDC
  onSuccess?: (signature: string, explorerUrl: string) => void;
  onError?: (error: string) => void;
}

export default function V2PaymentButton({
  bountyId = 1,
  defaultAmount = 15,
  onSuccess,
  onError,
}: V2PaymentButtonProps) {
  const { connection } = useConnection();
  const { publicKey, signTransaction, connected } = useWallet();
  const [amount, setAmount] = useState(defaultAmount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePayment = async () => {
    if (!connected || !publicKey || !signTransaction) {
      setError("Please connect your wallet");
      onError?.("Wallet not connected");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const entryAmount = usdcToSmallestUnit(amount);

      console.log(`🔄 Processing V2 payment: ${amount} USDC (${entryAmount} smallest units)`);

      const result = await processV2EntryPayment(
        connection,
        publicKey,
        signTransaction,
        bountyId,
        entryAmount
      );

      if (result.success && result.transactionSignature) {
        console.log("✅ Payment successful!", result.transactionSignature);
        onSuccess?.(result.transactionSignature, result.explorerUrl || "");
      } else {
        const errorMsg = result.error || "Payment failed";
        console.error("❌ Payment failed:", errorMsg);
        setError(errorMsg);
        onError?.(errorMsg);
      }
    } catch (err: any) {
      const errorMsg = err.message || String(err);
      console.error("❌ Payment error:", errorMsg);
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="v2-payment-button">
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Payment Amount (USDC)
        </label>
        <input
          type="number"
          min="1"
          step="0.1"
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
          disabled={loading || !connected}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-900 bg-white"
          placeholder="Enter amount"
        />
        <p className="text-xs text-gray-500 mt-1">
          Minimum: ~10 USDC (may vary due to price escalation)
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={handlePayment}
        disabled={loading || !connected || amount <= 0}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
      >
        {loading
          ? "Processing..."
          : !connected
          ? "Connect Wallet"
          : `Pay ${amount} USDC`}
      </button>

      {!connected && (
        <p className="text-sm text-gray-500 mt-2 text-center">
          Connect your Solana wallet to proceed
        </p>
      )}
    </div>
  );
}



