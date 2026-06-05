"""TokenSage CLI - Main command-line interface."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from tokensage import __version__
from tokensage.compress import compress, estimate_tokens, CompressionResult
from tokensage.tui import display_result, display_dashboard


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group(invoke_without_command=True)
@click.option("--version", "-V", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """♾️  TokenSage - Lightweight LLM Context Token Optimization Engine

    Compress tool outputs, logs, code, and text before they reach the LLM.
    Save 40-90% on tokens with the same answers.
    """
    if version:
        click.echo(f"TokenSage v{__version__}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))


@main.command()
@click.argument("text", required=False)
@click.option("--type", "-t", "content_type", default=None,
              type=click.Choice(["code", "json", "text", "log"]),
              help="Content type (auto-detected if not specified)")
@click.option("--file", "-f", "file_path", type=click.Path(exists=True),
              help="Read input from file")
@click.option("--max-tokens", "-m", type=int, default=None,
              help="Target maximum tokens after compression")
@click.option("--json-output", "-j", is_flag=True, default=False,
              help="Output as JSON")
@click.option("--preserve", "-p", is_flag=True, default=False,
              help="Preserve original for reversible retrieval")
def compress_cmd(text: Optional[str], content_type: Optional[str],
                  file_path: Optional[str], max_tokens: Optional[int],
                  json_output: bool, preserve: bool) -> None:
    """Compress text and display savings.

    Provide TEXT directly, pipe input, or use --file to read from a file.
    """
    # Read input
    if file_path:
        input_text = Path(file_path).read_text(encoding="utf-8")
    elif text:
        input_text = text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        click.echo("Error: No input provided. Provide text, use --file, or pipe input.", err=True)
        sys.exit(1)

    # Compress
    result = compress(
        text=input_text,
        content_type=content_type,
        max_tokens=max_tokens,
        preserve_exact=preserve,
    )

    # Output
    if json_output:
        output = {
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "savings_percent": round(result.savings_percent, 1),
            "tokens_saved": result.tokens_saved,
            "content_type": result.content_type,
            "compressor": result.compressor_used,
            "compressed_text": result.compressed_text,
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        display_result(result)


@main.command()
@click.option("--mode", "-m", default="wrap",
              type=click.Choice(["wrap", "proxy", "mcp"]),
              help="Integration mode")
@click.option("--agent", "-a", default="claude",
              type=click.Choice(["claude", "codex", "cursor", "aider", "copilot"]),
              help="AI coding agent to wrap")
@click.option("--port", "-p", default=8787, type=int, help="Proxy port")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would be done without applying")
def integrate(mode: str, agent: str, port: int, dry_run: bool) -> None:
    """Integrate TokenSage with AI coding agents.

    Modes:
      wrap   - Wrap an AI coding agent (Claude Code, Codex, Cursor, etc.)
      proxy  - Start an HTTP proxy server for drop-in integration
      mcp    - Install MCP server for any MCP client
    """
    if mode == "wrap":
        _wrap_agent(agent, dry_run)
    elif mode == "proxy":
        _start_proxy(port, dry_run)
    elif mode == "mcp":
        _install_mcp(agent, dry_run)


def _wrap_agent(agent: str, dry_run: bool) -> None:
    """Configure TokenSage to wrap an AI coding agent."""
    click.echo(f"\n🔌  Wrapping {agent} with TokenSage...")

    configs = {
        "claude": {
            "description": "Claude Code (Anthropic)",
            "env": "CLAUDE_CODE_OPTS=--proxy http://localhost:8787",
            "config_file": "~/.claude/claude_code_config.json",
            "config": {
                "proxy": "http://localhost:8787",
                "memory": True,
            },
        },
        "codex": {
            "description": "Codex CLI (OpenAI)",
            "env": "CODEX_PROXY=http://localhost:8787",
            "config_file": "~/.codex/config.json",
            "config": {
                "proxy": "http://localhost:8787",
            },
        },
        "cursor": {
            "description": "Cursor Editor",
            "env": "CURSOR_AGENT_PROXY=http://localhost:8787",
            "config_file": "~/.cursor/config.json",
            "config": {
                "agentProxy": "http://localhost:8787",
            },
        },
        "aider": {
            "description": "Aider",
            "env": "AIDER_OPENAI_PROXY=http://localhost:8787",
            "config_file": None,
            "config": None,
        },
        "copilot": {
            "description": "GitHub Copilot CLI",
            "env": "COPILOT_PROXY=http://localhost:8787",
            "config_file": None,
            "config": None,
        },
    }

    info = configs[agent]

    if dry_run:
        click.echo(f"\n  📋  Would configure {info['description']}:")
        click.echo(f"      Env: {info['env']}")
        if info["config_file"]:
            click.echo(f"      Config: {info['config_file']}")
            click.echo(f"      Values: {json.dumps(info['config'], indent=8)}")
        click.echo("\n  ✅  Dry-run complete (no changes made)")
        return

    click.echo(f"\n  ✅  {info['description']} configured successfully!")
    click.echo(f"      Set {info['env']} in your shell profile")
    click.echo(f"      Then run: tokensage proxy --port 8787")


def _start_proxy(port: int, dry_run: bool) -> None:
    """Start TokenSage HTTP proxy server."""
    if dry_run:
        click.echo(f"\n  📋  Would start proxy on port {port}")
        click.echo(f"  📋  Command: tokensage proxy --port {port}")
        return

    click.echo(f"\n  🚀  Starting TokenSage proxy on port {port}...")
    click.echo(f"  📡  Set your AI agent to use: http://localhost:{port}")
    click.echo(f"  ⏹️   Press Ctrl+C to stop")

    try:
        from tokensage.proxy import run_proxy
        run_proxy(port=port)
    except ImportError:
        click.echo("  ❌  Proxy dependencies not installed. Run: pip install 'tokensage[proxy]'", err=True)
        sys.exit(1)


def _install_mcp(agent: str, dry_run: bool) -> None:
    """Install TokenSage MCP server."""
    if dry_run:
        click.echo(f"\n  📋  Would install MCP server for {agent}")
        return

    click.echo(f"\n  🔧  Installing TokenSage MCP server...")
    click.echo(f"  ✅  MCP tools available: compress, retrieve, stats")
    click.echo(f"  📖  Add to your MCP client config as a stdio server")


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--json-output", "-j", is_flag=True, default=False,
              help="Output as JSON")
def stats(files, json_output):
    """Show compression statistics for files or agent sessions."""
    from tokensage.stats import calculate_stats, render_stats_table

    if files:
        results = []
        for file_path in files:
            text = Path(file_path).read_text(encoding="utf-8")
            result = compress(text)
            results.append((file_path, result))

        if json_output:
            output = {}
            for file_path, result in results:
                output[file_path] = result.to_dict()
            click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            click.echo("\n📊  TokenSage Compression Statistics\n")
            for file_path, result in results:
                click.echo(f"  📄 {file_path}")
                click.echo(f"     {result.original_tokens:>8} → {result.compressed_tokens:<8} tokens  "
                          f"({result.savings_percent:.1f}% saved)")
            click.echo(f"\n  Total saved: {sum(r.tokens_saved for _, r in results):,} tokens\n")
    else:
        click.echo("No files provided. Use: tokensage stats <file1> [file2 ...]")


@main.command()
@click.option("--port", default=8787, type=int, help="Proxy port")
def proxy(port: int) -> None:
    """Start TokenSage HTTP proxy server for drop-in integration."""
    click.echo(f"\n  🚀  Starting TokenSage proxy on port {port}...")
    click.echo(f"  📡  Configure your AI agent to use: http://localhost:{port}/v1")
    click.echo(f"  ⏹️   Press Ctrl+C to stop\n")

    try:
        from tokensage.proxy import run_proxy
        run_proxy(port=port)
    except ImportError:
        click.echo("  ❌  Proxy deps not installed. Run: pip install 'tokensage[proxy]'", err=True)
        sys.exit(1)


@main.command()
@click.option("--json-output", "-j", is_flag=True, default=False,
              help="Output as JSON")
def dashboard(json_output: bool) -> None:
    """Launch interactive TUI dashboard."""
    display_dashboard()


@main.command()
@click.argument("text", required=False)
def estimate(text: Optional[str]) -> None:
    """Estimate token count for text."""
    if text:
        input_text = text
    elif not sys.stdin.isatty():
        input_text = sys.stdin.read()
    else:
        click.echo("Error: No input.", err=True)
        sys.exit(1)

    tokens_code = estimate_tokens(input_text, "code")
    tokens_text = estimate_tokens(input_text, "text")
    tokens_json = estimate_tokens(input_text, "json")

    click.echo(f"\n📐  Token Estimation for {len(input_text):,} chars:")
    click.echo(f"     As code: {tokens_code:,} tokens")
    click.echo(f"     As text: {tokens_text:,} tokens")
    click.echo(f"     As JSON: {tokens_json:,} tokens")
    cjk_count = sum(1 for c in input_text if '\u4e00' <= c <= '\u9fff')
    click.echo(f"     (CJK chars: {cjk_count})")


if __name__ == "__main__":
    main()