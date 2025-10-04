# Smart Contract Deployment Guide

This guide covers deploying the autonomous lottery smart contract system that replaces backend-controlled fund transfers.

## Overview

The smart contract system provides:
- **Autonomous Fund Management**: All fund transfers handled by smart contract
- **Secure Fund Locking**: Funds immediately locked upon entry payment
- **Tamper-proof Randomness**: Winner selection using blockhash-based randomness
- **No Backend Control**: Backend cannot influence fund transfers

## Prerequisites

### Required Software
- Node.js 16+
- Rust 1.70+
- Solana CLI 1.17+
- Anchor Framework 0.29+

### Environment Setup
```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/v1.17.0/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Install Anchor
npm install -g @coral-xyz/anchor-cli

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

## Smart Contract Deployment

### 1. Build the Program
```bash
cd programs/billions-bounty
anchor build
```

### 2. Deploy to Localnet (Testing)
```bash
# Start local Solana cluster
solana-test-validator

# In another terminal, deploy to localnet
anchor deploy --provider.cluster localnet
```

### 3. Deploy to Devnet
```bash
# Configure for devnet
solana config set --url devnet

# Airdrop SOL for deployment
solana airdrop 2

# Deploy to devnet
anchor deploy --provider.cluster devnet
```

### 4. Deploy to Mainnet
```bash
# Configure for mainnet
solana config set --url mainnet-beta

# Deploy to mainnet (requires SOL for fees)
anchor deploy --provider.cluster mainnet-beta
```

## Backend Integration

### 1. Update Environment Variables
Add to your `.env` file:
```env
# Smart Contract Configuration
LOTTERY_PROGRAM_ID=B1LL10N5B0UNTY1111111111111111111111111111111111
SOLANA_RPC_ENDPOINT=https://api.mainnet-beta.solana.com

# USDC Configuration
USDC_MINT_ADDRESS=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v

# Authority Keypair (for emergency recovery)
AUTHORITY_PRIVATE_KEY=your_authority_private_key_here
```

### 2. Initialize the Lottery Contract
```python
from src.smart_contract_service import smart_contract_service

# Initialize lottery with $10,000 floor and $10 entry fee
result = await smart_contract_service.initialize_lottery(
    authority_keypair="your_authority_keypair",
    jackpot_wallet="your_jackpot_wallet_address"
)
```

### 3. Update API Endpoints
The backend now uses smart contract endpoints:
- `/api/lottery/status` - Get lottery state
- `/api/lottery/select-winner` - Select winner (autonomous)
- `/api/payment/create` - Process lottery entry through smart contract

## Frontend Integration

### 1. Install Dependencies
```bash
cd frontend
npm install @solana/web3.js @coral-xyz/anchor
```

### 2. Update Components
Replace `PaymentFlow.tsx` with `SmartContractIntegration.tsx` for smart contract interaction.

### 3. Wallet Integration
The frontend now directly interacts with the smart contract:
- Users sign transactions with their wallet
- Funds are immediately locked in the smart contract
- Winner selection is autonomous and verifiable

## Testing

### 1. Run Smart Contract Tests
```bash
cd programs/billions-bounty
anchor test
```

### 2. Test Backend Integration
```bash
cd Billions_Bounty
python -m pytest tests/test_smart_contract_integration.py
```

### 3. Test Frontend Integration
```bash
cd frontend
npm run test
```

## Security Considerations

### ✅ Implemented Security Measures
- **Autonomous Fund Management**: No backend control over transfers
- **Secure Randomness**: Blockhash-based winner selection
- **Fund Locking**: Immediate locking upon entry
- **Access Control**: Authority-only emergency recovery
- **Input Validation**: All inputs validated by smart contract

### ⚠️ Important Notes
- **Emergency Recovery**: Only use in genuine emergencies
- **Authority Keypair**: Store securely and never commit to version control
- **Program Upgrades**: Requires careful migration planning
- **Testing**: Thoroughly test on devnet before mainnet deployment

## Monitoring and Maintenance

### 1. Monitor Smart Contract Events
```typescript
// Listen for lottery events
const program = new Program<BillionsBounty>(idl, provider);
program.addEventListener('EntryProcessed', (event) => {
  console.log('New entry processed:', event);
});
```

### 2. Track Fund Flows
- All fund movements are recorded on-chain
- Use Solana Explorer to verify transactions
- Monitor jackpot growth and winner selections

### 3. Emergency Procedures
- Emergency recovery available for genuine emergencies only
- Requires authority keypair and proper justification
- All emergency actions are logged on-chain

## Migration from Backend Control

### 1. Phase 1: Deploy Smart Contract
- Deploy smart contract to devnet
- Test all functionality thoroughly
- Verify fund locking and winner selection

### 2. Phase 2: Update Backend
- Replace fund routing service with smart contract service
- Update API endpoints to use smart contract
- Maintain backward compatibility during transition

### 3. Phase 3: Update Frontend
- Integrate smart contract interaction
- Update payment flow to use smart contract
- Test end-to-end functionality

### 4. Phase 4: Production Deployment
- Deploy to mainnet
- Migrate existing funds to smart contract
- Deprecate old backend fund control

## Troubleshooting

### Common Issues

#### 1. Program Deployment Fails
```bash
# Check Solana CLI version
solana --version

# Check Anchor version
anchor --version

# Verify Rust installation
rustc --version
```

#### 2. Transaction Fails
- Check wallet has sufficient SOL for fees
- Verify USDC token account exists
- Check program is deployed and active

#### 3. Winner Selection Fails
- Ensure lottery has entries
- Check lottery is active
- Verify sufficient jackpot amount

### Debug Commands
```bash
# Check program account
solana account <PROGRAM_ID>

# Check lottery state
solana account <LOTTERY_PDA>

# Verify transaction
solana confirm <TRANSACTION_SIGNATURE>
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review smart contract logs
3. Open an issue in the repository
4. Contact the development team

## License

This smart contract system is licensed under the MIT License. See LICENSE file for details.
