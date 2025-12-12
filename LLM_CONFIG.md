# LLM Provider Configuration Guide

This project supports multiple LLM providers for flexibility and cost optimization.

## Supported Providers

1. **Groq** (Recommended) - Fast, cost-effective with Llama3
2. **OpenAI** - GPT-4 Turbo for higher quality

## Quick Setup

### Option 1: Groq (Recommended)

1. Get your API key from [Groq Console](https://console.groq.com/keys)
2. Update `.env`:
```bash
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant   # default, can be overridden
GROQ_API_KEY=gsk_your_key_here
```

### Option 2: OpenAI

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Update `.env`:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_key_here
```

## Provider Comparison

| Feature | Groq (Llama3) | OpenAI (GPT-4) |
|---------|---------------|----------------|
| **Speed** | ⚡ Very Fast | 🐢 Slower |
| **Cost** | 💰 Very Low/Free | 💰💰💰 Higher |
| **Quality** | ✅ Good | ✅✅ Excellent |
| **Model** | llama3-70b-versatile | gpt-4o-min|
| **Best For** | Production, high volume | Maximum quality |

## Switching Providers

Simply change the `LLM_PROVIDER` environment variable and restart the backend:

```bash
# Switch to Groq
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_key

# Switch to OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key
```

Or update your `.env` file and restart:
```bash
docker-compose restart backend
```

## Architecture

The system uses a provider abstraction layer (`llm_provider.py`) that:
- Automatically initializes the correct provider based on `LLM_PROVIDER`
- Provides a unified interface for all agents
- Handles provider-specific differences (e.g., tools support)

## Cost Savings

Using Groq instead of OpenAI can save **80-90%** on LLM costs:
- Groq: Free tier + very low per-request pricing
- OpenAI GPT-4: ~$0.01-0.03 per request

For a high-traffic shopping assistant, this can result in significant savings.

## Troubleshooting

### "GROQ_API_KEY is required"
- Make sure you've set `GROQ_API_KEY` in your `.env` file
- Verify the key is correct

### "OPENAI_API_KEY is required"
- Make sure you've set `OPENAI_API_KEY` in your `.env` file
- Check that `LLM_PROVIDER=openai` is set

### Provider not switching
- Restart the backend service: `docker-compose restart backend`
- Check that the `.env` file is being loaded correctly

## Advanced Configuration

You can also customize the model used by each provider:

```python
# In llm_provider.py, modify default models:
# Groq: "llama3-70b"
# OpenAI: "gpt-4-turbo-preview" or "gpt-3.5-turbo"
```

