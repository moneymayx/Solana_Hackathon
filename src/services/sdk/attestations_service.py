"""
Attestations SDK Service - Solana Attestations Service (SAS) Integration

Solana Attestations is an on-chain program for associating offchain data with
onchain accounts. It uses a framework of Credentials, Schemas, and Attestations
to create verifiable claims about accounts.

Architecture:
- Credentials: Authorities that can issue attestations
- Schemas: Define data structures for attestations (KYC, geographic, etc.)
- Attestations: Verifiable claims stored on-chain

This service queries the SAS program on-chain to verify attestations without
requiring expensive third-party KYC services.

Documentation: https://launch.solana.com/docs/attestations
Library: sas-lib (JavaScript/TypeScript) - For Python, we query program directly
"""
import logging
from typing import Optional, Dict, Any, List
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
import httpx
import os
import base64

logger = logging.getLogger(__name__)


class AttestationsService:
    """
    Service for verifying wallet attestations via Solana Attestations Service
    
    Since there's no official Python SDK for SAS (only sas-lib for JS/TS),
    this service queries the on-chain program directly via RPC.
    """
    
    def __init__(self):
        """Initialize Attestations service with SAS program configuration"""
        self.rpc_endpoint = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.devnet.solana.com")
        
        # SAS Program ID (Solana Attestations Service)
        # This is the on-chain program that manages attestations
        # 
        # ⚠️  CRITICAL: You must find the actual SAS program ID
        # The program ID may be different for devnet vs mainnet
        #
        # To find the program ID:
        # 1. Check official docs: https://launch.solana.com/docs/attestations
        # 2. Search Solana Explorer for "attestations" or "SAS"
        # 3. Check sas-lib examples on GitHub
        # 4. Use: python scripts/sdk/find_attestations_program.py
        #
        # Once found, set in .env:
        # ATTESTATIONS_PROGRAM_ID_DEVNET=<devnet_id>
        # ATTESTATIONS_PROGRAM_ID_MAINNET=<mainnet_id>
        #
        network = os.getenv("SOLANA_NETWORK", "devnet").lower()
        program_id_str = os.getenv(
            f"ATTESTATIONS_PROGRAM_ID_{network.upper()}",
            os.getenv(
                "ATTESTATIONS_PROGRAM_ID",
                # Placeholder - needs to be updated with actual SAS program ID
                "SASProgram111111111111111111111111111111"
            )
        )
        
        try:
            self.program_id = Pubkey.from_string(program_id_str)
        except Exception as e:
            logger.warning(f"Invalid Attestations program ID: {program_id_str}. Using placeholder.")
            # Fallback placeholder program ID
            self.program_id = Pubkey.from_string("11111111111111111111111111111111")
        
        self.enabled = os.getenv("ENABLE_ATTESTATIONS_SDK", "false").lower() == "true"
        
        if not self.enabled:
            logger.info("🔧 Attestations SDK is disabled (set ENABLE_ATTESTATIONS_SDK=true to enable)")
        else:
            logger.info(f"✅ Attestations SDK enabled - SAS Program: {self.program_id}")
    
    def is_enabled(self) -> bool:
        """Check if Attestations service is enabled"""
        return self.enabled
    
    def _derive_attestation_pda(
        self,
        wallet: Pubkey,
        credential: Optional[Pubkey] = None,
        schema: Optional[Pubkey] = None
    ) -> Pubkey:
        """
        Derive Program Derived Address (PDA) for an attestation
        
        SAS uses PDAs to store attestations on-chain.
        Structure: [attestation, wallet, credential?, schema?]
        
        Args:
            wallet: Wallet address being attested
            credential: Credential authority (optional, can query all)
            schema: Schema type (optional, can query all)
            
        Returns:
            PDA for the attestation account
        """
        seeds = [b"attestation", bytes(wallet)]
        
        if credential:
            seeds.append(bytes(credential))
        if schema:
            seeds.append(bytes(schema))
        
        pda, _ = Pubkey.find_program_address(seeds, self.program_id)
        return pda
    
    def _parse_attestation_account_data(self, base64_data: str) -> Dict[str, Any]:
        """
        Parse attestation account data from base64
        
        ⚠️  NOTE: Account structure depends on SAS program implementation
        This is a placeholder parser - actual structure needs to be determined
        by examining real attestation accounts on-chain.
        
        Typical structure may include:
        - Discriminator (8 bytes)
        - Wallet address (32 bytes)
        - Credential authority (32 bytes, optional)
        - Schema pubkey (32 bytes, optional)
        - Timestamp (8 bytes, optional)
        - Data fields (variable, depends on schema)
        
        Args:
            base64_data: Base64-encoded account data
            
        Returns:
            Dict with parsed fields (structure TBD based on actual accounts)
        """
        try:
            import base64
            account_bytes = base64.b64decode(base64_data)
            
            # Placeholder parsing - structure needs to be verified
            # This will be updated once we can examine actual attestation accounts
            return {
                "raw_data_length": len(account_bytes),
                "raw_data_preview": account_bytes[:64].hex() if len(account_bytes) >= 64 else account_bytes.hex(),
                "note": "Account structure needs to be verified by examining real attestation accounts. "
                       "Use Solana Explorer or RPC to query known attestation accounts and analyze their structure.",
                "next_steps": [
                    "Find a wallet with a known attestation",
                    "Query the account data using RPC",
                    "Analyze byte structure",
                    "Document field positions and types",
                    "Update this parser with correct structure"
            ]
            }
        except Exception as e:
            logger.warning(f"Error parsing attestation account data: {e}")
            return {
                "error": str(e),
                "raw_data": base64_data[:100] if len(base64_data) > 100 else base64_data
            }
    
    async def _query_attestation_account(
        self,
        account_pubkey: Pubkey
    ) -> Optional[Dict[str, Any]]:
        """Query an attestation account on-chain"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.rpc_endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getAccountInfo",
                        "params": [
                            str(account_pubkey),
                            {"encoding": "base64"}
                        ]
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result", {})
                    if result.get("value"):
                        account_data = result["value"].get("data", [""])[0]
                        # Decode base64 account data
                        return {
                            "account": str(account_pubkey),
                            "data": account_data,
                            "lamports": result["value"].get("lamports", 0),
                            "owner": result["value"].get("owner")
                        }
                return None
        except Exception as e:
            logger.error(f"Error querying attestation account: {e}")
            return None
    
    async def verify_kyc_attestation(
        self,
        wallet_address: str,
        credential_authority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify if a wallet has valid KYC attestation
        
        Queries the SAS program on-chain to check for KYC attestations.
        
        Args:
            wallet_address: Wallet address to check
            credential_authority: Optional specific credential authority to check
            
        Returns:
            Dict with KYC verification status and details
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Attestations service is disabled"
            }
        
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            credential_pubkey = None
            
            if credential_authority:
                credential_pubkey = Pubkey.from_string(credential_authority)
            
            # Derive PDA for attestation account
            attestation_pda = self._derive_attestation_pda(
                wallet=wallet_pubkey,
                credential=credential_pubkey
            )
            
            # Query on-chain account
            account_data = await self._query_attestation_account(attestation_pda)
            
            if account_data and account_data.get("data"):
                # Account exists - attestation found
                # Parse account data to extract KYC details
                parsed_data = self._parse_attestation_account_data(account_data.get("data"))
                
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "kyc_verified": True,
                    "attestation_account": str(attestation_pda),
                    "account_data": account_data,
                    "parsed_data": parsed_data,
                    "provider": "solana_attestations"
                }
            else:
                # No attestation account found
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "kyc_verified": False,
                    "message": "No KYC attestation found for this wallet",
                    "attestation_account": str(attestation_pda)
                }
        
        except Exception as e:
            logger.error(f"Error verifying KYC attestation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_attestations_by_schema(
        self,
        wallet_address: str,
        schema_pubkey: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all attestations for a wallet, optionally filtered by schema
        
        Args:
            wallet_address: Wallet address to query
            schema_pubkey: Optional schema to filter by (e.g., KYC schema, geographic schema)
            
        Returns:
            Dict with all matching attestations
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Attestations service is disabled"
            }
        
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            schema = None
            
            if schema_pubkey:
                schema = Pubkey.from_string(schema_pubkey)
            
            # Derive PDA for attestation
            attestation_pda = self._derive_attestation_pda(
                wallet=wallet_pubkey,
                schema=schema
            )
            
            # Query account
            account_data = await self._query_attestation_account(attestation_pda)
            
            attestations = []
            if account_data:
                attestations.append({
                    "account": attestation_pda,
                    "data": account_data
                })
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "attestations": attestations,
                "count": len(attestations)
            }
        
        except Exception as e:
            logger.error(f"Error getting attestations: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_geographic_attestation(
        self,
        wallet_address: str,
        allowed_countries: Optional[List[str]] = None,
        geographic_schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify if a wallet has geographic attestation matching allowed countries
        
        Queries SAS program for geographic attestation schema.
        
        Args:
            wallet_address: Wallet address to check
            allowed_countries: List of allowed country codes (e.g., ["US", "CA"])
            geographic_schema: Optional specific geographic schema to check
            
        Returns:
            Dict with geographic verification status
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Attestations service is disabled"
            }
        
        try:
            # Query attestations with geographic schema filter
            result = await self.get_attestations_by_schema(
                wallet_address=wallet_address,
                schema_pubkey=geographic_schema
            )
            
            if result.get("success") and result.get("attestations"):
                # TODO: Parse account data to extract country information
                # Check if country matches allowed_countries
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "country_verified": True,  # Placeholder - needs parsing
                    "country": None,  # Extract from account data
                    "allowed_countries": allowed_countries
                }
            else:
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "country_verified": False,
                    "message": "No geographic attestation found",
                    "allowed_countries": allowed_countries
                }
        
        except Exception as e:
            logger.error(f"Error verifying geographic attestation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_accreditation(
        self,
        wallet_address: str,
        accreditation_type: str = "investor",
        accreditation_schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify if a wallet has specific accreditation (e.g., accredited investor)
        
        Queries SAS program for accreditation attestation.
        
        Args:
            wallet_address: Wallet address to check
            accreditation_type: Type of accreditation to verify
            accreditation_schema: Optional specific accreditation schema to check
            
        Returns:
            Dict with accreditation verification status
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Attestations service is disabled"
            }
        
        try:
            # Query attestations with accreditation schema filter
            result = await self.get_attestations_by_schema(
                wallet_address=wallet_address,
                schema_pubkey=accreditation_schema
            )
            
            if result.get("success") and result.get("attestations"):
                # TODO: Parse account data to verify accreditation type
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "accreditation_verified": True,  # Placeholder
                    "accreditation_type": accreditation_type
                }
            else:
                return {
                    "success": True,
                    "wallet_address": wallet_address,
                    "accreditation_verified": False,
                    "message": f"No {accreditation_type} accreditation found",
                    "accreditation_type": accreditation_type
                }
        
        except Exception as e:
            logger.error(f"Error verifying accreditation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_all_attestations(
        self,
        wallet_address: str
    ) -> Dict[str, Any]:
        """
        Get all attestations for a wallet address
        
        Args:
            wallet_address: Wallet address to query
            
        Returns:
            Dict with all attestation types and their statuses
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Attestations service is disabled"
            }
        
        try:
            # Query all attestation types for this wallet
            kyc_result = await self.verify_kyc_attestation(wallet_address)
            geo_result = await self.verify_geographic_attestation(wallet_address)
            acc_result = await self.verify_accreditation(wallet_address)
            
            return {
                "success": True,
                "wallet_address": wallet_address,
                "attestations": {
                    "kyc": kyc_result,
                    "geographic": geo_result,
                    "accreditation": acc_result
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting all attestations: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
attestations_service = AttestationsService()

