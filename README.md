<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/CLI-ready-blueviolet" alt="CLI">
</p>

<div align="center">

[🇨🇳 简体中文](./README.md) | [🇭🇰 繁體中文](./README.zh-TW.md) | [🇬🇧 English](./README.en.md)

</div>

<h1 align="center">♾️ TokenSage 令牌智简</h1>
<p align="center"><b>轻量级LLM上下文令牌优化引擎</b></p>
<p align="center"><i>将AI Agent的Token消耗降低 40%~90%，省下每一分钱</i></p>

---

## 🎉 项目介绍

**TokenSage（令牌智简）** 是一款轻量级的 LLM 上下文 Token 优化引擎，专为解决 AI 开发者日常使用中的 Token 消耗痛点而设计。

### 为什么需要 TokenSage？

当你使用 Claude Code、Cursor、Codex 等 AI 编码 Agent 时，每一次工具调用、代码搜索、日志分析都会产生大量的 Token 消耗。这些 Token 中包含了大量冗余信息——重复的代码行、冗长的 JSON 结构、空行和无关注释、重复的日志模式。**你为这些冗余Token付出了真金白银，却没有获得任何额外价值。**

### 自研差异化亮点

- 🪶 **纯 Python 实现** —— 无需 Rust 编译环境，`pip install` 即可使用，零编译依赖
- 🇨🇳 **中文/英文双语优化** —— 专为 CJK 字符优化的压缩算法，完美兼容 GLM、DeepSeek、Qwen 等国产模型
- 🖥️ **Rich TUI 仪表盘** —— 酷炫的终端可视化界面，Token 节省一目了然
- 🔌 **三种集成模式** —— Library API 嵌入代码、HTTP Proxy 零代码接入、Agent Wrap 一键包装
- 🔄 **可逆压缩 (CCR)** —— 原始数据本地安全存储，LLM 可随时按需检索

### 灵感来源

受 GitHub Trending 热门项目 [headroom](https://github.com/chopratejas/headroom)（14K+ Stars）的启发，但 **TokenSage 是 100% 独立自研实现**，采用纯 Python 架构，聚焦中文生态与轻量化部署。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **CodeCompressor 智能代码压缩** | 基于 AST 感知的代码压缩，去除重复函数、无用注释、多余空行，**平均节省 20%~50%** |
| 📦 **JsonShrinker 智能JSON压缩** | 自动缩短冗长的 Key 名称（`description`→`desc`）、剔除 null/空值、数组去重，**节省 15%~40%** |
| 🌏 **TextOptimizer 中英文优化** | CJK 字符感知的文本压缩，合并空白符、去除重复段落，**节省 10%~30%** |
| 📋 **LogOptimizer 日志去重** | 自动识别重复日志模式，保留前 3 条并汇总其余，**节省 50%~90%** |
| 🎯 **智能内容路由** | 自动检测输入类型（Code/JSON/Log/Text），选择最优压缩策略 |
| 🚀 **HTTP Proxy 代理模式** | 零代码修改，作为代理层接入任何 OpenAI 兼容的 LLM，拦截并压缩请求 |
| 🔌 **Agent Wrap 一键集成** | 支持 Claude Code、Codex、Cursor、Aider、Copilot 等主流 AI 编码 Agent |
| 📊 **Rich TUI 仪表盘** | 实时展示压缩统计、Token 节省量、压缩比，让优化成果一目了然 |
| 🔐 **本地优先** | 所有压缩在本地完成，数据不出本机，无隐私泄露风险 |

---

## 🚀 快速开始

### 环境要求

- **Python 3.10+**
- pip（Python 包管理器）

### 安装

**方式一：pip 安装（推荐）**

```bash
pip install tokensage
```

**方式二：源码安装（获取最新版本）**

```bash
git clone https://github.com/gitstq/TokenSage-CLI.git
cd TokenSage-CLI
pip install -e .
```

**方式三：安装所有可选依赖**

```bash
pip install "tokensage[all]"
# 或按需安装
pip install "tokensage[proxy]"   # 仅 Proxy 模式
```

### 快速上手

```bash
# 1️⃣ 基础压缩 —— 直接压缩文本
tokensage compress "这是一段测试文本，用于展示 TokenSage 的压缩效果。"

# 2️⃣ 管道输入 —— 从文件或命令输出读取
cat large_log.txt | tokensage compress --type log

# 3️⃣ 从文件读取
tokensage compress --file messy_code.py --type code

# 4️⃣ 指定目标Token预算
tokensage compress --file input.txt --max-tokens 500

# 5️⃣ 统计文件压缩效果
tokensage stats *.py *.json

# 6️⃣ 估算Token数量
echo "Hello World" | tokensage estimate

# 7️⃣ 查看版本
tokensage --version
```

---

## 📖 详细使用指南

### 作为 Python 库使用

```python
from tokensage import compress

# 自动检测内容类型
result = compress("""
def hello(name):
    print(f"Hello, {name}!")
""")

print(f"原始: {result.original_tokens} tokens")
print(f"压缩后: {result.compressed_tokens} tokens")
print(f"节省: {result.savings_percent:.1f}%")
print(f"压缩器: {result.compressor_used}")
print(f"---\n{result.compressed_text}")

# 指定内容类型
result = compress('{"verbose_key": "value"}', content_type="json")

# 查看详细统计
stats = result.to_dict()
print(stats)
```

### 集成 AI 编码 Agent

**方式一：HTTP Proxy 代理**

在终端 1 中启动代理：

```bash
tokensage proxy --port 8787
```

在终端 2 中配置你的 AI Agent：

```bash
# Claude Code
export CLAUDE_CODE_OPTS="--proxy http://localhost:8787"

# Codex CLI
export CODEX_PROXY="http://localhost:8787"

# Cursor
export CURSOR_AGENT_PROXY="http://localhost:8787"
```

**方式二：一键集成**

```bash
# 查看所有集成选项
tokensage integrate --help

# 集成 Claude Code（预览模式）
tokensage integrate --mode wrap --agent claude --dry-run

# 集成 Codex
tokensage integrate --mode wrap --agent codex --dry-run

# 安装 MCP 服务器
tokensage integrate --mode mcp --agent claude --dry-run
```

### JSON 输出

适合与其他工具链集成：

```bash
tokensage compress --file data.json --type json --json-output
```

输出示例：

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

### 典型场景示例

| 场景 | 推荐参数 | 预期节省 |
|------|---------|---------|
| 代码搜索结果 | `--type code` | 40%~60% |
| SRE 故障排查日志 | `--type log` | 50%~90% |
| API 响应 JSON | `--type json` | 15%~40% |
| 中文对话历史 | `--type text` | 15%~30% |
| RAG 检索结果 | 自动检测 | 30%~60% |

---

## 💡 设计思路与迭代规划

### 设计理念

TokenSage 的设计遵循三个核心原则：

1. **轻量无依赖** —— 核心代码零 ML 依赖，纯算法实现，`pip install` 即用
2. **中文优先** —— 专为中文 LLM 生态优化，完美支持 CJK 字符的高效压缩
3. **灵活集成** —— 提供 Library、Proxy、Wrap 三种模式，适配各种使用场景

### 技术选型

| 选型 | 选择 | 原因 |
|------|------|------|
| 编程语言 | Python 3.10+ | 生态成熟、社区活跃、AI 领域事实标准 |
| CLI 框架 | Click | 功能完善、文档丰富、社区广泛使用 |
| TUI 渲染 | Rich | 最强大的 Python 终端美化库 |
| HTTP 服务 | Starlette + Uvicorn | 轻量异步、性能优异、适合 Proxy 场景 |

### 后续迭代计划

- [ ] **v1.1** —— 支持更多 AI Agent（Windsurf、OpenClaw、CodeBuddy）
- [ ] **v1.2** —— 基于 TF-IDF 的智能上下文裁切
- [ ] **v1.3** —— 跨会话持久化压缩记忆
- [ ] **v2.0** —— 插件系统，支持自定义压缩器
- [ ] **v2.1** —— Web 管理界面
- [ ] **v3.0** —— AI Agent 智能上下文管理器（自动学习优化策略）

---

## 📦 打包与部署指南

### 构建分发包

```bash
# 安装构建工具
pip install build

# 构建
python -m build

# 产物在 dist/ 目录
ls dist/
```

### 本地测试安装

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

### 兼容环境

- ✅ Windows 10/11（PowerShell、CMD、WSL）
- ✅ macOS 12+（Intel & Apple Silicon）
- ✅ Linux（Ubuntu 20.04+, Debian 11+, CentOS 8+, 等主流发行版）
- ✅ Docker 容器

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！无论是新功能、Bug 修复、文档改进还是使用反馈。

### 提交 PR

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m "feat: add amazing feature"`
4. 推送到分支：`git push origin feat/amazing-feature`
5. 创建 Pull Request

### Commit 规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

### 提交 Issue

使用 GitHub Issues 提交 Bug 报告或功能请求。请提供：
- 清晰的标题和描述
- 复现步骤（Bug）
- 期望行为
- 环境信息（OS、Python 版本）

---

## 📄 开源协议

本项目基于 **MIT 协议** 开源，您可以自由使用、修改和分发。

[查看完整协议](./LICENSE)

---

<p align="center">
  Made with ♾️ by <a href="https://github.com/gitstq">gitstq</a>
  <br>
  <sub>如果您觉得这个项目有帮助，请 ⭐ 一个 Star 吧！</sub>
</p>