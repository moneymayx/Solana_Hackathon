# V3 Environment Variable Troubleshooting

## Why the Checker Might Show "Disabled" Even When It's Set

**The Problem:** Next.js embeds `NEXT_PUBLIC_*` environment variables at build time. The browser can't directly read your `.env.local` file - it only sees what was embedded when the dev server started.

**The Solution:** The real test is whether V3 components actually render, not what `process.env` shows in the browser.

---

## Quick Fixes

### ✅ Fix 1: Verify File Location and Format

**File must be:** `Billions_Bounty/frontend/.env.local`

**Format must be exactly:**
```bash
NEXT_PUBLIC_USE_CONTRACT_V3=true
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

**Common mistakes:**
- ❌ `.env` (wrong - should be `.env.local`)
- ❌ `NEXT_PUBLIC_USE_CONTRACT_V3 = true` (spaces around `=`)
- ❌ `NEXT_PUBLIC_USE_CONTRACT_V3="true"` (quotes not needed)
- ❌ `USE_CONTRACT_V3=true` (missing `NEXT_PUBLIC_` prefix)
- ❌ File in wrong directory (must be in `frontend/` folder)

---

### ✅ Fix 2: Restart Dev Server

**Critical:** Next.js reads `.env.local` only when the server starts.

```bash
# Stop the server (Ctrl+C)
# Then restart
cd frontend
npm run dev
```

**If you changed `.env.local` while server was running:**
1. Stop server (Ctrl+C)
2. Wait a few seconds
3. Start again (`npm run dev`)

---

### ✅ Fix 3: Clear Next.js Cache

Sometimes Next.js caches environment variables:

```bash
cd frontend
rm -rf .next
npm run dev
```

This clears the build cache and forces Next.js to re-read environment variables.

---

### ✅ Fix 4: Hard Refresh Browser

After restarting server:

1. **Chrome/Edge:** `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. **Firefox:** `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (Mac)
3. **Or:** Clear browser cache manually

---

## How to Actually Verify V3 is Working

### Method 1: Look for the Badge (Best Test)

**If you see this on the page:**
```
🔒 Using V3 (Secure)
```

**Then V3 IS working!** Even if the environment variable checker says "disabled".

---

### Method 2: Check Browser Console

Open browser console (F12) and look for:

**✅ Working:**
```
🔒 Using V3 payment processor (secure) - AUTOMATIC ROUTING
```

**❌ Not working:**
```
🆕 Using V2 payment processor (parallel) - AUTOMATIC ROUTING
```
or
```
📌 V1 contract requires backend API
```

---

### Method 3: Check Component Rendering

In browser console, run:

```javascript
// Check what PaymentMethodSelector sees
const v3Flag = process.env.NEXT_PUBLIC_USE_CONTRACT_V3;
console.log('V3 Flag:', v3Flag);

// Check if V3 badge exists
const hasBadge = Array.from(document.querySelectorAll('*')).some(
  el => el.textContent?.includes('🔒 Using V3')
);
console.log('V3 Badge visible:', hasBadge);
```

**If badge is visible but env var is undefined, V3 is still working** - Next.js just embedded it differently.

---

## Step-by-Step Debugging

### Step 1: Verify File Exists and Format

```bash
# In frontend directory
cat .env.local | grep USE_CONTRACT
```

Should show:
```
NEXT_PUBLIC_USE_CONTRACT_V3=true
NEXT_PUBLIC_USE_CONTRACT_V2=false
```

---

### Step 2: Verify Server Read It

When you start `npm run dev`, check the terminal output. Next.js logs environment variables in development (though it hides values).

**Look for:**
- No errors about `.env.local`
- Server starts successfully

---

### Step 3: Check Component Behavior

1. Go to `http://localhost:3000/test-v3`
2. Look at the payment buttons
3. **Do you see "🔒 Using V3 (Secure)" badge?**

**If YES:** V3 is working! ✅ (Ignore the env var checker)

**If NO:** Continue to Step 4

---

### Step 4: Check Console Logs

1. Open browser console (F12)
2. Click the "Component Rendering Check" button
3. Look at console output

**What to look for:**
```javascript
// PaymentMethodSelector logs
const USE_V3 = process.env.NEXT_PUBLIC_USE_CONTRACT_V3 === "true";
console.log('USE_V3:', USE_V3);
```

**If this logs `false` or `undefined`:**
- Env var not picked up
- Need to restart server

---

## Common Issues and Solutions

### Issue: "Env var is undefined in browser"

**Cause:** Next.js didn't pick it up or server wasn't restarted.

**Solution:**
1. Verify `.env.local` exists and has correct format
2. Stop server completely
3. Run `rm -rf .next` to clear cache
4. Restart server
5. Hard refresh browser

---

### Issue: "Env var shows true but V3 badge doesn't appear"

**Possible causes:**
1. Component not using the flag correctly
2. Cached component rendering V2

**Solution:**
1. Check `PaymentMethodSelector.tsx` - does it check `USE_V3`?
2. Clear browser cache
3. Restart server

---

### Issue: "Both V2 and V3 seem active"

**Cause:** Both flags might be true, or priority not working.

**Solution:**
1. Make sure `NEXT_PUBLIC_USE_CONTRACT_V2=false`
2. Priority is V3 > V2 > V1
3. If V3 is true, V2 is ignored (this is correct behavior)

---

## The Real Test: Does It Work?

**Ultimately, the question is:** When you click "Pay", does it use V3?

**Check:**
1. Console shows "Using V3 payment processor"
2. Transaction uses V3 program ID
3. Solana Explorer shows V3 contract

**If all three are true, V3 is working - regardless of what `process.env` shows!**

---

## Alternative: Set Env Var at Runtime

If `.env.local` isn't working, you can temporarily set it when starting:

```bash
NEXT_PUBLIC_USE_CONTRACT_V3=true npm run dev
```

Or in PowerShell (Windows):
```powershell
$env:NEXT_PUBLIC_USE_CONTRACT_V3="true"; npm run dev
```

---

## Summary

**The environment variable checker can be misleading** because:
- Next.js embeds env vars at build time
- Browser can't directly read your `.env.local` file
- Caching can cause stale values

**The real test is:**
1. ✅ Do you see "🔒 Using V3 (Secure)" badge?
2. ✅ Does console show "Using V3 payment processor"?
3. ✅ Does transaction use V3 program ID?

**If yes to all three, V3 is working!** 🎉

Ignore the env var checker if components show V3 badge.

