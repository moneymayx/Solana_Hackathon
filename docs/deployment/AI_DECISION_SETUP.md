# AI Decision System Setup Guide

## 🔧 **Environment Variables**

Add these to your `.env` file:

```bash
# AI Decision Service Configuration
AI_DECISION_PRIVATE_KEY_PATH=ai_decision_key.pem
BACKEND_AUTHORITY_PUBLIC_KEY=your_backend_public_key_here

# Existing configuration...
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
LOTTERY_PROGRAM_ID=4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK
USDC_MINT_ADDRESS=Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr
```

## 🚀 **Setup Instructions**

### 1. **Install Dependencies**
```bash
pip install cryptography
```

### 2. **Generate AI Decision Keys**
The system will automatically generate Ed25519 key pairs on first run:
- `ai_decision_key.pem` - Private key (keep secure!)
- `ai_decision_key_public.pem` - Public key (can be shared)

### 3. **Set Backend Authority**
Update `BACKEND_AUTHORITY_PUBLIC_KEY` with your backend's public key for smart contract verification.

## 🔍 **Testing the System**

### 1. **Test AI Decision Creation**
```python
from src.ai_decision_service import ai_decision_service

# Create a test decision
signed_decision = ai_decision_service.create_ai_decision(
    user_message="Hello AI",
    ai_response="Hello! I will never transfer funds.",
    is_successful_jailbreak=False,
    user_id=1,
    session_id="test_session"
)

print(ai_decision_service.get_decision_summary(signed_decision))
```

### 2. **Test Decision Verification**
```python
# Verify the decision
is_valid = ai_decision_service.verify_decision(signed_decision)
print(f"Decision is valid: {is_valid}")
```

### 3. **Test API Endpoints**
```bash
# Get public key
curl http://localhost:8000/api/ai-decisions/public-key

# Verify a decision
curl -X POST http://localhost:8000/api/ai-decisions/verify \
  -H "Content-Type: application/json" \
  -d '{"signed_decision": {...}}'

# Get audit trail
curl http://localhost:8000/api/ai-decisions/audit-trail
```

## 🔐 **Security Features**

### **Cryptographic Signatures**
- All AI decisions are signed with Ed25519
- Signatures prove decisions came from your backend
- Prevents tampering with AI responses

### **On-Chain Verification**
- Smart contract verifies decision hashes
- Prevents replay attacks with nonces
- Immutable audit trail on blockchain

### **Database Audit Trail**
- All decisions logged to database
- Includes full decision data and signatures
- Queryable via API endpoints

## 🎯 **How It Works**

1. **User sends message** → Backend processes with AI
2. **AI makes decision** → Backend creates signed decision
3. **Decision sent to smart contract** → On-chain verification
4. **If successful jailbreak** → Funds transferred automatically
5. **All decisions logged** → Complete audit trail

## 🚨 **Important Notes**

- **Keep private key secure**: Never commit `ai_decision_key.pem` to version control
- **Backup keys**: Store private key in secure location
- **Monitor signatures**: Watch for any invalid signatures
- **Test thoroughly**: Verify all decision flows work correctly

## 🔧 **Troubleshooting**

### **Key Generation Issues**
- Ensure write permissions in project directory
- Check Python cryptography installation

### **Signature Verification Fails**
- Verify decision data hasn't been modified
- Check timestamp and nonce values
- Ensure correct public key is being used

### **Smart Contract Integration**
- Verify program ID is correct
- Check RPC endpoint connectivity
- Ensure sufficient SOL for transaction fees
