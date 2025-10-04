#!/usr/bin/env python3
"""
Script to get the backend authority public key
"""
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from src.ai_decision_service import ai_decision_service

def main():
    print("🔑 Backend Authority Public Key")
    print("=" * 50)
    
    # Get the public key from the AI decision service
    public_key_bytes = ai_decision_service.get_public_key_bytes()
    public_key_hex = public_key_bytes.hex()
    
    print(f"Public Key (hex): {public_key_hex}")
    print(f"Public Key (base58): {public_key_bytes}")
    print(f"Length: {len(public_key_bytes)} bytes")
    
    print("\n📋 Add this to your .env file:")
    print(f"BACKEND_AUTHORITY_PUBLIC_KEY={public_key_hex}")
    
    print("\n🔧 For Solana smart contract, you'll need the base58 format:")
    # Convert to base58 (you'll need base58 library for this)
    try:
        import base58
        public_key_base58 = base58.b58encode(public_key_bytes).decode()
        print(f"BACKEND_AUTHORITY_PUBLIC_KEY_BASE58={public_key_base58}")
    except ImportError:
        print("Install base58 library to get base58 format: pip install base58")
    
    print("\n✅ This public key corresponds to the private key in:")
    print("   ai_decision_key.pem")

if __name__ == "__main__":
    main()
