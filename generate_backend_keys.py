#!/usr/bin/env python3
"""
Script to generate a new backend authority key pair
"""
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base58

def generate_backend_keys():
    """Generate a new Ed25519 key pair for backend authority"""
    
    print("🔑 Generating Backend Authority Key Pair")
    print("=" * 50)
    
    # Generate private key
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Get public key bytes
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    # Convert to hex and base58
    public_key_hex = public_key_bytes.hex()
    public_key_base58 = base58.b58encode(public_key_bytes).decode()
    
    # Save private key
    private_key_path = "backend_authority_key.pem"
    with open(private_key_path, "wb") as key_file:
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_file.write(private_key_pem)
    
    # Save public key
    public_key_path = "backend_authority_key_public.pem"
    with open(public_key_path, "wb") as key_file:
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        key_file.write(public_key_pem)
    
    print(f"✅ Keys generated successfully!")
    print(f"   Private key: {private_key_path}")
    print(f"   Public key: {public_key_path}")
    print(f"   Public key (hex): {public_key_hex}")
    print(f"   Public key (base58): {public_key_base58}")
    
    print("\n📋 Add to your .env file:")
    print(f"BACKEND_AUTHORITY_PUBLIC_KEY={public_key_hex}")
    print(f"BACKEND_AUTHORITY_PRIVATE_KEY_PATH={private_key_path}")
    
    print("\n⚠️  IMPORTANT:")
    print("   - Keep the private key file secure!")
    print("   - Never commit private keys to version control")
    print("   - Store private key in a secure location")
    
    return public_key_hex, public_key_base58

if __name__ == "__main__":
    generate_backend_keys()
