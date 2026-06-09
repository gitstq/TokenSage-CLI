"""Unit tests for compressor module."""

import json
import os
import tempfile
import unittest

from tokensage.compressor import (
    CodeCompressor,
    Compressor,
    JSONCompressor,
    MarkdownCompressor,
    TextCompressor,
)
from tokensage.models.compression import (
    CompressionConfig,
    CompressionLevel,
    CompressionResult,
    ContentType,
)


class TestJSONCompressor(unittest.TestCase):
    """Tests for the JSONCompressor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mild = JSONCompressor(level=CompressionLevel.MILD)
        self.medium = JSONCompressor(level=CompressionLevel.MEDIUM)
        self.aggressive = JSONCompressor(level=CompressionLevel.AGGRESSIVE)

    def test_simple_json(self):
        """Test compressing simple JSON."""
        text = json.dumps({"name": "test", "value": 42}, indent=2)
        result = self.medium.compress(text)
        self.assertIn("name", result)
        self.assertIn("test", result)

    def test_compact_output(self):
        """Test that output is compact (no extra whitespace)."""
        text = json.dumps({"a": 1, "b": 2, "c": 3}, indent=4)
        result = self.medium.compress(text)
        # Compact JSON should not have newlines between keys
        self.assertNotIn("\n", result)

    def test_float_precision(self):
        """Test float precision reduction."""
        text = json.dumps({"pi": 3.14159265358979, "avg": 12.345678})
        result = self.aggressive.compress(text)
        data = json.loads(result)
        # Aggressive should reduce precision
        self.assertLessEqual(len(str(data["pi"])), 10)

    def test_nested_json(self):
        """Test compressing nested JSON."""
        text = json.dumps({
            "user": {
                "name": "John",
                "address": {
                    "city": "New York",
                    "country": "USA"
                }
            }
        }, indent=2)
        result = self.medium.compress(text)
        data = json.loads(result)
        self.assertEqual(data["user"]["name"], "John")

    def test_json_array(self):
        """Test compressing JSON array."""
        text = json.dumps([1, 2, 3, 4, 5], indent=2)
        result = self.medium.compress(text)
        data = json.loads(result)
        self.assertEqual(len(data), 5)

    def test_invalid_json(self):
        """Test that invalid JSON raises error."""
        with self.assertRaises(Exception):
            self.medium.compress("{invalid json")

    def test_string_whitespace_compression(self):
        """Test string value whitespace compression."""
        text = json.dumps({"text": "Hello   world   test"})
        result = self.medium.compress(text)
        data = json.loads(result)
        # Multiple spaces should be collapsed
        self.assertNotIn("   ", data["text"])


class TestCodeCompressor(unittest.TestCase):
    """Tests for the CodeCompressor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.medium = CodeCompressor(level=CompressionLevel.MEDIUM)
        self.aggressive = CodeCompressor(level=CompressionLevel.AGGRESSIVE)

    def test_remove_comments(self):
        """Test comment removal."""
        code = "x = 1  # This is a comment\ny = 2"
        result = self.medium.compress(code)
        self.assertNotIn("# This is a comment", result)
        self.assertIn("x = 1", result)

    def test_remove_blank_lines_aggressive(self):
        """Test blank line removal in aggressive mode."""
        code = "x = 1\n\n\n\ny = 2"
        result = self.aggressive.compress(code)
        lines = result.split("\n")
        # Should not have consecutive blank lines
        blank_count = sum(1 for l in lines if not l.strip())
        self.assertLessEqual(blank_count, 1)

    def test_preserve_functionality(self):
        """Test that code functionality is preserved."""
        code = "def add(a, b):\n    return a + b\n\n# Main\nresult = add(1, 2)"
        result = self.medium.compress(code)
        self.assertIn("def add", result)
        self.assertIn("return a + b", result)

    def test_python_code(self):
        """Test Python code compression."""
        code = '''# Calculate factorial
def factorial(n):
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test
print(factorial(5))'''
        result = self.medium.compress(code)
        self.assertIn("def factorial", result)

    def test_javascript_code(self):
        """Test JavaScript code compression."""
        code = "// Function to add numbers\nfunction add(a, b) {\n    return a + b;\n}\n// Call function\nadd(1, 2);"
        result = self.medium.compress(code, language="javascript")
        self.assertNotIn("// Function to add numbers", result)
        self.assertIn("function add", result)


class TestMarkdownCompressor(unittest.TestCase):
    """Tests for the MarkdownCompressor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.medium = MarkdownCompressor(level=CompressionLevel.MEDIUM)
        self.aggressive = MarkdownCompressor(level=CompressionLevel.AGGRESSIVE)

    def test_basic_markdown(self):
        """Test basic Markdown compression."""
        md = "# Title\n\nThis is  some   text.\n\n## Section\n\nMore text."
        result = self.medium.compress(md)
        self.assertIn("# Title", result)
        self.assertIn("## Section", result)

    def test_remove_html_comments(self):
        """Test HTML comment removal."""
        md = "# Title\n<!-- This is a comment -->\nSome text"
        result = self.medium.compress(md)
        self.assertNotIn("<!--", result)

    def test_collapse_newlines(self):
        """Test newline collapsing."""
        md = "# Title\n\n\n\n\nSome text"
        result = self.medium.compress(md)
        # Should not have more than 2 consecutive newlines
        self.assertNotIn("\n\n\n", result)

    def test_list_compression(self):
        """Test list item compression."""
        md = "-   Item 1\n-   Item 2\n-   Item 3"
        result = self.medium.compress(md)
        # List items should have single space after marker
        self.assertIn("Item 1", result)
        self.assertIn("Item 2", result)
        self.assertIn("Item 3", result)

    def test_bold_conversion_aggressive(self):
        """Test bold marker conversion in aggressive mode."""
        md = "This is **bold** text."
        result = self.aggressive.compress(md)
        self.assertIn("*bold*", result)


class TestTextCompressor(unittest.TestCase):
    """Tests for the TextCompressor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.medium = TextCompressor(level=CompressionLevel.MEDIUM)
        self.aggressive = TextCompressor(level=CompressionLevel.AGGRESSIVE)

    def test_basic_text(self):
        """Test basic text compression."""
        text = "Hello   world!   This   is   a   test."
        result = self.medium.compress(text)
        self.assertNotIn("   ", result)

    def test_newline_collapse(self):
        """Test newline collapsing."""
        text = "Line 1\n\n\n\n\nLine 2"
        result = self.medium.compress(text)
        self.assertNotIn("\n\n\n", result)

    def test_token_limit(self):
        """Test token limit truncation."""
        text = "The quick brown fox jumps over the lazy dog. " * 50
        compressor = TextCompressor(
            level=CompressionLevel.MEDIUM,
            max_tokens=20,
        )
        result = compressor.compress(text)
        self.assertLess(len(result), len(text))

    def test_empty_text(self):
        """Test empty text."""
        result = self.medium.compress("")
        self.assertEqual(result, "")

    def test_repeated_lines(self):
        """Test repeated line removal in aggressive mode."""
        text = "Same line\nSame line\nSame line\nDifferent line"
        result = self.aggressive.compress(text)
        lines = result.strip().split("\n")
        # Should reduce repeated lines
        same_count = sum(1 for l in lines if l.strip() == "Same line")
        self.assertLessEqual(same_count, 2)


class TestCompressor(unittest.TestCase):
    """Tests for the main Compressor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.compressor = Compressor()

    def test_empty_text(self):
        """Test compressing empty text."""
        result = self.compressor.compress("")
        self.assertEqual(result.compressed_text, "")
        self.assertEqual(result.original_tokens, 0)

    def test_auto_detect_json(self):
        """Test auto-detection of JSON content."""
        text = json.dumps({"name": "test", "value": 42})
        result = self.compressor.compress(text)
        self.assertEqual(result.content_type, ContentType.JSON)
        self.assertGreater(result.original_tokens, 0)

    def test_auto_detect_code(self):
        """Test auto-detection of code content."""
        text = "def hello():\n    print('Hello')\n    return True"
        result = self.compressor.compress(text)
        self.assertIn(result.content_type, (ContentType.CODE, ContentType.TEXT))

    def test_auto_detect_markdown(self):
        """Test auto-detection of Markdown content."""
        text = "# Title\n\nThis is **bold** text.\n\n- Item 1"
        result = self.compressor.compress(text)
        self.assertEqual(result.content_type, ContentType.MARKDOWN)

    def test_compression_result_fields(self):
        """Test that CompressionResult has all expected fields."""
        text = "Hello, world! This is a test."
        result = self.compressor.compress(text)
        self.assertIsInstance(result, CompressionResult)
        self.assertGreater(result.original_tokens, 0)
        self.assertGreaterEqual(result.compressed_tokens, 0)
        self.assertGreaterEqual(result.compression_ratio, 0)
        self.assertIn(result.strategy, ("json", "code", "markdown", "text"))

    def test_result_to_dict(self):
        """Test CompressionResult.to_dict()."""
        text = "Hello, world!"
        result = self.compressor.compress(text)
        d = result.to_dict()
        self.assertIn("original_tokens", d)
        self.assertIn("compressed_tokens", d)
        self.assertIn("compression_ratio", d)

    def test_result_str(self):
        """Test CompressionResult.__str__()."""
        text = "Hello, world!"
        result = self.compressor.compress(text)
        s = str(result)
        self.assertIn("Compression Result", s)

    def test_compress_file(self):
        """Test compressing a file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write(json.dumps({"key": "value", "number": 42}, indent=2))
            f.flush()
            path = f.name

        try:
            result = self.compressor.compress_file(path)
            self.assertGreater(result.original_tokens, 0)
            self.assertGreater(result.compressed_tokens, 0)
        finally:
            os.unlink(path)

    def test_chinese_text_optimization(self):
        """Test that Chinese text gets optimized."""
        text = "众所周知，从宏观角度来看，这个问题需要进行一个深入的分析。"
        result = self.compressor.compress(text)
        self.assertGreater(result.original_tokens, 0)
        # Compressed should be shorter or equal
        self.assertLessEqual(result.compressed_tokens, result.original_tokens)

    def test_config_level_mild(self):
        """Test mild compression level."""
        config = CompressionConfig(level=CompressionLevel.MILD)
        compressor = Compressor(config)
        text = "Hello   world!   Test   text."
        result = compressor.compress(text)
        self.assertEqual(result.level, CompressionLevel.MILD)

    def test_config_level_aggressive(self):
        """Test aggressive compression level."""
        config = CompressionConfig(level=CompressionLevel.AGGRESSIVE)
        compressor = Compressor(config)
        text = "Hello   world!   Test   text."
        result = compressor.compress(text)
        self.assertEqual(result.level, CompressionLevel.AGGRESSIVE)


if __name__ == "__main__":
    unittest.main()
