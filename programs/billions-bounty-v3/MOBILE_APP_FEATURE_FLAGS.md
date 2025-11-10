# Mobile App Feature Flag Integration

## Summary

**Good news: Your mobile app doesn't need ANY changes!** 🎉

The mobile app calls your **backend API**, not the smart contracts directly. Since all the feature flags are handled automatically in the backend, your mobile app automatically gets the benefits without any code changes.

---

## How It Works

### Mobile App Architecture

```
Mobile App (Kotlin/Android)
       ↓
   HTTP/REST API Calls
       ↓
Backend API (FastAPI/Python)
       ↓
Feature Flag Check (Automatic)
       ↓
Smart Contract (V3/V2/V1)
```

**Key Point**: Mobile app never directly calls contracts - it always goes through backend.

---

## Feature Flag Status for Mobile App

### ✅ Backend Flags (Fully Automatic)

These flags work automatically because the mobile app calls backend APIs:

| Flag | Backend Auto? | Mobile App Needs Changes? |
|------|---------------|---------------------------|
| `USE_CONTRACT_V3` | ✅ Yes | ❌ No - Backend handles it |
| `USE_CONTRACT_V2` | ✅ Yes | ❌ No - Backend handles it |
| `ENABLE_MULTI_PERSONALITY` | ✅ Yes | ❌ No - Backend handles it |
| `ENABLE_KORA_SDK` | ✅ Yes | ❌ No - Backend handles it |

**How it works:**
- Mobile app calls: `POST /api/payment/create`
- Backend checks `USE_CONTRACT_V3` flag
- Backend automatically uses V3/V2/V1
- Mobile app doesn't know or care which version is used

### ❓ Frontend-Specific Flags

These are frontend-only and don't apply to mobile:

| Flag | Applies to Mobile? | Reason |
|------|-------------------|--------|
| `NEXT_PUBLIC_ENABLE_ACTIVITY_TRACKER` | ❓ Maybe | Only if you want activity tracker in mobile UI |
| `NEXT_PUBLIC_USE_CONTRACT_V3` | ❌ No | Mobile doesn't build transactions client-side |

---

## What Mobile App Actually Uses

### 1. Payment Flow

**Mobile App Flow:**
```kotlin
// PaymentViewModel.kt
apiRepository.createPayment(
    walletAddress = walletAddress,
    amountUsd = amount,
    paymentMethod = "wallet"
)
```

**Backend Handles:**
```python
# main.py - /api/payment/create
if USE_CONTRACT_V3:
    # Uses V3 adapter automatically
elif USE_CONTRACT_V2:
    # Uses V2 automatically
else:
    # Uses V1 automatically
```

**Result**: Mobile app gets V3/V2/V1 automatically based on backend flag! ✅

### 2. Chat Flow

**Mobile App Flow:**
```kotlin
// ChatViewModel.kt
apiRepository.sendChatMessage(
    bountyId = bountyId,
    message = message
)
```

**Backend Handles:**
```python
# main.py - /api/bounty/{bounty_id}/chat
if ENABLE_MULTI_PERSONALITY and multi_agent:
    chat_result = await multi_agent.chat(...)  # Multi-personality
else:
    chat_result = await agent.chat(...)  # Single personality
```

**Result**: Mobile app gets multi-personality automatically based on backend flag! ✅

### 3. Kora Fee Abstraction

**Mobile App Flow:**
```kotlin
// Calls backend API (if implemented)
apiRepository.signTransaction(...)
```

**Backend Handles:**
```python
# app_integration.py
if ENABLE_KORA_SDK:
    app.include_router(kora_router)  # Kora endpoints available
```

**Result**: Mobile app can use Kora endpoints if backend flag is enabled! ✅

---

## What Mobile App Doesn't Need

### ❌ No Contract Version Selection

**Frontend (Web)** needs to know:
- Which contract to call (V3/V2/V1)
- Which PDAs to derive
- Which instruction format to use

**Mobile App** doesn't need to know:
- It just calls `/api/payment/create`
- Backend figures out which contract to use

### ❌ No Client-Side Transaction Building

**Frontend (Web)** builds transactions:
```typescript
// Frontend builds transaction client-side
processV3EntryPayment(...)  // Builds transaction in browser
```

**Mobile App** doesn't build transactions:
```kotlin
// Mobile app just calls backend
apiRepository.createPayment(...)  // Backend builds transaction
```

---

## Activity Tracker for Mobile

**Question**: Should mobile app have activity tracker?

**Answer**: If you want activity tracker in mobile UI, you'd need to:

1. **Backend**: Already supports activity tracking (no changes needed)
2. **Mobile**: Would need to add UI components to display activities

But this is **optional** - you can deploy mobile app without it.

**If you want to add it:**
- Backend already returns activity data
- Mobile just needs UI components to display it
- No feature flag needed in mobile (it's a UI feature)

---

## Configuration for Mobile App

### Required Configuration

**NetworkModule.kt** - Only needs backend URL:
```kotlin
private const val BASE_URL = "http://192.168.0.206:8000/"  // Or production URL
```

**That's it!** The mobile app doesn't need any feature flag configuration.

### Backend Configuration (Separate)

Backend needs the flags (in `.env` or DigitalOcean):
```bash
USE_CONTRACT_V3=true
USE_CONTRACT_V2=false
ENABLE_MULTI_PERSONALITY=true
ENABLE_KORA_SDK=false
```

But mobile app doesn't need to know about these! ✅

---

## Summary

| Feature | Mobile App Ready? | Why |
|---------|------------------|-----|
| **V3 Contract** | ✅ Yes | Backend auto-routes |
| **V2 Contract** | ✅ Yes | Backend auto-routes |
| **Multi-Personality** | ✅ Yes | Backend auto-routes |
| **Kora SDK** | ✅ Yes | Backend endpoints auto-available |
| **Activity Tracker** | ⚠️ Optional | UI feature, backend already supports |

**Conclusion**: Your mobile app is **100% ready** for all backend feature flags. Just configure the backend flags, and mobile app automatically gets the features! 🎉

No code changes needed in mobile app! ✨

