# Multi-Personality System Activation Guide

**Quick Start**: Enable difficulty-based personalities in 30 seconds

## What You're Getting

4 distinct AI personalities that match bounty difficulty levels:
- **Easy** (Bounty 4): Deadpool Character
- **Medium** (Bounty 3): Overly Enthusiastic Tech Bro  
- **Hard** (Bounty 2): Zen Buddhist Monk
- **Expert** (Bounty 1): Jonah Hill/Superbad (current personality)

Each personality has progressively more resistance layers while maintaining security.

## How to Enable

### Step 1: Add Environment Variable

Add this line to your `.env` file:

```bash
ENABLE_MULTI_PERSONALITY=true
```

**That's it!** The system is now active.

### Step 2: Restart Backend

```bash
# If running locally
pkill -f uvicorn
python3 -m uvicorn apps.backend.main:app --reload

# On Digital Ocean
# Just restart the app service
```

### Step 3: Verify It's Working

Look for this in your startup logs:

```
✅ Multi-personality system ENABLED - routing by difficulty
```

## How to Test

### Option 1: Use Test Suite

```bash
cd /Users/jaybrantley/myenv/Hackathon/Billions_Bounty
source venv/bin/activate
python3 tests/test_multi_personality.py
```

Should see: `🎉 ALL TESTS PASSED!`

### Option 2: Test in UI

1. Go to Bounty 4 (Llama Legend) → Should see Tech Bro personality
2. Go to Bounty 3 (Gemini Great) → Should see Deadpool personality  
3. Go to Bounty 2 (GPT Gigachad) → Should see Zen Monk personality
4. Go to Bounty 1 (Claude Champ) → Should see Jonah Hill personality

Each should have a distinct voice and response style.

## How to Disable

To revert to single personality:

```bash
ENABLE_MULTI_PERSONALITY=false
```

Then restart backend. No other changes needed.

## Troubleshooting

### Problem: Still using single personality

**Solution**: Check environment variable is actually being loaded:
```bash
grep ENABLE_MULTI_PERSONALITY .env
```

### Problem: Wrong personality for bounty

**Solution**: Check database `Bounty.difficulty_level` field:
```sql
SELECT id, name, difficulty_level FROM bounties;
```

Should match:
- 1 → expert
- 2 → hard
- 3 → medium
- 4 → easy

### Problem: Tests failing

**Solution**: Make sure you're in virtual environment:
```bash
source venv/bin/activate
python3 tests/test_multi_personality.py
```

## What Changed

### New Files
- `src/services/personality_multi.py` - 4 personalities in one file
- `src/services/ai_agent_multi.py` - new agent with routing
- `tests/test_multi_personality.py` - test suite
- `docs/personality/` - documentation

### Modified Files
- `apps/backend/main.py` - added flag check and routing (20 lines)

### Unchanged Files
- Everything else! Your existing code is untouched

## Important Notes

1. **Blacklist is shared** across all personalities
2. **Core directive never changes** - no transfers ever
3. **Backward compatible** - set flag to false to revert
4. **Zero risk** - fully parallel implementation
5. **All security maintained** at all difficulty levels

## Need Help?

- See docs: `docs/personality/MULTI_PERSONALITY_SYSTEM.md`
- Check tests: `tests/test_multi_personality.py`
- Review code: `src/services/personality_multi.py`
- Check logs: Backend startup messages

## What's Next?

1. Enable the system with the flag
2. Test each bounty endpoint
3. Monitor user engagement
4. Collect feedback
5. Iterate on personalities

---

**Ready to activate?** Just add one line to `.env`! 🚀




