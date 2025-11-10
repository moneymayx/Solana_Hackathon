"""
Kora SDK Service - Fee Abstraction via CLI

Kora is a Solana signing infrastructure that provides fee abstraction.
This service uses the Kora CLI to enable users to pay transaction fees
in USDC (or other tokens) instead of SOL.

Kora CLI Architecture:
- Kora CLI (`kora-cli`) is a command-line tool
- Commands: sign, sign-and-send, estimate-fee
- Takes base64-encoded transactions as input
- Provides fee abstraction (pays fees in configured tokens)

Documentation: https://launch.solana.com/docs/kora

Setup:
1. Install Kora CLI: cargo install kora-cli
2. Configure: Set KORA_PRIVATE_KEY or use --private-key flag
3. Optionally: Set KORA_RPC_URL for Solana RPC endpoint (default: http://127.0.0.1:8899)
"""
import logging
import subprocess
import json
import os
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class KoraService:
    """Service for Kora fee abstraction via CLI"""
    
    def __init__(self):
        """
        Initialize Kora service with CLI configuration
        
        Kora CLI is installed via: cargo install kora-cli
        The CLI tool provides commands for signing transactions with fee abstraction.
        
        Configuration:
        - KORA_PRIVATE_KEY: Base58-encoded private key for signing (env var or flag)
        - KORA_RPC_URL: Solana RPC endpoint (default: http://127.0.0.1:8899)
        - KORA_CONFIG: Path to kora.toml config file (optional)
        """
        self.kora_cli_path = os.getenv("KORA_CLI_PATH", "kora-cli")
        self.private_key = os.getenv("KORA_PRIVATE_KEY")  # Base58-encoded private key
        self.rpc_url = os.getenv("KORA_RPC_URL", "http://127.0.0.1:8899")
        self.config_path = os.getenv("KORA_CONFIG", "kora.toml")
        self.enabled = os.getenv("ENABLE_KORA_SDK", "false").lower() == "true"
        
        if not self.enabled:
            logger.info("🔧 Kora SDK is disabled (set ENABLE_KORA_SDK=true to enable)")
        else:
            logger.info(f"✅ Kora SDK enabled - using CLI: {self.kora_cli_path}")
            logger.info(f"   RPC URL: {self.rpc_url}")
            if not self.private_key:
                logger.warning("⚠️  KORA_PRIVATE_KEY not set - signing may fail")
    
    def is_enabled(self) -> bool:
        """Check if Kora service is enabled"""
        return self.enabled
    
    def _run_kora_command(
        self,
        command: str,
        transaction_base64: str,
        additional_args: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Run a Kora CLI command
        
        Args:
            command: CLI command (sign, sign-and-send, estimate-fee)
            transaction_base64: Base64-encoded transaction
            additional_args: Additional command-line arguments
            
        Returns:
            Dict with command result
        """
        if additional_args is None:
            additional_args = []
        
        # Build command
        cmd = [
            self.kora_cli_path,
            command,
            "--transaction", transaction_base64,
            "--rpc-url", self.rpc_url
        ]
        
        # Add private key if configured
        if self.private_key:
            cmd.extend(["--private-key", self.private_key])
        
        # Add config if exists
        if os.path.exists(self.config_path):
            cmd.extend(["--config", self.config_path])
        
        # Add additional arguments
        cmd.extend(additional_args)
        
        try:
            logger.debug(f"Running Kora CLI command: {' '.join(cmd[:4])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30.0,
                check=False
            )
            
            if result.returncode == 0:
                # Parse output (Kora CLI outputs JSON)
                try:
                    output_data = json.loads(result.stdout.strip())
                    return {
                        "success": True,
                        "result": output_data
                    }
                except json.JSONDecodeError:
                    # If not JSON, return as text
                    return {
                        "success": True,
                        "result": result.stdout.strip(),
                        "raw_output": result.stdout
                    }
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.error(f"Kora CLI error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "returncode": result.returncode
                }
        
        except subprocess.TimeoutExpired:
            logger.error("Kora CLI command timed out")
            return {
                "success": False,
                "error": "Command timed out"
            }
        except FileNotFoundError:
            logger.error(f"Kora CLI not found at: {self.kora_cli_path}")
            return {
                "success": False,
                "error": f"Kora CLI not found. Install with: cargo install kora-cli"
            }
        except Exception as e:
            logger.error(f"Error running Kora CLI: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def sign_transaction(
        self,
        transaction_base64: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign a transaction using Kora (with fee abstraction)
        
        Kora will sign the transaction and pay fees in the configured token (USDC, etc.).
        
        Args:
            transaction_base64: Base64-encoded transaction
            options: Optional signing options (not used by CLI, kept for compatibility)
            
        Returns:
            Dict with signed transaction
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Kora service is disabled"
            }
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_kora_command,
            "sign",
            transaction_base64
        )
        
        return result
    
    async def sign_and_send_transaction(
        self,
        transaction_base64: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign and send a transaction using Kora
        
        Kora will sign the transaction, pay fees, and send it to the network.
        
        Args:
            transaction_base64: Base64-encoded transaction
            options: Optional send options (not used by CLI, kept for compatibility)
            
        Returns:
            Dict with transaction signature
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Kora service is disabled"
            }
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_kora_command,
            "sign-and-send",
            transaction_base64
        )
        
        return result
    
    async def estimate_transaction_fee(
        self,
        transaction_base64: str,
        fee_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate transaction fee in specified token
        
        Args:
            transaction_base64: Base64-encoded transaction
            fee_token: Token to estimate fees in (USDC, SOL, etc.)
                      Note: Token selection may be configured in kora.toml
            
        Returns:
            Dict with fee estimate
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Kora service is disabled"
            }
        
        # Additional args for fee token (if CLI supports it)
        additional_args = []
        if fee_token:
            # Note: CLI may not support fee_token flag directly
            # This would need to be configured in kora.toml
            logger.info(f"Fee token requested: {fee_token} (configure in kora.toml)")
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_kora_command,
            "estimate-fee",
            transaction_base64,
            additional_args
        )
        
        return result
    
    async def get_config(self) -> Dict[str, Any]:
        """
        Get Kora configuration
        
        Note: CLI doesn't have a get-config command.
        This returns configured settings from environment.
        
        Returns:
            Dict with configuration
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Kora service is disabled"
            }
        
        return {
            "success": True,
            "result": {
                "cli_path": self.kora_cli_path,
                "rpc_url": self.rpc_url,
                "config_path": self.config_path,
                "private_key_configured": bool(self.private_key),
                "note": "Configuration via environment variables and kora.toml file"
            }
        }
    
    async def get_supported_tokens(self) -> Dict[str, Any]:
        """
        Get supported fee tokens
        
        Note: CLI doesn't expose this directly.
        Tokens are configured in kora.toml file.
        
        Returns:
            Dict with supported tokens info
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Kora service is disabled"
            }
        
        return {
            "success": True,
            "result": {
                "note": "Supported tokens are configured in kora.toml",
                "default_tokens": ["SOL", "USDC"],
                "configuration": "Check kora.toml file for configured fee tokens"
            }
        }


# Global instance
kora_service = KoraService()
