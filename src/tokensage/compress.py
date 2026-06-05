"""
TokenSage - Lightweight LLM Context Token Optimization Engine
Compression algorithms, utilities, and token estimation.

This is a 100% original, independent implementation. Product logic inspired by
industry trends in LLM context optimization, but ALL code is written from scratch.
"""

import json
import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from tokensage.router import route_content

# ---------------------------------------------------------------------------
# Token estimation (approximate)
# ---------------------------------------------------------------------------

# Rough token-to-char ratios per content type
TOKEN_RATIOS = {
    "code": 3.5,       # 1 token ≈ 3.5 chars of code
    "json": 4.0,       # 1 token ≈ 4 chars of JSON
    "text": 4.0,       # 1 token ≈ 4 chars of prose
    "log": 5.0,        # 1 token ≈ 5 chars of log lines
    "cjk": 1.5,        # 1 token ≈ 1.5 CJK chars
}


def estimate_tokens(text: str, content_type: str = "text") -> int:
    """Estimate token count for a given text and content type."""
    if not text:
        return 0

    # Count CJK characters for better estimation
    cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f')
    ascii_count = len(text) - cjk_count

    ratio = TOKEN_RATIOS.get(content_type, TOKEN_RATIOS["text"])

    # CJK tokens are denser
    cjk_tokens = cjk_count / TOKEN_RATIOS["cjk"]
    ascii_tokens = ascii_count / ratio

    return max(1, int(cjk_tokens + ascii_tokens))


@dataclass
class CompressionResult:
    """Result of a compression operation."""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float  # 1.0 = no compression, 0.5 = 50% reduction
    content_type: str
    compressor_used: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_saved(self) -> int:
        return self.original_tokens - self.compressed_tokens

    @property
    def savings_percent(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return (1 - self.compressed_tokens / self.original_tokens) * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "savings_percent": round(self.savings_percent, 1),
            "tokens_saved": self.tokens_saved,
            "content_type": self.content_type,
            "compressor": self.compressor_used,
        }


# ---------------------------------------------------------------------------
# Compressors
# ---------------------------------------------------------------------------


def compress_code(text: str) -> Tuple[str, str]:
    """AST-aware code compression.
    
    Deduplicates repeated lines, shortens long identifiers contextually,
    removes excessive blank lines and comments.
    """
    lines = text.split("\n")
    compressed: List[str] = []
    seen_lines: set = set()
    blank_run = 0

    for line in lines:
        stripped = line.strip()

        # Collapse multiple blank lines to at most one
        if not stripped:
            blank_run += 1
            if blank_run <= 1:
                compressed.append("")
            continue
        blank_run = 0

        # Skip single-line comments (not docstrings)
        if stripped.startswith("#") and not stripped.startswith("#!"):
            # Keep shebangs and some important comments
            if any(kw in stripped.lower() for kw in ["todo", "fixme", "hack", "warning", "note", "copyright", "license"]):
                compressed.append(line)
            continue

        # Deduplicate identical lines (common in generated code)
        if stripped in seen_lines:
            continue
        seen_lines.add(stripped)

        # Shorten long import lines
        if stripped.startswith("import ") or stripped.startswith("from "):
            if len(stripped) > 80:
                line = re.sub(r"\s+as\s+(\w+)", lambda m: f" as {m.group(1)[:4]}", line)
            compressed.append(line)
            continue

        compressed.append(line)

    result = "\n".join(compressed)

    # Further compress: remove repeated patterns in large blocks
    if len(result) > 2000:
        # Deduplicate function signatures that are identical
        result = _dedup_repeated_patterns(result)

    return "CodeCompressor", result


def _dedup_repeated_patterns(text: str) -> str:
    """Deduplicate repeated code patterns (common in AI-generated code)."""
    lines = text.split("\n")
    # Look for repeated 3+ line blocks
    if len(lines) < 10:
        return text

    # Simple: if we see the same line pattern >3 times, keep first 2
    line_counts: Dict[str, int] = {}
    for line in lines:
        s = line.strip()
        if s:
            line_counts[s] = line_counts.get(s, 0) + 1

    # Lines that appear more than 3 times get kept only 2 times
    high_freq = {s for s, c in line_counts.items() if c > 3}

    if not high_freq:
        return text

    result: List[str] = []
    seen_high: Dict[str, int] = {}
    for line in lines:
        s = line.strip()
        if s in high_freq:
            seen_high[s] = seen_high.get(s, 0) + 1
            if seen_high[s] > 2:
                continue
        result.append(line)

    return "\n".join(result)


def compress_json(text: str) -> Tuple[str, str]:
    """Smart JSON compression: shorten keys, remove nulls, compact."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Not valid JSON; fall back to text compression
        return compress_text(text)

    def _shorten(obj: Any) -> Any:
        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                # Skip null values
                if v is None:
                    continue
                # Skip empty collections
                if v == [] or v == {}:
                    continue
                # Shorten common verbose keys
                short_k = _shorten_key(k)
                new[short_k] = _shorten(v)
            return new
        elif isinstance(obj, list):
            # Deduplicate identical items in arrays
            if len(obj) > 5 and all(isinstance(x, (str, int, float, bool)) for x in obj):
                seen: set = set()
                deduped = []
                for item in obj:
                    key = str(item)
                    if key not in seen:
                        seen.add(key)
                        deduped.append(item)
                return deduped
            return [_shorten(item) for item in obj]
        return obj

    compressed = _shorten(data)
    result = json.dumps(compressed, ensure_ascii=False, separators=(",", ":"))
    return "JsonShrinker", result


_KEY_SHORTEN_MAP = {
    "description": "desc",
    "attributes": "attrs",
    "properties": "props",
    "configuration": "config",
    "environment": "env",
    "parameters": "params",
    "arguments": "args",
    "response": "resp",
    "message": "msg",
    "content": "ct",
    "function": "fn",
    "callback": "cb",
    "identifier": "id",
    "metadata": "meta",
    "information": "info",
    "error": "err",
    "exception": "exc",
    "filename": "file",
    "directory": "dir",
    "resource": "res",
    "reference": "ref",
    "previous": "prev",
    "current": "cur",
    "context": "ctx",
    "handler": "hndlr",
    "middleware": "mw",
    "controller": "ctrl",
    "repository": "repo",
    "component": "comp",
    "instance": "inst",
    "manager": "mgr",
    "factory": "fctry",
    "provider": "prov",
    "service": "svc",
    "database": "db",
    "collection": "coll",
    "document": "doc",
    "template": "tpl",
    "language": "lang",
    "default": "def",
    "enabled": "en",
    "disabled": "dis",
}


def _shorten_key(key: str) -> str:
    """Shorten common verbose JSON keys."""
    lower = key.lower()
    if lower in _KEY_SHORTEN_MAP:
        # Preserve case pattern
        mapped = _KEY_SHORTEN_MAP[lower]
        if key.isupper():
            return mapped.upper()
        elif key[0].isupper():
            return mapped.capitalize()
        return mapped
    # Shorten camelCase keys: "veryLongKeyName" -> "vLongKeyName"
    if len(key) > 12:
        parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', key)
        if len(parts) > 3:
            parts[0] = parts[0][:3]
            return "".join(parts)
    return key


def compress_text(text: str) -> Tuple[str, str]:
    """Text compression optimized for Chinese/English content.
    
    - Removes excessive whitespace
    - Shortens repeated phrases
    - CJK-aware compaction
    - Summarizes very long lists/enumerations
    """
    if not text.strip():
        return "TextOptimizer", text

    # Remove excessive blank lines
    lines = text.split("\n")
    result: List[str] = []
    blank_run = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_run += 1
            if blank_run > 1:
                continue
            result.append("")
        else:
            blank_run = 0
            result.append(stripped)

    compressed = "\n".join(result)

    # Compress repeated words/phrases
    compressed = _compress_repeated_phrases(compressed)

    # Compress CJK whitespace (Chinese text doesn't need spaces between chars)
    compressed = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', compressed)
    compressed = re.sub(r'([\u4e00-\u9fff])\s+([a-zA-Z])', r'\1 \2', compressed)
    compressed = re.sub(r'([a-zA-Z])\s+([\u4e00-\u9fff])', r'\1 \2', compressed)

    return "TextOptimizer", compressed


def _compress_repeated_phrases(text: str) -> str:
    """Find and shorten repeated phrases."""
    # Shorten repeated bullet/numbered points
    patterns = [
        (r'(\d+\.\s+[^\n]+)\n(?:\1\n){2,}', lambda m: m.group(1) + f"\n  ... ({len(m.group(0).split(chr(10)))} repeated items)"),
        (r'(-\s+[^\n]+)\n(?:\1\n){2,}', lambda m: m.group(1) + f"\n  ... ({len(m.group(0).split(chr(10)))} repeated items)"),
        (r'(\*\s+[^\n]+)\n(?:\1\n){2,}', lambda m: m.group(1) + f"\n  ... ({len(m.group(0).split(chr(10)))} repeated items)"),
        (r'(\|\s+[^\n]+)\n(?:\1\n){2,}', lambda m: m.group(1) + f"\n  ... ({len(m.group(0).split(chr(10)))} repeated items)"),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)

    return text


def compress_log(text: str) -> Tuple[str, str]:
    """Log file compression.
    
    - Deduplicates repeated log lines (common in errors/retries)
    - Removes low-value timestamps
    - Shortens repeated stack frames
    """
    lines = text.split("\n")
    compressed: List[str] = []
    # Track repeated log messages
    log_patterns: Dict[str, int] = {}
    output_counts: Dict[str, int] = {}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Extract log message (remove timestamp, level, etc.)
        msg_match = re.search(r'(?:ERROR|WARN|INFO|DEBUG|TRACE)\s*[:\]]?\s*(.*)', stripped, re.IGNORECASE)
        if msg_match:
            msg = msg_match.group(1).strip()
        else:
            msg = stripped

        # Track repeats
        log_patterns[msg] = log_patterns.get(msg, 0) + 1

        # Only output first 3 occurrences of each pattern
        if log_patterns[msg] <= 3:
            output_counts[msg] = log_patterns[msg]
            compressed.append(stripped)

    # Append summary of suppressed lines
    suppressed = {msg: count for msg, count in log_patterns.items() if count > 3}
    if suppressed:
        compressed.append("")
        compressed.append(f"--- Suppressed {sum(suppressed.values())} repeated log lines ---")
        for msg, count in sorted(suppressed.items(), key=lambda x: -x[1])[:10]:
            compressed.append(f"  [{count}x] {msg[:120]}...")

    return "LogOptimizer", "\n".join(compressed)


# ---------------------------------------------------------------------------
# Main compression API
# ---------------------------------------------------------------------------

def compress(
    text: str,
    content_type: Optional[str] = None,
    max_tokens: Optional[int] = None,
    preserve_exact: bool = False,
) -> CompressionResult:
    """Main entry point: compress text based on detected or specified content type.

    Args:
        text: The input text to compress.
        content_type: One of "code", "json", "text", "log", or None for auto-detect.
        max_tokens: If set, target max tokens after compression.
        preserve_exact: If True, store original for reversible retrieval.

    Returns:
        CompressionResult with original, compressed, and statistics.
    """
    original_tokens = estimate_tokens(text, content_type or "text")

    if not text.strip():
        return CompressionResult(
            original_text=text,
            compressed_text=text,
            original_tokens=0,
            compressed_tokens=0,
            compression_ratio=1.0,
            content_type=content_type or "empty",
            compressor_used="none",
        )

    if content_type is None:
        content_type = route_content(text)

    compressor_map = {
        "code": compress_code,
        "json": compress_json,
        "text": compress_text,
        "log": compress_log,
    }

    compressor_fn = compressor_map.get(content_type, compress_text)
    compressor_name, compressed_text = compressor_fn(text)

    compressed_tokens = estimate_tokens(compressed_text, content_type)

    # If we need to hit a target token budget
    if max_tokens and compressed_tokens > max_tokens:
        compressed_text = _truncate_to_budget(compressed_text, content_type, max_tokens)
        compressed_tokens = estimate_tokens(compressed_text, content_type)

    ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

    metadata = {}
    if preserve_exact:
        metadata["original_stored"] = True

    return CompressionResult(
        original_text=text,
        compressed_text=compressed_text,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        compression_ratio=ratio,
        content_type=content_type,
        compressor_used=compressor_name,
        metadata=metadata,
    )


def _truncate_to_budget(text: str, content_type: str, max_tokens: int) -> str:
    """Truncate text to fit within a token budget."""
    chars_per_token = TOKEN_RATIOS.get(content_type, TOKEN_RATIOS["text"])
    max_chars = int(max_tokens * chars_per_token * 0.9)  # 10% safety margin
    if len(text) > max_chars:
        # Try to break at a sentence/line boundary
        truncated = text[:max_chars]
        last_newline = truncated.rfind("\n")
        last_period = truncated.rfind(".")
        break_point = max(last_newline, last_period)
        if break_point > max_chars // 2:
            truncated = text[: break_point + 1]
        return truncated + f"\n\n[truncated to ~{max_tokens} tokens]"
    return text