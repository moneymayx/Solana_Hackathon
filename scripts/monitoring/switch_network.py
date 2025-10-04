#!/usr/bin/env python3
"""
Network Switching Utility
Easily switch between devnet and mainnet configurations
"""
import os
import sys
from dotenv import load_dotenv

def switch_network(network):
    """Switch to the specified network"""
    if network not in ["devnet", "mainnet"]:
        print("❌ Invalid network. Use 'devnet' or 'mainnet'")
        return False
    
    # Load current .env
    load_dotenv()
    
    # Update SOLANA_NETWORK
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Clean up any malformed lines and update SOLANA_NETWORK
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith("SOLANA_NETWORK="):
                cleaned_lines.append(line.strip())
        
        # Add the new SOLANA_NETWORK setting
        cleaned_lines.append(f"SOLANA_NETWORK={network}")
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(cleaned_lines) + '\n')
        
        print(f"✅ Switched to {network.upper()}")
        print(f"   - RPC Endpoint: {os.getenv(f'SOLANA_RPC_{network.upper()}_ENDPOINT')}")
        return True
    else:
        print("❌ .env file not found")
        return False

def show_current_network():
    """Show current network configuration"""
    load_dotenv()
    from network_config import print_network_info
    print_network_info()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("🌐 Network Configuration Utility")
        print("=" * 40)
        print("Usage:")
        print("  python3 switch_network.py devnet    # Switch to devnet")
        print("  python3 switch_network.py mainnet   # Switch to mainnet")
        print("  python3 switch_network.py status    # Show current network")
        print()
        show_current_network()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_current_network()
    elif command in ["devnet", "mainnet"]:
        switch_network(command)
        print()
        show_current_network()
    else:
        print("❌ Invalid command. Use 'devnet', 'mainnet', or 'status'")

if __name__ == "__main__":
    main()
