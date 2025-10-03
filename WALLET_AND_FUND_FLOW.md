# Wallet Architecture & Direct Payment Flow

## 🎯 **Executive Summary**

This document explains the new streamlined payment architecture that eliminates private key storage while maintaining full autonomous operation. The system now uses direct payments from users to smart contracts.

**Key Points**:
- ✅ **No Private Keys Stored**: System operates without storing any private keys
- ✅ **Direct User Payments**: Users pay USDC directly to smart contract
- ✅ **MoonPay Integration**: Apple Pay/PayPal → USDC → User Wallet → Smart Contract
- ✅ **Autonomous Execution**: All fund management handled by smart contracts
- 🔐 **Simplified Security**: Fewer attack vectors, reduced complexity

---

## 🏦 **The Three Types of Accounts**

### 1. **Lottery PDA (Program Derived Address)** 📦

```
Address: GXJ8MvC683r6WXcijEtnKNypGgWH5FFyshd3uciK1LSv
Type: Program Derived Address (PDA)
Seeds: ["lottery"]
Private Key: NONE - Doesn't exist!
Controlled by: Smart contract code
```

**Purpose**:
- Stores lottery state data (jackpot amount, entries, etc.)
- Acts as "owner" of the jackpot token account
- Signs transactions using cryptographic seeds (not a private key)

**What it holds**:
- Lottery configuration
- Current jackpot amount (as data)
- Total entries
- Last rollover timestamp

**Security**:
- ✅ Cannot be hacked (no private key to steal)
- ✅ Only controlled by program code
- ✅ Immutable unless program is upgraded

---

### 2. **Jackpot Token Account (Associated Token Account)** 💰

```
Address: [Derived from: USDC Mint + Lottery PDA]
Type: SPL Token Account (Associated Token Account)
Owner: Lottery PDA
Contains: All USDC jackpot funds
Controlled by: Lottery PDA (via smart contract)
```

**Purpose**:
- Holds ALL the actual USDC funds
- Receives entry payments from users
- Pays out jackpots to winners
- Source for emergency recovery

**What it holds**:
- Example: 10,000 USDC (actual tokens)

**Security**:
- ✅ Owned by PDA (no private key)
- ✅ Can only be spent by smart contract code
- ✅ Autonomous payout - no human signature needed
- ⚠️ Emergency recovery requires authority authorization

---

### 3. **Authority Wallet** 🔑

```
Current (Devnet):
  Address: FH7b3Fare6gGX6mWvPRWshDhyToQ1QggeHZHW2Jczd9p
  Type: Software wallet (JSON file)
  Private Key: Exists (stored in lottery-authority-devnet.json)
  Controlled by: Owner of private key

Recommended (Mainnet):
  Type: Hardware wallet (Ledger Nano X/S)
  Private Key: Stored on hardware device
  Controlled by: Physical device + PIN
```

**Purpose**:
- Emergency fund recovery (last resort)
- Program upgrades (bug fixes)
- Lottery parameter updates (if needed)

**What it holds**:
- Small amount of SOL for transaction fees (~1-2 SOL)
- NO jackpot funds (funds are in PDA's token account)

**Security**:
- ⚠️ CRITICAL: Must be secured with hardware wallet on mainnet
- ⚠️ If compromised: Can drain entire jackpot via emergency recovery
- ✅ Not needed for daily operations (winner payouts)

---

## 💸 **New Direct Payment Flow**

### **1. MoonPay Payment (Fiat → USDC)**

```
┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ User's Bank  │───▶│   MoonPay   │───▶│ User's Wallet│
│ $10 USD      │    │ (Apple Pay) │    │ 10 USDC      │
└──────────────┘    └─────────────┘    └──────┬───────┘
                                               │
                                               │ Direct transfer
                                               │ (no private keys)
                                               ↓
```

### **2. Lottery Entry Payment (User → Smart Contract)**

```
┌──────────────┐
│ User's Wallet│
│ 10 USDC      │
└──────┬───────┘
       │ User signs transaction
       │ (approves transfer to smart contract)
       ↓
┌──────────────────────────┐
│ Smart Contract           │
│ process_entry_payment()  │
└──────┬───────────────────┘
       │ Autonomous processing
       ↓
┌───────────────────────────┐
│ Jackpot Token Account     │
│ (PDA's USDC account)      │
│ +10 USDC                  │
│ Total: 10,010 USDC        │
└───────────────────────────┘
       │
       ↓
┌───────────────────────────┐
│ Lottery PDA State         │
│ total_entries++           │
│ current_jackpot += 8 USDC │
│ (80% to jackpot)          │
└───────────────────────────┘

Result:
- User's wallet: -10 USDC
- Jackpot account: +10 USDC
- System private keys: NONE ✅
- Authority wallet: Not involved ✅
```

**Code Reference** (lines 46-97 in lib.rs):
```rust
pub fn process_entry_payment(
    ctx: Context<ProcessEntryPayment>,
    entry_amount: u64,
    user_wallet: Pubkey,
) -> Result<()> {
    // Transfer from user to jackpot account
    let transfer_instruction = Transfer {
        from: ctx.accounts.user_token_account.to_account_info(),
        to: ctx.accounts.jackpot_token_account.to_account_info(), // ← PDA's account
        authority: ctx.accounts.user.to_account_info(),
    };
    token::transfer(cpi_ctx, entry_amount)?;
    
    // Update lottery state
    lottery.current_jackpot += research_contribution;
    lottery.total_entries += 1;
}
```

**Authority Wallet Involvement**: NONE ✅

---

### **2. Winner Payout (Autonomous)**

```
┌───────────────────────────┐
│ Smart Contract            │
│ select_winner()           │
│ (called by anyone/cron)   │
└──────┬────────────────────┘
       │ 1. Generate random number
       │ 2. Select winner index
       │ 3. Record winner
       ↓
┌───────────────────────────┐
│ Lottery PDA               │
│ Signs using seeds:        │
│ ["lottery", bump]         │
│ NO PRIVATE KEY NEEDED!    │
└──────┬────────────────────┘
       │ PDA signature
       ↓
┌───────────────────────────┐
│ Jackpot Token Account     │
│ (PDA's USDC account)      │
│ -10,000 USDC              │
│ Remaining: 10 USDC        │
└──────┬────────────────────┘
       │ Transfer
       ↓
┌───────────────────────────┐
│ Winner's Wallet           │
│ +10,000 USDC              │
└───────────────────────────┘

Result:
- Winner's wallet: +10,000 USDC
- Jackpot account: -10,000 USDC
- Authority wallet: Not involved ✅
```

**Code Reference** (lines 99-165 in lib.rs):
```rust
pub fn select_winner(ctx: Context<SelectWinner>) -> Result<()> {
    // ... winner selection logic ...
    
    // PDA signs the transfer (autonomous!)
    let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
    let signer = &[&seeds[..]];  // ← PDA signature, NOT authority!
    
    let cpi_ctx = CpiContext::new_with_signer(
        ctx.accounts.token_program.to_account_info(),
        transfer_instruction,
        signer,  // ← Smart contract signs
    );
    
    token::transfer(cpi_ctx, transfer_amount)?;
}
```

**Authority Wallet Involvement**: NONE ✅

---

### **3. Emergency Recovery (Manual)**

```
⚠️ EMERGENCY SCENARIO ONLY ⚠️

┌───────────────────────────┐
│ Authority Wallet          │
│ Signs transaction         │
│ REQUIRES PRIVATE KEY      │
└──────┬────────────────────┘
       │ Authority signature
       ↓
┌───────────────────────────┐
│ Smart Contract            │
│ emergency_recovery()      │
│ Checks: Is signer == authority? │
└──────┬────────────────────┘
       │ Authorized
       ↓
┌───────────────────────────┐
│ Lottery PDA               │
│ Signs using seeds         │
│ (on behalf of authority)  │
└──────┬────────────────────┘
       │ PDA signature
       ↓
┌───────────────────────────┐
│ Jackpot Token Account     │
│ -1,000 USDC (example)     │
└──────┬────────────────────┘
       │ Transfer
       ↓
┌───────────────────────────┐
│ Authority's Token Account │
│ +1,000 USDC               │
└───────────────────────────┘

Result:
- Authority wallet: +1,000 USDC
- Jackpot account: -1,000 USDC
- Public record: Transaction visible on-chain
```

**Code Reference** (lines 167-206 in lib.rs):
```rust
pub fn emergency_recovery(ctx: Context<EmergencyRecovery>, amount: u64) -> Result<()> {
    // REQUIRES AUTHORITY SIGNATURE
    require!(
        ctx.accounts.authority.key() == lottery.authority, 
        ErrorCode::Unauthorized
    );
    
    // PDA signs, but only if authority authorized
    let seeds = &[b"lottery".as_ref(), &[lottery_bump]];
    let signer = &[&seeds[..]];
    
    token::transfer(cpi_ctx, amount)?;
}
```

**Authority Wallet Involvement**: CRITICAL 🔐

**When Used**:
- Smart contract bug discovered
- Funds need to be moved to new contract
- Catastrophic failure requiring intervention

**Frequency**: Hopefully NEVER (< 0.01% probability)

---

## 📊 **Security Comparison**

| Wallet/Account | Holds Jackpot? | Private Key? | Hack Impact | Daily Use |
|----------------|---------------|--------------|-------------|-----------|
| **Lottery PDA** | No (just state) | ❌ None | None (can't be hacked) | Every transaction |
| **Jackpot Token Account** | ✅ YES | ❌ None (owned by PDA) | None (no key to steal) | Every transaction |
| **Authority Wallet** | ❌ No | ✅ Yes | 🚨 CRITICAL - Can drain all | Almost never |

**Key Insight**: 
- The jackpot IS vulnerable to authority wallet compromise
- But ONLY through the emergency_recovery function
- Which creates a public on-chain transaction (visible to all)
- And can be monitored/alerted

---

## 🔐 **Hardware Wallet Integration Guide**

### **Phase 1: Devnet (Current) - Software Wallet OK**

```bash
# Current setup - FINE for testing
Authority Wallet: lottery-authority-devnet.json
Network: Devnet
Funds at Risk: $0 (test tokens)
Security: Software wallet acceptable
```

**No action needed** ✅

---

### **Phase 2: Mainnet Preparation - Hardware Wallet Required**

#### **Step 1: Purchase Hardware Wallet**

**Recommended**: Ledger Nano X or Nano S Plus

```
Where to Buy: https://www.ledger.com/ (ONLY official site!)
Cost: $79 (Nano S Plus) or $149 (Nano X)
Shipping: 1-2 weeks

⚠️ NEVER buy from third parties (Amazon, eBay, etc.)
⚠️ Always verify authenticity when received
```

#### **Step 2: Initialize Ledger**

```bash
1. Unbox and connect Ledger to computer
2. Follow on-screen setup
3. Generate NEW seed phrase (24 words)
4. Write seed phrase on provided recovery sheet
5. Set PIN code (8 digits recommended)
6. Install Ledger Live app on computer
```

**CRITICAL**: 
- ✅ Store seed phrase in fireproof safe
- ✅ Never take photos of seed phrase
- ✅ Never store seed phrase digitally
- ✅ Consider metal backup (Cryptosteel)

#### **Step 3: Install Solana App on Ledger**

```bash
1. Open Ledger Live
2. Go to Manager
3. Search "Solana"
4. Click Install
5. Confirm on Ledger device
```

#### **Step 4: Get Ledger's Solana Address**

```bash
# Connect Ledger and open Solana app on device
# Then run:
solana-keygen pubkey usb://ledger?key=0

# Example output:
# 7xXK8mVW9WqbKJz9zPq1QmK8FvBn2J1rG4sT3vN5mP8c

# This is your new authority address!
```

#### **Step 5: Fund the Ledger Wallet**

```bash
# Send 2-3 SOL to Ledger for transaction fees
solana transfer 7xXK8mVW9WqbKJz9zPq1QmK8FvBn2J1rG4sT3vN5mP8c 2 \
  --url https://api.mainnet-beta.solana.com
```

#### **Step 6: Deploy Program with Ledger as Authority**

```bash
# Make sure Ledger is connected and Solana app is open
cd /path/to/Billions_Bounty

# Deploy program (Ledger will prompt for confirmation)
solana program deploy \
  programs/billions-bounty/target/deploy/billions_bounty.so \
  --program-id programs/billions-bounty/target/deploy/billions_bounty-keypair.json \
  --keypair usb://ledger?key=0 \
  --url https://api.mainnet-beta.solana.com

# Confirm on Ledger device (press both buttons)
```

#### **Step 7: Initialize Lottery with Ledger as Authority**

```bash
# Run initialization script with Ledger
python scripts/initialize_lottery.py \
  --keypair usb://ledger?key=0 \
  --jackpot-wallet YOUR_JACKPOT_WALLET_ADDRESS \
  --network mainnet

# Ledger will show:
# "Sign initialization transaction?"
# Press both buttons to confirm
```

#### **Step 8: Verify Authority**

```bash
# Check program authority
solana program show YOUR_PROGRAM_ID

# Should show:
# Authority: 7xXK8mVW9WqbKJz9zPq1QmK8FvBn2J1rG4sT3vN5mP8c (Ledger)
```

---

### **Phase 3: Advanced - Multi-Sig Setup**

**For jackpots > $100K, use multi-sig:**

#### **Step 1: Get Multiple Ledgers**

```
Purchase 3-5 Ledger devices
Distribute to trusted parties:
- Owner 1 (you)
- Owner 2 (co-founder/trusted partner)
- Owner 3 (advisor/board member)
```

#### **Step 2: Create Squads Multi-Sig**

```bash
# Go to https://squads.so/
# Connect each Ledger
# Create multi-sig wallet with 2-of-3 or 3-of-5 threshold

Example Setup:
├── Member 1: Your Ledger
├── Member 2: Co-founder's Ledger
├── Member 3: Advisor's Ledger
└── Threshold: 2-of-3 signatures required
```

#### **Step 3: Transfer Program Authority to Multi-Sig**

```bash
# Transfer program upgrade authority
solana program set-upgrade-authority \
  YOUR_PROGRAM_ID \
  --new-upgrade-authority MULTISIG_ADDRESS \
  --keypair usb://ledger?key=0

# Requires your Ledger signature
```

#### **Step 4: Test Emergency Recovery**

```bash
# Propose emergency recovery (requires multiple signatures)
# Member 1 proposes on Squads dashboard
# Member 2 approves with their Ledger
# Transaction executes when threshold reached
```

---

## 🚨 **Emergency Recovery Procedure**

### **When to Use**

Only in genuine emergencies:
- ✅ Smart contract bug discovered
- ✅ Funds need migration to new contract
- ✅ Critical security vulnerability found
- ❌ NOT for normal operations
- ❌ NOT for convenience

### **How to Execute (Hardware Wallet)**

```bash
# 1. Analyze the emergency
#    - What's the bug?
#    - How much to recover?
#    - Where to send funds?

# 2. Connect Ledger and open Solana app

# 3. Run emergency recovery
python scripts/emergency_recovery.py \
  --amount 10000 \
  --keypair usb://ledger?key=0 \
  --network mainnet

# 4. Review on Ledger screen:
#    "Emergency Recovery"
#    "Amount: 10,000 USDC"
#    "Approve?"

# 5. Press both buttons to confirm

# 6. Document publicly:
#    - Why recovery was needed
#    - What bug was found
#    - Where funds went
#    - Remediation plan
```

### **Transparency Requirements**

If emergency recovery is ever used:
1. ✅ Announce on Discord/Twitter immediately
2. ✅ Explain the bug/issue
3. ✅ Show on-chain transaction
4. ✅ Explain remediation
5. ✅ Publish post-mortem

---

## 📋 **Security Checklist**

### Before Mainnet Launch

- [ ] Hardware wallet purchased from official source
- [ ] Seed phrase written down and stored securely
- [ ] Ledger initialized with strong PIN
- [ ] Solana app installed on Ledger
- [ ] Test deployment on devnet with Ledger
- [ ] Backup seed phrase in second secure location
- [ ] Authority wallet address documented
- [ ] Emergency recovery procedure tested
- [ ] Team trained on Ledger usage
- [ ] Monitoring alerts configured

### After Mainnet Launch

- [ ] Verify authority address matches Ledger
- [ ] Ledger stored in secure location
- [ ] Seed phrase in fireproof safe
- [ ] Regular security audits scheduled
- [ ] Emergency contact list maintained
- [ ] Recovery procedure documented
- [ ] Team has access to emergency plan
- [ ] Consider upgrading to multi-sig when jackpot > $100K

---

## 🎯 **Summary Table**

| Scenario | Authority Wallet Used? | Hardware Wallet Needed? | Frequency |
|----------|----------------------|----------------------|-----------|
| User entry payment | ❌ No | N/A | Every entry |
| Winner payout | ❌ No | N/A | Daily/Weekly |
| Lottery initialization | ✅ Yes | ✅ For mainnet | Once |
| Program upgrade | ✅ Yes | ✅ For mainnet | Rarely |
| Emergency recovery | ✅ Yes | ✅ CRITICAL | Hopefully never |

---

## ❓ **FAQ**

**Q: Can't I just use a regular wallet for mainnet?**  
A: Technically yes, but ONE malware infection = losing the entire jackpot. Hardware wallet prevents this.

**Q: What if I lose my Ledger?**  
A: Use the seed phrase to recover on a new Ledger. This is why seed phrase backup is critical.

**Q: What if someone steals my Ledger?**  
A: They still need your PIN (3 wrong attempts = device wipes). Then they'd need to bypass physical security.

**Q: How often will I need to use the Ledger?**  
A: Almost never! Winner payouts are autonomous. Only for emergencies or upgrades.

**Q: Can I use a different hardware wallet (Trezor, etc.)?**  
A: Ledger has the best Solana support. Trezor works but setup is more complex.

**Q: What about key ceremony/MPC instead?**  
A: Advanced option, but multi-sig with Ledgers is simpler and well-tested.

---

## 📚 **Additional Resources**

- Solana Program Derived Addresses: https://docs.solana.com/developing/programming-model/calling-between-programs#program-derived-addresses
- Ledger Solana Guide: https://support.ledger.com/hc/en-us/articles/360016265659
- Squads Multi-Sig: https://squads.so/
- Smart Contract Source: `programs/billions-bounty/src/lib.rs`

---

**Last Updated**: $(date)  
**Status**: ✅ Public documentation  
**Audience**: Users, auditors, security researchers

**Recommendation**: This document should be PUBLIC - it builds trust and demonstrates professional security practices.

