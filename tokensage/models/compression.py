"""Data models for compression operations."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CompressionLevel(Enum):
    """Compression intensity levels."""

    MILD = "mild"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"


class ContentType(Enum):
    """Types of content that can be compressed."""

    AUTO = "auto"
    JSON = "json"
    CODE = "code"
    MARKDOWN = "markdown"
    TEXT = "text"


class CompressionStrategy(Enum):
    """Available compression strategies."""

    JSON_COMPRESS = "json"
    CODE_COMPRESS = "code"
    MARKDOWN_COMPRESS = "markdown"
    TEXT_COMPRESS = "text"
    CN_OPTIMIZE = "cn_optimize"


@dataclass
class CompressionResult:
    """Result of a compression operation.

    Attributes:
        original_text: The original text before compression.
        compressed_text: The text after compression.
        original_tokens: Estimated token count of original text.
        compressed_tokens: Estimated token count of compressed text.
        compression_ratio: Percentage of tokens saved.
        strategy: The compression strategy used.
        level: The compression level applied.
        content_type: The detected content type.
        metadata: Additional metadata about the compression.
        reversible: Whether the compression is reversible.
        index_data: Index data for reversible decompression.
    """

    original_text: str = ""
    compressed_text: str = ""
    original_tokens: int = 0
    compressed_tokens: int = 0
    compression_ratio: float = 0.0
    strategy: str = ""
    level: CompressionLevel = CompressionLevel.MEDIUM
    content_type: ContentType = ContentType.AUTO
    metadata: Dict[str, Any] = field(default_factory=dict)
    reversible: bool = False
    index_data: Optional[Dict[str, Any]] = None

    @property
    def tokens_saved(self) -> int:
        """Number of tokens saved by compression."""
        return self.original_tokens - self.compressed_tokens

    @property
    def text_reduction_ratio(self) -> float:
        """Percentage of text length reduction."""
        if len(self.original_text) == 0:
            return 0.0
        return (
            (len(self.original_text) - len(self.compressed_text))
            / len(self.original_text)
            * 100.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a dictionary for serialization.

        Returns:
            Dictionary representation of the compression result.
        """
        return {
            "original_length": len(self.original_text),
            "compressed_length": len(self.compressed_text),
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "tokens_saved": self.tokens_saved,
            "compression_ratio": self.compression_ratio,
            "text_reduction_ratio": self.text_reduction_ratio,
            "strategy": self.strategy,
            "level": self.level.value,
            "content_type": self.content_type.value,
            "reversible": self.reversible,
        }

    def __str__(self) -> str:
        """Human-readable summary of the compression result."""
        lines = [
            f"Compression Result ({self.strategy})",
            f"  Level: {self.level.value}",
            f"  Content Type: {self.content_type.value}",
            f"  Original: {self.original_tokens} tokens ({len(self.original_text)} chars)",
            f"  Compressed: {self.compressed_tokens} tokens ({len(self.compressed_text)} chars)",
            f"  Tokens Saved: {self.tokens_saved} ({self.compression_ratio:.1f}%)",
            f"  Text Reduction: {self.text_reduction_ratio:.1f}%",
        ]
        return "\n".join(lines)


@dataclass
class CompressionConfig:
    """Configuration for a compression operation.

    Attributes:
        level: Compression intensity level.
        content_type: Type of content (or AUTO for detection).
        strategy: Specific strategy to use (or None for auto-selection).
        reversible: Whether to enable reversible compression.
        preserve_structure: Whether to preserve document structure.
        max_output_tokens: Maximum tokens for compressed output.
        language_hint: Language hint for optimization ('en', 'zh', 'mixed').
    """

    level: CompressionLevel = CompressionLevel.MEDIUM
    content_type: ContentType = ContentType.AUTO
    strategy: Optional[CompressionStrategy] = None
    reversible: bool = False
    preserve_structure: bool = True
    max_output_tokens: Optional[int] = None
    language_hint: str = "auto"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompressionConfig":
        """Create a CompressionConfig from a dictionary.

        Args:
            data: Dictionary with configuration values.

        Returns:
            A CompressionConfig instance.
        """
        config = cls()
        if "level" in data:
            config.level = CompressionLevel(data["level"])
        if "content_type" in data:
            config.content_type = ContentType(data["content_type"])
        if "strategy" in data:
            config.strategy = CompressionStrategy(data["strategy"])
        if "reversible" in data:
            config.reversible = bool(data["reversible"])
        if "preserve_structure" in data:
            config.preserve_structure = bool(data["preserve_structure"])
        if "max_output_tokens" in data:
            config.max_output_tokens = int(data["max_output_tokens"])
        if "language_hint" in data:
            config.language_hint = data["language_hint"]
        return config


@dataclass
class BatchCompressionResult:
    """Result of a batch compression operation.

    Attributes:
        results: List of individual compression results.
        total_original_tokens: Total tokens across all inputs.
        total_compressed_tokens: Total tokens after compression.
        total_savings: Total tokens saved.
    """

    results: List[CompressionResult] = field(default_factory=list)

    @property
    def total_original_tokens(self) -> int:
        """Sum of original token counts."""
        return sum(r.original_tokens for r in self.results)

    @property
    def total_compressed_tokens(self) -> int:
        """Sum of compressed token counts."""
        return sum(r.compressed_tokens for r in self.results)

    @property
    def total_savings(self) -> int:
        """Total tokens saved."""
        return self.total_original_tokens - self.total_compressed_tokens

    @property
    def overall_ratio(self) -> float:
        """Overall compression ratio percentage."""
        if self.total_original_tokens == 0:
            return 0.0
        return self.total_savings / self.total_original_tokens * 100.0
