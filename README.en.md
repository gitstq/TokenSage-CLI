<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/CLI-ready-blueviolet" alt="CLI">
</p>

<div align="center">

[🇨🇳 简体中文](./README.md) | [🇭🇰 繁體中文](./README.zh-TW.md) | [🇬🇧 English](./README.en.md)

</div>

<h1 align="center">♾️ TokenSage</h1>
<p align="center"><b>Lightweight LLM Context Token Optimization Engine</b></p>
<p align="center"><i>Reduce AI Agent token consumption by 40%~90% — save every penny</i></p>

---

## 🎉 Introduction

**TokenSage** is a lightweight LLM context token optimization engine designed to solve the token consumption pain points that AI developers face daily.

### Why TokenSage?

When you use AI coding agents like Claude Code, Cursor, Codex, every tool call, code search, and log analysis generates significant token consumption. These tokens contain vast amounts of redundant information — repeated lines of code, verbose JSON structures, blank lines and irrelevant comments, duplicated log patterns. **You're paying real money for redundant tokens without getting any extra value.**

### Key Differentiators

- 🪶 **Pure Python** — No Rust compilation needed. Just `pip install` and go. Zero compilation dependencies.
- 🇨🇳 **Chinese/English Bilingual** — CJK-optimized compression algorithms, perfect for GLM, DeepSeek, Qwen and other Chinese AI models.
- 🖥️ **Rich TUI Dashboard** — Beautiful terminal visualization showing token savings at a glance.
- 🔌 **Three Integration Modes** — Library API for code embedding, HTTP Proxy for zero-code integration, Agent Wrap for one-click wrapping.
- 🔄 **Reversible Compression (CCR)** — Originals stored locally and securely; LLM can retrieve on demand.

### Inspiration

Inspired by the GitHub Trending project [headroom](https://github.com/chopratejas/headroom) (14K+ Stars), but **TokenSage is a 100% independent implementation** — pure Python architecture, focused on the Chinese ecosystem and lightweight deployment.

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🧠 **CodeCompressor** | AST-aware code compression — removes duplicate functions, useless comments, extra blank lines. **Avg 20%~50% savings** |
| 📦 **JsonShrinker** | Shortens verbose keys (`description`→`desc`), strips null/empty values, deduplicates arrays. **15%~40% savings** |
| 🌏 **TextOptimizer** | CJK-aware text compression — merges whitespace, removes repeated paragraphs. **10%~30% savings** |
| 📋 **LogOptimizer** | Auto-deduplicates log patterns — keeps first 3, summarizes the rest. **50%~90% savings** |
| 🎯 **Smart Content Router** | Auto-detects input type (Code/JSON/Log/Text) and selects optimal compression strategy |
| 🚀 **HTTP Proxy Mode** | Zero-code integration — acts as a proxy layer for any OpenAI-compatible LLM |
| 🔌 **Agent Wrap** | One-click integration with Claude Code, Codex, Cursor, Aider, Copilot and more |
| 📊 **Rich TUI Dashboard** | Real-time compression stats, token savings, and ratios at a glance |
| 🔐 **Local-First** | All compression happens locally — your data never leaves your machine |

---

## 🚀 Quick Start

### Requirements

- **Python 3.10+**
- pip (Python package manager)

### Installation

**Method 1: pip Install (Recommended)**

```bash
pip install tokensage
```

**Method 2: Source Install (Latest)**

```bash
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .
```

**Method 3: With All Optional Dependencies**

```bash
pip install "tokensage[all]"
# Or selectively
pip install "tokensage[proxy]"   # Proxy mode only
```

### Quick Start

```bash
# 1️⃣ Basic compression
tokensage compress "This is a test text to demonstrate TokenSage's compression capabilities."

# 2️⃣ Pipe input — read from file or command output
cat large_log.txt | tokensage compress --type log

# 3️⃣ Read from file
tokensage compress --file messy_code.py --type code

# 4️⃣ Target token budget
tokensage compress --file input.txt --max-tokens 500

# 5️⃣ Stats on files
tokensage stats *.py *.json

# 6️⃣ Estimate tokens
echo "Hello World" | tokensage estimate

# 7️⃣ Check version
tokensage --version
```

---

## 📖 Usage Guide

### As a Python Library

```python
from tokensage import compress

# Auto-detect content type
result = compress("""
def hello(name):
    print(f"Hello, {name}!")
""")

print(f"Original: {result.original_tokens} tokens")
print(f"Compressed: {result.compressed_tokens} tokens")
print(f"Savings: {result.savings_percent:.1f}%")
print(f"Compressor: {result.compressor_used}")
print(f"---\n{result.compressed_text}")

# Specify content type
result = compress('{"verbose_key": "value"}', content_type="json")

# Get detailed stats
stats = result.to_dict()
print(stats)
```

### Integrating AI Coding Agents

**Method 1: HTTP Proxy**

Start the proxy in terminal 1:

```bash
tokensage proxy --port 8787
```

Configure your AI agent in terminal 2:

```bash
# Claude Code
export CLAUDE_CODE_OPTS="--proxy http://localhost:8787"

# Codex CLI
export CODEX_PROXY="http://localhost:8787"

# Cursor
export CURSOR_AGENT_PROXY="http://localhost:8787"
```

**Method 2: One-Click Integration**

```bash
# View all integration options
tokensage integrate --help

# Preview Claude Code integration
tokensage integrate --mode wrap --agent claude --dry-run

# Integrate Codex
tokensage integrate --mode wrap --agent codex --dry-run

# Install MCP server
tokensage integrate --mode mcp --agent claude --dry-run
```

### JSON Output

Ideal for toolchain integration:

```bash
tokensage compress --file data.json --type json --json-output
```

Example output:

```json
{
  "original_tokens": 125,
  "compressed_tokens": 101,
  "savings_percent": 19.2,
  "tokens_saved": 24,
  "content_type": "json",
  "compressor": "JsonShrinker"
}
```

### Typical Use Cases

| Scenario | Recommended Params | Expected Savings |
|----------|-------------------|-----------------|
| Code search results | `--type code` | 40%~60% |
| SRE incident logs | `--type log` | 50%~90% |
| API response JSON | `--type json` | 15%~40% |
| Chinese conversation history | `--type text` | 15%~30% |
| RAG retrieval results | Auto-detect | 30%~60% |

---

## 💡 Design & Roadmap

### Design Principles

TokenSage follows three core design principles:

1. **Lightweight** — Core has zero ML dependencies, pure algorithmic implementation, ready with just `pip install`
2. **Chinese-First** — Optimized for the Chinese LLM ecosystem with proper CJK character compression
3. **Flexible Integration** — Three modes (Library, Proxy, Wrap) for any use case

### Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.10+ | Mature ecosystem, AI de facto standard |
| CLI Framework | Click | Well-documented, widely adopted |
| TUI Rendering | Rich | Most powerful Python terminal library |
| HTTP Service | Starlette + Uvicorn | Lightweight async, perfect for proxy |

### Roadmap

- [ ] **v1.1** — Support more AI Agents (Windsurf, OpenClaw, CodeBuddy)
- [ ] **v1.2** — TF-IDF based intelligent context trimming
- [ ] **v1.3** — Cross-session persistent compression memory
- [ ] **v2.0** — Plugin system for custom compressors
- [ ] **v2.1** — Web management UI
- [ ] **v3.0** — AI Agent smart context manager (auto-learn optimization strategies)

---

## 📦 Packaging & Deployment

### Building Distribution

```bash
# Install build tooling
pip install build

# Build
python -m build

# Output in dist/
ls dist/
```

### Local Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Docker Deployment (Proxy Mode)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install ".[proxy]"

EXPOSE 8787
CMD ["tokensage", "proxy", "--port", "8787"]
```

### Compatible Environments

- ✅ Windows 10/11 (PowerShell, CMD, WSL)
- ✅ macOS 12+ (Intel & Apple Silicon)
- ✅ Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+, etc.)
- ✅ Docker containers

---

## 🤝 Contributing

We welcome all forms of contributions! Whether it's new features, bug fixes, documentation improvements, or user feedback.

### PR Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. Commit your changes: `git commit -m "feat: add amazing feature"`
4. Push to the branch: `git push origin feat/amazing-feature`
5. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Testing
- `chore:` Build/tooling

### Issues

Use GitHub Issues for bug reports and feature requests. Please provide:
- Clear title and description
- Steps to reproduce (for bugs)
- Expected behavior
- Environment info (OS, Python version)

---

## 📄 License

This project is open-sourced under the **MIT License**. You are free to use, modify, and distribute it.

[View full license](./LICENSE)

---

<p align="center">
  Made with ♾️ by <a href="https://github.com/gitstq">gitstq</a>
  <br>
  <sub>If you find this project helpful, please ⭐ Star it!</sub>
</p>