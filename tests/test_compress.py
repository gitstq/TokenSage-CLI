"""Tests for TokenSage compression engine."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tokensage.compress import (
    compress, compress_code, compress_json, compress_text, compress_log,
    estimate_tokens, CompressionResult
)
from tokensage.router import route_content


def test_estimate_tokens():
    """Test token estimation."""
    # Empty
    assert estimate_tokens("") == 0

    # Simple text
    tokens = estimate_tokens("Hello, world!")
    assert tokens > 0

    # CJK text
    cjk_text = "你好世界这是一段中文测试文本"
    cjk_tokens = estimate_tokens(cjk_text)
    text_tokens = estimate_tokens("Hello world this is a test")
    assert cjk_tokens > 0
    assert text_tokens > 0


def test_compress_empty():
    """Test compressing empty input."""
    result = compress("")
    assert result.original_tokens == 0
    assert result.compressed_tokens == 0


def test_compress_text():
    """Test text compression."""
    text = "This is a test sentence.\n\n\n\nWith multiple blank lines.\n\n\nAnd more."
    result = compress(text, content_type="text")
    assert result.compressed_tokens <= result.original_tokens
    assert result.savings_percent >= 0
    assert result.compressor_used == "TextOptimizer"


def test_compress_code():
    """Test code compression."""
    code = '''import os
import sys
import json
from typing import List, Optional, Dict, Any

# This is a comment that should be removed
# Another comment

def hello_world_function(name: str) -> str:
    """A docstring that should be kept."""
    print(f"Hello, {name}!")
    return f"Hello, {name}!"


def hello_world_function(name: str) -> str:
    """Duplicate function that should be deduplicated."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    hello_world_function("World")
'''
    result = compress(code, content_type="code")
    assert result.compressor_used == "CodeCompressor"
    assert result.compressed_tokens <= result.original_tokens or result.compressed_text != code
    assert result.savings_percent >= 0


def test_compress_json():
    """Test JSON compression."""
    data = {
        "description": "A test object with verbose keys",
        "configuration": {
            "parameters": {
                "enabled": True,
                "timeout_seconds": 30,
                "retry_count": 3,
            },
            "environment": "production",
            "metadata": {
                "version": "1.0.0",
                "description": "Production config",
            }
        },
        "items": [1, 2, 3, 1, 2, 3, 4, 5, 1, 2],
        "null_field": None,
        "empty_list": [],
    }
    text = json.dumps(data, indent=2)
    result = compress(text, content_type="json")
    assert result.compressor_used == "JsonShrinker"
    # Should have compressed (shorter keys, removed nulls/empties, dedup)
    assert len(result.compressed_text) <= len(result.original_text)


def test_compress_log():
    """Test log compression."""
    log = """2024-01-01 10:00:00 ERROR Connection timeout to database
2024-01-01 10:00:01 ERROR Connection timeout to database
2024-01-01 10:00:02 ERROR Connection timeout to database
2024-01-01 10:00:03 WARN Retrying connection...
2024-01-01 10:00:04 ERROR Connection timeout to database
2024-01-01 10:00:05 ERROR Connection timeout to database
2024-01-01 10:00:06 INFO Connection established successfully
"""
    result = compress(log, content_type="log")
    assert result.compressor_used == "LogOptimizer"
    # Should be compressed via dedup
    assert result.compressed_tokens <= result.original_tokens


def test_auto_detect():
    """Test content type auto-detection."""
    assert route_content("def hello():\n    pass\n") == "code"
    assert route_content('{"key": "value"}') == "json"
    assert route_content("Hello, how are you?") == "text"
    assert route_content("2024-01-01 10:00:00 ERROR test") == "log"


def test_result_properties():
    """Test CompressionResult properties."""
    result = compress("Hello world", content_type="text")
    assert result.tokens_saved >= 0
    assert isinstance(result.savings_percent, float)
    assert isinstance(result.to_dict(), dict)
    assert "savings_percent" in result.to_dict()


def test_max_tokens():
    """Test max_tokens constraint."""
    long_text = "word " * 1000
    result = compress(long_text, content_type="text", max_tokens=50)
    assert result.compressed_tokens <= 100 or "truncated" in result.compressed_text


def test_cjk_compression():
    """Test CJK text compression."""
    cjk_text = "这是一段中文测试文本，用于验证TokenSage的中文压缩能力。\n\n\n\n应该能正确处理多余的空行和空格。"
    result = compress(cjk_text, content_type="text")
    assert result.savings_percent >= 0


def test_preserve_exact():
    """Test preserve_exact flag."""
    text = "Test preserve mode"
    result = compress(text, preserve_exact=True)
    assert "original_stored" in result.metadata
    assert result.metadata["original_stored"] is True


if __name__ == "__main__":
    test_estimate_tokens()
    print("✓ test_estimate_tokens")
    test_compress_empty()
    print("✓ test_compress_empty")
    test_compress_text()
    print("✓ test_compress_text")
    test_compress_code()
    print("✓ test_compress_code")
    test_compress_json()
    print("✓ test_compress_json")
    test_compress_log()
    print("✓ test_compress_log")
    test_auto_detect()
    print("✓ test_auto_detect")
    test_result_properties()
    print("✓ test_result_properties")
    test_max_tokens()
    print("✓ test_max_tokens")
    test_cjk_compression()
    print("✓ test_cjk_compression")
    test_preserve_exact()
    print("✓ test_preserve_exact")
    print("\n✅ All tests passed!")