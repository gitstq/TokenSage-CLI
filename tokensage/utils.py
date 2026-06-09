"""Utility functions for TokenSage-CLI."""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


def detect_content_type(text: str) -> str:
    """Detect the type of content in the given text.

    Args:
        text: The text to analyze.

    Returns:
        Content type string: 'json', 'code', 'markdown', or 'text'.
    """
    stripped = text.strip()

    # JSON detection
    if stripped and stripped[0] in ("{", "["):
        try:
            json.loads(stripped)
            return "json"
        except (json.JSONDecodeError, ValueError):
            pass

    # Markdown detection - look for common markdown patterns
    markdown_patterns = [
        r"^#{1,6}\s",  # Headers
        r"^\*\s",  # Unordered list
        r"^\d+\.\s",  # Ordered list
        r"\[.+\]\(.+\)",  # Links
        r"```[\w]*\n",  # Code blocks
        r"^\|.*\|.*\|",  # Tables
        r"^>\s",  # Blockquotes
        r"^-{3,}$",  # Horizontal rules
    ]
    for pattern in markdown_patterns:
        if re.search(pattern, stripped, re.MULTILINE):
            return "markdown"

    # Code detection - look for code-like patterns
    code_indicators = [
        r"^\s*(def |class |import |from |return |if |for |while |async |await )",
        r"^\s*(function |const |let |var |=> |export )",
        r"^\s*(public |private |protected |static |void |int |string )",
        r"^\s*#\s*include",
        r"^\s*package\s+\w+",
        r"^\s*(fn |use |mod |pub |impl |struct |enum )",
    ]
    code_match_count = 0
    for pattern in code_indicators:
        if re.search(pattern, stripped, re.MULTILINE):
            code_match_count += 1
    if code_match_count >= 2:
        return "code"

    # Check if it looks like code by indentation and syntax
    lines = stripped.split("\n")
    indented_lines = sum(1 for line in lines if line.startswith(("  ", "\t")) and line.strip())
    if indented_lines > len(lines) * 0.3 and len(lines) > 3:
        return "code"

    return "text"


def detect_language(text: str) -> str:
    """Detect the primary language of the text.

    Args:
        text: The text to analyze.

    Returns:
        Language code: 'zh', 'en', 'mixed', or 'unknown'.
    """
    if not text:
        return "unknown"

    total_chars = 0
    cjk_chars = 0
    latin_chars = 0

    for char in text:
        if char.isspace() or char in '.,;:!?\'"()-[]{}<>@#$%^&*_+=|\\/~`':
            continue
        total_chars += 1
        # CJK Unified Ideographs and common CJK ranges
        cp = ord(char)
        if (
            (0x4E00 <= cp <= 0x9FFF)  # CJK Unified Ideographs
            or (0x3400 <= cp <= 0x4DBF)  # CJK Extension A
            or (0x20000 <= cp <= 0x2A6DF)  # CJK Extension B
            or (0xF900 <= cp <= 0xFAFF)  # CJK Compatibility Ideographs
            or (0x2F800 <= cp <= 0x2FA1F)  # CJK Compatibility Supplement
            or (0x3000 <= cp <= 0x303F)  # CJK Symbols and Punctuation
            or (0xFF00 <= cp <= 0xFFEF)  # Fullwidth Forms
        ):
            cjk_chars += 1
        elif char.isalpha():
            latin_chars += 1

    if total_chars == 0:
        return "unknown"

    cjk_ratio = cjk_chars / total_chars
    latin_ratio = latin_chars / total_chars

    if cjk_ratio > 0.7:
        return "zh"
    elif latin_ratio > 0.7:
        return "en"
    elif cjk_ratio > 0.1 and latin_ratio > 0.1:
        return "mixed"
    elif cjk_ratio > latin_ratio:
        return "zh"
    else:
        return "en"


def format_number(n: int) -> str:
    """Format a number with comma separators.

    Args:
        n: The number to format.

    Returns:
        Formatted string with comma separators.
    """
    return f"{n:,}"


def format_cost(cost: float, currency: str = "USD") -> str:
    """Format a cost value.

    Args:
        cost: The cost value in USD.
        currency: Currency symbol.

    Returns:
        Formatted cost string.
    """
    if cost < 0.01:
        return f"{currency} ${cost:.6f}"
    elif cost < 1.0:
        return f"{currency} ${cost:.4f}"
    else:
        return f"{currency} ${cost:.2f}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length with a suffix.

    Args:
        text: The text to truncate.
        max_length: Maximum length including suffix.
        suffix: Suffix to add when truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def read_file_safe(filepath: str, encoding: str = "utf-8") -> str:
    """Safely read a file with encoding fallback.

    Args:
        filepath: Path to the file.
        encoding: Preferred encoding.

    Returns:
        File contents as string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to common encodings
        for fallback_enc in ("utf-8-sig", "gbk", "gb2312", "gb18030", "latin-1"):
            try:
                with open(filepath, "r", encoding=fallback_enc) as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        raise IOError(f"Cannot decode file: {filepath}")


def write_file_safe(
    filepath: str, content: str, encoding: str = "utf-8"
) -> None:
    """Safely write content to a file, creating directories as needed.

    Args:
        filepath: Path to the file.
        content: Content to write.
        encoding: File encoding.

    Raises:
        IOError: If the file cannot be written.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


def get_config_dir() -> str:
    """Get the configuration directory for TokenSage.

    Returns:
        Path to the configuration directory.
    """
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return os.path.join(base, "TokenSage")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/TokenSage")
    else:
        return os.path.expanduser("~/.config/tokensage")


def get_data_dir() -> str:
    """Get the data directory for TokenSage (history, cache, etc.).

    Returns:
        Path to the data directory.
    """
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return os.path.join(base, "TokenSage", "data")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/TokenSage/data")
    else:
        return os.path.expanduser("~/.local/share/tokensage")


def is_rich_available() -> bool:
    """Check if the rich library is available.

    Returns:
        True if rich is importable, False otherwise.
    """
    try:
        __import__("rich")
        return True
    except ImportError:
        return False


def create_ascii_bar(value: float, max_value: float, width: int = 30) -> str:
    """Create an ASCII progress bar.

    Args:
        value: Current value.
        max_value: Maximum value.
        width: Bar width in characters.

    Returns:
        ASCII bar string.
    """
    if max_value == 0:
        ratio = 0.0
    else:
        ratio = min(value / max_value, 1.0)
    filled = int(ratio * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"


def create_ascii_chart(
    data: List[Tuple[str, float]], width: int = 50, height: int = 15
) -> str:
    """Create a simple ASCII bar chart.

    Args:
        data: List of (label, value) tuples.
        width: Maximum bar width.
        height: Not used (kept for API compatibility).

    Returns:
        ASCII chart as a string.
    """
    if not data:
        return "No data to display."

    max_val = max(v for _, v in data) if data else 1
    if max_val == 0:
        max_val = 1

    lines = []
    max_label_len = max(len(label) for label, _ in data)
    for label, value in data:
        bar_len = int((value / max_val) * width) if max_val > 0 else 0
        bar = "#" * bar_len
        line = f"{label:>{max_label_len}} | {bar} {value:.1f}"
        lines.append(line)

    return "\n".join(lines)


def estimate_tokens_simple(text: str) -> int:
    """Very simple token estimation (rough approximation).

    This is a fast, rough estimate: ~4 chars per token for English,
    ~1.5 chars per token for Chinese.

    Args:
        text: The text to estimate.

    Returns:
        Estimated token count.
    """
    if not text:
        return 0

    cjk_count = 0
    other_count = 0
    for char in text:
        cp = ord(char)
        if (
            (0x4E00 <= cp <= 0x9FFF)
            or (0x3400 <= cp <= 0x4DBF)
            or (0xF900 <= cp <= 0xFAFF)
            or (0xFF00 <= cp <= 0xFFEF)
        ):
            cjk_count += 1
        else:
            other_count += 1

    # CJK characters average ~1.5 tokens per character
    # Latin characters average ~4 characters per token
    cjk_tokens = int(cjk_count / 1.5)
    latin_tokens = int(other_count / 4.0)
    return cjk_tokens + latin_tokens
