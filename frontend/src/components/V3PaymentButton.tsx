/**
 * V3 Payment Button Component
 * 
 * React component for processing V3 entry payments using the secure payment processor
 * Similar to V2PaymentButton but uses V3 contract with enhanced security
 */
"use client";

import { useState } from "react";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import {
  processV3EntryPayment,
  usdcToSmallestUnit,
} from "@/lib/v3/paymentProcessor";
import { ExternalLink, Loader2, AlertCircle } from "lucide-react";

interface V3PaymentButtonProps {
  defaultAmount?: number; // Default amount in USDC
  onSuccess?: (signature: string, explorerUrl: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

export default function V3PaymentButton({
  defaultAmount = 10,
  onSuccess,
  onError,
  className = "",
}: V3PaymentButtonProps) {
  const { connection } = useConnection();
  const { publicKey, signTransaction, connected } = useWallet();
  const [amount, setAmount] = useState(defaultAmount);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{
    signature: string;
    explorerUrl: string;
  } | null>(null);

  const handlePayment = async () => {
    if (!connected || !publicKey || !signTransaction) {
      const errorMsg = "Please connect your wallet";
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    if (amount <= 0) {
      const errorMsg = "Amount must be greater than 0";
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const entryAmount = usdcToSmallestUnit(amount);

      // Check for mock payment mode
      const isMock = process.env.NEXT_PUBLIC_PAYMENT_MODE === "mock";
      
      if (isMock) {
        console.log(`🧪 MOCK MODE: Processing V3 payment: ${amount} USDC (no real funds will be charged)`);
      } else {
        console.log(`🔄 Processing V3 payment: ${amount} USDC (${entryAmount} smallest units)`);
      }

      const result = await processV3EntryPayment(
        connection,
        publicKey,
        signTransaction,
        entryAmount,
        isMock
      );

      if (result.success && result.transactionSignature) {
        console.log("✅ Payment successful!", result.transactionSignature);
        const successData = {
          signature: result.transactionSignature,
          explorerUrl: result.explorerUrl || "",
        };
        setSuccess(successData);
        onSuccess?.(successData.signature, successData.explorerUrl);
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
    <div className={`v3-payment-button space-y-4 ${className}`}>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Payment Amount (USDC)
        </label>
        <input
          type="number"
          min="1"
          step="0.1"
          value={amount}
          onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
          disabled={loading || !connected}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-900 bg-white"
          placeholder="Enter amount"
        />
        <p className="text-xs text-gray-500 mt-1">
          Minimum: 1 USDC
        </p>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">Payment Failed</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {success && (
        <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg">
          <ExternalLink className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium">Payment Successful!</p>
            <a
              href={success.explorerUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm underline hover:text-green-800 flex items-center gap-1"
            >
              View on Explorer
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}

      <button
        onClick={handlePayment}
        disabled={loading || !connected || amount <= 0}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium disabled:bg-gray-400 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Processing...
          </>
        ) : !connected ? (
          "Connect Wallet"
        ) : (
          `Pay ${amount} USDC`
        )}
      </button>

      {!connected && (
        <p className="text-sm text-gray-500 text-center">
          Connect your Solana wallet to proceed with payment
        </p>
      )}
    </div>
  );
}
