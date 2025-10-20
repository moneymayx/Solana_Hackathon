# ✅ TESTING CHECKLIST - Quick Reference

**Both servers are running!** 🎉

---

## 🌐 Quick Links

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | http://localhost:8000/docs | ✅ Running |
| **Frontend** | http://localhost:3000 | ✅ Running |

---

## 🧪 Test in This Order:

### **1️⃣ API Test Page** (⏱️ 5 min)
```
http://localhost:3000/test-api
```
- [ ] Click "Check Health" for Context → Should return green ✅
- [ ] Click "Check Health" for Token → Should return green ✅
- [ ] Click "Check Health" for Teams → Should return green ✅
- [ ] Click "Get Discounts" → Should show 3 tiers
- [ ] Click "Browse Teams" → Should show teams list

---

### **2️⃣ Token Dashboard** (⏱️ 5 min)
```
http://localhost:3000/token
```
- [ ] See 3 discount tier cards (10%, 25%, 50%)
- [ ] Click "Connect Wallet" → Mock wallet connects
- [ ] Click "Refresh Balance" → Shows balance interface
- [ ] See platform metrics at bottom

---

### **3️⃣ Staking Interface** (⏱️ 5 min)
```
http://localhost:3000/staking
```
- [ ] Click "Connect Wallet"
- [ ] Click 90-day period → Highlights (50% allocation)
- [ ] Enter amount: 1000000
- [ ] See estimated rewards preview
- [ ] View tier stats at bottom

---

### **4️⃣ Create Team** (⏱️ 10 min)
```
http://localhost:3000/teams
```
- [ ] Click green "Create Team" button
- [ ] Enter name: "My Test Team"
- [ ] Enter description: "Testing"
- [ ] Click "Create Team"
- [ ] Get alert with invite code
- [ ] Redirect to team dashboard

---

### **5️⃣ Team Dashboard** (⏱️ 10 min)
```
http://localhost:3000/teams/5
```
(Or your new team ID)

- [ ] See team stats (pool, members, attempts)
- [ ] Click invite code → Copies to clipboard
- [ ] Click "Contribute to Pool"
- [ ] Enter amount: 100
- [ ] See pool balance update
- [ ] View members list on left

---

### **6️⃣ Team Chat** (⏱️ 10 min)
```
Still on: http://localhost:3000/teams/5
```
- [ ] Type message: "Testing chat feature!"
- [ ] Press Enter or click send button
- [ ] Wait 3 seconds
- [ ] See message appear in chat
- [ ] Send another message
- [ ] Verify auto-refresh works

---

### **7️⃣ Navigation** (⏱️ 5 min)
```
http://localhost:3000/features
```
- [ ] Click "Token Dashboard" button
- [ ] Use nav to go to "Teams"
- [ ] Navigate to "Staking"
- [ ] Check active page highlighting
- [ ] Test on mobile (resize browser)

---

## ✅ **All Tests Should Pass If:**

- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000
- ✅ PostgreSQL database connected
- ✅ User ID 1 exists in database
- ✅ Team ID 5 exists (or create new one)

---

## 🐛 **If You Hit Issues:**

### **"Page Not Found"**
```bash
# Restart frontend
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty/frontend
npm run dev
```

### **"API Error 500"**
```bash
# Restart backend
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
./start_server.sh
```

### **"Team Message Fails"**
Try via curl first:
```bash
curl -X POST "http://localhost:8000/api/teams/5/messages" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "content": "Test", "message_type": "text"}'
```

If curl works, then restart frontend.

---

## 🎯 **Success Criteria:**

✅ All 7 tests above pass  
✅ No console errors  
✅ APIs return data  
✅ Chat messages send  
✅ Navigation works  

---

## 📊 **Testing Progress:**

- [ ] Test 1: API Test Page
- [ ] Test 2: Token Dashboard
- [ ] Test 3: Staking Interface
- [ ] Test 4: Create Team
- [ ] Test 5: Team Dashboard
- [ ] Test 6: Team Chat
- [ ] Test 7: Navigation

---

## 🎉 **After All Tests Pass:**

1. ✅ Take screenshots
2. ✅ Note any issues
3. ✅ Push to GitHub
4. ✅ Celebrate! 🎊

---

**START HERE:** http://localhost:3000/test-api

**Click the buttons and watch it work!** 🚀

