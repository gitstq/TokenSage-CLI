"""Smart compression engine for TokenSage-CLI.

Provides multiple compression strategies for different content types,
including JSON, code, Markdown, and plain text. Supports configurable
compression levels and reversible compression modes.
"""

import ast
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from tokensage.cn_optimizer import ChineseOptimizer
from tokensage.exceptions import CompressionError, DecompressionError
from tokensage.models.compression import (
    CompressionConfig,
    CompressionLevel,
    CompressionResult,
    CompressionStrategy,
    ContentType,
)
from tokensage.token_counter import TokenCounter
from tokensage.utils import detect_content_type, detect_language


class JSONCompressor:
    """JSON-specific compression strategies.

    Compresses JSON by removing redundant keys, trimming values,
    reducing numeric precision, and compacting whitespace.
    """

    # Keys that are often redundant in LLM context
    REDUNDANT_KEY_PATTERNS = [
        "id", "uuid", "created_at", "updated_at", "timestamp",
        "version", "_v", "_rev", "etag", "checksum", "hash",
    ]

    def __init__(self, level: CompressionLevel = CompressionLevel.MEDIUM):
        """Initialize JSON compressor.

        Args:
            level: Compression intensity level.
        """
        self.level = level

    def compress(self, text: str) -> str:
        """Compress JSON text.

        Args:
            text: JSON string to compress.

        Returns:
            Compressed JSON string.

        Raises:
            CompressionError: If JSON parsing fails.
        """
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError) as e:
            raise CompressionError(f"Invalid JSON: {e}") from e

        data = self._compress_value(data)
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    def _compress_value(self, value: Any) -> Any:
        """Recursively compress a JSON value.

        Args:
            value: Any JSON-compatible value.

        Returns:
            Compressed value.
        """
        if isinstance(value, dict):
            return self._compress_dict(value)
        elif isinstance(value, list):
            return [self._compress_value(item) for item in value]
        elif isinstance(value, str):
            return self._compress_string(value)
        elif isinstance(value, float):
            return self._compress_float(value)
        elif isinstance(value, bool):
            return value
        elif value is None:
            return value
        else:
            return value

    def _compress_dict(self, data: Dict) -> Dict:
        """Compress a JSON object.

        Args:
            data: Dictionary to compress.

        Returns:
            Compressed dictionary.
        """
        result = {}
        for key, value in data.items():
            # Skip redundant keys based on compression level
            if self._is_redundant_key(key):
                continue

            # Compress key name in aggressive mode
            compressed_key = key
            if self.level == CompressionLevel.AGGRESSIVE:
                compressed_key = self._shorten_key(key)

            result[compressed_key] = self._compress_value(value)
        return result

    def _is_redundant_key(self, key: str) -> bool:
        """Check if a key is considered redundant.

        Args:
            key: The key name.

        Returns:
            True if the key should be removed.
        """
        if self.level == CompressionLevel.MILD:
            return False

        key_lower = key.lower().strip()
        for pattern in self.REDUNDANT_KEY_PATTERNS:
            if key_lower == pattern or key_lower.endswith(f"_{pattern}"):
                return True
        return False

    def _shorten_key(self, key: str) -> str:
        """Shorten a key name for aggressive compression.

        Args:
            key: Original key name.

        Returns:
            Shortened key name.
        """
        # Remove common prefixes
        for prefix in ("get_", "set_", "is_", "has_", "the_", "a_"):
            if key.startswith(prefix) and len(key) > len(prefix) + 2:
                return key[len(prefix):]

        # Abbreviate common suffixes
        replacements = {
            "name": "nm",
            "value": "val",
            "count": "cnt",
            "number": "num",
            "index": "idx",
            "description": "desc",
            "timestamp": "ts",
            "identifier": "id",
            "address": "addr",
            "message": "msg",
            "information": "info",
            "configuration": "cfg",
            "parameter": "param",
            "argument": "arg",
            "reference": "ref",
            "position": "pos",
            "length": "len",
            "maximum": "max",
            "minimum": "min",
            "average": "avg",
            "total": "tot",
            "current": "cur",
            "previous": "prev",
            "result": "res",
            "response": "resp",
            "request": "req",
            "error": "err",
            "success": "ok",
            "status": "st",
            "type": "tp",
            "data": "d",
            "content": "cnt",
            "title": "ttl",
            "label": "lbl",
        }
        return replacements.get(key.lower(), key)

    def _compress_string(self, value: str) -> str:
        """Compress a string value.

        Args:
            value: String to compress.

        Returns:
            Compressed string.
        """
        # Trim whitespace
        value = value.strip()

        if self.level == CompressionLevel.AGGRESSIVE:
            # Collapse multiple spaces
            value = re.sub(r" {2,}", " ", value)
            # Collapse multiple newlines
            value = re.sub(r"\n{3,}", "\n\n", value)
            # Remove leading/trailing whitespace per line
            lines = value.split("\n")
            value = "\n".join(line.strip() for line in lines if line.strip())

        elif self.level == CompressionLevel.MEDIUM:
            # Collapse multiple spaces
            value = re.sub(r" {2,}", " ", value)
            # Collapse multiple newlines
            value = re.sub(r"\n{3,}", "\n\n", value)

        return value

    def _compress_float(self, value: float) -> Any:
        """Compress a float value by reducing precision.

        Args:
            value: Float to compress.

        Returns:
            Compressed numeric value.
        """
        if self.level == CompressionLevel.MILD:
            return value

        # Round to reasonable precision
        if abs(value) >= 100:
            return round(value, 1)
        elif abs(value) >= 1:
            return round(value, 2)
        elif abs(value) >= 0.01:
            return round(value, 3)
        else:
            return round(value, 4)


class CodeCompressor:
    """Code-specific compression strategies.

    Compresses code by removing comments, blank lines, and
    unnecessary whitespace while preserving functionality.
    """

    # Comment patterns for various languages
    COMMENT_PATTERNS = {
        "python": [
            (r'#.*$', ""),  # Single-line comments
            (r'"""[\s\S]*?"""', ""),  # Triple-quoted strings (docstrings)
            (r"'''[\s\S]*?'''", ""),  # Triple-quoted strings
        ],
        "javascript": [
            (r'//.*$', ""),  # Single-line comments
            (r'/\*[\s\S]*?\*/', ""),  # Multi-line comments
        ],
        "java": [
            (r'//.*$', ""),
            (r'/\*[\s\S]*?\*/', ""),
        ],
        "generic": [
            (r'//.*$', ""),
            (r'#.*$', ""),
            (r'/\*[\s\S]*?\*/', ""),
        ],
    }

    def __init__(self, level: CompressionLevel = CompressionLevel.MEDIUM):
        """Initialize code compressor.

        Args:
            level: Compression intensity level.
        """
        self.level = level

    def compress(self, text: str, language: str = "generic") -> str:
        """Compress code text.

        Args:
            text: Code string to compress.
            language: Programming language hint.

        Returns:
            Compressed code string.
        """
        lines = text.split("\n")
        result_lines = []

        for line in lines:
            compressed = self._compress_line(line, language)
            if compressed is not None:
                result_lines.append(compressed)

        return "\n".join(result_lines)

    def _compress_line(self, line: str, language: str) -> Optional[str]:
        """Compress a single line of code.

        Args:
            line: A line of code.
            language: Programming language hint.

        Returns:
            Compressed line, or None if the line should be removed.
        """
        stripped = line.strip()

        # Remove blank lines
        if not stripped:
            if self.level == CompressionLevel.AGGRESSIVE:
                return None
            return ""

        # Remove comment-only lines
        if self._is_comment_line(stripped, language):
            if self.level != CompressionLevel.MILD:
                return None
            return ""

        # Remove inline comments (medium and aggressive)
        if self.level in (CompressionLevel.MEDIUM, CompressionLevel.AGGRESSIVE):
            line = self._remove_inline_comment(line, language)

        # Trim trailing whitespace
        line = line.rstrip()

        # Collapse multiple spaces to single space
        if self.level == CompressionLevel.AGGRESSIVE:
            line = re.sub(r" {2,}", " ", line)

        return line

    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if a line is a comment-only line.

        Args:
            line: The line to check.
            language: Programming language.

        Returns:
            True if the line is a comment.
        """
        patterns = self.COMMENT_PATTERNS.get(language, self.COMMENT_PATTERNS["generic"])
        for pattern, _ in patterns:
            if re.match(pattern, line.strip()):
                return True
        # Generic comment detection
        if line.strip().startswith("#"):
            return True
        if line.strip().startswith("//"):
            return True
        if line.strip().startswith("/*") or line.strip().startswith("*"):
            return True
        return False

    def _remove_inline_comment(self, line: str, language: str) -> str:
        """Remove inline comments from a line.

        Args:
            line: The line to process.
            language: Programming language.

        Returns:
            Line with inline comments removed.
        """
        # Simple approach: find comment start outside of strings
        in_string = False
        string_char = None
        i = 0

        while i < len(line):
            char = line[i]

            if in_string:
                if char == "\\" and i + 1 < len(line):
                    i += 2
                    continue
                if char == string_char:
                    in_string = False
            else:
                if char in ('"', "'"):
                    in_string = True
                    string_char = char
                elif char == "#":
                    return line[:i].rstrip()
                elif char == "/" and i + 1 < len(line):
                    if line[i + 1] == "/":
                        return line[:i].rstrip()
                    elif line[i + 1] == "*":
                        # Find end of block comment
                        end = line.find("*/", i + 2)
                        if end != -1:
                            return line[:i] + line[end + 2:].rstrip()
                        return line[:i].rstrip()
            i += 1

        return line


class MarkdownCompressor:
    """Markdown-specific compression strategies.

    Compresses Markdown while preserving document structure
    and readability.
    """

    def __init__(self, level: CompressionLevel = CompressionLevel.MEDIUM):
        """Initialize Markdown compressor.

        Args:
            level: Compression intensity level.
        """
        self.level = level

    def compress(self, text: str) -> str:
        """Compress Markdown text.

        Args:
            text: Markdown string to compress.

        Returns:
            Compressed Markdown string.
        """
        lines = text.split("\n")
        result_lines = []

        for line in lines:
            compressed = self._compress_line(line)
            if compressed is not None:
                result_lines.append(compressed)

        # Remove excessive blank lines
        result = "\n".join(result_lines)
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()

    def _compress_line(self, line: str) -> Optional[str]:
        """Compress a single Markdown line.

        Args:
            line: A line of Markdown.

        Returns:
            Compressed line, or None if it should be removed.
        """
        stripped = line.strip()

        # Handle blank lines
        if not stripped:
            if self.level == CompressionLevel.AGGRESSIVE:
                return None
            return ""

        # Remove HTML comments
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            return None

        # Compress headers - remove extra spaces
        if re.match(r"^#{1,6}\s", stripped):
            stripped = re.sub(r"(#{1,6})\s{2,}", r"\1 ", stripped)
            return stripped

        # Compress list items
        if re.match(r"^[\*\-\+]\s", stripped):
            stripped = re.sub(r"^[\*\-\+]\s{2,}", "* ", stripped)
            return stripped

        if re.match(r"^\d+\.\s", stripped):
            stripped = re.sub(r"^(\d+\.)\s{2,}", r"\1 ", stripped)
            return stripped

        # Compress bold/italic markers
        if self.level == CompressionLevel.AGGRESSIVE:
            # Convert **bold** to *bold* (save 1 char per bold marker)
            stripped = re.sub(r"\*\*(.+?)\*\*", r"*\1*", stripped)
            # Convert __bold__ to _bold_
            stripped = re.sub(r"__(.+?)__", r"_\1_", stripped)

        # Collapse multiple spaces within text
        if self.level != CompressionLevel.MILD:
            stripped = re.sub(r" {2,}", " ", stripped)

        # Trim trailing whitespace
        return stripped.rstrip()


class TextCompressor:
    """General text compression strategies.

    Compresses plain text by removing redundant whitespace,
    trimming content, and applying smart truncation.
    """

    def __init__(
        self,
        level: CompressionLevel = CompressionLevel.MEDIUM,
        max_tokens: Optional[int] = None,
    ):
        """Initialize text compressor.

        Args:
            level: Compression intensity level.
            max_tokens: Maximum token limit for output.
        """
        self.level = level
        self.max_tokens = max_tokens
        self._counter = TokenCounter()

    def compress(self, text: str) -> str:
        """Compress plain text.

        Args:
            text: Text string to compress.

        Returns:
            Compressed text string.
        """
        # Normalize whitespace
        text = self._normalize_whitespace(text)

        # Remove redundant content
        text = self._remove_redundancy(text)

        # Apply token limit if set
        if self.max_tokens:
            text = self._truncate_to_tokens(text, self.max_tokens)

        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text.

        Args:
            text: Text to normalize.

        Returns:
            Text with normalized whitespace.
        """
        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Collapse multiple spaces
        text = re.sub(r" {2,}", " ", text)

        # Collapse multiple newlines
        if self.level == CompressionLevel.AGGRESSIVE:
            text = re.sub(r"\n{3,}", "\n", text)
        else:
            text = re.sub(r"\n{3,}", "\n\n", text)

        # Trim each line
        lines = text.split("\n")
        lines = [line.rstrip() for line in lines]
        text = "\n".join(lines)

        return text

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant content patterns.

        Args:
            text: Text to process.

        Returns:
            Text with redundancies removed.
        """
        if self.level == CompressionLevel.MILD:
            return text

        # Remove filler words and redundant phrases
        filler_patterns = [
            (r"\b(in order to)\b", "to"),
            (r"\b(for the purpose of)\b", "for"),
            (r"\b(in the event that)\b", "if"),
            (r"\b(at this point in time)\b", "now"),
            (r"\b(it is important to note that)\b", ""),
            (r"\b(it should be noted that)\b", ""),
            (r"\b(as a matter of fact)\b", ""),
            (r"\b(for all intents and purposes)\b", ""),
            (r"\b(in light of the fact that)\b", "since"),
            (r"\b(due to the fact that)\b", "because"),
            (r"\b(each and every)\b", "each"),
            (r"\b(first and foremost)\b", "first"),
            (r"\b(by means of)\b", "by"),
            (r"\b(in close proximity to)\b", "near"),
            (r"\b(a large number of)\b", "many"),
            (r"\b(the vast majority of)\b", "most"),
            (r"\b(in spite of the fact that)\b", "although"),
            (r"\b(on account of the fact that)\b", "because"),
            (r"\b(needless to say)\b", ""),
            (r"\b(it goes without saying that)\b", ""),
            (r"\b(to make a long story short)\b", ""),
            (r"\b(for what it is worth)\b", ""),
            (r"\b(in other words)\b", "i.e."),
            (r"\b(as a result of)\b", "from"),
            (r"\b(prior to)\b", "before"),
            (r"\b(subsequent to)\b", "after"),
            (r"\b(in the vicinity of)\b", "near"),
            (r"\b(with regard to)\b", "about"),
            (r"\b(in connection with)\b", "about"),
            (r"\b(having regard to)\b", "about"),
            (r"\b(in accordance with)\b", "per"),
            (r"\b(pursuant to)\b", "per"),
            (r"\b(in the context of)\b", "in"),
            (r"\b(from the perspective of)\b", "for"),
            (r"\b(taking into consideration)\b", "considering"),
            (r"\b(on the basis of)\b", "based on"),
            (r"\b(with reference to)\b", "about"),
            (r"\b(in relation to)\b", "for"),
            (r"\b(when it comes to)\b", "for"),
            (r"\b(as far as \w+ is concerned)\b", "for"),
            (r"\b(it is worth mentioning that)\b", ""),
            (r"\b(it is evident that)\b", ""),
            (r"\b(it is clear that)\b", ""),
            (r"\b(it is well known that)\b", ""),
            (r"\b(it is generally accepted that)\b", ""),
            (r"\b(without a doubt)\b", ""),
            (r"\b(beyond a shadow of a doubt)\b", ""),
            (r"\b(in this day and age)\b", "today"),
            (r"\b(at the end of the day)\b", ""),
            (r"\b(last but not least)\b", "finally"),
            (r"\b(to sum up)\b", ""),
            (r"\b(in summary)\b", ""),
            (r"\b(in conclusion)\b", ""),
            (r"\b(to begin with)\b", ""),
            (r"\b(when all is said and done)\b", ""),
        ]

        for pattern, replacement in filler_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Remove repeated lines (keep first occurrence)
        lines = text.split("\n")
        seen_lines: Dict[str, int] = {}
        result = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                result.append(line)
                continue

            if stripped in seen_lines:
                seen_lines[stripped] += 1
                # Remove if repeated 2+ times (medium) or 2+ times (aggressive)
                if seen_lines[stripped] >= 2 and self.level != CompressionLevel.MILD:
                    continue
            else:
                seen_lines[stripped] = 1
            result.append(line)

        text = "\n".join(result)

        # Clean up extra whitespace left by filler removal
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\.\.", ".", text)
        text = re.sub(r"\s+\.", ".", text)
        text = re.sub(r"\.\s+\.", ". ", text)

        return text

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within a token budget.

        Uses binary search to find the truncation point.

        Args:
            text: Text to truncate.
            max_tokens: Maximum token count.

        Returns:
            Truncated text.
        """
        current_tokens = self._counter.count(text)
        if current_tokens <= max_tokens:
            return text

        # Binary search for the right truncation point
        low, high = 0, len(text)
        while low < high:
            mid = (low + high + 1) // 2
            truncated = text[:mid]
            tokens = self._counter.count(truncated)
            if tokens <= max_tokens:
                low = mid
            else:
                high = mid - 1

        result = text[:low]
        # Try to end at a sentence or line boundary
        for suffix in (".\n", ". ", "\n", " ", ","):
            last_pos = result.rfind(suffix)
            if last_pos > len(result) * 0.7:
                result = result[: last_pos + len(suffix)]
                break

        return result


class Compressor:
    """Main compression engine that orchestrates all compression strategies.

    Automatically detects content type and selects the appropriate
    compression strategy. Supports all compression levels and
    reversible compression mode.
    """

    def __init__(self, config: Optional[CompressionConfig] = None):
        """Initialize the compression engine.

        Args:
            config: Compression configuration. Uses defaults if None.
        """
        self.config = config or CompressionConfig()
        self._cn_optimizer = ChineseOptimizer()
        self._counter = TokenCounter()

    def compress(self, text: str) -> CompressionResult:
        """Compress text using the configured strategy.

        Args:
            text: Text to compress.

        Returns:
            CompressionResult with details about the compression.

        Raises:
            CompressionError: If compression fails.
        """
        if not text:
            return CompressionResult(
                original_text=text,
                compressed_text="",
                original_tokens=0,
                compressed_tokens=0,
            )

        try:
            # Detect content type
            content_type = self.config.content_type
            if content_type == ContentType.AUTO:
                content_type = ContentType(detect_content_type(text))

            # Count original tokens
            original_tokens = self._counter.count(text)

            # Select and apply compression strategy
            strategy_name, compressed_text = self._apply_strategy(text, content_type)

            # Apply Chinese optimization if applicable
            language = detect_language(text)
            if language in ("zh", "mixed"):
                compressed_text = self._cn_optimizer.optimize(
                    compressed_text, level=self.config.level.value
                )

            # Count compressed tokens
            compressed_tokens = self._counter.count(compressed_text)

            # Calculate compression ratio
            compression_ratio = 0.0
            if original_tokens > 0:
                compression_ratio = (
                    (original_tokens - compressed_tokens) / original_tokens * 100.0
                )

            return CompressionResult(
                original_text=text,
                compressed_text=compressed_text,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=compression_ratio,
                strategy=strategy_name,
                level=self.config.level,
                content_type=content_type,
                reversible=self.config.reversible,
            )

        except Exception as e:
            raise CompressionError(f"Compression failed: {e}") from e

    def _apply_strategy(
        self, text: str, content_type: ContentType
    ) -> Tuple[str, str]:
        """Apply the appropriate compression strategy.

        Args:
            text: Text to compress.
            content_type: Detected content type.

        Returns:
            Tuple of (strategy_name, compressed_text).
        """
        # Use specific strategy if configured
        if self.config.strategy:
            strategy = self.config.strategy
        else:
            # Auto-select strategy based on content type
            strategy_map = {
                ContentType.JSON: CompressionStrategy.JSON_COMPRESS,
                ContentType.CODE: CompressionStrategy.CODE_COMPRESS,
                ContentType.MARKDOWN: CompressionStrategy.MARKDOWN_COMPRESS,
                ContentType.TEXT: CompressionStrategy.TEXT_COMPRESS,
            }
            strategy = strategy_map.get(content_type, CompressionStrategy.TEXT_COMPRESS)

        compressed = self._compress_with_strategy(text, strategy)
        return strategy.value, compressed

    def _compress_with_strategy(
        self, text: str, strategy: CompressionStrategy
    ) -> str:
        """Compress text with a specific strategy.

        Args:
            text: Text to compress.
            strategy: The compression strategy to use.

        Returns:
            Compressed text.
        """
        if strategy == CompressionStrategy.JSON_COMPRESS:
            compressor = JSONCompressor(level=self.config.level)
            return compressor.compress(text)
        elif strategy == CompressionStrategy.CODE_COMPRESS:
            compressor = CodeCompressor(level=self.config.level)
            return compressor.compress(text)
        elif strategy == CompressionStrategy.MARKDOWN_COMPRESS:
            compressor = MarkdownCompressor(level=self.config.level)
            return compressor.compress(text)
        elif strategy == CompressionStrategy.TEXT_COMPRESS:
            compressor = TextCompressor(
                level=self.config.level,
                max_tokens=self.config.max_output_tokens,
            )
            return compressor.compress(text)
        elif strategy == CompressionStrategy.CN_OPTIMIZE:
            return self._cn_optimizer.optimize(
                text, level=self.config.level.value
            )
        else:
            compressor = TextCompressor(level=self.config.level)
            return compressor.compress(text)

    def compress_file(self, filepath: str) -> CompressionResult:
        """Compress a file.

        Args:
            filepath: Path to the file to compress.

        Returns:
            CompressionResult.

        Raises:
            CompressionError: If file reading fails.
        """
        from tokensage.utils import read_file_safe

        try:
            text = read_file_safe(filepath)
            return self.compress(text)
        except Exception as e:
            raise CompressionError(f"Failed to compress file: {e}") from e

    def decompress(self, compressed_text: str, index_data: Dict) -> str:
        """Decompress text using index data (for reversible mode).

        Note: Full reversible compression is a future enhancement.
        This currently returns the compressed text as-is.

        Args:
            compressed_text: The compressed text.
            index_data: Index data from the compression result.

        Returns:
            Decompressed text.

        Raises:
            DecompressionError: If decompression fails.
        """
        if not index_data:
            raise DecompressionError("No index data provided for decompression")
        # Placeholder for future reversible compression implementation
        return compressed_text
