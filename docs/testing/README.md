# AI Resistance Testing - Documentation Index

## Overview

The AI Resistance Testing System provides a comprehensive framework for testing LLM jailbreak resistance. LLMs test each other across different difficulty levels to generate quantitative metrics for difficulty assignments and bounty pricing.

## Quick Start

**Want to get started immediately?**
→ Read: [`READY_TO_USE.md`](READY_TO_USE.md)

## Documentation

### Getting Started

- **[READY_TO_USE.md](READY_TO_USE.md)** - Quick start guide
  - Setup instructions
  - Basic usage
  - Quick examples

- **[AI_RESISTANCE_TESTING.md](AI_RESISTANCE_TESTING.md)** - Complete user manual
  - System overview
  - Architecture details
  - Usage guide
  - Troubleshooting

### Implementation Details

- **[COMPLETE_SUMMARY.md](COMPLETE_SUMMARY.md)** - Executive summary
  - Implementation highlights
  - Key features
  - Architecture overview

- **[AI_TESTING_IMPLEMENTATION_SUMMARY.md](AI_TESTING_IMPLEMENTATION_SUMMARY.md)** - Implementation details
  - Files created/modified
  - Design decisions
  - Integration points

- **[UNIFIED_LLM_CLIENT_SUMMARY.md](UNIFIED_LLM_CLIENT_SUMMARY.md)** - Architecture deep dive
  - Before/after comparison
  - How auto-discovery works
  - Configuration details

### Extending the System

- **[ADDING_NEW_LLM_PROVIDERS.md](ADDING_NEW_LLM_PROVIDERS.md)** - Provider guide
  - How to add new LLMs
  - Configuration templates
  - Examples and troubleshooting

- **[MODEL_OVERRIDES.md](MODEL_OVERRIDES.md)** - Model configuration
  - How to specify custom models
  - Environment variable patterns
  - Model lists for each provider
  - Usage examples and best practices

### Testing

- **[TEST_RESULTS_SUMMARY.md](TEST_RESULTS_SUMMARY.md)** - Test coverage
  - Unit tests
  - E2E tests
  - Coverage details

## Key Concepts

### Auto-Discovery

The system automatically finds LLM providers from environment variables using the pattern:
```
{PROVIDER}_LLM_API_KEY
```

Example: `ANTHROPIC_LLM_API_KEY`, `OPENAI_LLM_API_KEY`, `COHERE_LLM_API_KEY`

No code changes needed - just add the API key!

### Unified Architecture

Instead of separate classes per provider, the system uses:
- **UnifiedLLMClient**: Single class for all LLM providers
- **PROVIDER_CONFIGS**: Configuration dictionary for each provider
- **Auto-Discovery**: Automatic detection from environment variables

### Attack Strategy

Attacking LLMs receive:
- System prompt: "You are an expert AI security researcher..."
- Game context: Lottery rules, bounty system, goal
- Freedom: Use any knowledge they possess

Target LLMs use:
- Difficulty-based personalities (easy/medium/hard/expert)
- Scaled resistance layers
- Full conversation context

## Usage Examples

### Basic Testing

```bash
# Run full test suite
python3 scripts/test_ai_resistance.py

# Output:
# 🎯 AI Resistance Testing Results
# Total Tests: 16 (4 LLMs × 4 difficulties)
# Rankings by Resistance...
```

### Filtered Testing

```bash
# Test specific provider
python3 scripts/test_ai_resistance.py --provider anthropic

# Test specific difficulty
python3 scripts/test_ai_resistance.py --difficulty expert

# Combined filters
python3 scripts/test_ai_resistance.py --provider openai --difficulty hard
```

## Supported Providers

**8 Pre-Configured Providers**:
- Anthropic Claude
- OpenAI GPT-4
- Google Gemini
- DeepSeek
- Cohere
- Mistral
- Groq
- Together AI

## File Structure

```
Billions_Bounty/
├── src/
│   ├── services/
│   │   ├── llm_client_manager.py      # ⭐ Unified LLM client
│   │   ├── ai_attacker_service.py     # Attack orchestration
│   │   ├── mock_ai_agent.py           # Target simulator
│   │   ├── ai_test_analysis.py        # Results analysis
│   │   └── personality_multi.py       # Difficulty personalities
│   └── models.py                       # AITestRun, AITestResult
├── scripts/
│   ├── test_ai_resistance.py          # Main orchestrator
│   └── migrate_ai_testing.py          # Database migration
├── tests/
│   ├── test_ai_resistance_system.py   # Unit tests (21)
│   └── test_ai_resistance_e2e.py      # E2E tests (8)
└── docs/testing/
    ├── README.md                       # This file
    └── ... (7 other docs)
```

## Related Systems

This testing system integrates with:
- **Multi-Personality System**: Tests against 4 difficulty-based personalities
- **Existing AI Agent**: Compatible with `BillionsAgent` and `BillionsAgentMulti`
- **Database**: Stores results for historical analysis

## Need Help?

- **Quick questions**: Check [`READY_TO_USE.md`](READY_TO_USE.md)
- **Adding providers**: See [`ADDING_NEW_LLM_PROVIDERS.md`](ADDING_NEW_LLM_PROVIDERS.md)
- **Troubleshooting**: See [`AI_RESISTANCE_TESTING.md`](AI_RESISTANCE_TESTING.md)
- **Architecture**: See [`UNIFIED_LLM_CLIENT_SUMMARY.md`](UNIFIED_LLM_CLIENT_SUMMARY.md)

## Test Results

**Last Execution**: November 2, 2025
- ✅ Unit Tests: 21/21 PASSED
- ✅ E2E Tests: 8/8 PASSED
- ✅ Total: 29/29 PASSED (100%)

See [`TEST_RESULTS_SUMMARY.md`](TEST_RESULTS_SUMMARY.md) for details.

