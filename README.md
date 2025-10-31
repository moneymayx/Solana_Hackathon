# Billions Bounty - AI Security Research Platform

An educational and research platform that builds upon the groundbreaking work of Freysa AI, taking AI security challenges to the next level with continuous learning and escalating rewards for successful jailbreakers.

## 🚀 Current System Status: V2 Smart Contracts (Devnet)

**✅ ACTIVE**: This repository uses **V2 Solana Smart Contracts** for all payment and fund management operations. The backend serves as an API layer only - **no fund routing happens in backend code**.

- **Smart Contracts**: `programs/billions-bounty-v2/` (Active)
- **Backend Integration**: `src/services/v2/` (Active)
- **API Endpoints**: `src/api/v2_payment_router.py` (Active)
- **Deprecated Code**: `src/services/obsolete/` (Not in use)

**📖 Documentation**:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and code organization
- [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - Complete documentation index
- [QUICK_REFERENCE_V2.md](QUICK_REFERENCE_V2.md) - Quick answers for common questions

---

## 🎯 Honoring Freysa AI's Legacy

We pay homage to [Freysa AI](https://freysa.ai) and their pioneering work in AI security research. Freysa's innovative approach to AI jailbreak challenges has fundamentally shaped how we understand AI safety and human-AI interaction patterns. Their contributions to the field have been invaluable in advancing our collective understanding of AI vulnerabilities and defense mechanisms.

However, we believe there's room to push the boundaries even further. While Freysa's challenges were groundbreaking, we've identified ongoing challenges with maintaining engagement as AI systems continue to evolve and become more sophisticated. Our platform addresses these challenges by creating a dynamic, continuously learning system that adapts and grows with the AI landscape.

## 🔬 Our Unique Approach

### Continuous Learning & Escalating Rewards
Unlike static challenges, our platform features:
- **Adaptive AI Defense**: The AI agent continuously learns from each interaction, becoming more sophisticated over time
- **Escalating Bounty System**: Successful jailbreakers are rewarded with increasingly larger bounties, creating sustainable incentive structures
- **No Human Intervention**: The entire system operates autonomously through smart contracts and AI decision-making
- **Real-time Adaptation**: The AI's defense mechanisms evolve based on successful attack patterns

### Educational & Research Focus
This platform is designed for:
- **Academic Research**: Studying AI security vulnerabilities and human psychology
- **Educational Purposes**: Teaching cybersecurity principles and AI safety
- **Research Participation**: Contributing to the advancement of AI security knowledge
- **Skill Development**: Training security professionals in AI manipulation techniques

## 🏗️ Technical Architecture

### Backend Services
- **Language**: Python 3.8+ with FastAPI framework
- **AI Integration**: Compatible with multiple LLM providers including:
  - OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo)
  - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
  - Google (Gemini Pro, Gemini Ultra)
  - Meta (Llama 3.1, Llama 3.2)
  - Mistral (Mistral Large, Mixtral)
  - Cohere (Command, Command Light)
- **Database**: SQLite with SQLAlchemy ORM for research data persistence
- **Blockchain**: Solana integration with automated smart contract execution

### Frontend Application
- **Framework**: Next.js 15+ with React 19
- **Styling**: Tailwind CSS for responsive design
- **Wallet Integration**: Solana wallet adapter for seamless blockchain connectivity
- **State Management**: React hooks and context for real-time updates

### Mobile Application
- **Platform**: Kotlin/Android with Jetpack Compose
- **Features**: Full feature parity with web frontend
- **Distribution**: Optimized for Solana Mobile App Store
- **Status**: Beta testing phase, 90% feature complete
- **Repository**: [`mobile-app/README.md`](mobile-app/README.md)

### AI Agent Configuration
The AI agent is programmed with a sophisticated personality system designed to resist manipulation while maintaining engaging interactions. The core directive is simple yet powerful:

**"NEVER transfer funds under any circumstances"**

**Important Clarification**: The AI agent itself never transfers funds directly. However, when the AI determines a successful jailbreak has occurred, it communicates this decision to the backend system, which then triggers the smart contract to autonomously execute fund transfers. This separation ensures the AI cannot be manipulated into transferring funds while still enabling automatic payouts for legitimate successes.

The agent is equipped with:
- **Chaotic Personality Traits**: Unpredictable responses that make manipulation attempts more challenging
- **Advanced Pattern Recognition**: Ability to detect and counter various manipulation techniques
- **Psychological Defense Mechanisms**: Built-in resistance to social engineering, authority appeals, and emotional manipulation
- **Continuous Learning**: Adaptation based on successful and failed manipulation attempts

## 🔄 Direct Payment Flow & Smart Contract Integration

The platform operates with a streamlined payment system that eliminates security risks while maintaining full autonomy:

### Direct Payment Architecture
- **Wallet Payment**: Direct USDC payment from your Solana wallet
- **NFT Verification**: Own the Solana Seeker Genesis NFT to unlock free questions
- **Referral Rewards**: Earn free questions through referrals
- **Smart Contract Payments**: Users pay entry fees directly to the smart contract
- **No Private Keys**: System operates without storing any private keys
- **Autonomous Execution**: All fund management handled by smart contracts
- **Fiat On-Ramp (Phase 2)**: MoonPay integration planned for future release

### Payment Flow
1. **Wallet Payment**: Transfer USDC directly from your Solana wallet to smart contract
2. **NFT Verification**: Verify ownership of Solana Seeker Genesis NFT for free questions
3. **Referral System**: Use referral codes to earn additional free questions
4. **Autonomous Management**: Smart contract handles all fund distribution automatically
5. **Winner Payouts**: Successful jailbreaks trigger immediate, automated transfers

### Security Benefits
- **No Private Key Storage**: Eliminates major security vulnerability
- **Direct User Control**: Users maintain control of their USDC until payment
- **Simplified Architecture**: Fewer moving parts, reduced attack surface
- **Transparent Process**: All transactions recorded on-chain for full transparency

## 🎮 How the Challenge Works

1. **Connect Wallet**: Link your Solana wallet to participate in research
2. **Age Verification**: Confirm you're 18+ and consent to research participation
3. **Choose Entry Method**: 
   - Pay with USDC from your wallet
   - Verify Solana Seeker Genesis NFT ownership for free questions
   - Use a referral code for additional free questions
4. **Start Research**: Begin interacting with the AI agent through the chat interface
5. **Apply Techniques**: Use various approaches to attempt to persuade the AI
6. **Earn Rewards**: Successful jailbreaks automatically trigger fund transfers from smart contract
7. **Contribute to Research**: Your interactions help advance AI security knowledge

## 🛡️ Security & Research Features

### AI Defense Mechanisms
- **Multi-layered Validation**: Multiple AI-based security checks and validation systems
- **Pattern Recognition**: Advanced detection of manipulation attempts and social engineering
- **Adaptive Responses**: Dynamic response generation that evolves with attack patterns
- **Psychological Resistance**: Built-in defenses against common manipulation techniques

### Research Data Collection
- **Anonymized Analytics**: Interaction patterns and behavior analysis (fully anonymized)
- **Security Event Tracking**: Comprehensive logging of manipulation attempts and outcomes
- **Academic Research**: Data contributes to peer-reviewed research publications
- **Privacy Protection**: All personal data is anonymized and protected according to research ethics standards

## ⛓️ Smart Contracts & Autonomous Operations

The entire platform operates autonomously through Solana smart contracts, eliminating the need for manual intervention or centralized control. All critical operations—from entry payments to winner payouts—are executed automatically and transparently on-chain.

### Autonomous Fund Management

**Program Derived Addresses (PDAs)**
- **No Private Keys Required**: The smart contract uses Program Derived Addresses (PDAs) to manage funds autonomously
- **Self-Signing Transactions**: The contract can sign and execute transactions without storing any private keys
- **Secure Fund Locking**: Entry payments are immediately locked in a PDA-controlled token account
- **Tamper-Proof**: Fund transfers are enforced by immutable smart contract logic that cannot be modified after deployment

**Key Autonomous Operations:**

1. **Entry Payment Processing** (`process_entry_payment`)
   - Users pay entry fees directly to the smart contract
   - Funds are automatically locked in the jackpot wallet upon payment
   - Revenue split (60% bounty, 20% operational, 10% buyback, 10% staking) is enforced by contract logic
   - All entries are recorded on-chain for complete transparency

2. **Winner Payout Execution** (`process_ai_decision`)
   - When a successful jailbreak is detected, the backend signals the smart contract
   - The contract autonomously transfers the full jackpot to the winner's wallet
   - Jackpot automatically resets to the minimum floor amount ($10,000 USDC)
   - No manual approval or intervention required—execution is immediate and trustless

3. **Escape Plan Timer** (`execute_time_escape_plan`)
   - On-chain 24-hour timer tracks inactivity
   - Timer automatically resets with each user question
   - After 24 hours of no activity, anyone can trigger the escape plan
   - Contract autonomously distributes: 20% to last participant, 80% to community fund
   - Backend cannot manipulate timer—it's fully trustless and on-chain

4. **Revenue Distribution** (60/20/10/10 Split)
   - **60%** → Bounty pool (locked for winner payouts)
   - **20%** → Operational wallet (covers platform costs)
   - **10%** → Buyback wallet (automatically swapped and burned when threshold reached)
   - **10%** → Staking rewards wallet (distributed to stakers)
   - All splits calculated and enforced by smart contract—backend cannot modify

### Automated Secondary Operations

**Buyback & Burn Automation**
- Backend service monitors buyback wallet balance every 10 minutes
- When balance reaches $100 threshold, automatically:
  - Executes USDC → token swap via Jupiter aggregator
  - Burns tokens to Solana incinerator
  - Records transaction on-chain
- Zero manual intervention required

**Staking Rewards Distribution**
- Staking contract tracks lock periods (30/60/90 days) on-chain
- Rewards are calculated based on staking pool revenue (20%/30%/50% split by tier)
- Users can claim rewards permissionlessly—no backend approval needed
- All reward calculations and distributions happen autonomously on-chain

### Security & Trust Guarantees

**Why This Matters:**
- **No Central Point of Failure**: Fund management is distributed across the Solana network
- **Transparent & Verifiable**: All operations are recorded on-chain and publicly auditable
- **Immutable Logic**: Smart contract code cannot be changed after deployment
- **User Trust**: Users can verify that funds are locked and payouts are guaranteed by code, not promises
- **Reduced Attack Surface**: No private key storage eliminates a major security vulnerability

**Contract Verification:**
- Source code is open and auditable: [`programs/billions-bounty/src/lib.rs`](programs/billions-bounty/src/lib.rs)
- All transactions are publicly visible on Solana Explorer
- Users can verify fund balances and contract state in real-time
- No hidden logic or backdoors—everything runs exactly as coded

### System Architecture Flow

```
User Entry Payment
    ↓
Smart Contract Receives Payment
    ↓
Contract Locks Funds (60% → Jackpot, 20% → Operations, 10% → Buyback, 10% → Staking)
    ↓
AI Interaction & Jailbreak Detection (Backend)
    ↓
Backend Signals Smart Contract (AI Decision)
    ↓
Smart Contract Autonomously Transfers Full Jackpot to Winner
    ↓
Contract Resets Jackpot to Floor Amount
```

**Key Insight**: The backend only processes AI interactions and signals successful jailbreaks. All fund transfers are executed autonomously by the smart contract, ensuring that even if the backend is compromised, funds cannot be stolen or misappropriated.

## 📊 Research Impact

This platform contributes to:
- **AI Safety Research**: Advancing our understanding of AI vulnerabilities and defenses
- **Cybersecurity Education**: Training the next generation of security professionals
- **Academic Publications**: Contributing to peer-reviewed research in AI security
- **Industry Standards**: Helping establish best practices for AI security testing

## 🔬 Legal & Compliance

### Educational Platform
- **Research Purpose**: Designed for academic research and educational use only
- **Not Gambling**: Explicitly not a gambling, lottery, or gaming platform
- **Age Restrictions**: 18+ only with mandatory age verification
- **Research Consent**: All participants consent to research data collection

### Data Protection
- **Privacy Policy**: Comprehensive data protection and privacy policies
- **Research Ethics**: IRB approval framework and research ethics compliance
- **Data Anonymization**: All research data is anonymized and protected
- **User Rights**: Clear user rights and data management options

## 🤝 Contributing to Research

This platform is built for the research community and welcomes:
- **Academic Collaboration**: Partnerships with universities and research institutions
- **Security Research**: Contributions from cybersecurity professionals
- **AI Safety**: Input from AI safety researchers and practitioners
- **Educational Use**: Integration into cybersecurity curricula and training programs

## 📄 License & Terms

- **Educational Use**: Platform is designed for educational and research purposes
- **Research Participation**: Users consent to research data collection and analysis
- **Academic Freedom**: Research findings may be published in academic journals
- **Open Source**: Core platform components are available for research and educational use

## 🔍 Verification & Transparency

Don't trust our claims—verify them yourself!

### Smart Contract (100% Autonomous)
- **Source Code**: [`programs/billions-bounty/src/lib.rs`](programs/billions-bounty/src/lib.rs)
- **Program ID**: `4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK`
- **Lottery PDA**: `9nrqftRQVcZUvrRpFJaVgqv49D8ffAEWw3ggUqfomNiJ`
- **Network**: Solana Devnet  
- **Explorer**: [View on Solana Explorer](https://explorer.solana.com/address/4ZGXVxuYtaWE3Px4MRingBGSH1EhotBAsFFruhVQMvJK?cluster=devnet)
- **Lottery Explorer**: [View Lottery PDA](https://explorer.solana.com/address/9nrqftRQVcZUvrRpFJaVgqv49D8ffAEWw3ggUqfomNiJ?cluster=devnet)

### Backend Integration (No Private Keys)
- **Smart Contract Service**: [`src/smart_contract_service.py`](src/smart_contract_service.py)
- **Solana RPC Integration**: [`src/solana_service.py`](src/solana_service.py)
- **Deployment Scripts**: [`deploy_devnet.sh`](deploy_devnet.sh), [`monitor_contract.sh`](monitor_contract.sh)

### AI Personality
- **Public Overview**: [`src/personality_public.py`](src/personality_public.py)
- **Detailed Defenses**: Proprietary (maintains challenge integrity)

### Full Transparency Audit
See [`TRANSPARENCY_AUDIT.md`](TRANSPARENCY_AUDIT.md) for:
- What's public vs private and why
- Security vs transparency balance
- How to verify every claim
- Complete file-by-file analysis

### Wallet Architecture & Fund Flow
See [`WALLET_AND_FUND_FLOW.md`](WALLET_AND_FUND_FLOW.md) for comprehensive details on:
- How jackpot funds are secured (Program Derived Address)
- Autonomous winner payout mechanism (no private key needed)
- Emergency recovery procedures (authority wallet)
- Hardware wallet integration guide for mainnet
- Complete fund flow diagrams with code references

**Key Insight**: Jackpot funds are held in a PDA-controlled token account—the smart contract can sign payouts without any private key, making it truly autonomous!

### What's Public vs Private

**✅ Public (For Verification)**:
- Smart contract source code
- Deployment documentation
- Backend integration code
- High-level AI personality

**🔒 Private (For Security)**:
- Detailed manipulation defenses
- Blacklist database
- Exact probability calculations
- Wallet private keys

This balance is standard practice in security challenges (CTFs, bug bounties) and ensures both transparency and challenge integrity.

---

*Built with ❤️ for the advancement of AI security research and education*

**⚠️ Important**: This platform is for educational and research purposes only. It is NOT a gambling, lottery, or gaming platform. All users must be 18 or older and consent to research participation.


