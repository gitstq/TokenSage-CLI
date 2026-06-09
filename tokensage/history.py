"""History record management for TokenSage-CLI."""

import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from tokensage.utils import get_data_dir, write_file_safe, read_file_safe


class HistoryRecord:
    """A single history record for a compression operation.

    Attributes:
        timestamp: Unix timestamp of the operation.
        operation: Type of operation (compress, count, cost).
        input_text_preview: First 200 chars of input text.
        original_tokens: Original token count.
        compressed_tokens: Compressed token count.
        strategy: Compression strategy used.
        level: Compression level.
        content_type: Detected content type.
        savings_percent: Percentage of tokens saved.
        cost_savings: Estimated cost savings in USD.
        model: LLM model used for cost calculation.
        metadata: Additional metadata.
    """

    def __init__(
        self,
        operation: str = "compress",
        input_text_preview: str = "",
        original_tokens: int = 0,
        compressed_tokens: int = 0,
        strategy: str = "",
        level: str = "medium",
        content_type: str = "text",
        savings_percent: float = 0.0,
        cost_savings: float = 0.0,
        model: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.timestamp = time.time()
        self.operation = operation
        self.input_text_preview = input_text_preview[:200]
        self.original_tokens = original_tokens
        self.compressed_tokens = compressed_tokens
        self.strategy = strategy
        self.level = level
        self.content_type = content_type
        self.savings_percent = savings_percent
        self.cost_savings = cost_savings
        self.model = model
        self.metadata = metadata or {}

    @property
    def datetime_str(self) -> str:
        """Formatted datetime string."""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def tokens_saved(self) -> int:
        """Number of tokens saved."""
        return self.original_tokens - self.compressed_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "input_text_preview": self.input_text_preview,
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "strategy": self.strategy,
            "level": self.level,
            "content_type": self.content_type,
            "savings_percent": self.savings_percent,
            "cost_savings": self.cost_savings,
            "model": self.model,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoryRecord":
        """Create a HistoryRecord from a dictionary."""
        record = cls(
            operation=data.get("operation", "compress"),
            input_text_preview=data.get("input_text_preview", ""),
            original_tokens=data.get("original_tokens", 0),
            compressed_tokens=data.get("compressed_tokens", 0),
            strategy=data.get("strategy", ""),
            level=data.get("level", "medium"),
            content_type=data.get("content_type", "text"),
            savings_percent=data.get("savings_percent", 0.0),
            cost_savings=data.get("cost_savings", 0.0),
            model=data.get("model", ""),
            metadata=data.get("metadata", {}),
        )
        if "timestamp" in data:
            record.timestamp = data["timestamp"]
        return record


class HistoryManager:
    """Manages compression history records.

    Stores records in a JSON file in the data directory.
    Supports adding, querying, and clearing history.
    """

    def __init__(self, history_file: Optional[str] = None):
        """Initialize the history manager.

        Args:
            history_file: Path to the history file. If None, uses default.
        """
        if history_file:
            self.history_file = history_file
        else:
            data_dir = get_data_dir()
            self.history_file = os.path.join(data_dir, "history.json")
        self._records: List[HistoryRecord] = []
        self._load()

    def _load(self) -> None:
        """Load history from file."""
        if os.path.exists(self.history_file):
            try:
                content = read_file_safe(self.history_file)
                data = json.loads(content)
                self._records = [HistoryRecord.from_dict(r) for r in data]
            except (json.JSONDecodeError, IOError, KeyError):
                self._records = []
        else:
            self._records = []

    def _save(self) -> None:
        """Save history to file."""
        data = [r.to_dict() for r in self._records]
        write_file_safe(self.history_file, json.dumps(data, indent=2, ensure_ascii=False))

    def add_record(self, record: HistoryRecord) -> None:
        """Add a new history record.

        Args:
            record: The HistoryRecord to add.
        """
        self._records.append(record)
        self._save()

    def get_records(
        self,
        limit: int = 20,
        operation: Optional[str] = None,
        strategy: Optional[str] = None,
    ) -> List[HistoryRecord]:
        """Get history records, optionally filtered.

        Args:
            limit: Maximum number of records to return.
            operation: Filter by operation type.
            strategy: Filter by compression strategy.

        Returns:
            List of HistoryRecord objects, most recent first.
        """
        records = list(self._records)
        if operation:
            records = [r for r in records if r.operation == operation]
        if strategy:
            records = [r for r in records if r.strategy == strategy]
        records.reverse()
        return records[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics from history.

        Returns:
            Dictionary with aggregate statistics.
        """
        if not self._records:
            return {
                "total_operations": 0,
                "total_tokens_saved": 0,
                "total_cost_savings": 0.0,
                "average_savings_percent": 0.0,
                "most_used_strategy": "",
            }

        total_saved = sum(r.tokens_saved for r in self._records)
        total_cost = sum(r.cost_savings for r in self._records)
        avg_savings = sum(r.savings_percent for r in self._records) / len(self._records)

        # Most used strategy
        strategy_counts: Dict[str, int] = {}
        for r in self._records:
            if r.strategy:
                strategy_counts[r.strategy] = strategy_counts.get(r.strategy, 0) + 1
        most_used = max(strategy_counts, key=strategy_counts.get) if strategy_counts else ""

        return {
            "total_operations": len(self._records),
            "total_tokens_saved": total_saved,
            "total_cost_savings": total_cost,
            "average_savings_percent": avg_savings,
            "most_used_strategy": most_used,
        }

    def clear(self) -> int:
        """Clear all history records.

        Returns:
            Number of records that were cleared.
        """
        count = len(self._records)
        self._records = []
        self._save()
        return count

    def __len__(self) -> int:
        """Return the number of history records."""
        return len(self._records)
