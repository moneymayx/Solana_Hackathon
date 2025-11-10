/**
 * Payment Method Selector Component
 * 
 * Wraps V2 and V3 payment components with feature flag logic
 * This is what you use instead of directly importing V2PaymentButton or V3PaymentButton
 */
"use client";

import { useState } from "react";
import V2PaymentButton from "@/components/V2PaymentButton";
import V3PaymentButton from "@/components/V3PaymentButton";

interface PaymentMethodSelectorProps {
  bountyId?: number;
  defaultAmount?: number;
  onSuccess?: (signature: string, explorerUrl: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

export default function PaymentMethodSelector({
  bountyId = 1,
  defaultAmount = 10,
  onSuccess,
  onError,
  className = "",
}: PaymentMethodSelectorProps) {
  // Feature flag check - this is how you conditionally use V3
  const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";

  const handleSuccess = (signature: string, explorerUrl: string) => {
    console.log(USE_V3 ? "V3" : "V2", "payment successful:", signature);
    onSuccess?.(signature, explorerUrl);
  };

  const handleError = (error: string) => {
    console.error(USE_V3 ? "V3" : "V2", "payment error:", error);
    onError?.(error);
  };

  // Conditional rendering based on feature flag
  // This is the integration - the flag determines which component renders
  if (USE_V3) {
    return (
      <div className={className}>
        <div className="mb-2 text-xs text-blue-600 font-medium">🔒 Using V3 (Secure)</div>
        <V3PaymentButton
          defaultAmount={defaultAmount}
          onSuccess={handleSuccess}
          onError={handleError}
        />
      </div>
    );
  } else {
    return (
      <div className={className}>
        <V2PaymentButton
          bountyId={bountyId}
          defaultAmount={defaultAmount}
          onSuccess={handleSuccess}
          onError={handleError}
        />
      </div>
    );
  }
}

