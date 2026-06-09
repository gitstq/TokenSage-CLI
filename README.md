<div align="center">

# 🧠 TokenSage-CLI

**Lightweight Terminal AI Token Compression & Cost Optimization Engine**

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success.svg)]()
[![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![19 LLM Models](https://img.shields.io/badge/LLM%20Models-19-orange.svg)]()

</div>

---

## English

### 🎉 About TokenSage-CLI

TokenSage-CLI is an **independently developed**, lightweight terminal tool for **AI Token compression and cost optimization**. Inspired by the growing need to reduce LLM API costs, it provides intelligent text compression, precise token counting, and comprehensive cost analysis across 19 major LLM models.

**Why TokenSage-CLI?**
- LLM API costs are skyrocketing — a single month's bill can reach hundreds of dollars
- Most developers waste 30-60% of tokens on redundant, compressible content
- Existing solutions are heavy, complex, or lack Chinese language optimization
- TokenSage-CLI solves all of these problems with **zero dependencies** and a **single-file install**

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔧 **Multi-Strategy Compression** | JSON, Code, Markdown, and plain text — each with tailored compression algorithms |
| 🇨🇳 **Chinese Optimization** | Word-segmentation-aware compression, CJK character handling, redundant phrase removal |
| 📊 **Token Counting** | BPE-approximate, character-level, and hybrid counting strategies |
| 💰 **Cost Calculator** | Built-in pricing for **19 LLM models** from OpenAI, Anthropic, Google, DeepSeek, and more |
| 📈 **TUI Dashboard** | Beautiful terminal UI with Rich (auto-degrades to plain text) |
| 🔄 **Proxy Mode** | Transparent HTTP proxy — compress API requests without changing your code |
| ⚡ **Zero Dependencies** | Pure Python standard library — `rich` is optional |
| 🌍 **Cross-Platform** | Works on Windows, macOS, and Linux |
| 📝 **History Tracking** | Automatic logging of all compression operations |
| 🧪 **Benchmarking** | Built-in compression benchmark suite |

### 🚀 Quick Start

**Installation:**

```bash
# Clone the repository
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI

# Install (zero dependencies)
pip install -e .

# Optional: install with Rich TUI support
pip install -e ".[rich]"
```

**Basic Usage:**

```bash
# Compress text with medium level
tokensage compress "Your long text with redundant words here"

# Compress a JSON file aggressively
tokensage compress -f data.json --level aggressive

# Count tokens in text
tokensage count "Hello world, this is a test" --compare

# Calculate API cost for GPT-4o
tokensage cost "Your prompt text" --model gpt-4o --output-tokens 1000

# Compare costs across all models
tokensage cost "Your prompt text" --compare-models

# Calculate savings from compression
tokensage savings "Your long text..." --model gpt-4o

# Start transparent proxy mode
tokensage proxy --port 8080

# Open TUI dashboard
tokensage dashboard

# Run compression benchmarks
tokensage benchmark --iterations 10

# View compression history
tokensage history --limit 10
```

### 📖 Detailed Usage Guide

#### Compression Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `mild` | Minimal compression, preserves all structure | Sensitive content, code |
| `medium` | Balanced compression with filler removal | General text, prompts |
| `aggressive` | Maximum compression, may restructure | Cost-sensitive bulk processing |

#### Supported Content Types

- **JSON**: Removes redundant keys (`id`, `uuid`, `timestamp`), shortens key names, reduces float precision
- **Code**: Strips comments, blank lines, and unnecessary whitespace (AST-aware)
- **Markdown**: Preserves structure, compresses formatting markers
- **Text**: Removes filler phrases, collapses whitespace, deduplicates lines

#### Proxy Mode

```bash
# Start proxy on port 8080
tokensage proxy --port 8080

# Point your LLM client to the proxy
# OpenAI-compatible APIs are automatically compressed
export OPENAI_API_BASE=http://localhost:8080/v1
```

### 💰 Supported LLM Models (19)

| Provider | Models |
|----------|--------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, o1, o1-mini |
| **Anthropic** | Claude-3.5-Sonnet, Claude-3-Haiku, Claude-3-Opus |
| **Google** | Gemini-1.5-Pro, Gemini-1.5-Flash |
| **DeepSeek** | DeepSeek-V3, DeepSeek-Chat |
| **Zhipu AI** | GLM-4, GLM-4-Flash |
| **Alibaba** | Qwen-Max, Qwen-Plus, Qwen-Turbo |
| **ByteDance** | Doubao-Pro-32K |
| **Moonshot** | Moonshot-V1 |
| **Mistral** | Mistral-Large |

### 💡 Design Philosophy & Roadmap

**Design Principles:**
- **Zero dependency first** — works everywhere Python runs
- **Progressive enhancement** — Rich TUI is optional, plain text always works
- **Chinese-first optimization** — not an afterthought, but a core feature
- **Transparent compression** — proxy mode requires zero code changes

**Roadmap:**
- [ ] Reversible compression with content indexing
- [ ] Team cost tracking and budget alerts
- [ ] VS Code / JetBrains plugin integration
- [ ] Web-based cost dashboard
- [ ] Plugin system for custom compression strategies

### 📦 Installation & Deployment

```bash
# From source
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .

# Run tests
python -m unittest discover -s tests -v

# Generate configuration
tokensage config --generate
```

### 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and commit conventions.

### 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 简体中文

### 🎉 项目介绍

TokenSage-CLI 是一款**独立自研**的轻量级终端 AI Token 智能压缩与成本优化引擎。面对日益高涨的 LLM API 调用费用，它提供智能文本压缩、精准 Token 计数和全面的成本分析，覆盖 19 个主流大语言模型。

**为什么选择 TokenSage-CLI？**
- LLM API 费用飙升——单月账单可达数百美元
- 大多数开发者浪费了 30-60% 的 Token 在可压缩的冗余内容上
- 现有方案要么太重、太复杂，要么缺乏中文优化
- TokenSage-CLI 以**零依赖**和**单文件安装**解决所有这些问题

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔧 **多策略压缩** | JSON、代码、Markdown、纯文本——每种都有专属压缩算法 |
| 🇨🇳 **中文专项优化** | 分词感知压缩、CJK字符处理、冗余表达精简 |
| 📊 **Token 计数** | BPE近似、字符级、混合三种计数策略 |
| 💰 **成本计算器** | 内置 **19 个 LLM 模型** 定价数据（OpenAI、Anthropic、Google、DeepSeek等） |
| 📈 **TUI 仪表盘** | Rich 终端 UI（无 Rich 时自动降级为纯文本） |
| 🔄 **代理模式** | 透明 HTTP 代理——无需修改代码即可压缩 API 请求 |
| ⚡ **零依赖** | 纯 Python 标准库——`rich` 为可选增强 |
| 🌍 **跨平台** | 支持 Windows、macOS、Linux |
| 📝 **历史记录** | 自动记录所有压缩操作 |
| 🧪 **基准测试** | 内置压缩效果基准测试套件 |

### 🚀 快速开始

**安装：**

```bash
# 克隆仓库
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI

# 安装（零依赖）
pip install -e .

# 可选：安装 Rich TUI 支持
pip install -e ".[rich]"
```

**基本用法：**

```bash
# 压缩文本（中等强度）
tokensage compress "你的长文本，包含冗余词语"

# 激进压缩 JSON 文件
tokensage compress -f data.json --level aggressive

# 计算 Token 数量
tokensage count "你好世界，这是一段测试文本" --compare

# 计算 GPT-4o 的 API 调用成本
tokensage cost "你的提示词文本" --model gpt-4o --output-tokens 1000

# 对比所有模型的成本
tokensage cost "你的提示词文本" --compare-models

# 计算压缩节省的费用
tokensage savings "你的长文本..." --model gpt-4o

# 启动透明代理模式
tokensage proxy --port 8080

# 打开 TUI 仪表盘
tokensage dashboard

# 运行压缩基准测试
tokensage benchmark --iterations 10

# 查看压缩历史
tokensage history --limit 10
```

### 📖 详细使用指南

#### 压缩级别

| 级别 | 描述 | 适用场景 |
|------|------|----------|
| `mild` | 最小压缩，保留所有结构 | 敏感内容、代码 |
| `medium` | 平衡压缩，去除冗余表达 | 通用文本、提示词 |
| `aggressive` | 最大压缩，可能重构内容 | 成本敏感的批量处理 |

#### 支持的内容类型

- **JSON**：移除冗余键（`id`、`uuid`、`timestamp`）、缩短键名、降低浮点精度
- **代码**：去除注释、空行和不必要的空白（AST感知）
- **Markdown**：保留文档结构，压缩格式标记
- **文本**：去除冗余短语、合并空白、去重重复行

#### 代理模式

```bash
# 在 8080 端口启动代理
tokensage proxy --port 8080

# 将 LLM 客户端指向代理
# OpenAI 兼容 API 自动压缩
export OPENAI_API_BASE=http://localhost:8080/v1
```

### 💰 支持的 LLM 模型（19个）

| 供应商 | 模型 |
|--------|------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, o1, o1-mini |
| **Anthropic** | Claude-3.5-Sonnet, Claude-3-Haiku, Claude-3-Opus |
| **Google** | Gemini-1.5-Pro, Gemini-1.5-Flash |
| **DeepSeek** | DeepSeek-V3, DeepSeek-Chat |
| **智谱 AI** | GLM-4, GLM-4-Flash |
| **阿里** | Qwen-Max, Qwen-Plus, Qwen-Turbo |
| **字节跳动** | Doubao-Pro-32K |
| **Moonshot** | Moonshot-V1 |
| **Mistral** | Mistral-Large |

### 💡 设计思路与迭代规划

**设计理念：**
- **零依赖优先**——Python 能运行的地方就能用
- **渐进增强**——Rich TUI 可选，纯文本始终可用
- **中文优先优化**——不是附加功能，而是核心特性
- **透明压缩**——代理模式无需修改任何代码

**迭代规划：**
- [ ] 可逆压缩与内容索引
- [ ] 团队成本追踪与预算告警
- [ ] VS Code / JetBrains 插件集成
- [ ] Web 版成本仪表盘
- [ ] 自定义压缩策略插件系统

### 📦 安装与部署

```bash
# 从源码安装
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .

# 运行测试
python -m unittest discover -s tests -v

# 生成配置文件
tokensage config --generate
```

### 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 发起 Pull Request

详情请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 📄 开源协议

本项目基于 MIT 开源协议发布——详见 [LICENSE](LICENSE) 文件。

---

## 繁體中文

### 🎉 專案介紹

TokenSage-CLI 是一款**獨立自研**的輕量級終端 AI Token 智慧壓縮與成本最佳化引擎。面對日益高漲的 LLM API 呼叫費用，它提供智慧文字壓縮、精準 Token 計數和全面的成本分析，涵蓋 19 個主流大型語言模型。

**為什麼選擇 TokenSage-CLI？**
- LLM API 費用飆升——單月帳單可達數百美元
- 大多數開發者浪費了 30-60% 的 Token 在可壓縮的冗餘內容上
- 現有方案要麼太重、太複雜，要麼缺乏中文優化
- TokenSage-CLI 以**零依賴**和**單檔案安裝**解決所有這些問題

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔧 **多策略壓縮** | JSON、程式碼、Markdown、純文字——每種都有專屬壓縮演算法 |
| 🇨🇳 **中文專項優化** | 分詞感知壓縮、CJK字元處理、冗餘表達精簡 |
| 📊 **Token 計數** | BPE近似、字元級、混合三種計數策略 |
| 💰 **成本計算器** | 內建 **19 個 LLM 模型** 定價資料（OpenAI、Anthropic、Google、DeepSeek等） |
| 📈 **TUI 儀表盤** | Rich 終端 UI（無 Rich 時自動降級為純文字） |
| 🔄 **代理模式** | 透明 HTTP 代理——無需修改程式碼即可壓縮 API 請求 |
| ⚡ **零依賴** | 純 Python 標準庫——`rich` 為可選增強 |
| 🌍 **跨平台** | 支援 Windows、macOS、Linux |
| 📝 **歷史記錄** | 自動記錄所有壓縮操作 |
| 🧪 **基準測試** | 內建壓縮效果基準測試套件 |

### 🚀 快速開始

**安裝：**

```bash
# 克隆倉庫
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI

# 安裝（零依賴）
pip install -e .

# 可選：安裝 Rich TUI 支援
pip install -e ".[rich]"
```

**基本用法：**

```bash
# 壓縮文字（中等強度）
tokensage compress "你的長文本，包含冗餘詞語"

# 激進壓縮 JSON 檔案
tokensage compress -f data.json --level aggressive

# 計算 Token 數量
tokensage count "你好世界，這是一段測試文本" --compare

# 計算 GPT-4o 的 API 呼叫成本
tokensage cost "你的提示詞文本" --model gpt-4o --output-tokens 1000

# 對比所有模型的成本
tokensage cost "你的提示詞文本" --compare-models

# 計算壓縮節省的費用
tokensage savings "你的長文本..." --model gpt-4o

# 啟動透明代理模式
tokensage proxy --port 8080

# 打開 TUI 儀表盤
tokensage dashboard

# 執行壓縮基準測試
tokensage benchmark --iterations 10

# 查看壓縮歷史
tokensage history --limit 10
```

### 📖 詳細使用指南

#### 壓縮級別

| 級別 | 描述 | 適用場景 |
|------|------|----------|
| `mild` | 最小壓縮，保留所有結構 | 敏感內容、程式碼 |
| `medium` | 平衡壓縮，去除冗餘表達 | 通用文字、提示詞 |
| `aggressive` | 最大壓縮，可能重構內容 | 成本敏感的批次處理 |

#### 支援的內容類型

- **JSON**：移除冗餘鍵（`id`、`uuid`、`timestamp`）、縮短鍵名、降低浮點精度
- **程式碼**：去除註釋、空行和不必要的空白（AST感知）
- **Markdown**：保留文件結構，壓縮格式標記
- **文字**：去除冗餘短語、合併空白、去重重複行

#### 代理模式

```bash
# 在 8080 連接埠啟動代理
tokensage proxy --port 8080

# 將 LLM 客戶端指向代理
# OpenAI 相容 API 自動壓縮
export OPENAI_API_BASE=http://localhost:8080/v1
```

### 💰 支援的 LLM 模型（19個）

| 供應商 | 模型 |
|--------|------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, o1, o1-mini |
| **Anthropic** | Claude-3.5-Sonnet, Claude-3-Haiku, Claude-3-Opus |
| **Google** | Gemini-1.5-Pro, Gemini-1.5-Flash |
| **DeepSeek** | DeepSeek-V3, DeepSeek-Chat |
| **智譜 AI** | GLM-4, GLM-4-Flash |
| **阿里** | Qwen-Max, Qwen-Plus, Qwen-Turbo |
| **字節跳動** | Doubao-Pro-32K |
| **Moonshot** | Moonshot-V1 |
| **Mistral** | Mistral-Large |

### 💡 設計思路與迭代規劃

**設計理念：**
- **零依賴優先**——Python 能執行的地方就能用
- **漸進增強**——Rich TUI 可選，純文字始終可用
- **中文優先優化**——不是附加功能，而是核心特性
- **透明壓縮**——代理模式無需修改任何程式碼

**迭代規劃：**
- [ ] 可逆壓縮與內容索引
- [ ] 團隊成本追蹤與預算告警
- [ ] VS Code / JetBrains 外掛整合
- [ ] Web 版成本儀表盤
- [ ] 自訂壓縮策略外掛系統

### 📦 安裝與部署

```bash
# 從原始碼安裝
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .

# 執行測試
python -m unittest discover -s tests -v

# 產生設定檔
tokensage config --generate
```

### 🤝 貢獻指南

1. Fork 本倉庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交變更（`git commit -m 'feat: add amazing feature'`）
4. 推送分支（`git push origin feature/amazing-feature`）
5. 發起 Pull Request

詳情請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 📄 開源協議

本專案基於 MIT 開源協議發布——詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Built with ❤️ by [gitstq](https://github.com/gitstq)**

**Inspired by the need to reduce LLM API costs for developers worldwide**

</div>
