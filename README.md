# TokenSage-CLI

> Lightweight Terminal AI Token Compression & Cost Optimization Engine

TokenSage-CLI is an independent, self-developed LLM token compression and cost optimization tool. It provides intelligent text compression, token counting, and API cost analysis for major LLM providers.

## Features

- **Multi-strategy Compression**: JSON, code, Markdown, and plain text compression
- **Chinese Optimization**: Specialized optimization for Chinese and CJK text
- **Token Counting**: BPE-approximate, character-level, and hybrid counting strategies
- **Cost Analysis**: Built-in pricing for 20+ LLM models from major providers
- **TUI Dashboard**: Rich terminal UI (with plain text fallback)
- **Proxy Mode**: Transparent HTTP proxy for automatic API compression
- **Zero Dependencies**: Only Python standard library required (rich is optional)

## Installation

```bash
pip install -e .
# Or with rich support:
pip install -e ".[rich]"
```

## Quick Start

```bash
# Compress text
tokensage compress "Your text here"

# Compress a file
tokensage compress -f input.json --level aggressive

# Count tokens
tokensage count -f document.md

# Calculate cost
tokensage cost -f prompt.txt --model gpt-4o --output-tokens 1000

# Compare model costs
tokensage cost "Hello world" --compare-models

# Calculate savings
tokensage savings -f prompt.txt --model claude-3.5-sonnet

# Start proxy mode
tokensage proxy --port 8080

# Open dashboard
tokensage dashboard

# Run benchmark
tokensage benchmark --iterations 10

# View history
tokensage history --limit 10
```

## Supported Models

| Provider | Models |
|----------|--------|
| OpenAI | GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo |
| Anthropic | Claude-3.5-Sonnet, Claude-3-Haiku, Claude-3-Opus |
| Google | Gemini-1.5-Pro, Gemini-1.5-Flash |
| DeepSeek | DeepSeek-V3, DeepSeek-Chat |
| Zhipu AI | GLM-4, GLM-4-Flash |
| Alibaba | Qwen-Max, Qwen-Plus, Qwen-Turbo |
| ByteDance | Doubao-Pro-32K |
| Moonshot | Moonshot-V1 |
| Mistral | Mistral-Large |

## License

MIT License
