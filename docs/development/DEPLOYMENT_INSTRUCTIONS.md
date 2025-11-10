# Step-by-Step Deployment Instructions for V2 Staging

**Current Status**: ✅ V2 contract deployed to devnet, code pushed to GitHub  
**Your Location**: Local Mac (`/Users/jaybrantley/myenv/Hackathon/Billions_Bounty`)  
**What's Left**: Deploy backend and frontend to staging environments

---

## 🎯 Overview

You have **3 environments**:
1. **Your Local Mac** - Where you develop (you are here now)
2. **DigitalOcean Server** - Where your backend runs
3. **Vercel** - Where your frontend is hosted

---

## Part 1: Verify Everything is Ready (On Your Mac)

Run this command on your Mac to make sure everything passes:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty && ./scripts/staging/validate_v2_deployment.sh
```

**Expected Output**: `🎉 All validations passed! (6/6)`

If this fails, stop and fix issues before proceeding.

---

## Part 2: Deploy Backend to DigitalOcean

### Step 2.1: Get Your Server Information

You need to know:
- **Server IP Address**: 162.159.140.98
- **SSH Username**: jaybrantley
- **Backend Directory Path**: Where your backend code lives on the server

**Don't know these?** Check:
- DigitalOcean dashboard for IP address
- Your previous SSH commands for username
- Run `pwd` after SSHing to see current directory

### Step 2.2: SSH into Your DigitalOcean Server

**On your Mac terminal**, run:

```bash
ssh jaybrantley@162.159.140.98
```

**Example**:
```bash
ssh root@123.45.67.89
```

**Troubleshooting**:
- If it asks for a password, enter it
- If it asks "Are you sure you want to continue connecting?", type `yes`
- If you use SSH keys, make sure they're set up

### Step 2.3: Navigate to Your Backend Directory

**Once connected to the server**, run:

```bash
cd /path/to/your/backend
```

**Don't know the path?** Try:
```bash
# Common locations:
cd ~/backend
# OR
cd /var/www/backend
# OR
cd /home/YOUR_USERNAME/backend
```

To find it, you can run:
```bash
find ~ -name "package.json" -o -name "requirements.txt" 2>/dev/null | head -10
```

### Step 2.4: Pull the Latest Code

**On the server**, run:

```bash
git pull origin staging-v2
```

**Expected Output**: Should show files being updated

**Troubleshooting**:
- If it says "fatal: not a git repository", you're in the wrong directory
- If it says "Permission denied", you may need to set up SSH keys for GitHub on the server

### Step 2.5: Add Environment Variables

**On the server**, edit your `.env` file:

```bash
nano .env
```

**Add these lines** (or update if they exist):

```
USE_CONTRACT_V2=false
LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
V2_GLOBAL_PDA=BursCahsMxKjiSUgTCy11uUTWnaZ1eqcGcADUxiMzHMb
V2_BOUNTY_1_PDA=2J455GTdBfceWWUF7dcPawixW4PEfWBdVgX7Soqc3trb
V2_USDC_MINT=JBJctjHYUCMBhQQQdmDm9CFmiLQou7siDRwhn2EUGEKh
V2_BOUNTY_POOL_WALLET=CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF
V2_OPERATIONAL_WALLET=46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D
V2_BUYBACK_WALLET=7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya
V2_STAKING_WALLET=Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX
SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
```

**To save in nano**:
1. Press `Ctrl + O` (to write)
2. Press `Enter` (to confirm)
3. Press `Ctrl + X` (to exit)

**Alternative**: If you don't have a `.env` file, create it:
```bash
touch .env
nano .env
```

### Step 2.6: Restart Your Backend Service

**On the server**, restart your backend:

**If using PM2**:
```bash
pm2 restart backend
```

**If using systemd**:
```bash
sudo systemctl restart your-backend-service
```

**If running directly**:
```bash
# Stop the current process (Ctrl+C if running in foreground)
# Then restart it
python3 app.py
# OR
npm start
```

**Don't know which?** Check what's running:
```bash
pm2 list
# OR
systemctl list-units | grep backend
# OR
ps aux | grep python
```

### Step 2.7: Check Logs

**On the server**, verify it started correctly:

**If using PM2**:
```bash
pm2 logs backend --lines 50
```

**If using systemd**:
```bash
sudo journalctl -u your-backend-service -n 50
```

**Look for**:
- ✅ "Server started" or similar message
- ✅ No errors about missing environment variables
- ✅ No Python/Node errors

### Step 2.8: Test the Backend

**On the server** (or from your Mac), test that it's responding:

```bash
curl http://localhost:PORT/health
```

Replace `PORT` with your backend port (commonly 3000, 5000, 8000, etc.)

**Expected**: Should return a success response

### Step 2.9: Exit the Server

**On the server**, disconnect:

```bash
exit
```

You should now be back on your Mac.

---

## Part 3: Deploy Frontend to Vercel

### Step 3.1: Go to Vercel Dashboard

1. Open your browser
2. Go to https://vercel.com
3. Log in
4. Find your project (Billions Bounty or similar)

### Step 3.2: Add Environment Variables

1. Click on your project
2. Click **Settings** (top menu)
3. Click **Environment Variables** (left sidebar)
4. For each variable below, click **Add New**:

**Add these variables**:

| Key | Value | Environment |
|-----|-------|-------------|
| `NEXT_PUBLIC_USE_CONTRACT_V2` | `false` | Preview |
| `NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2` | `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm` | Preview |

**Important**: Select **Preview** environment (not Production)

### Step 3.3: Deploy the Branch

**Option A: Automatic (if GitHub integration is set up)**:
1. Vercel should automatically detect the new `staging-v2` branch
2. It will create a preview deployment
3. Wait for it to finish (usually 2-5 minutes)

**Option B: Manual**:
1. Click **Deployments** (top menu)
2. Click **Deploy** button
3. Select branch: `staging-v2`
4. Click **Deploy**

### Step 3.4: Get the Preview URL

1. Once deployed, Vercel will show a URL like:
   - `https://your-project-staging-v2.vercel.app`
   - Or `https://your-project-git-staging-v2-yourname.vercel.app`
2. **Copy this URL** - you'll need it for testing

### Step 3.5: Test the Frontend

1. Open the preview URL in your browser
2. Check that:
   - ✅ Site loads without errors
   - ✅ No console errors (open DevTools with F12)
   - ✅ Existing features work

---

## Part 4: Smoke Testing (V2 Disabled)

### Test 4.1: Backend Health Check

**On your Mac**, test the backend:

```bash
curl https://your-backend-staging-url.com/health
```

**Expected**: Success response

### Test 4.2: Frontend Loads

1. Open the Vercel preview URL
2. Navigate through the site
3. Test existing lottery features
4. **Should work exactly as before** (V2 is disabled)

### Test 4.3: Check for Errors

**Backend**:
```bash
ssh YOUR_USERNAME@YOUR_SERVER_IP
pm2 logs backend --lines 100 | grep -i error
exit
```

**Frontend**:
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

**If you see errors**: Stop and investigate before enabling V2

---

## Part 5: Enable V2 (After Smoke Tests Pass)

### Step 5.1: Enable on Backend

**SSH to server**:
```bash
ssh YOUR_USERNAME@YOUR_SERVER_IP
cd /path/to/your/backend
nano .env
```

**Change this line**:
```
USE_CONTRACT_V2=false
```

**To**:
```
USE_CONTRACT_V2=true
```

**Save** (Ctrl+O, Enter, Ctrl+X)

**Restart**:
```bash
pm2 restart backend
```

**Check logs**:
```bash
pm2 logs backend --lines 50
```

**Exit**:
```bash
exit
```

### Step 5.2: Enable on Frontend (Optional for Now)

1. Go to Vercel Dashboard
2. Settings → Environment Variables
3. Find `NEXT_PUBLIC_USE_CONTRACT_V2`
4. Change value from `false` to `true`
5. Redeploy the `staging-v2` branch

**Note**: You can leave frontend at `false` initially and just test backend

---

## Part 6: Test V2 Features

### Test 6.1: Entry Payment

**On your Mac**, test an entry payment:

```bash
curl -X POST https://your-backend-staging-url.com/api/entry \
  -H "Content-Type: application/json" \
  -d '{"bounty_id": 1, "amount": 10000000, "user_wallet": "YOUR_TEST_WALLET"}'
```

**Expected**: Success response with transaction signature

### Test 6.2: Verify On-Chain

1. Copy the transaction signature from the response
2. Go to: https://explorer.solana.com/?cluster=devnet
3. Paste the signature in the search box
4. Verify:
   - ✅ Transaction succeeded
   - ✅ 4 token transfers (60/20/10/10 split)
   - ✅ Correct amounts to each wallet

### Test 6.3: Check Wallet Balances

**On your Mac**:

```bash
# Check bounty pool wallet
solana balance CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF --url devnet

# Check operational wallet  
solana balance 46efqh88qk2szzH3WGtk8Pv8dQtAve6NjsqTB9dtoR2D --url devnet

# Check buyback wallet
solana balance 7iVPm2STfZUxryYGkctM924M5bP3ZFiozzUb1TTUGjya --url devnet

# Check staking wallet
solana balance Fzj8pyBehQQ3Tu1h5fb6RRqtphVBzPbB9srAw1P5q6WX --url devnet
```

**Expected**: Balances should reflect the 60/20/10/10 split

---

## Part 7: Monitor for 24 Hours

### What to Monitor

**Backend Logs** (check every few hours):
```bash
ssh YOUR_USERNAME@YOUR_SERVER_IP
pm2 logs backend --lines 100
exit
```

**Look for**:
- ❌ Errors related to V2
- ❌ Failed transactions
- ❌ Timeout errors
- ✅ Successful entry payments

**Frontend** (check periodically):
- Open the preview URL
- Check browser console for errors
- Test user flows

**Solana Explorer**:
- Check recent transactions for your wallets
- Verify splits are correct

---

## Part 8: Rollback (If Issues Occur)

### Quick Rollback

**If anything goes wrong**:

1. **SSH to server**:
   ```bash
   ssh YOUR_USERNAME@YOUR_SERVER_IP
   cd /path/to/your/backend
   nano .env
   ```

2. **Change**:
   ```
   USE_CONTRACT_V2=true
   ```
   **To**:
   ```
   USE_CONTRACT_V2=false
   ```

3. **Restart**:
   ```bash
   pm2 restart backend
   exit
   ```

4. **Verify** existing features work again

---

## Troubleshooting

### "Command not found: pm2"

**You're on your Mac** - these commands are for the server. SSH first:
```bash
ssh YOUR_USERNAME@YOUR_SERVER_IP
```

### "Permission denied"

**On server**, you may need `sudo`:
```bash
sudo pm2 restart backend
```

### "Cannot find module"

**On server**, install dependencies:
```bash
npm install
# OR
pip3 install -r requirements.txt
```

### "Port already in use"

**On server**, kill the old process:
```bash
pm2 delete backend
pm2 start your-app.js --name backend
```

### Backend not responding

**Check if it's running**:
```bash
ssh YOUR_USERNAME@YOUR_SERVER_IP
pm2 list
# OR
ps aux | grep python
```

---

## Quick Reference

### Your Key Information

Fill this in for quick reference:

- **Server IP**: `_________________`
- **SSH Username**: `_________________`
- **Backend Directory**: `_________________`
- **Backend Port**: `_________________`
- **Vercel Project**: `_________________`
- **Vercel Preview URL**: `_________________`

### Important Addresses

- **Program ID**: `HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm`
- **Bounty Pool**: `CaCqZkMC8uH2YD9Bq8XwxM41TiamXz4oHGzknmP6TAQF`
- **Solana Explorer**: https://explorer.solana.com/?cluster=devnet

---

## Summary Checklist

- [ ] Part 1: Validation passed on Mac
- [ ] Part 2: Backend deployed to DigitalOcean
- [ ] Part 3: Frontend deployed to Vercel
- [ ] Part 4: Smoke tests passed (V2 disabled)
- [ ] Part 5: V2 enabled on backend
- [ ] Part 6: V2 features tested successfully
- [ ] Part 7: Monitoring for 24 hours
- [ ] Part 8: Rollback plan ready (if needed)

---

**Need Help?**
- Check `V2_COMPLETION_REPORT.md` for technical details
- Check `STAGING_CHECKLIST.md` for additional context
- Review logs on both server and browser console

**Last Updated**: October 30, 2024



