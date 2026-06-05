"""
TokenSage basic usage examples.
Run: python examples/basic_usage.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tokensage import compress
from tokensage.compress import estimate_tokens
from tokensage.router import route_content


def example_1_basic_compression():
    """Basic text compression."""
    print("=" * 60)
    print("Example 1: Basic Text Compression")
    print("=" * 60)

    text = """
TokenSage is a lightweight LLM context token optimization engine.
It helps reduce the number of tokens consumed by AI agents, saving
you money and improving response times.

It works by:
1. Automatically detecting the content type (code, JSON, logs, prose)
2. Applying the optimal compression strategy for each type
3. Preserving semantic meaning while reducing token count
4. Supporting reversible compression for critical content

Key features include:
- Smart code compression with AST awareness
- JSON key shortening and deduplication
- CJK-optimized text compression
- Log pattern deduplication
- Cross-platform CLI and library API
- HTTP proxy for drop-in integration
    """

    result = compress(text)
    print(f"Content type: {result.content_type}")
    print(f"Compressor: {result.compressor_used}")
    print(f"Original: {result.original_tokens:,} tokens ({len(text)} chars)")
    print(f"Compressed: {result.compressed_tokens:,} tokens ({len(result.compressed_text)} chars)")
    print(f"Savings: {result.savings_percent:.1f}%")
    print()


def example_2_code_compression():
    """Code compression example."""
    print("=" * 60)
    print("Example 2: Code Compression")
    print("=" * 60)

    code = '''
import os
import sys
import json
from typing import List, Optional

# Configuration constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

class DataProcessor:
    """Processes data from various sources."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.timeout = self.config.get("timeout", DEFAULT_TIMEOUT)
        self.retries = self.config.get("retries", MAX_RETRIES)

    def process_item(self, item: dict) -> dict:
        """Process a single data item."""
        result = {}
        for key, value in item.items():
            if value is not None:
                transformed = self._transform(key, value)
                if transformed is not None:
                    result[key] = transformed
        return result

    def _transform(self, key: str, value: any) -> any:
        """Transform a single value."""
        if isinstance(value, str):
            return value.strip().lower()
        elif isinstance(value, (int, float)):
            return value * 2
        return value


def main():
    processor = DataProcessor()
    data = {"name": "  Hello  ", "count": 5, "active": True}
    result = processor.process_item(data)
    print(f"Processed: {result}")
    return result


if __name__ == "__main__":
    main()
'''

    result = compress(code, content_type="code")
    print(f"Content type: {result.content_type}")
    print(f"Compressor: {result.compressor_used}")
    print(f"Original: {result.original_tokens:,} tokens ({len(code)} chars)")
    print(f"Compressed: {result.compressed_tokens:,} tokens ({len(result.compressed_text)} chars)")
    print(f"Savings: {result.savings_percent:.1f}%")
    print()


def example_3_json_compression():
    """JSON compression example."""
    print("=" * 60)
    print("Example 3: JSON Compression")
    print("=" * 60)

    import json
    data = {
        "configuration": {
            "application_name": "TokenSage",
            "version_number": "1.0.0",
            "environment_settings": {
                "production_mode": True,
                "debug_logging_enabled": False,
                "maximum_connections": 100,
                "connection_timeout_seconds": 30,
            },
            "database_configuration": {
                "host_name": "localhost",
                "port_number": 5432,
                "database_name": "tokensage",
                "username": "admin",
                "password": None,
            },
            "features": ["compression", "proxy", "memory", "wrap", "compression", "proxy"],
            "empty_list": [],
            "null_field": None,
        }
    }
    text = json.dumps(data, indent=2)

    result = compress(text, content_type="json")
    print(f"Content type: {result.content_type}")
    print(f"Compressor: {result.compressor_used}")
    print(f"Original: {result.original_tokens:,} tokens ({len(text)} chars)")
    print(f"Compressed: {result.compressed_tokens:,} tokens ({len(result.compressed_text)} chars)")
    print(f"Savings: {result.savings_percent:.1f}%")
    print()


def example_4_auto_detect():
    """Auto-detection example."""
    print("=" * 60)
    print("Example 4: Content Type Auto-Detection")
    print("=" * 60)

    samples = [
        ("Code", "def hello():\n    print('world')"),
        ("JSON", '{"name": "test", "value": 42}'),
        ("Log", "2024-06-05 10:30:00 ERROR Connection refused"),
        ("Text", "This is plain English text for testing purposes."),
        ("CJK Text", "这是一段中文测试文本，用于验证内容类型自动检测功能。"),
    ]

    for label, text in samples:
        detected = route_content(text)
        print(f"  {label:8s} → {detected}")
    print()


if __name__ == "__main__":
    example_1_basic_compression()
    example_2_code_compression()
    example_3_json_compression()
    example_4_auto_detect()