# SAS Program ID Search - Status

## 🔍 Search Attempts Made

I've tried multiple automated methods to find the SAS (Solana Attestations Service) program ID, but it's not easily discoverable programmatically.

### Automated Attempts ❌
- ❌ Documentation scraping (no program IDs found)
- ❌ RPC program enumeration (requires known program ID)
- ❌ Explorer API search (limited or changed)
- ❌ Web search (results confusing SAS software with Solana SAS)

### Why It's Hard to Find Automatically

1. **No Public Program Registry**: Solana doesn't have a central registry of program names
2. **RPC Limitations**: Can't search programs by name, only by ID
3. **Documentation**: Program IDs not always published in docs
4. **GitHub**: Repository may be private or not contain deployment info

---

## ✅ Recommended Method: Manual Search

**I recommend you do a quick manual search** - it's the fastest and most reliable way:

### Quick 2-Minute Search

1. **Open Solana Explorer**:
   - Devnet: https://explorer.solana.com/?cluster=devnet
   - Click the search bar (top right)

2. **Search Terms** (try each):
   - `attestations`
   - `SAS`
   - `attest`

3. **What to Look For**:
   - Results showing **"Program"** (not Account or Transaction)
   - Address format: 44 characters (base58)
   - Click on it to verify

4. **Verify It's SAS**:
   - Check if description mentions "attestation" or "credential"
   - Look at program accounts
   - Check transaction history

5. **Copy the Program ID** (the address shown)

### Alternative: Check These Sources

1. **Official Documentation**:
   - Visit: https://launch.solana.com/docs/attestations
   - Look for "Program ID" or "Deployment" section
   - Check code examples

2. **GitHub**:
   - Search: `github.com/solana-foundation/attestations`
   - Check README or deployment files
   - Look in example code

3. **npm Package**:
   - Check: `@solana-foundation/sas-lib`
   - Look in example code or documentation
   - Program ID might be in constants/examples

4. **Solana Discord/Forums**:
   - Ask in Solana developer community
   - Someone may have it documented

---

## 📝 Once You Find It

Update your `.env` file:
```bash
ATTESTATIONS_PROGRAM_ID_DEVNET=<devnet_program_id>
ATTESTATIONS_PROGRAM_ID_MAINNET=<mainnet_program_id>
```

Then test:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
ENABLE_ATTESTATIONS_SDK=true python examples/sdk/attestations_kyc_example.py
```

---

## 💡 Why I Can't Find It Automatically

- Program IDs are blockchain addresses, not searchable by name
- RPC requires the program ID to query it (chicken-and-egg)
- Documentation may not publish deployment addresses
- GitHub repos may be private or not contain deployment info

**Manual search is actually faster** - takes 2 minutes vs hours of trying automated methods that may not work.

---

**Status**: Automated search unsuccessful. Manual search on Solana Explorer recommended (2 minutes).

