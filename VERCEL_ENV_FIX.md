# Fix NFT Verification on Vercel

## Problem
The NFT verification is failing on Vercel with a 500 error because the `PAYMENT_MODE` environment variable is not set, causing the backend to run in "real" mode and try to access Solana blockchain (which fails with 403).

## Solution: Add Environment Variable to Vercel

### Option 1: Vercel Dashboard (Recommended)

1. Go to your Vercel project dashboard
2. Click on **Settings** tab
3. Click on **Environment Variables** in the left sidebar
4. Add a new environment variable:
   - **Name:** `PAYMENT_MODE`
   - **Value:** `mock`
   - **Environment:** Select all (Production, Preview, Development)
5. Click **Save**
6. **Redeploy** your application for changes to take effect

### Option 2: Vercel CLI

```bash
# Install Vercel CLI if you don't have it
npm i -g vercel

# Set the environment variable
vercel env add PAYMENT_MODE

# When prompted:
# - Enter value: mock
# - Select environments: Production, Preview, Development

# Redeploy
vercel --prod
```

### Option 3: Create .env.production file (Alternative)

Create a `.env.production` file in the root of your project:

```bash
# Vercel Production Environment
PAYMENT_MODE=mock

# Add other production variables
DATABASE_URL=your_production_database_url
NEXT_PUBLIC_API_URL=https://billions-bounty-iwnh3.ondigitalocean.app
```

**Note:** Make sure to add `.env.production` to `.gitignore` if it contains sensitive data.

## After Setting the Environment Variable

1. **Redeploy** your application on Vercel
2. Check the deployment logs to confirm `PAYMENT_MODE=mock` is loaded
3. Test the NFT verification - it should now work without 403 errors

## Verify the Fix

After redeploying, you should see in the browser console:
```
🎨 MOCK NFT mode - using backend response
```

Instead of:
```
💎 REAL NFT mode - checking blockchain
```

## Technical Details

The backend checks this environment variable at:
- **File:** `apps/backend/main.py`
- **Line:** 1955
- **Endpoint:** `/api/nft/status/{wallet_address}`

```python
payment_mode = os.getenv("PAYMENT_MODE", "real")

if payment_mode == "mock":
    # Use mock NFT service - no blockchain calls
    ...
else:
    # Real mode - requires Solana RPC access
    ...
```

## Important Notes

- **Mock mode** is recommended for testing and development
- **Real mode** requires:
  - Solana RPC access (can be expensive)
  - Deployed smart contracts on mainnet
  - Proper NFT collection setup
  
For production with real NFTs, you'll need to:
1. Deploy the NFT verification smart contract
2. Set up a reliable Solana RPC provider (Alchemy, QuickNode, etc.)
3. Update `AUTHORIZED_NFT_MINT` in the frontend
4. Change `PAYMENT_MODE=real` when ready

