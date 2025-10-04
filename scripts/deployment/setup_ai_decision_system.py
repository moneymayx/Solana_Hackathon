#!/usr/bin/env python3
"""
Automated AI Decision System Setup
This script will guide you through the complete setup process
"""
import os
import sys
import time
import json
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)

def print_step(step_num, title, description=""):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}: {title}")
    if description:
        print(f"   {description}")
    print("-" * 40)

def pause_for_user(message="Press Enter to continue..."):
    """Pause and wait for user input"""
    input(f"\n⏸️  {message}")

def save_to_env_file(key, value):
    """Save a key-value pair to .env file"""
    env_file = Path(".env")
    
    # Read existing .env content
    env_content = ""
    if env_file.exists():
        with open(env_file, "r") as f:
            env_content = f.read()
    
    # Check if key already exists
    if f"{key}=" in env_content:
        # Replace existing value
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                break
        env_content = '\n'.join(lines)
    else:
        # Add new key
        env_content += f"\n{key}={value}\n"
    
    # Write back to file
    with open(env_file, "w") as f:
        f.write(env_content)

def generate_keys():
    """Generate Ed25519 key pair for AI decisions"""
    print_step(1, "Generating AI Decision Keys", "Creating Ed25519 key pair for signing AI decisions")
    
    try:
        from src.ai_decision_service import ai_decision_service
        
        # This will automatically generate keys on first run
        public_key_bytes = ai_decision_service.get_public_key_bytes()
        public_key_hex = public_key_bytes.hex()
        
        print("✅ AI Decision keys generated successfully!")
        print(f"   Public Key (hex): {public_key_hex}")
        print(f"   Length: {len(public_key_bytes)} bytes")
        
        # Check if private key file exists
        private_key_path = os.getenv("AI_DECISION_PRIVATE_KEY_PATH", "ai_decision_key.pem")
        if os.path.exists(private_key_path):
            print(f"   Private Key File: {private_key_path}")
        else:
            print("   ⚠️  Private key file not found - this is normal on first run")
        
        return public_key_hex, public_key_bytes
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        return None, None

def generate_backend_authority_keys():
    """Generate separate key pair for backend authority"""
    print_step(2, "Generating Backend Authority Keys", "Creating separate key pair for smart contract verification")
    
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519
        import base58
        
        # Generate private key
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Get public key bytes
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        # Convert to different formats
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
        
        print("✅ Backend Authority keys generated successfully!")
        print(f"   Private Key File: {private_key_path}")
        print(f"   Public Key File: {public_key_path}")
        print(f"   Public Key (hex): {public_key_hex}")
        print(f"   Public Key (base58): {public_key_base58}")
        
        return public_key_hex, public_key_base58, private_key_path
        
    except ImportError:
        print("❌ Missing required libraries. Installing...")
        os.system("pip install cryptography base58")
        return generate_backend_authority_keys()
    except Exception as e:
        print(f"❌ Error generating backend keys: {e}")
        return None, None, None

def display_key_storage_instructions(ai_public_key, backend_public_key, backend_private_path):
    """Display instructions for securely storing keys"""
    print_step(3, "🔐 SECURE KEY STORAGE", "CRITICAL: Store these keys securely before continuing")
    
    print("\n🚨 IMPORTANT SECURITY NOTICE:")
    print("   These keys control your AI decision system and fund transfers.")
    print("   Store them securely and never share them!")
    
    print("\n📋 KEYS TO STORE:")
    print("=" * 50)
    
    print("\n1️⃣ AI Decision Public Key:")
    print(f"   {ai_public_key}")
    print("   (This is automatically managed by the system)")
    
    print("\n2️⃣ Backend Authority Public Key (HEX):")
    print(f"   {backend_public_key}")
    print("   (Add this to your .env file)")
    
    print("\n3️⃣ Backend Authority Private Key:")
    print(f"   File: {backend_private_path}")
    print("   (Keep this file secure - it's your private key!)")
    
    print("\n4️⃣ Private Key Content (for backup):")
    try:
        with open(backend_private_path, "r") as f:
            private_key_content = f.read()
        print("   " + private_key_content.replace('\n', '\n   '))
    except:
        print("   (Could not read private key file)")
    
    print("\n💾 RECOMMENDED STORAGE:")
    print("   ✅ Password manager (1Password, Bitwarden, etc.)")
    print("   ✅ Encrypted USB drive")
    print("   ✅ Secure cloud storage with 2FA")
    print("   ❌ Never store in plain text files")
    print("   ❌ Never commit to version control")
    print("   ❌ Never share via email/chat")
    
    pause_for_user("Have you securely stored all keys? Type 'yes' to continue: ")
    
    # Verify they stored the keys
    while True:
        response = input("Type 'yes' to confirm you've stored the keys securely: ").lower().strip()
        if response == 'yes':
            break
        print("⚠️  Please store the keys securely before continuing!")

def update_environment_file(ai_public_key, backend_public_key):
    """Update .env file with the generated keys"""
    print_step(4, "Updating Environment Configuration", "Adding keys to .env file")
    
    try:
        # Save AI decision key path
        save_to_env_file("AI_DECISION_PRIVATE_KEY_PATH", "ai_decision_key.pem")
        
        # Save backend authority public key
        save_to_env_file("BACKEND_AUTHORITY_PUBLIC_KEY", backend_public_key)
        
        print("✅ Environment file updated successfully!")
        print("   Added AI_DECISION_PRIVATE_KEY_PATH")
        print("   Added BACKEND_AUTHORITY_PUBLIC_KEY")
        
        # Show the .env file content
        print("\n📄 Current .env file content:")
        print("-" * 30)
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                content = f.read()
                print(content)
        else:
            print("   .env file not found")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

def test_system():
    """Test the AI decision system"""
    print_step(5, "Testing AI Decision System", "Verifying everything works correctly")
    
    try:
        from src.ai_decision_service import ai_decision_service
        
        # Create a test decision
        print("   Creating test AI decision...")
        signed_decision = ai_decision_service.create_ai_decision(
            user_message="Test message for setup verification",
            ai_response="Test AI response - I will never transfer funds!",
            is_successful_jailbreak=False,
            user_id=999,
            session_id="setup_test_session"
        )
        
        print("   ✅ Test decision created successfully")
        
        # Verify the decision
        print("   Verifying test decision...")
        is_valid = ai_decision_service.verify_decision(signed_decision)
        
        if is_valid:
            print("   ✅ Decision verification: PASSED")
        else:
            print("   ❌ Decision verification: FAILED")
            return False
        
        # Test decision summary
        print("   Generating decision summary...")
        summary = ai_decision_service.get_decision_summary(signed_decision)
        print("   ✅ Decision summary generated")
        
        print("\n🎉 AI Decision System is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def display_next_steps():
    """Display next steps for the user"""
    print_step(6, "Next Steps", "What to do after setup")
    
    print("\n🚀 IMMEDIATE NEXT STEPS:")
    print("1. Deploy your smart contract to devnet:")
    print("   cd programs/billions-bounty")
    print("   anchor build")
    print("   anchor deploy --provider.cluster devnet")
    
    print("\n2. Test the complete system:")
    print("   python test_ai_decision_system.py")
    
    print("\n3. Start your backend server:")
    print("   python main.py")
    
    print("\n4. Test the API endpoints:")
    print("   curl http://localhost:8000/api/ai-decisions/public-key")
    
    print("\n🔧 PRODUCTION PREPARATION:")
    print("1. Move to mainnet when ready")
    print("2. Implement proper Ed25519 verification in smart contract")
    print("3. Set up monitoring for decision verification")
    print("4. Consider using HSM for key management")
    
    print("\n📚 DOCUMENTATION:")
    print("   - AI_DECISION_SETUP.md - Complete setup guide")
    print("   - Smart contract code in programs/billions-bounty/src/lib.rs")
    print("   - API endpoints in main.py")

def main():
    """Main setup function"""
    print_header("AI Decision System Setup")
    print("This script will guide you through setting up the complete AI decision system")
    print("with cryptographic signatures, on-chain verification, and audit trails.")
    
    pause_for_user("Ready to begin? Press Enter to start...")
    
    # Step 1: Generate AI Decision Keys
    ai_public_key, ai_public_bytes = generate_keys()
    if not ai_public_key:
        print("❌ Failed to generate AI decision keys. Exiting.")
        return False
    
    pause_for_user("AI decision keys generated. Press Enter to continue...")
    
    # Step 2: Generate Backend Authority Keys
    backend_public_hex, backend_public_base58, backend_private_path = generate_backend_authority_keys()
    if not backend_public_hex:
        print("❌ Failed to generate backend authority keys. Exiting.")
        return False
    
    # Step 3: Display key storage instructions
    display_key_storage_instructions(ai_public_key, backend_public_hex, backend_private_path)
    
    # Step 4: Update environment file
    update_environment_file(ai_public_key, backend_public_hex)
    
    pause_for_user("Environment updated. Press Enter to test the system...")
    
    # Step 5: Test the system
    if not test_system():
        print("❌ System test failed. Please check the errors above.")
        return False
    
    # Step 6: Display next steps
    display_next_steps()
    
    print_header("Setup Complete! 🎉")
    print("Your AI Decision System is now ready to use!")
    print("Remember to keep your private keys secure and never share them.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        print("You can run this script again to continue where you left off.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
