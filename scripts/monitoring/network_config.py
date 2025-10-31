#!/usr/bin/env python3
"""
Network Configuration Utility
Manages Solana network configuration for different environments
"""
import os
from dotenv import load_dotenv

load_dotenv()

class NetworkConfig:
    """Manages Solana network configuration"""
    
    def __init__(self):
        # Reload .env file to get latest changes
        load_dotenv(override=True)
        self.network = os.getenv("SOLANA_NETWORK", "devnet").lower()
        self.devnet_endpoint = os.getenv("SOLANA_RPC_DEVNET_ENDPOINT", "https://api.devnet.solana.com")
        self.mainnet_endpoint = os.getenv("SOLANA_RPC_MAINNET_ENDPOINT", "https://api.mainnet-beta.solana.com")
        
    def get_rpc_endpoint(self):
        """Get the appropriate RPC endpoint based on network setting"""
        if self.network == "mainnet":
            return self.mainnet_endpoint
        else:
            return self.devnet_endpoint
    
    def get_usdc_mint(self):
        """Get the appropriate USDC mint address based on network"""
        if self.network == "mainnet":
            return "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Mainnet USDC
        else:
            return "JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh"  # Test token with mint authority
    
    def get_program_id(self):
        """Get the appropriate program ID based on network"""
        if self.network == "mainnet":
            return os.getenv("LOTTERY_PROGRAM_ID_MAINNET", "4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK")
        else:
            return os.getenv("LOTTERY_PROGRAM_ID_DEVNET", "4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK")
    
    def is_devnet(self):
        """Check if currently using devnet"""
        return self.network == "devnet"
    
    def is_mainnet(self):
        """Check if currently using mainnet"""
        return self.network == "mainnet"
    
    def get_network_info(self):
        """Get comprehensive network information"""
        return {
            "network": self.network,
            "rpc_endpoint": self.get_rpc_endpoint(),
            "usdc_mint": self.get_usdc_mint(),
            "program_id": self.get_program_id(),
            "is_devnet": self.is_devnet(),
            "is_mainnet": self.is_mainnet()
        }

def get_network_config():
    """Get the current network configuration"""
    return NetworkConfig()

def print_network_info():
    """Print current network configuration"""
    config = get_network_config()
    info = config.get_network_info()
    
    print("🌐 Solana Network Configuration")
    print("=" * 40)
    print(f"Network: {info['network'].upper()}")
    print(f"RPC Endpoint: {info['rpc_endpoint']}")
    print(f"USDC Mint: {info['usdc_mint']}")
    print(f"Program ID: {info['program_id']}")
    print(f"Environment: {'Development' if info['is_devnet'] else 'Production'}")

if __name__ == "__main__":
    print_network_info()
