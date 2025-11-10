"""
SDK Integration Services - Parallel Development

This module contains SDK integration services for:
- Kora: Fee abstraction and custom signing RPCs
- Attestations: Permissionless verifiable credentials (KYC replacement)
- Solana Pay: Standardized payments framework

These services are being developed in parallel and tested independently
before integration into production code.
"""

# Feature flags - set via environment variables
import os

# Enable/disable SDK features
ENABLE_KORA = os.getenv("ENABLE_KORA_SDK", "false").lower() == "true"
ENABLE_ATTESTATIONS = os.getenv("ENABLE_ATTESTATIONS_SDK", "false").lower() == "true"
ENABLE_SOLANA_PAY = os.getenv("ENABLE_SOLANA_PAY_SDK", "false").lower() == "true"

__all__ = [
    "ENABLE_KORA",
    "ENABLE_ATTESTATIONS", 
    "ENABLE_SOLANA_PAY",
]

