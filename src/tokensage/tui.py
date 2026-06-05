"""TokenSage TUI - Terminal dashboard for compression statistics."""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

from tokensage.compress import CompressionResult

console = Console()


def display_result(result: CompressionResult) -> None:
    """Display a single compression result with rich formatting."""
    # Header
    savings_color = "green" if result.savings_percent >= 50 else "yellow" if result.savings_percent >= 20 else "red"

    console.print()
    console.print(Panel(
        Text.assemble(
            ("♾️  ", "bold cyan"),
            ("TokenSage Compression Result", "bold"),
        ),
        box=box.HEAVY,
    ))

    # Metrics table
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    table.add_row("Content Type", result.content_type.upper())
    table.add_row("Compressor", result.compressor_used)
    table.add_row("Original Tokens", f"{result.original_tokens:,}")
    table.add_row("Compressed Tokens", f"{result.compressed_tokens:,}")
    table.add_row("Tokens Saved", f"[bold green]{result.tokens_saved:,}[/bold green]")
    table.add_row("Savings", f"[bold {savings_color}]{result.savings_percent:.1f}%[/bold {savings_color}]")

    console.print(table)
    console.print()

    # Preview compressed output
    preview = result.compressed_text[:500]
    if len(result.compressed_text) > 500:
        preview += "\n... (truncated)"

    console.print(Panel(
        preview,
        title="[bold]Compressed Output (preview)[/bold]",
        border_style="dim",
        box=box.ROUNDED,
    ))
    console.print()


def display_dashboard() -> None:
    """Display interactive TUI dashboard placeholder."""
    console.print(Panel(
        Text.assemble(
            ("♾️  TokenSage Dashboard\n\n", "bold cyan"),
            ("This is the interactive TUI dashboard.\n", ""),
            ("Use the CLI commands instead:\n", "dim"),
            ("  tokensage compress <text>    - Compress text\n", "green"),
            ("  tokensage stats <files>      - Show compression stats\n", "green"),
            ("  tokensage integrate --agent  - Wrap an AI agent\n", "green"),
            ("  tokensage proxy --port 8787  - Start proxy server\n", "green"),
        ),
        box=box.HEAVY,
        title="♾️  TokenSage",
    ))
    console.print()