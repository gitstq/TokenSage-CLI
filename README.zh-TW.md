<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/CLI-ready-blueviolet" alt="CLI">
</p>

<div align="center">

[🇨🇳 简体中文](./README.md) | [🇭🇰 繁體中文](./README.zh-TW.md) | [🇬🇧 English](./README.en.md)

</div>

<h1 align="center">♾️ TokenSage 令牌智簡</h1>
<p align="center"><b>輕量級LLM上下文令牌優化引擎</b></p>
<p align="center"><i>將 AI Agent 的 Token 消耗降低 40%~90%，省下每一分錢</i></p>

---

## 🎉 項目介紹

**TokenSage（令牌智簡）** 是一款輕量級的 LLM 上下文 Token 優化引擎，專為解決 AI 開發者日常使用中的 Token 消耗痛點而設計。

### 為什麼需要 TokenSage？

當你使用 Claude Code、Cursor、Codex 等 AI 編碼 Agent 時，每一次工具調用、代碼搜索、日誌分析都會產生大量的 Token 消耗。這些 Token 中包含大量冗餘信息——重複的代碼行、冗長的 JSON 結構、空白行和無關註釋、重複的日誌模式。**你為這些冗餘 Token 付出了真金白銀，卻沒有獲得任何額外價值。**

### 自研差異化亮點

- 🪶 **純 Python 實現** —— 無需 Rust 編譯環境，`pip install` 即可使用，零編譯依賴
- 🇨🇳 **中文/英文雙語優化** —— 專為 CJK 字符優化的壓縮算法，完美兼容 GLM、DeepSeek、Qwen 等國產模型
- 🖥️ **Rich TUI 儀表盤** —— 酷炫的終端可視化界面，Token 節省一目了然
- 🔌 **三種集成模式** —— Library API 嵌入代碼、HTTP Proxy 零代碼接入、Agent Wrap 一鍵包裝
- 🔄 **可逆壓縮 (CCR)** —— 原始數據本地安全存儲，LLM 可隨時按需檢索

### 靈感來源

受 GitHub Trending 熱門項目 [headroom](https://github.com/chopratejas/headroom)（14K+ Stars）的啟發，但 **TokenSage 是 100% 獨立自研實現**，採用純 Python 架構，聚焦中文生態與輕量化部署。

---

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🧠 **CodeCompressor 智能代碼壓縮** | 基於 AST 感知的代碼壓縮，去除重複函數、無用註釋、多餘空白行，**平均節省 20%~50%** |
| 📦 **JsonShrinker 智能JSON壓縮** | 自動縮短冗長的 Key 名稱（`description`→`desc`）、剔除 null/空值、陣列去重，**節省 15%~40%** |
| 🌏 **TextOptimizer 中英文優化** | CJK 字符感知的文本壓縮，合併空白符、去除重複段落，**節省 10%~30%** |
| 📋 **LogOptimizer 日誌去重** | 自動識別重複日誌模式，保留前 3 條並匯總其餘，**節省 50%~90%** |
| 🎯 **智能內容路由** | 自動檢測輸入類型（Code/JSON/Log/Text），選擇最優壓縮策略 |
| 🚀 **HTTP Proxy 代理模式** | 零代碼修改，作為代理層接入任何 OpenAI 兼容的 LLM，攔截並壓縮請求 |
| 🔌 **Agent Wrap 一鍵集成** | 支持 Claude Code、Codex、Cursor、Aider、Copilot 等主流 AI 編碼 Agent |
| 📊 **Rich TUI 儀表盤** | 實時展示壓縮統計、Token 節省量、壓縮比，讓優化成果一目了然 |
| 🔐 **本地優先** | 所有壓縮在本地完成，數據不出本機，無隱私洩露風險 |

---

## 🚀 快速開始

### 環境要求

- **Python 3.10+**
- pip（Python 包管理器）

### 安裝

**方式一：pip 安裝（推薦）**

```bash
pip install tokensage
```

**方式二：源碼安裝（獲取最新版本）**

```bash
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .
```

**方式三：安裝所有可選依賴**

```bash
pip install "tokensage[all]"
# 或按需安裝
pip install "tokensage[proxy]"   # 僅 Proxy 模式
```

### 快速上手

```bash
# 1️⃣ 基礎壓縮 —— 直接壓縮文本
tokensage compress "這是一段測試文本，用於展示 TokenSage 的壓縮效果。"

# 2️⃣ 管道輸入 —— 從文件或命令輸出讀取
cat large_log.txt | tokensage compress --type log

# 3️⃣ 從文件讀取
tokensage compress --file messy_code.py --type code

# 4️⃣ 指定目標Token預算
tokensage compress --file input.txt --max-tokens 500

# 5️⃣ 統計文件壓縮效果
tokensage stats *.py *.json

# 6️⃣ 估算Token數量
echo "Hello World" | tokensage estimate

# 7️⃣ 查看版本
tokensage --version
```

---

## 📖 詳細使用指南

### 作為 Python 庫使用

```python
from tokensage import compress

# 自動檢測內容類型
result = compress("""
def hello(name):
    print(f"Hello, {name}!")
""")

print(f"原始: {result.original_tokens} tokens")
print(f"壓縮後: {result.compressed_tokens} tokens")
print(f"節省: {result.savings_percent:.1f}%")
print(f"壓縮器: {result.compressor_used}")
print(f"---\n{result.compressed_text}")

# 指定內容類型
result = compress('{"verbose_key": "value"}', content_type="json")

# 查看詳細統計
stats = result.to_dict()
print(stats)
```

### 集成 AI 編碼 Agent

**方式一：HTTP Proxy 代理**

在終端 1 中啟動代理：

```bash
tokensage proxy --port 8787
```

在終端 2 中配置你的 AI Agent：

```bash
# Claude Code
export CLAUDE_CODE_OPTS="--proxy http://localhost:8787"

# Codex CLI
export CODEX_PROXY="http://localhost:8787"

# Cursor
export CURSOR_AGENT_PROXY="http://localhost:8787"
```

**方式二：一鍵集成**

```bash
# 查看所有集成選項
tokensage integrate --help

# 集成 Claude Code（預覽模式）
tokensage integrate --mode wrap --agent claude --dry-run

# 集成 Codex
tokensage integrate --mode wrap --agent codex --dry-run

# 安裝 MCP 服務器
tokensage integrate --mode mcp --agent claude --dry-run
```

### JSON 輸出

適合與其他工具鏈集成：

```bash
tokensage compress --file data.json --type json --json-output
```

輸出示例：

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

### 典型場景示例

| 場景 | 推薦參數 | 預期節省 |
|------|---------|---------|
| 代碼搜索結果 | `--type code` | 40%~60% |
| SRE 故障排查日誌 | `--type log` | 50%~90% |
| API 響應 JSON | `--type json` | 15%~40% |
| 中文對話歷史 | `--type text` | 15%~30% |
| RAG 檢索結果 | 自動檢測 | 30%~60% |

---

## 💡 設計思路與迭代規劃

### 設計理念

TokenSage 的設計遵循三個核心原則：

1. **輕量無依賴** —— 核心代碼零 ML 依賴，純算法實現，`pip install` 即用
2. **中文優先** —— 專為中文 LLM 生態優化，完美支持 CJK 字符的高效壓縮
3. **靈活集成** —— 提供 Library、Proxy、Wrap 三種模式，適配各種使用場景

### 技術選型

| 選型 | 選擇 | 原因 |
|------|------|------|
| 編程語言 | Python 3.10+ | 生態成熟、社區活躍、AI 領域事實標準 |
| CLI 框架 | Click | 功能完善、文檔豐富、社區廣泛使用 |
| TUI 渲染 | Rich | 最強大的 Python 終端美化庫 |
| HTTP 服務 | Starlette + Uvicorn | 輕量異步、性能優異、適合 Proxy 場景 |

### 後續迭代計劃

- [ ] **v1.1** —— 支持更多 AI Agent（Windsurf、OpenClaw、CodeBuddy）
- [ ] **v1.2** —— 基於 TF-IDF 的智能上下文裁切
- [ ] **v1.3** —— 跨會話持久化壓縮記憶
- [ ] **v2.0** —— 插件系統，支持自定義壓縮器
- [ ] **v2.1** —— Web 管理界面
- [ ] **v3.0** —— AI Agent 智能上下文管理器（自動學習優化策略）

---

## 📦 打包與部署指南

### 構建分發包

```bash
# 安裝構建工具
pip install build

# 構建
python -m build

# 產物在 dist/ 目錄
ls dist/
```

### 本地測試安裝

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Docker 部署（Proxy 模式）

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install ".[proxy]"

EXPOSE 8787
CMD ["tokensage", "proxy", "--port", "8787"]
```

### 兼容環境

- ✅ Windows 10/11（PowerShell、CMD、WSL）
- ✅ macOS 12+（Intel & Apple Silicon）
- ✅ Linux（Ubuntu 20.04+, Debian 11+, CentOS 8+, 等主流發行版）
- ✅ Docker 容器

---

## 🤝 貢獻指南

我們歡迎任何形式的貢獻！無論是新功能、Bug 修復、文檔改進還是使用反饋。

### 提交 PR

1. Fork 本倉庫
2. 創建特性分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m "feat: add amazing feature"`
4. 推送到分支：`git push origin feat/amazing-feature`
5. 創建 Pull Request

### Commit 規範

我們遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat:` 新功能
- `fix:` Bug 修復
- `docs:` 文檔更新
- `refactor:` 代碼重構
- `test:` 測試相關
- `chore:` 構建/工具相關

### 提交 Issue

使用 GitHub Issues 提交 Bug 報告或功能請求。請提供：
- 清晰的標題和描述
- 復現步驟（Bug）
- 期望行為
- 環境信息（OS、Python 版本）

---

## 📄 開源協議

本項目基於 **MIT 協議** 開源，您可以自由使用、修改和分發。

[查看完整協議](./LICENSE)

---

<p align="center">
  Made with ♾️ by <a href="https://github.com/gitstq">gitstq</a>
  <br>
  <sub>如果您覺得這個項目有幫助，請 ⭐ 一個 Star 吧！</sub>
</p>