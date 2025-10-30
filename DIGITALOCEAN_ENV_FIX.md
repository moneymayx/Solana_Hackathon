# Fix NFT Verification on DigitalOcean Backend

## Problem
The NFT verification is failing with a 500 error because the backend (running on DigitalOcean) doesn't have the `PAYMENT_MODE=mock` environment variable set.

## Architecture
- **Frontend (Vercel):** Next.js app at your Vercel domain
- **Backend (DigitalOcean):** FastAPI Python app at `billions-bounty-iwnh3.ondigitalocean.app`

The environment variable needs to be set on the **BACKEND (DigitalOcean)**, not the frontend.

## Solution: Add Environment Variable to DigitalOcean

### Method 1: DigitalOcean Dashboard (Easiest)

1. Log in to [DigitalOcean Dashboard](https://cloud.digitalocean.com/)
2. Click **Apps** in the left sidebar
3. Select your **billions-bounty** app
4. Click the **Settings** tab
5. Scroll down to **Environment Variables**
6. Click **Edit** next to "App-Level Environment Variables"
7. Click **Add Variable**
8. Add:
   - **Key:** `PAYMENT_MODE`
   - **Value:** `mock`
   - **Encrypt:** Unchecked (not sensitive)
   - **Scope:** All components
9. Click **Save**
10. DigitalOcean will automatically trigger a **redeploy** (takes 2-5 minutes)

### Method 2: Edit App Spec YAML

If you have an `app.yaml` or `.do/app.yaml` file:

```yaml
name: billions-bounty
services:
  - name: backend
    envs:
      - key: PAYMENT_MODE
        value: mock
      - key: DATABASE_URL
        value: ${DATABASE_URL}  # Existing vars
      # ... other environment variables
```

Then update via CLI:
```bash
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

### Method 3: DigitalOcean CLI (doctl)

```bash
# Install doctl
brew install doctl

# Authenticate
doctl auth init

# List your apps
doctl apps list

# Get app spec
doctl apps spec get YOUR_APP_ID > app.yaml

# Edit app.yaml and add PAYMENT_MODE=mock to envs

# Update the app
doctl apps update YOUR_APP_ID --spec app.yaml
```

## Verify the Fix

### 1. Check Backend Logs
After redeployment, check your DigitalOcean app logs:

```
✅ Loaded .env from: ...
💳 PAYMENT_MODE: mock
```

### 2. Check Frontend Console
When you open a bounty page and check NFT status, you should see:

```
🎨 MOCK NFT mode - using backend response
```

Instead of:

```
💎 REAL NFT mode - checking blockchain
Error: 403 Forbidden
```

### 3. Test API Directly
```bash
curl https://billions-bounty-iwnh3.ondigitalocean.app/api/nft/status/WaVZM6QGi8HyFVoUFTeU4pbP8jHVuJrgohPkLe1o8HH
```

Should return:
```json
{
  "success": true,
  "is_mock": true,
  "has_nft": false,
  "verified": false,
  "questions_remaining": 0
}
```

## Common Issues

### Issue: Still getting 500 error after adding env var
**Solution:** Make sure DigitalOcean finished redeploying. Check the **Activity** tab to see deployment status.

### Issue: Backend not picking up environment variable
**Solution:** 
1. Check that the variable is set at the **app level** or **component level** (not just in build env)
2. Make sure the variable name is exactly `PAYMENT_MODE` (case-sensitive)
3. Make sure the value is exactly `mock` (lowercase)

### Issue: Frontend still showing "REAL NFT mode"
**Solution:** 
1. Hard refresh the frontend (Cmd+Shift+R or Ctrl+Shift+R)
2. Clear browser cache
3. Check the API response directly with curl (see above)

## Production vs. Mock Mode

### Mock Mode (Current Setup)
- `PAYMENT_MODE=mock`
- No blockchain calls
- Instant verification
- Great for testing and development

### Real Mode (Future Production)
- `PAYMENT_MODE=real`
- Requires actual NFTs on Solana blockchain
- Needs deployed smart contracts
- Requires reliable Solana RPC provider
- Set when ready to go to production

## Need to Switch to Real Mode?

When ready for production with real NFTs:

1. Deploy NFT verification smart contract to Solana mainnet
2. Update `AUTHORIZED_NFT_MINT` in frontend code
3. Set up Solana RPC provider (Alchemy, QuickNode, etc.)
4. Update DigitalOcean env var: `PAYMENT_MODE=real`
5. Add `SOLANA_RPC_URL` env var with your paid RPC endpoint

