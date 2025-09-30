# Billions Bounty Smart Contract

An autonomous lottery system built on Solana that implements secure fund locking, autonomous fund transfers, and tamper-proof randomness.

## Features

### 🔒 **Autonomous Fund Management**
- **No Backend Control**: All fund transfers are handled by the smart contract
- **Automatic Fund Locking**: Funds are immediately locked upon entry payment
- **Secure Transfers**: Uses Solana's SPL token program for secure USDC transfers
- **Emergency Recovery**: Authority can recover funds in emergency situations only

### 🎲 **Secure Randomness**
- **Blockhash-based Randomness**: Uses recent blockhash for unpredictable winner selection
- **No Centralized Control**: Winner selection is completely autonomous
- **Tamper-proof**: Cannot be manipulated by external parties

### 💰 **Fund Distribution**
- **80% Research Fund**: Contributes to the research fund for AI security research
- **20% Operational Fee**: Covers operational costs
- **Automatic Calculation**: Fund distribution is calculated and enforced by the contract

### 🏆 **Lottery Mechanics**
- **Fixed Research Fund Floor**: $10,000 minimum jackpot
- **Rollover System**: Unclaimed jackpots roll over to the next round
- **Entry Tracking**: All entries are recorded on-chain
- **Winner Verification**: Winners are selected and verified autonomously

## Smart Contract Architecture

### Core Accounts

#### `Lottery`
- **Authority**: Contract authority (can be automated)
- **Jackpot Wallet**: Where funds are locked
- **Research Fund Floor**: Minimum jackpot amount ($10,000)
- **Research Fee**: Entry fee amount ($10)
- **Current Jackpot**: Current jackpot amount
- **Total Entries**: Number of entries in current round
- **Is Active**: Whether lottery is accepting entries

#### `Entry`
- **User Wallet**: User's wallet address
- **Amount Paid**: Entry payment amount
- **Research Contribution**: Amount going to research fund
- **Operational Fee**: Amount for operational costs
- **Timestamp**: When entry was made
- **Is Processed**: Whether entry has been processed

#### `Winner`
- **Lottery ID**: Reference to lottery round
- **Winner Index**: Index of winning entry
- **Jackpot Amount**: Amount won
- **Timestamp**: When winner was selected
- **Is Claimed**: Whether winnings have been claimed

### Key Functions

#### `initialize_lottery`
Initializes the lottery system with configuration parameters.

#### `process_entry_payment`
Processes a lottery entry payment and locks funds in the jackpot wallet.

#### `select_winner`
Autonomously selects a winner and transfers the jackpot.

#### `emergency_recovery`
Allows authority to recover funds in emergency situations.

## Security Features

### 🔐 **Access Control**
- Only authorized accounts can perform sensitive operations
- Emergency recovery restricted to contract authority
- User entries are validated before processing

### 🛡️ **Fund Protection**
- Funds are immediately locked upon entry
- No way to withdraw funds except through winner selection or emergency recovery
- All transfers are verified and logged

### 🎯 **Randomness Security**
- Uses Solana's recent blockhash for randomness
- Cannot be predicted or manipulated
- Winner selection is completely autonomous

## Usage

### Prerequisites
- Node.js 16+
- Rust 1.70+
- Solana CLI 1.17+
- Anchor Framework 0.29+

### Installation
```bash
# Install dependencies
npm install

# Build the program
npm run build

# Run tests
npm run test
```

### Deployment

#### Local Development
```bash
# Start local Solana cluster
solana-test-validator

# Deploy to localnet
npm run deploy:local
```

#### Devnet
```bash
# Deploy to devnet
npm run deploy:devnet
```

#### Mainnet
```bash
# Deploy to mainnet
npm run deploy:mainnet
```

### Integration

#### Initialize Lottery
```typescript
import { BillionsBountyClient } from './ts/client';

const client = new BillionsBountyClient(provider);

// Initialize lottery with $10,000 floor and $10 entry fee
await client.initializeLottery(
    10000, // $10,000 research fund floor
    10,    // $10 entry fee
    jackpotWallet,
    authority
);
```

#### Process Entry
```typescript
// Process a $10 entry payment
await client.processEntryPayment(
    10, // $10 entry amount
    userWallet,
    user,
    usdcMint
);
```

#### Select Winner
```typescript
// Select winner (can be automated)
await client.selectWinner(
    lotteryAuthority,
    winnerWallet,
    usdcMint
);
```

## Testing

The smart contract includes comprehensive tests covering:

- ✅ Lottery initialization
- ✅ Entry payment processing
- ✅ Fund locking mechanisms
- ✅ Winner selection
- ✅ Emergency recovery
- ✅ Access control
- ✅ Input validation
- ✅ Error handling

Run tests with:
```bash
npm run test
```

## Security Considerations

### ✅ **Implemented Security Measures**
- All fund transfers are handled by the smart contract
- No backend control over fund movements
- Secure randomness using blockhash
- Access control for sensitive operations
- Input validation and error handling

### ⚠️ **Important Notes**
- Emergency recovery should only be used in genuine emergencies
- Winner selection is autonomous and cannot be influenced
- All operations are logged and verifiable on-chain
- Funds are locked immediately upon entry payment

## Development

### Project Structure
```
programs/billions-bounty/
├── src/
│   ├── lib.rs          # Main program logic
│   └── main.rs         # Program entry point
├── ts/
│   └── client.ts       # TypeScript client
├── tests/
│   └── billions-bounty.ts  # Test suite
├── Cargo.toml          # Rust dependencies
├── package.json        # TypeScript dependencies
└── README.md          # This file
```

### Key Dependencies
- **anchor-lang**: Solana program framework
- **anchor-spl**: SPL token integration
- **spl-token**: Token operations
- **solana-program**: Core Solana functionality

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues, please open an issue in the repository or contact the development team.
