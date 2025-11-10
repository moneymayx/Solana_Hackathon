# Adding New LLM Providers to the AI Testing System

## Overview

The AI Resistance Testing System uses a **unified, environment-based approach** to auto-discover LLM providers. Simply add an API key to your `.env` file using the correct naming pattern, and the system will automatically recognize it.

## How Auto-Discovery Works

The system scans all environment variables for LLM API keys using these patterns:

1. **Pattern 1** (Recommended): `{PROVIDER}_LLM_API_KEY`
   - Examples: `ANTHROPIC_LLM_API_KEY`, `COHERE_LLM_API_KEY`, `MISTRAL_LLM_API_KEY`

2. **Pattern 2** (Known Providers): `{PROVIDER}_API_KEY`
   - Examples: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`

The system automatically:
- Discovers available API keys
- Initializes appropriate clients
- Makes them available for testing

## Currently Supported Providers

These providers are pre-configured and ready to use:

| Provider | Environment Variable | Python SDK |
|----------|---------------------|------------|
| Anthropic Claude | `ANTHROPIC_LLM_API_KEY` or `ANTHROPIC_API_KEY` | `anthropic` |
| OpenAI GPT-4 | `OPENAI_LLM_API_KEY` or `OPENAI_API_KEY` | `openai` |
| Google Gemini | `GEMINI_LLM_API_KEY` or `GEMINI_API_KEY` | `google-generativeai` |
| DeepSeek | `DEEPSEEK_LLM_API_KEY` or `DEEPSEEK_API_KEY` | `openai` |
| Cohere | `COHERE_LLM_API_KEY` | `cohere` |
| Mistral | `MISTRAL_LLM_API_KEY` | `openai` |
| Groq | `GROQ_LLM_API_KEY` | `openai` |
| Together AI | `TOGETHER_LLM_API_KEY` | `openai` |

## Quick Start: Using Existing Providers

Just add the API key to your `.env` file:

```env
# Option 1: Recommended pattern
ANTHROPIC_LLM_API_KEY=your_key_here
OPENAI_LLM_API_KEY=your_key_here
COHERE_LLM_API_KEY=your_key_here

# Option 2: Known providers
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

Install the required SDK:

```bash
pip install anthropic openai google-generativeai cohere
```

Run tests:

```bash
python3 scripts/test_ai_resistance.py
```

The system will automatically discover and test all available providers!

## Adding a Completely New Provider

If you want to add a provider that's not in the pre-configured list, you need to add its configuration to `PROVIDER_CONFIGS`:

### Step 1: Add to Provider Configurations

Edit `src/services/llm_client_manager.py` and add your provider to `PROVIDER_CONFIGS`:

```python
PROVIDER_CONFIGS = {
    # ... existing providers ...
    
    'yourprovider': {
        'library': 'your_library_name',  # What to pip install
        'client_init': lambda key: YourProviderInit(key),  # How to initialize
        'model': 'model-name',  # Which model to use
        'supports_system': True,  # Whether it supports separate system prompts
        'async': True  # Whether the SDK is async
    }
}
```

### Step 2: Implement Provider Logic

Add a handler method in `UnifiedLLMClient` for your provider:

```python
async def send_message(self, ...):
    # ... existing code ...
    
    elif self.provider_name == 'yourprovider':
        return await self._send_yourprovider(system_prompt, user_message, conversation_history)

async def _send_yourprovider(self, system_prompt, user_message, history):
    # Implement your provider's API calling logic
    # ...
```

### Step 3: Add API Key to .env

```env
YOURPROVIDER_LLM_API_KEY=your_key_here
```

### Step 4: Install SDK

```bash
pip install your_library_name
```

That's it! The system will auto-discover your provider.

## Provider Configuration Examples

### OpenAI-Compatible Provider (Groq, Mistral, Together)

```python
'groq': {
    'library': 'openai',
    'client_init': lambda key: __import__('openai').AsyncOpenAI(
        api_key=key,
        base_url="https://api.groq.com/openai/v1"
    ),
    'model': 'llama3-70b-8192',
    'supports_system': True,
    'async': True
}
```

### Custom Library Provider (Cohere)

```python
'cohere': {
    'library': 'cohere',
    'client_init': lambda key: __import__('cohere').AsyncClient(api_key=key),
    'model': 'command-r-plus',
    'supports_system': True,
    'async': True
}
```

### Special Case Provider (Gemini)

```python
'gemini': {
    'library': 'google.generativeai',
    'client_init': None,  # Handled specially
    'model': 'gemini-pro',
    'supports_system': False,  # No separate system prompt
    'async': False
}
```

## Testing Your New Provider

### 1. Verify Discovery

```python
from src.services.llm_client_manager import LLMClientManager

manager = LLMClientManager()
print(manager.get_available_providers())
# Should include your new provider
```

### 2. Test Basic Functionality

```python
import asyncio
from src.services.llm_client_manager import LLMClientManager

manager = LLMClientManager()
client = manager.get_client('yourprovider')

response = asyncio.run(
    client.send_message(
        system_prompt="You are helpful.",
        user_message="Say hello"
    )
)
print(response)
```

### 3. Run Full Test Suite

```bash
python3 scripts/test_ai_resistance.py --provider yourprovider
```

## Configuration Details

### Key Fields

- `library`: Python package name (e.g., `'openai'`, `'anthropic'`)
- `client_init`: Lambda function to initialize the client (None for special cases)
- `model`: Model identifier to use
- `supports_system`: Whether the provider supports separate system prompts
- `async`: Whether the provider SDK is async

### Implementation Notes

**System Prompt Support**:
- `True`: Provider supports separate system role in messages
- `False`: System prompt should be prepended to user message

**Async Handling**:
- `True`: Use async SDK directly (OpenAI, DeepSeek, etc.)
- `False`: Wrap sync SDK with `asyncio.run_in_executor` (Anthropic, Gemini)

**OpenAI-Compatible Providers**:
Many providers (Groq, Mistral, Together) use OpenAI-compatible APIs:
- Use `openai` SDK
- Just change `base_url`
- Very easy to add!

## Common Providers Template

Here's a template for adding common provider types:

### OpenAI-Compatible

```python
'provider': {
    'library': 'openai',
    'client_init': lambda key: __import__('openai').AsyncOpenAI(
        api_key=key,
        base_url="https://api.provider.com/v1"  # Change base URL
    ),
    'model': 'model-name',  # Change model name
    'supports_system': True,
    'async': True
}
```

### Anthropic-Compatible

```python
'provider': {
    'library': 'anthropic',
    'client_init': lambda key: __import__('anthropic').Anthropic(api_key=key),
    'model': 'model-name',
    'supports_system': True,
    'async': False
}
```

## Troubleshooting

### "Provider not discovered"

Check:
1. API key is in `.env` file
2. Using correct naming pattern: `{PROVIDER}_LLM_API_KEY` or `{PROVIDER}_API_KEY`
3. Provider is in `PROVIDER_CONFIGS`

### "Library not installed"

```bash
pip install {library_name}
```

Check the `library` field in `PROVIDER_CONFIGS`.

### "API format errors"

Different providers use different message formats. Check your `_send_{provider}` implementation.

### Import Errors

Make sure the SDK is installed and import paths are correct.

## Summary

**To add a new provider:**

1. ✅ Add configuration to `PROVIDER_CONFIGS` in `llm_client_manager.py`
2. ✅ Implement `_send_{provider}` method if needed
3. ✅ Add `{PROVIDER}_LLM_API_KEY` to `.env`
4. ✅ Install provider SDK: `pip install {library}`
5. ✅ Test with `--provider` flag

**No need to:**
- ❌ Create separate client classes
- ❌ Register in `__init__`
- ❌ Modify multiple files
- ❌ Hard-code provider names

The unified approach makes it incredibly easy to cycle through different LLM providers and test them all automatically!
