# 🌐 Network Configuration Guide

## Overview

Your Billions Bounty platform now supports both **Devnet** and **Mainnet** configurations with automatic network detection and switching capabilities.

## 🔧 Environment Variables

Add these to your `.env` file:

```bash
# Network Selection
SOLANA_NETWORK=devnet  # or "mainnet"

# RPC Endpoints
SOLANA_RPC_DEVNET_ENDPOINT=https://api.devnet.solana.com
SOLANA_RPC_MAINNET_ENDPOINT=https://api.mainnet-beta.solana.com

# Program IDs (optional - defaults provided)
LOTTERY_PROGRAM_ID_DEVNET=4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK
LOTTERY_PROGRAM_ID_MAINNET=4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK
```

## 🚀 Quick Start

### Switch Networks
```bash
# Switch to devnet
python3 switch_network.py devnet

# Switch to mainnet  
python3 switch_network.py mainnet

# Check current network
python3 switch_network.py status
```

### Check Network Configuration
```bash
python3 network_config.py
```

## 📋 Network Details

### Devnet (Development)
- **RPC Endpoint**: `https://api.devnet.solana.com`
- **USDC Mint**: `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh`
- **Program ID**: `4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK`
- **Purpose**: Testing and development
- **SOL**: Free from faucet
- **Tokens**: Test tokens only

### Mainnet (Production)
- **RPC Endpoint**: `https://api.mainnet-beta.solana.com`
- **USDC Mint**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **Program ID**: `4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK`
- **Purpose**: Production use
- **SOL**: Real SOL required
- **Tokens**: Real USDC/USDT

## 🔄 Automatic Configuration

All services automatically detect the network setting and configure themselves:

### Services Updated
- ✅ **SmartContractService** - Uses correct RPC and USDC mint
- ✅ **SolanaService** - Uses correct RPC endpoint
- ✅ **WalletConnectService** - Uses correct RPC endpoint
- ✅ **AIDecisionIntegration** - Uses correct network settings
- ✅ **Test Scripts** - Show current network configuration

### Configuration Flow
1. **Environment Detection**: Reads `SOLANA_NETWORK` from `.env`
2. **RPC Selection**: Chooses appropriate RPC endpoint
3. **Token Selection**: Selects correct USDC mint address
4. **Program ID**: Uses network-specific program ID
5. **Service Initialization**: All services use correct settings

## 🧪 Testing

### Test Current Configuration
```bash
# Test with current network settings
python3 test_ai_decision_deployment.py

# Test with specific network
SOLANA_NETWORK=devnet python3 test_ai_decision_deployment.py
SOLANA_NETWORK=mainnet python3 test_ai_decision_deployment.py
```

### Network-Specific Tests
```bash
# Devnet tests
python3 switch_network.py devnet
python3 test_ai_decision_deployment.py

# Mainnet tests (requires real SOL)
python3 switch_network.py mainnet
python3 test_ai_decision_deployment.py
```

## 🔐 Security Considerations

### Devnet
- ✅ Safe for testing
- ✅ Free SOL from faucet
- ✅ No real money at risk
- ✅ Full functionality testing

### Mainnet
- ⚠️ Real money involved
- ⚠️ Requires real SOL for transactions
- ⚠️ Permanent on-chain records
- ⚠️ Production environment

## 📊 Network Comparison

| Feature | Devnet | Mainnet |
|---------|--------|---------|
| **RPC Endpoint** | `api.devnet.solana.com` | `api.mainnet-beta.solana.com` |
| **USDC Mint** | `JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh` | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| **SOL Cost** | Free (faucet) | Real SOL required |
| **Transaction Cost** | Free | Real fees |
| **Data Persistence** | Temporary | Permanent |
| **Use Case** | Development/Testing | Production |

## 🛠️ Development Workflow

### 1. Development Phase
```bash
# Start with devnet
python3 switch_network.py devnet

# Develop and test
python3 main.py
python3 test_ai_decision_deployment.py
```

### 2. Production Deployment
```bash
# Switch to mainnet
python3 switch_network.py mainnet

# Deploy to production
python3 main.py
```

### 3. Monitoring
```bash
# Check current network
python3 switch_network.py status

# Monitor network-specific metrics
python3 network_config.py
```

## 🔧 Troubleshooting

### Common Issues

1. **Wrong Network**: Check `SOLANA_NETWORK` in `.env`
2. **RPC Errors**: Verify RPC endpoint is correct
3. **Token Errors**: Ensure correct USDC mint for network
4. **Program Not Found**: Check program ID matches network

### Debug Commands
```bash
# Check environment variables
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Network:', os.getenv('SOLANA_NETWORK')); print('Devnet RPC:', os.getenv('SOLANA_RPC_DEVNET_ENDPOINT')); print('Mainnet RPC:', os.getenv('SOLANA_RPC_MAINNET_ENDPOINT'))"

# Test network configuration
python3 network_config.py

# Test service initialization
python3 -c "from src.smart_contract_service import SmartContractService; service = SmartContractService(); print(f'RPC: {service.rpc_endpoint}'); print(f'USDC: {service.usdc_mint}')"
```

## 📝 Migration Notes

### From Old Configuration
If you were using the old `SOLANA_RPC_ENDPOINT` variable:

1. **Add new variables** to `.env`:
   ```bash
   SOLANA_NETWORK=devnet
   SOLANA_RPC_DEVNET_ENDPOINT=https://api.devnet.solana.com
   SOLANA_RPC_MAINNET_ENDPOINT=https://api.mainnet-beta.solana.com
   ```

2. **Remove old variable**:
   ```bash
   # Remove this line from .env
   # SOLANA_RPC_ENDPOINT=...
   ```

3. **Test configuration**:
   ```bash
   python3 switch_network.py status
   ```

## 🎯 Best Practices

1. **Always test on devnet first**
2. **Use `switch_network.py` for network changes**
3. **Check network status before deployment**
4. **Verify RPC endpoints are accessible**
5. **Test with small amounts on mainnet first**

---

**Status**: ✅ **FULLY CONFIGURED**

Your network configuration system is now ready for both development and production use!
