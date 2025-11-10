# Model Override Quick Reference

## TL;DR

Add this to your `.env` file to use a custom model:

```env
{PROVIDER}_MODEL=model-name

# Optional: select a named variant without editing the model string
{PROVIDER}_MODEL_V1=model-a
{PROVIDER}_MODEL_V2=model-b
{PROVIDER}_MODEL_ACTIVE=V2

# Optional: spin up multiple concurrent clients (e.g. Groq)
{PROVIDER}_MODEL_ALIASES=v1,creative
{PROVIDER}_MODEL_V1=llama-3.3-8b
{PROVIDER}_MODEL_CREATIVE=mixtral-8x7b-32768
```

## Quick Examples

### Groq Models
```env
GROQ_LLM_API_KEY=your_key
GROQ_MODEL=llama-3.3-70b-versatile  # Latest, best model
GROQ_MODEL=llama-70b-8192          # 70B with large context
GROQ_MODEL=llama-3.3-8b            # Smaller, faster

# Multiple Groq variants live at once
GROQ_MODEL_ALIASES=v1,v2
GROQ_MODEL_V1=llama-3.3-8b
GROQ_MODEL_V2=mixtral-8x7b-32768
```

You can address these at runtime as `groq` (default), `groq:v1`, and `groq:v2`.

### Anthropic Models
```env
ANTHROPIC_LLM_API_KEY=your_key
ANTHROPIC_MODEL=claude-opus-20240229        # Most capable
ANTHROPIC_MODEL=claude-sonnet-4-20250514    # Current best (default)
ANTHROPIC_MODEL=claude-haiku-20240307       # Fastest
```

### OpenAI Models
```env
OPENAI_LLM_API_KEY=your_key
OPENAI_MODEL=gpt-4-turbo-preview   # Latest
OPENAI_MODEL=gpt-4                 # Standard GPT-4
OPENAI_MODEL=gpt-3.5-turbo         # Cheaper, faster
```

## Common Model Names by Provider

| Provider | Model Name | Notes |
|----------|-----------|-------|
| **Groq** | `llama-3.3-70b-versatile` | Latest, most capable |
| **Groq** | `llama-70b-8192` | Large context window |
| **Groq** | `llama-3.3-8b` | Smaller, faster |
| **Groq** | `mixtral-8x7b-32768` | Mixtral model |
| **Anthropic** | `claude-opus-20240229` | Most capable |
| **Anthropic** | `claude-sonnet-4-20250514` | Best balance (default) |
| **Anthropic** | `claude-haiku-20240307` | Fastest |
| **OpenAI** | `gpt-4-turbo-preview` | Latest preview |
| **OpenAI** | `gpt-4` | Standard GPT-4 |
| **OpenAI** | `gpt-3.5-turbo` | Fast, cheaper |
| **Cohere** | `command-r-plus` | Default |
| **Cohere** | `command-nightly` | Latest |
| **DeepSeek** | `deepseek-chat` | Default |
| **DeepSeek** | `deepseek-coder` | For code |
| **Mistral** | `mistral-large-latest` | Latest |
| **Mistral** | `mistral-medium-latest` | Medium |
| **Gemini** | `gemini-pro` | Default |
| **Gemini** | `gemini-pro-vision` | With vision |

## The Pattern

```env
# Provider API Key (required)
{PROVIDER}_LLM_API_KEY=your_api_key

# Model Override (optional)
{PROVIDER}_MODEL=model-name
```

**Examples:**
- `GROQ_LLM_API_KEY` + `GROQ_MODEL`
- `ANTHROPIC_LLM_API_KEY` + `ANTHROPIC_MODEL`
- `OPENAI_LLM_API_KEY` + `OPENAI_MODEL`
- etc.

## Verification

When a model override is detected, you'll see:

```
✅ Using model override for groq: llama-3.3-70b-versatile
```

## Default Models

If you don't specify `{PROVIDER}_MODEL`, these defaults are used:

- **Groq**: `llama-3.3-70b-versatile`
- **Anthropic**: `claude-sonnet-4-20250514`
- **OpenAI**: `gpt-4`
- **Cohere**: `command-r-plus`
- **DeepSeek**: `deepseek-chat`
- **Mistral**: `mistral-large`
- **Gemini**: `gemini-pro`
- **Together**: `meta-llama/Meta-Llama-3-70B-Instruct`

## Need More Info?

- **Full Guide**: [MODEL_OVERRIDES.md](MODEL_OVERRIDES.md)
- **User Manual**: [AI_RESISTANCE_TESTING.md](AI_RESISTANCE_TESTING.md)
- **Quick Start**: [READY_TO_USE.md](READY_TO_USE.md)




