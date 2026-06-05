"""TokenSage statistics and benchmarking."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table

from tokensage.compress import CompressionResult

console = Console()


@dataclass
class StatsSummary:
    """Summary of multiple compression results."""
    total_original: int = 0
    total_compressed: int = 0
    count: int = 0
    results: List[CompressionResult] = field(default_factory=list)

    @property
    def total_saved(self) -> int:
        return self.total_original - self.total_compressed

    @property
    def avg_savings(self) -> float:
        if self.total_original == 0:
            return 0.0
        return (1 - self.total_compressed / self.total_original) * 100


def calculate_stats(results: List[CompressionResult]) -> StatsSummary:
    """Aggregate statistics from multiple compression results."""
    summary = StatsSummary()
    for r in results:
        summary.total_original += r.original_tokens
        summary.total_compressed += r.compressed_tokens
        summary.count += 1
        summary.results.append(r)
    return summary


def render_stats_table(summary: StatsSummary, title: str = "Compression Statistics") -> str:
    """Render statistics as a rich table."""
    table = Table(title=title, box=None)
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="green")

    table.add_row("Files/Documents", str(summary.count))
    table.add_row("Total Original Tokens", f"{summary.total_original:,}")
    table.add_row("Total Compressed Tokens", f"{summary.total_compressed:,}")
    table.add_row("Total Tokens Saved", f"{summary.total_saved:,}")
    table.add_row("Average Savings", f"{summary.avg_savings:.1f}%")

    console.print(table)
    return str(table)