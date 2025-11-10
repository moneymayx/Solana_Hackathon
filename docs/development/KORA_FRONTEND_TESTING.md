# Testing Kora SDK on the Frontend

This guide explains how to verify that the Kora SDK is working correctly from the frontend.

## Quick Test Methods

### Method 1: Browser Console (Easiest)

Open your browser's developer console (F12) on any page and run:

```javascript
// Check Kora SDK status
fetch('http://localhost:8000/api/sdk-test/kora/status')
  .then(r => r.json())
  .then(data => console.log('✅ Kora Status:', data))
  .catch(err => console.error('❌ Error:', err));

// Get Kora configuration
fetch('http://localhost:8000/api/sdk-test/kora/config')
  .then(r => r.json())
  .then(data => console.log('✅ Kora Config:', data))
  .catch(err => console.error('❌ Error:', err));

// Get supported tokens
fetch('http://localhost:8000/api/sdk-test/kora/supported-tokens')
  .then(r => r.json())
  .then(data => console.log('✅ Supported Tokens:', data))
  .catch(err => console.error('❌ Error:', err));
```

**What to look for:**

✅ **Success Indicators:**
- Status endpoint returns `{"enabled": true, ...}`
- Config endpoint returns Kora server configuration
- Supported tokens returns list like `["USDC", "USDT", "SOL"]`

❌ **Failure Indicators:**
- Network errors (backend not running)
- `{"detail": "Kora SDK is disabled"}` (need `ENABLE_KORA_SDK=true`)
- `{"error": "Kora CLI not found"}` (need to install `kora-cli`)

---

### Method 2: Test API Page

Visit: `http://localhost:3000/test-api`

The test page now includes a "Kora SDK Tests" section with buttons to test all endpoints.

**Steps:**
1. Make sure backend is running: `./start_server.sh`
2. Make sure `ENABLE_KORA_SDK=true` in backend `.env`
3. Visit `http://localhost:3000/test-api`
4. Click Kora SDK test buttons
5. Check results displayed on the page

---

### Method 3: Using the API Client Utility

In your React components or utils, you can use the existing `backendFetch` utility:

```typescript
import { backendFetch } from '@/lib/api/client';

// Check status
const status = await backendFetch('/api/sdk-test/kora/status');
console.log('Kora enabled:', status.enabled);

// Get config
const config = await backendFetch('/api/sdk-test/kora/config');

// Get supported tokens
const tokens = await backendFetch('/api/sdk-test/kora/supported-tokens');
```

---

## Expected Responses

### ✅ Status Endpoint (`GET /api/sdk-test/kora/status`)

**Success Response:**
```json
{
  "enabled": true,
  "rpc_url": "https://api.devnet.solana.com",
  "private_key_configured": true,
  "cli_path": "kora-cli"
}
```

**Failure Response (disabled):**
```json
{
  "enabled": false,
  "rpc_url": "http://127.0.0.1:8899",
  "private_key_configured": false,
  "cli_path": "kora-cli"
}
```

---

### ✅ Config Endpoint (`GET /api/sdk-test/kora/config`)

**Success Response:**
```json
{
  "success": true,
  "result": {
    "supported_tokens": ["USDC", "USDT"],
    "rpc_url": "https://api.devnet.solana.com",
    ...
  }
}
```

**Error Response (Kora CLI not found):**
```json
{
  "success": false,
  "error": "Kora CLI not found. Install with: cargo install kora-cli"
}
```

---

### ✅ Supported Tokens (`GET /api/sdk-test/kora/supported-tokens`)

**Success Response:**
```json
{
  "supported_tokens": ["USDC", "USDT", "SOL"],
  "default_token": "USDC"
}
```

**Fallback Response (if Kora server query fails):**
```json
{
  "supported_tokens": ["USDC", "USDT", "SOL"],
  "default_token": "USDC",
  "note": "Using fallback tokens - Kora server query failed"
}
```

---

## Troubleshooting

### ❌ Backend Not Responding

**Symptoms:**
- Network errors in console
- `Failed to fetch` errors

**Fix:**
1. Check if backend is running: `curl http://localhost:8000/api/health`
2. Start backend: `./start_server.sh`
3. Check backend logs for errors

---

### ❌ Kora SDK Disabled

**Symptoms:**
- Status shows `"enabled": false`
- Endpoints return `{"detail": "Kora SDK is disabled"}`

**Fix:**
1. Add to backend `.env`:
   ```bash
   ENABLE_KORA_SDK=true
   KORA_PRIVATE_KEY=your_base58_private_key
   KORA_RPC_URL=https://api.devnet.solana.com
   ```
2. Restart backend server

---

### ❌ Kora CLI Not Found

**Symptoms:**
- Error: `"Kora CLI not found. Install with: cargo install kora-cli"`

**Fix:**
```bash
cargo install kora-cli
```

Verify installation:
```bash
kora-cli --version
```

---

### ❌ CORS Errors

**Symptoms:**
- `CORS policy: No 'Access-Control-Allow-Origin' header`

**Fix:**
- Backend should already handle CORS
- Check backend `main.py` has CORS middleware configured
- Ensure backend is running on `http://localhost:8000`

---

## Integration Testing

Once basic endpoints work, test the full flow:

### 1. Build a Transaction

```typescript
import { Transaction } from '@solana/web3.js';

// Your payment transaction (example from V2 processor)
const transaction = new Transaction();
// ... add instructions ...

// Serialize to base64
const transactionBase64 = Buffer.from(transaction.serialize({ requireAllSignatures: false })).toString('base64');
```

### 2. Send to Kora for Fee Abstraction

```typescript
const result = await backendFetch('/api/sdk-test/kora/sign-and-send', {
  method: 'POST',
  body: JSON.stringify({
    transaction_base64: transactionBase64
  })
});

console.log('Transaction signed and sent:', result);
```

### 3. Verify Success

Check for:
- `result.success === true`
- `result.signature` exists (transaction signature)
- Transaction appears on Solana Explorer

---

## Next Steps

Once Kora SDK is verified working:

1. **Integrate into Payment Flow:**
   - Update `frontend/src/lib/v2/paymentProcessor.ts`
   - Replace user wallet signing with Kora signing
   - Users pay fees in USDC instead of SOL

2. **Add UI Indicators:**
   - Show "Pay fees in USDC" badge when Kora is enabled
   - Display fee estimates in USDC

3. **Error Handling:**
   - Gracefully fallback to regular signing if Kora fails
   - Show user-friendly error messages

---

## Summary Checklist

Use this checklist to verify Kora SDK is working:

- [ ] Backend is running and accessible
- [ ] `ENABLE_KORA_SDK=true` in backend `.env`
- [ ] Status endpoint returns `enabled: true`
- [ ] Config endpoint returns valid configuration
- [ ] Supported tokens endpoint returns token list
- [ ] No CORS errors in browser console
- [ ] Kora CLI installed (if using CLI mode)

Once all checked, Kora SDK is ready for integration! 🎉

