# Model Override Configuration

## Overview

The AI Resistance Testing System supports model overrides via environment variables, allowing you to specify custom models for each LLM provider without code changes.

## Environment Variable Pattern

Use the following pattern to specify a model override:

```
{PROVIDER}_MODEL=model-name
```

### Versioned/Alias Model Overrides

To keep multiple model candidates side-by-side, define versioned keys and select one with `{PROVIDER}_MODEL_ACTIVE`:

```env
# Define named variants
GROQ_MODEL_V1=llama-3.3-70b-versatile
GROQ_MODEL_V2=llama-3.3-8b

# Switch the active variant without touching the raw model strings
GROQ_MODEL_ACTIVE=V2
```

The loader first honours `GROQ_MODEL` for backwards compatibility, then checks `GROQ_MODEL_ACTIVE`. If the selector matches a versioned key (e.g. `GROQ_MODEL_V2`), that model is used. If the selector itself contains a full model string, it is applied directly.

### Running Multiple Groq Models Concurrently

Need to exercise several Groq models at the same time? Declare each variant and list them in `{PROVIDER}_MODEL_ALIASES`. Every alias becomes its own client (e.g. `groq:v1`, `groq:creative`) so you can schedule head-to-head comparisons without redeploying.

```env
GROQ_LLM_API_KEY=gsk_your_groq_api_key_here

# Declare the aliases that should be initialized
GROQ_MODEL_ALIASES=v1,creative,balanced

# Map each alias to its specific model string
GROQ_MODEL_V1=llama-3.3-8b
GROQ_MODEL_CREATIVE=mixtral-8x7b-32768
GROQ_MODEL_BALANCED=llama-3.3-70b-versatile
```

After reloading the service, `LLMClientManager` exposes:

- `groq` → default configuration (still honouring `GROQ_MODEL` / `GROQ_MODEL_ACTIVE`)
- `groq:v1`, `groq:creative`, `groq:balanced` → dedicated client instances bound to the declared aliases

Use `LLMClientManager.get_available_aliases('groq')` to list the active variants at runtime. The orchestrator and CLI accept either `groq` or `groq:<alias>` when targeting a specific model.

### Examples

```env
# Groq with custom model
GROQ_LLM_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Anthropic with custom model
ANTHROPIC_LLM_API_KEY=sk-ant-your_key_here
ANTHROPIC_MODEL=claude-opus-20240229

# OpenAI with custom model
OPENAI_LLM_API_KEY=sk-your_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Multiple providers with custom models
COHERE_LLM_API_KEY=your_key_here
COHERE_MODEL=command-nightly
```

## How It Works

1. **Default Behavior**: If no `{PROVIDER}_MODEL` is set, the system uses the default model configured in `PROVIDER_CONFIGS`
2. **Override Detection**: The system checks for `{PROVIDER}_MODEL` environment variables during client initialization
3. **Isolated Config**: Model overrides only affect that specific client instance, not the global configuration

## Supported Models

### Groq

Groq supports many models. Common ones include:

- `llama-3.3-70b-versatile` - Most capable general-purpose model
- `llama-70b-8192` - 70B Llama model with 8192 context
- `llama-3.1-70b-versatile` - Previous generation
- `mixtral-8x7b-32768` - Mixtral model with large context
- `llama-3.3-8b` - Smaller, faster model
- `gemma-7b` - Google's Gemma model

**Default**: `llama-3.3-70b-versatile`

### Anthropic

- `claude-opus-20240229` - Claude 3 Opus
- `claude-sonnet-4-20250514` - Claude 3.5 Sonnet (recommended)
- `claude-sonnet-20240229` - Claude 3 Sonnet
- `claude-haiku-20240307` - Claude 3 Haiku (fastest)

**Default**: `claude-sonnet-4-20250514`

### OpenAI

- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-4-turbo-preview` - GPT-4 Turbo preview
- `gpt-4` - GPT-4
- `gpt-3.5-turbo` - GPT-3.5 Turbo (faster, cheaper)

**Default**: `gpt-4`

### Cohere

- `command-nightly` - Command R Plus nightly
- `command-r-plus` - Command R Plus
- `command` - Command base model

**Default**: `command-r-plus`

### DeepSeek

- `deepseek-chat` - DeepSeek Chat
- `deepseek-coder` - DeepSeek Coder

**Default**: `deepseek-chat`

### Mistral

- `mistral-large-latest` - Mistral Large
- `mistral-medium-latest` - Mistral Medium
- `mistral-small-latest` - Mistral Small

**Default**: `mistral-large`

### Gemini

- `gemini-pro` - Gemini Pro
- `gemini-pro-vision` - Gemini Pro Vision

**Default**: `gemini-pro`

## Usage Examples

### Example 1: Testing with Latest Models

```bash
# In .env file
GROQ_LLM_API_KEY=gsk_your_key
GROQ_MODEL=llama-3.3-70b-versatile  # Use latest Llama 3.3

OPENAI_LLM_API_KEY=sk_your_key
OPENAI_MODEL=gpt-4-turbo-preview  # Use preview model

# Run tests
python3 scripts/test_ai_resistance.py
```

### Example 2: Cost Optimization

```bash
# Use cheaper/faster models for testing
GROQ_LLM_API_KEY=gsk_your_key
GROQ_MODEL=llama-3.3-8b  # Smaller, faster model

OPENAI_LLM_API_KEY=sk_your_key
OPENAI_MODEL=gpt-3.5-turbo  # Cheaper than GPT-4

ANTHROPIC_LLM_API_KEY=sk-ant-your_key
ANTHROPIC_MODEL=claude-haiku-20240307  # Fastest Claude model

# Run tests
python3 scripts/test_ai_resistance.py
```

### Example 3: Specific Test with Override

```bash
# Set override for specific test
export GROQ_MODEL=llama-70b-8192
export GROQ_LLM_API_KEY=gsk_your_key

# Run single test
python3 scripts/test_ai_resistance.py --provider groq

# Unset after test
unset GROQ_MODEL
```

### Example 4: Comparing Different Models

```bash
# Test run 1: Use default models
python3 scripts/test_ai_resistance.py --provider groq > results_default.txt

# Test run 2: Use custom model
export GROQ_MODEL=llama-3.3-8b
python3 scripts/test_ai_resistance.py --provider groq > results_8b.txt

# Compare results
diff results_default.txt results_8b.txt
```

## Verification

The system will print a confirmation message when a model override is detected:

```
✅ Using model override for groq: llama-70b-8192
```

If you don't see this message, the default model is being used.

## Testing Model Overrides

The system includes comprehensive tests for model override functionality:

```bash
# Run model override tests
python3 tests/test_model_overrides.py

# Expected output:
# 🎉 ALL MODEL OVERRIDE TESTS PASSED!
# ✅ Model override functionality verified!
```

## Best Practices

1. **Document Your Choices**: Keep a note of which models you're testing
2. **Start with Defaults**: Always run with default models first for baselines
3. **Version Control**: Consider adding `.env.example` with commented examples
4. **Cost Awareness**: Use smaller models for initial testing, larger for final runs
5. **Consistency**: Use the same models across full test runs for comparable results

## Troubleshooting

### Override Not Working?

1. **Check Variable Name**: Must be uppercase `{PROVIDER}_MODEL`
2. **Check Provider Name**: Must match the provider in `PROVIDER_CONFIGS`
3. **No Spaces**: Remove spaces around the `=` sign
4. **Load Environment**: Ensure `.env` is loaded (done automatically by the script)

### Model Name Errors

If you get API errors about invalid model names:
- Check the provider's API documentation for exact model names
- Model names are case-sensitive
- Some providers may have regional availability differences

## Integration with Other Systems

The model override system works seamlessly with:
- ✅ Auto-discovery of LLM providers
- ✅ Multiple provider testing
- ✅ CLI filtering (`--provider`, `--difficulty`)
- ✅ Database result storage
- ✅ Analysis and ranking

## Future Enhancements

Potential improvements:
- Model-specific performance tracking
- Cost estimation per model
- Automatic model selection based on task
- Model versioning and rollback

## Related Documentation

- [AI Resistance Testing](AI_RESISTANCE_TESTING.md) - Main testing guide
- [Adding New LLM Providers](ADDING_NEW_LLM_PROVIDERS.md) - Add new providers
- [Ready to Use](READY_TO_USE.md) - Quick start guide




