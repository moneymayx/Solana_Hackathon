# Frontend Deployment Fix Guide

**Date**: October 31, 2025  
**Issue**: Vercel deployment returns 404 for all routes  
**Status**: 🔧 NEEDS FIX

---

## 🔍 Problem Diagnosis

### Current Status:
- **URL**: `https://billions-bounty.vercel.app`
- **Error**: `DEPLOYMENT_NOT_FOUND`
- **HTTP Status**: 404 for all routes
- **Vercel Headers**: Present (deployment exists)

### Root Cause:
The Vercel project exists but is not properly deployed. Possible reasons:
1. Build failed
2. No recent deployments
3. Project not linked to GitHub repository
4. Wrong branch configured
5. Build configuration missing

---

## ✅ Solution Steps

### Step 1: Check Vercel Dashboard

1. **Go to Vercel Dashboard**:
   - URL: https://vercel.com/dashboard
   - Login with your account

2. **Find Your Project**:
   - Look for "billions-bounty" or similar
   - Check if it exists

3. **Check Deployment Status**:
   - Click on the project
   - Look at "Deployments" tab
   - Check for:
     - Recent deployments
     - Build errors
     - Failed deployments

---

### Step 2: Verify GitHub Integration

1. **Check Git Connection**:
   - In Vercel project settings
   - Go to "Git" tab
   - Verify:
     - ✅ Connected to `moneymayx/Solana_Hackathon`
     - ✅ Correct branch (main or staging-v2)
     - ✅ Auto-deploy enabled

2. **If Not Connected**:
   - Click "Connect Git Repository"
   - Select your GitHub repo
   - Choose branch: `staging-v2` for staging or `main` for production

---

### Step 3: Configure Build Settings

1. **Go to Project Settings → General**

2. **Set Build & Development Settings**:
   ```
   Framework Preset: Next.js
   Root Directory: frontend/
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

3. **Node.js Version**:
   ```
   Node.js Version: 20.x
   ```

---

### Step 4: Add Environment Variables

1. **Go to Project Settings → Environment Variables**

2. **Add These Variables** (for all environments):
   ```bash
   # Backend API
   NEXT_PUBLIC_API_URL=https://billions-bounty-iwnh3.ondigitalocean.app
   
   # V2 Smart Contract (initially false)
   NEXT_PUBLIC_USE_CONTRACT_V2=false
   NEXT_PUBLIC_LOTTERY_PROGRAM_ID_V2=HDAfSw1n9o9iZynfEP54tnCf2KRa2cPVFnpTRFtM7Cfm
   
   # Solana Network
   NEXT_PUBLIC_SOLANA_NETWORK=devnet
   NEXT_PUBLIC_SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com
   ```

3. **Apply to**:
   - ✅ Production
   - ✅ Preview
   - ✅ Development

---

### Step 5: Trigger New Deployment

#### Option A: Via Vercel Dashboard
1. Go to "Deployments" tab
2. Click "Redeploy" on the latest deployment
3. Or click "Deploy" → "Create Deployment"

#### Option B: Via Git Push
1. Make a small change to trigger deployment:
   ```bash
   cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
   
   # Create a deployment trigger file
   echo "# Deployment trigger $(date)" >> frontend/README.md
   
   # Commit and push
   git add frontend/README.md
   git commit -m "trigger: Redeploy frontend to Vercel"
   git push origin staging-v2
   ```

2. Vercel will automatically detect the push and deploy

#### Option C: Via Vercel CLI
```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend
vercel --prod
```

---

### Step 6: Monitor Build Progress

1. **Watch Build Logs**:
   - In Vercel dashboard → Deployments
   - Click on the running deployment
   - Watch "Build Logs" tab

2. **Look for Errors**:
   - TypeScript errors
   - Missing dependencies
   - Environment variable issues
   - Build failures

3. **Common Issues**:
   - **Missing dependencies**: Run `npm install` locally first
   - **TypeScript errors**: Check `npm run build` locally
   - **Environment variables**: Ensure all required vars are set

---

### Step 7: Verify Deployment

Once deployment completes:

1. **Check Deployment URL**:
   ```bash
   curl -I https://billions-bounty.vercel.app/
   ```
   - Should return HTTP 200
   - Should have HTML content

2. **Test Homepage**:
   - Open https://billions-bounty.vercel.app/ in browser
   - Should load the homepage
   - No 404 errors

3. **Test API Connection**:
   - Check if frontend can reach backend
   - Look for CORS errors in browser console
   - Verify API calls work

---

## 🛠️ Alternative: Deploy from Scratch

If the above doesn't work, create a new Vercel project:

### 1. Remove Old Project (if needed)
- In Vercel dashboard
- Project Settings → Advanced → Delete Project

### 2. Create New Project
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select `moneymayx/Solana_Hackathon`
4. Configure:
   ```
   Project Name: billions-bounty
   Framework: Next.js
   Root Directory: frontend/
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

5. Add environment variables (see Step 4 above)

6. Click "Deploy"

---

## 🧪 Local Testing First

Before deploying to Vercel, test locally:

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend

# Install dependencies
npm install

# Build
npm run build

# Start production server
npm run start

# Test
curl http://localhost:3000/
```

If local build fails, fix errors before deploying to Vercel.

---

## 📋 Checklist

### Pre-Deployment:
- [ ] Frontend builds locally without errors
- [ ] All dependencies installed
- [ ] TypeScript compiles successfully
- [ ] No linter errors

### Vercel Configuration:
- [ ] Project exists in Vercel dashboard
- [ ] GitHub repository connected
- [ ] Correct branch selected (staging-v2 or main)
- [ ] Build settings configured
- [ ] Environment variables added
- [ ] Auto-deploy enabled

### Post-Deployment:
- [ ] Deployment succeeded
- [ ] Homepage loads (HTTP 200)
- [ ] No 404 errors
- [ ] API calls work
- [ ] No CORS errors
- [ ] Wallet connection works

---

## 🚨 Troubleshooting

### Build Fails with TypeScript Errors
```bash
# Fix TypeScript errors locally first
cd frontend
npm run build

# Fix any errors shown
# Then commit and push
```

### Build Fails with Missing Dependencies
```bash
# Ensure package-lock.json is committed
cd frontend
npm install
git add package-lock.json
git commit -m "fix: Update package-lock.json"
git push
```

### Environment Variables Not Working
- Ensure variables start with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding/changing variables
- Check "Environment Variables" tab in Vercel

### CORS Errors
- Backend should have `access-control-allow-origin: *` (already configured)
- Check `NEXT_PUBLIC_API_URL` points to correct backend

### 404 on All Routes
- Check "Root Directory" is set to `frontend/`
- Verify `Output Directory` is `.next`
- Ensure `next.config.ts` doesn't have routing issues

---

## 📞 Quick Commands

### Test Deployment Status:
```bash
curl -I https://billions-bounty.vercel.app/
```

### Trigger Redeploy:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
echo "# Deploy $(date)" >> frontend/README.md
git add frontend/README.md
git commit -m "trigger: Redeploy frontend"
git push origin staging-v2
```

### Check Build Locally:
```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend
npm run build
```

---

## ✅ Success Criteria

Deployment is successful when:
1. ✅ Homepage returns HTTP 200
2. ✅ No 404 errors on main routes
3. ✅ Frontend can call backend API
4. ✅ Wallet connection works
5. ✅ No console errors
6. ✅ All pages load correctly

---

## 📝 Next Steps After Fix

Once frontend is deployed:
1. Enable V2 on frontend (`NEXT_PUBLIC_USE_CONTRACT_V2=true`)
2. Test V2 entry payment flow
3. Verify 4-way split works
4. Test all user flows end-to-end

---

**Need Help?**
- Check Vercel docs: https://vercel.com/docs
- Check build logs in Vercel dashboard
- Test locally first: `npm run build`

