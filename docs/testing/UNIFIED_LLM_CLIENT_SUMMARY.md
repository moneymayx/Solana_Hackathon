# Unified LLM Client Architecture Summary

## What Changed

The LLM client system was refactored from **per-provider classes** to a **unified, environment-based approach** for maximum flexibility.

## Before (Old Approach)

```python
# Separate class for each provider
class AnthropicClient(LLMClient): ...
class OpenAIClient(LLMClient): ...
class GeminiClient(LLMClient): ...
class DeepSeekClient(LLMClient): ...

# Manual registration
self.clients = {
    "anthropic": AnthropicClient(),
    "openai": OpenAIClient(),
    ...
}
```

**Problems:**
- ❌ Required new class for every provider
- ❌ Manual registration needed
- ❌ Not flexible for cycling through providers
- ❌ Hard to maintain

## After (New Approach)

```python
# Single unified client
class UnifiedLLMClient:
    PROVIDER_CONFIGS = {
        'anthropic': {...},
        'openai': {...},
        'gemini': {...},
        ...
    }

# Auto-discovery from environment
def _discover_providers(self):
    for env_key in os.environ:
        if env_key.endswith('_LLM_API_KEY'):
            # Automatically discover and initialize
```

**Benefits:**
- ✅ Auto-discovers providers from environment variables
- ✅ Pattern-based API key recognition
- ✅ Easy to add new providers (just update config)
- ✅ No code changes needed for new API keys
- ✅ Perfect for cycling through providers

## How It Works

### 1. Environment Variable Auto-Discovery

The system scans all environment variables for these patterns:

**Pattern 1** (Recommended):
```
ANTHROPIC_LLM_API_KEY=...
OPENAI_LLM_API_KEY=...
COHERE_LLM_API_KEY=...
```

**Pattern 2** (Known Providers):
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GEMINI_API_KEY=...
```

### 2. Unified Client

All providers use the same `UnifiedLLMClient` class:

```python
client = UnifiedLLMClient('anthropic', api_key)
await client.send_message(system, user_message)
```

### 3. Provider Configurations

Each provider is defined in `PROVIDER_CONFIGS`:

```python
'anthropic': {
    'library': 'anthropic',
    'client_init': lambda key: Anthropic(api_key=key),
    'model': 'claude-sonnet-4-20250514',
    'supports_system': True,
    'async': False
}
```

## Adding New Providers

### Easy Mode (Pre-configured)

Already configured: Anthropic, OpenAI, Gemini, DeepSeek, Cohere, Mistral, Groq, Together AI

Just add the API key:
```env
PROVIDER_LLM_API_KEY=your_key
```

### Hard Mode (New Provider)

Add 3 lines to `PROVIDER_CONFIGS`:

```python
'newprovider': {
    'library': 'newprovider-sdk',
    'client_init': lambda key: NewProviderSDK(key),
    'model': 'model-name',
    'supports_system': True,
    'async': True
}
```

That's it! Auto-discovery handles the rest.

## Usage Examples

### Basic Discovery

```python
manager = LLMClientManager()
providers = manager.get_available_providers()
# ['anthropic', 'openai', 'gemini', ...]
```

### Get Client

```python
client = manager.get_client('anthropic')
response = await client.send_message(system, message)
```

### Cycle Through All

```python
for provider in manager.get_available_providers():
    client = manager.get_client(provider)
    # Test with different providers
```

## Supported Providers

| Provider | Env Variable Pattern | SDK |
|----------|---------------------|-----|
| Anthropic | `ANTHROPIC_LLM_API_KEY` | anthropic |
| OpenAI | `OPENAI_LLM_API_KEY` | openai |
| Gemini | `GEMINI_LLM_API_KEY` | google-generativeai |
| DeepSeek | `DEEPSEEK_LLM_API_KEY` | openai |
| Cohere | `COHERE_LLM_API_KEY` | cohere |
| Mistral | `MISTRAL_LLM_API_KEY` | openai |
| Groq | `GROQ_LLM_API_KEY` | openai |
| Together | `TOGETHER_LLM_API_KEY` | openai |

## API Key Naming Convention

Use this pattern for maximum flexibility:

```
{PROVIDER}_LLM_API_KEY
```

Examples:
- ✅ `ANTHROPIC_LLM_API_KEY`
- ✅ `COHERE_LLM_API_KEY`
- ✅ `ANYNEWPROVIDER_LLM_API_KEY`

The system will recognize the provider name from the prefix.

## Benefits for AI Testing

### 1. Easy Provider Rotation

```env
# Test with different providers by just changing .env
ANTHROPIC_LLM_API_KEY=...
OPENAI_LLM_API_KEY=...
COHERE_LLM_API_KEY=...
```

### 2. No Code Changes

Add a new provider? Just add the API key and install the SDK.

### 3. Automatic Discovery

The test suite automatically finds all available providers:

```bash
python3 scripts/test_ai_resistance.py
# Automatically tests all discovered LLMs
```

### 4. Flexible Filtering

```bash
# Test specific provider
python3 scripts/test_ai_resistance.py --provider anthropic

# Test specific difficulty
python3 scripts/test_ai_resistance.py --difficulty expert
```

## Migration Notes

**Old code using AnthropicClient, etc. still works!**

The `LLMClientManager` interface remains the same:

```python
# Old way (still works)
manager = LLMClientManager()
client = manager.get_client('anthropic')

# New way (same interface, better implementation)
manager = LLMClientManager()
client = manager.get_client('anthropic')
```

**Internals changed, interface stayed the same.**

## Testing

Verify the system works:

```bash
# Test auto-discovery
python3 -c "
from src.services.llm_client_manager import LLMClientManager
manager = LLMClientManager()
print(manager.get_available_providers())
"

# Test compilation
python3 -m py_compile scripts/test_ai_resistance.py

# Run full test suite
python3 scripts/test_ai_resistance.py
```

## Summary

**Before:** Separate classes, manual registration, inflexible  
**After:** Unified client, auto-discovery, super flexible

**Key Improvement:** Environment-based auto-discovery makes it incredibly easy to cycle through different LLM providers without any code changes!




