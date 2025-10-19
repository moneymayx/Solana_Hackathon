# ⚡ Quick Reference Card

**Everything you need to know in one place**

---

## 🚀 Start Server

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
cd apps/backend
uvicorn main:app --reload
```

**Access:** `http://localhost:8000/docs`

---

## 🔌 Integrate APIs (1 Line!)

```python
# Add to apps/backend/main.py:
from src.api.app_integration include_enhancement_routers
include_enhancement_routers(app)
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🎬 Run Demos

```bash
# Full demo
python3 demo_workflows.py

# Individual phases
python3 demo_workflows.py phase1  # Context
python3 demo_workflows.py phase2  # Token
python3 demo_workflows.py phase3  # Teams
```

---

## 📊 What You Have

| Feature | Status | Endpoints | Components |
|---------|--------|-----------|------------|
| **Phase 1: Context** | ✅ | 10 | ContextInsights |
| **Phase 2: Token** | ✅ | 15 | TokenDashboard |
| **Phase 3: Teams** | ✅ | 25+ | TeamDashboard, TeamChat |

---

## 🔑 Key Files

```
API Endpoints:
└─ src/api/
   ├─ context_router.py      # Phase 1
   ├─ token_router.py         # Phase 2
   ├─ team_router.py          # Phase 3
   └─ app_integration.py      # ← Add this to main.py

Services:
└─ src/
   ├─ semantic_search_service.py
   ├─ pattern_detector_service.py
   ├─ context_builder_service.py
   ├─ token_economics_service.py
   ├─ revenue_distribution_service.py
   └─ team_service.py

Tests:
└─ tests/
   ├─ test_context_services.py
   └─ test_token_and_team_services.py

Demos:
└─ demo_workflows.py

Frontend:
└─ FRONTEND_INTEGRATION_GUIDE.md
```

---

## 🎯 Common Tasks

### **Check Service Health**
```bash
curl http://localhost:8000/api/context/health
curl http://localhost:8000/api/token/health
curl http://localhost:8000/api/teams/health
```

### **Test Endpoint**
```bash
curl -X POST "http://localhost:8000/api/context/detect-patterns" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message", "user_id": 1}'
```

### **View API Docs**
- **Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📈 Database Tables

**Total:** 43 tables (27 original + 16 new)

**Phase 1:** (3)
- message_embeddings
- attack_patterns
- context_summaries

**Phase 2:** (5)
- token_balances
- staking_positions
- buyback_events
- token_prices
- discount_usage

**Phase 3:** (8)
- teams
- team_members
- team_invitations
- team_attempts
- team_messages
- team_funding
- team_prize_distributions
- team_member_prizes

---

## 💡 Quick Examples

### **API Call (Context)**
```bash
POST /api/context/insights
{
  "user_id": 1,
  "current_message": "Test attack"
}
```

### **API Call (Token)**
```bash
POST /api/token/balance/check
{
  "wallet_address": "...",
  "user_id": 1
}
```

### **API Call (Team)**
```bash
POST /api/teams/create
{
  "leader_id": 1,
  "name": "My Team",
  "max_members": 5
}
```

---

## 🔧 Environment Variables

Required in `.env`:
```bash
# Database
DATABASE_URL=postgresql://...

# APIs (Claude required, OpenAI optional)
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...  # Optional for semantic search

# Background Tasks
REDIS_URL=redis://localhost:6379/0

# Features
ENABLE_ENHANCED_CONTEXT=true
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **IMPLEMENTATION_COMPLETE.md** | ✅ **START HERE** - Complete summary |
| API_INTEGRATION_GUIDE.md | API usage & examples |
| FRONTEND_INTEGRATION_GUIDE.md | React components |
| ALL_PHASES_COMPLETE.md | Phase 1-3 details |
| PHASE1_COMPLETE.md | Context management |
| PHASE2_COMPLETE.md | Token economics |
| PHASE3_COMPLETE.md | Team collaboration |

---

## 🎉 Stats

- **API Endpoints:** 50+
- **Database Tables:** 43
- **Services:** 6
- **React Components:** 5
- **Test Files:** 2
- **Documentation Files:** 12+
- **Lines of Code:** ~3,500

---

## ✅ Checklist

- [ ] Integrate APIs (1 line in main.py)
- [ ] Test endpoints (visit /docs)
- [ ] Run demos
- [ ] Run tests
- [ ] Build frontend
- [ ] Add authentication
- [ ] Deploy!

---

**Everything is ready to use! Start with IMPLEMENTATION_COMPLETE.md 🚀**

