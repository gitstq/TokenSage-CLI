"""TUI Dashboard for TokenSage-CLI.

Provides a terminal-based dashboard using the rich library (optional dependency).
Automatically degrades to plain text mode when rich is not available.
"""

import os
import sys
from typing import Any, Dict, List, Optional

from tokensage.history import HistoryManager, HistoryRecord
from tokensage.utils import (
    create_ascii_bar,
    create_ascii_chart,
    format_cost,
    format_number,
    is_rich_available,
)


class PlainTextDashboard:
    """Plain text fallback dashboard when rich is not available.

    Provides basic text-based visualization of compression statistics,
    history, and cost information.
    """

    def __init__(self):
        """Initialize the plain text dashboard."""
        self._history = HistoryManager()

    def show_welcome(self) -> str:
        """Generate welcome banner.

        Returns:
            Welcome banner string.
        """
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ██████╗ ███╗   ██╗ ██████╗ ██████╗ ███████╗       ║
║  ██╔════╝██╔═══██╗████╗  ██║██╔════╝ ██╔══██╗██╔════╝       ║
║  ██║     ██║   ██║██╔██╗ ██║██║  ███╗██████╔╝█████╗         ║
║  ██║     ██║   ██║██║╚██╗██║██║   ██║██╔══██╗██╔══╝         ║
║  ╚██████╗╚██████╔╝██║ ╚████║╚██████╔╝██║  ██║███████╗      ║
║   ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝      ║
║                                                              ║
║   Token Compression & Cost Optimization Engine              ║
║   Version 0.1.0 | Zero Dependencies Required                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        return banner

    def show_compression_result(self, result: Dict[str, Any]) -> str:
        """Display compression results.

        Args:
            result: Compression result dictionary.

        Returns:
            Formatted result string.
        """
        lines = [
            "",
            "=" * 60,
            "  COMPRESSION RESULT",
            "=" * 60,
            "",
            f"  Strategy:     {result.get('strategy', 'N/A')}",
            f"  Level:        {result.get('level', 'N/A')}",
            f"  Content Type: {result.get('content_type', 'N/A')}",
            "",
            "  --- Token Analysis ---",
            f"  Original Tokens:   {format_number(result.get('original_tokens', 0))}",
            f"  Compressed Tokens: {format_number(result.get('compressed_tokens', 0))}",
            f"  Tokens Saved:      {format_number(result.get('tokens_saved', 0))}",
            f"  Savings:           {result.get('compression_ratio', 0):.1f}%",
            "",
            "  --- Text Analysis ---",
            f"  Original Length:   {format_number(result.get('original_length', 0))} chars",
            f"  Compressed Length: {format_number(result.get('compressed_length', 0))} chars",
            f"  Text Reduction:     {result.get('text_reduction_ratio', 0):.1f}%",
            "",
            "  --- Compression Visualization ---",
            create_ascii_bar(
                result.get("compressed_tokens", 0),
                result.get("original_tokens", 1),
                width=40,
            ),
            f"  {'Compressed':^20} {'Original':^20}",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    def show_cost_analysis(self, result: Dict[str, Any]) -> str:
        """Display cost analysis results.

        Args:
            result: Cost analysis dictionary.

        Returns:
            Formatted cost analysis string.
        """
        lines = [
            "",
            "=" * 60,
            "  COST ANALYSIS",
            "=" * 60,
            "",
            f"  Model:              {result.get('model', 'N/A')}",
            f"  Provider:           {result.get('provider', 'N/A')}",
            "",
            "  --- Token Usage ---",
            f"  Original Input:     {format_number(result.get('original_input_tokens', 0))} tokens",
            f"  Compressed Input:  {format_number(result.get('compressed_input_tokens', 0))} tokens",
            f"  Tokens Saved:      {format_number(result.get('tokens_saved', 0))}",
            f"  Token Savings:     {result.get('token_savings_percent', 0):.1f}%",
            "",
            "  --- Cost Breakdown ---",
            f"  Original Cost:      {format_cost(result.get('original_cost', 0))}",
            f"  Compressed Cost:   {format_cost(result.get('compressed_cost', 0))}",
            f"  Total Savings:      {format_cost(result.get('savings', 0))}",
            f"  Savings Percentage: {result.get('savings_percent', 0):.1f}%",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    def show_model_comparison(self, comparisons: List[Dict[str, Any]]) -> str:
        """Display model cost comparison.

        Args:
            comparisons: List of model comparison dictionaries.

        Returns:
            Formatted comparison table.
        """
        if not comparisons:
            return "\n  No models to compare."

        header = (
            f"  {'Model':<25} {'Provider':<12} "
            f"{'Input $/1K':<12} {'Output $/1K':<12} {'Total Cost':<12}"
        )
        separator = "  " + "-" * 73

        lines = [
            "",
            "=" * 80,
            "  MODEL COST COMPARISON",
            "=" * 80,
            "",
            header,
            separator,
        ]

        for comp in comparisons:
            line = (
                f"  {comp['model']:<25} {comp['provider']:<12} "
                f"${comp['input_cost']:<11.4f} ${comp['output_cost']:<11.4f} "
                f"${comp['total_cost']:<11.4f}"
            )
            lines.append(line)

        lines.append(separator)
        lines.append("")
        return "\n".join(lines)

    def show_history(self, records: List[HistoryRecord], limit: int = 20) -> str:
        """Display compression history.

        Args:
            records: List of history records.
            limit: Maximum records to display.

        Returns:
            Formatted history string.
        """
        if not records:
            return "\n  No history records found."

        lines = [
            "",
            "=" * 80,
            f"  COMPRESSION HISTORY (showing {min(len(records), limit)} records)",
            "=" * 80,
            "",
            f"  {'Time':<20} {'Operation':<12} {'Strategy':<15} "
            f"{'Saved':<10} {'Savings %':<10} {'Preview':<20}",
            "  " + "-" * 87,
        ]

        for record in records[:limit]:
            preview = (record.input_text_preview or "")[:18] + ".."
            line = (
                f"  {record.datetime_str:<20} {record.operation:<12} "
                f"{record.strategy:<15} {record.tokens_saved:<10} "
                f"{record.savings_percent:<10.1f} {preview:<20}"
            )
            lines.append(line)

        lines.append("")
        return "\n".join(lines)

    def show_stats(self, stats: Dict[str, Any]) -> str:
        """Display aggregate statistics.

        Args:
            stats: Statistics dictionary.

        Returns:
            Formatted statistics string.
        """
        lines = [
            "",
            "=" * 60,
            "  AGGREGATE STATISTICS",
            "=" * 60,
            "",
            f"  Total Operations:     {format_number(stats.get('total_operations', 0))}",
            f"  Total Tokens Saved:    {format_number(stats.get('total_tokens_saved', 0))}",
            f"  Total Cost Savings:    {format_cost(stats.get('total_cost_savings', 0))}",
            f"  Average Savings:       {stats.get('average_savings_percent', 0):.1f}%",
            f"  Most Used Strategy:    {stats.get('most_used_strategy', 'N/A')}",
            "",
        ]
        return "\n".join(lines)

    def show_savings_chart(self, records: List[HistoryRecord]) -> str:
        """Display savings trend chart.

        Args:
            records: History records for chart data.

        Returns:
            ASCII chart string.
        """
        if not records:
            return "\n  No data for chart."

        # Group by date
        daily_savings: Dict[str, float] = {}
        for record in records:
            date = record.datetime_str.split(" ")[0]
            daily_savings[date] = daily_savings.get(date, 0) + record.tokens_saved

        if not daily_savings:
            return "\n  No savings data available."

        data = list(daily_savings.items())
        chart = create_ascii_chart(data, width=40)

        lines = [
            "",
            "=" * 60,
            "  TOKEN SAVINGS TREND",
            "=" * 60,
            "",
            chart,
            "",
        ]
        return "\n".join(lines)


class RichDashboard:
    """Rich-powered TUI dashboard with enhanced visualization.

    Requires the rich library. Falls back to PlainTextDashboard
    if rich is not available.
    """

    def __init__(self):
        """Initialize the rich dashboard."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text
            from rich.layout import Layout
            from rich.columns import Columns
            from rich.progress import Progress, BarColumn, TextColumn
            from rich.tree import Tree

            self._console = Console()
            self._Panel = Panel
            self._Table = Table
            self._Text = Text
            self._Layout = Layout
            self._Columns = Columns
            self._Progress = Progress
            self._BarColumn = BarColumn
            self._TextColumn = TextColumn
            self._Tree = Tree
            self._available = True
        except ImportError:
            self._available = False
            self._console = None

        self._history = HistoryManager()
        self._plain = PlainTextDashboard()

    @property
    def available(self) -> bool:
        """Whether rich is available."""
        return self._available

    def show_welcome(self) -> None:
        """Display welcome banner."""
        if not self._available:
            print(self._plain.show_welcome())
            return

        welcome_text = Text()
        welcome_text.append("TokenSage-CLI", style="bold cyan")
        welcome_text.append("\n")
        welcome_text.append("Token Compression & Cost Optimization Engine", style="dim")
        welcome_text.append(f"\nVersion 0.1.0 | Python {sys.version.split()[0]}")

        panel = Panel(
            welcome_text,
            title="[bold green]TokenSage[/bold green]",
            subtitle="[dim]Zero Dependencies Required[/dim]",
            border_style="blue",
            padding=(1, 4),
        )
        self._console.print(panel)

    def show_compression_result(self, result: Dict[str, Any]) -> None:
        """Display compression results with rich formatting.

        Args:
            result: Compression result dictionary.
        """
        if not self._available:
            print(self._plain.show_compression_result(result))
            return

        # Create main table
        table = self._Table(
            title="Compression Result",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Strategy", str(result.get("strategy", "N/A")))
        table.add_row("Level", str(result.get("level", "N/A")))
        table.add_row("Content Type", str(result.get("content_type", "N/A")))
        table.add_row("", "")
        table.add_row("Original Tokens", format_number(result.get("original_tokens", 0)))
        table.add_row("Compressed Tokens", format_number(result.get("compressed_tokens", 0)))
        table.add_row("Tokens Saved", format_number(result.get("tokens_saved", 0)))
        table.add_row(
            "Savings",
            f"[bold green]{result.get('compression_ratio', 0):.1f}%[/bold green]",
        )
        table.add_row("", "")
        table.add_row("Original Length", f"{format_number(result.get('original_length', 0))} chars")
        table.add_row("Compressed Length", f"{format_number(result.get('compressed_length', 0))} chars")
        table.add_row("Text Reduction", f"{result.get('text_reduction_ratio', 0):.1f}%")

        self._console.print()
        self._console.print(table)

        # Progress bar visualization
        original = result.get("original_tokens", 1)
        compressed = result.get("compressed_tokens", 0)
        ratio = compressed / original if original > 0 else 0

        bar_text = (
            f"Compression: [cyan]{ratio:.1%}[/cyan] of original tokens "
            f"([green]saved {(1-ratio)*100:.1f}%[/green])"
        )
        panel = Panel(bar_text, border_style="green")
        self._console.print(panel)

    def show_cost_analysis(self, result: Dict[str, Any]) -> None:
        """Display cost analysis with rich formatting.

        Args:
            result: Cost analysis dictionary.
        """
        if not self._available:
            print(self._plain.show_cost_analysis(result))
            return

        table = self._Table(
            title="Cost Analysis",
            show_header=True,
            header_style="bold magenta",
            border_style="yellow",
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Model", str(result.get("model", "N/A")))
        table.add_row("Provider", str(result.get("provider", "N/A")))
        table.add_row("", "")
        table.add_row("Original Input Tokens", format_number(result.get("original_input_tokens", 0)))
        table.add_row("Compressed Input Tokens", format_number(result.get("compressed_input_tokens", 0)))
        table.add_row("Tokens Saved", format_number(result.get("tokens_saved", 0)))
        table.add_row("Token Savings", f"{result.get('token_savings_percent', 0):.1f}%")
        table.add_row("", "")
        table.add_row("Original Cost", format_cost(result.get("original_cost", 0)))
        table.add_row("Compressed Cost", format_cost(result.get("compressed_cost", 0)))
        table.add_row(
            "Total Savings",
            f"[bold green]{format_cost(result.get('savings', 0))}[/bold green]",
        )
        table.add_row(
            "Savings %",
            f"[bold green]{result.get('savings_percent', 0):.1f}%[/bold green]",
        )

        self._console.print()
        self._console.print(table)

    def show_model_comparison(self, comparisons: List[Dict[str, Any]]) -> None:
        """Display model cost comparison table.

        Args:
            comparisons: List of model comparison dictionaries.
        """
        if not self._available:
            print(self._plain.show_model_comparison(comparisons))
            return

        table = self._Table(
            title="Model Cost Comparison",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
        )
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Provider", style="dim")
        table.add_column("Input Cost", justify="right")
        table.add_column("Output Cost", justify="right")
        table.add_column("Total Cost", justify="right", style="bold green")

        for comp in comparisons:
            table.add_row(
                comp["model"],
                comp["provider"],
                f"${comp['input_cost']:.4f}",
                f"${comp['output_cost']:.4f}",
                f"${comp['total_cost']:.4f}",
            )

        self._console.print()
        self._console.print(table)

    def show_history(self, records: List[HistoryRecord], limit: int = 20) -> None:
        """Display compression history table.

        Args:
            records: List of history records.
            limit: Maximum records to display.
        """
        if not self._available:
            print(self._plain.show_history(records, limit))
            return

        if not records:
            self._console.print("[dim]No history records found.[/dim]")
            return

        table = self._Table(
            title=f"Compression History ({min(len(records), limit)} records)",
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
        )
        table.add_column("Time", style="dim", no_wrap=True)
        table.add_column("Operation")
        table.add_column("Strategy")
        table.add_column("Saved", justify="right")
        table.add_column("Savings %", justify="right")
        table.add_column("Preview", max_width=25)

        for record in records[:limit]:
            preview = (record.input_text_preview or "")[:22] + ".."
            table.add_row(
                record.datetime_str,
                record.operation,
                record.strategy,
                str(record.tokens_saved),
                f"{record.savings_percent:.1f}%",
                preview,
            )

        self._console.print()
        self._console.print(table)

    def show_stats(self, stats: Dict[str, Any]) -> None:
        """Display aggregate statistics.

        Args:
            stats: Statistics dictionary.
        """
        if not self._available:
            print(self._plain.show_stats(stats))
            return

        table = self._Table(
            title="Aggregate Statistics",
            show_header=True,
            header_style="bold magenta",
            border_style="green",
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="bold green")

        table.add_row("Total Operations", format_number(stats.get("total_operations", 0)))
        table.add_row("Total Tokens Saved", format_number(stats.get("total_tokens_saved", 0)))
        table.add_row("Total Cost Savings", format_cost(stats.get("total_cost_savings", 0)))
        table.add_row("Average Savings", f"{stats.get('average_savings_percent', 0):.1f}%")
        table.add_row("Most Used Strategy", str(stats.get("most_used_strategy", "N/A")))

        self._console.print()
        self._console.print(table)

    def show_savings_chart(self, records: List[HistoryRecord]) -> None:
        """Display savings trend chart.

        Args:
            records: History records for chart data.
        """
        if not self._available:
            print(self._plain.show_savings_chart(records))
            return

        # Group by date
        daily_savings: Dict[str, float] = {}
        for record in records:
            date = record.datetime_str.split(" ")[0]
            daily_savings[date] = daily_savings.get(date, 0) + record.tokens_saved

        if not daily_savings:
            self._console.print("[dim]No savings data available.[/dim]")
            return

        chart_text = create_ascii_chart(list(daily_savings.items()), width=50)
        panel = Panel(
            chart_text,
            title="[bold]Token Savings Trend[/bold]",
            border_style="cyan",
        )
        self._console.print()
        self._console.print(panel)


def get_dashboard() -> object:
    """Get the appropriate dashboard based on rich availability.

    Returns:
        A RichDashboard if rich is available, PlainTextDashboard otherwise.
    """
    if is_rich_available():
        dashboard = RichDashboard()
        if dashboard.available:
            return dashboard
    return PlainTextDashboard()
