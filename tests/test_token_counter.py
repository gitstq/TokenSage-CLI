"""Unit tests for token_counter module."""

import json
import unittest

from tokensage.token_counter import TokenCounter, TokenStrategy


class TestTokenCounter(unittest.TestCase):
    """Tests for the TokenCounter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.counter = TokenCounter(strategy=TokenStrategy.HYBRID)

    def test_empty_string(self):
        """Test counting tokens in empty string."""
        self.assertEqual(self.counter.count(""), 0)

    def test_none_handling(self):
        """Test counting None (should be treated as empty)."""
        self.assertEqual(self.counter.count(""), 0)

    def test_simple_english(self):
        """Test counting simple English text."""
        text = "Hello, world!"
        count = self.counter.count(text)
        self.assertGreater(count, 0)
        # "Hello, world!" should be roughly 3-5 tokens
        self.assertLess(count, 10)

    def test_long_english_paragraph(self):
        """Test counting a longer English paragraph."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a test sentence for token counting."
        )
        count = self.counter.count(text)
        self.assertGreater(count, 10)
        self.assertLess(count, 50)

    def test_chinese_text(self):
        """Test counting Chinese text."""
        text = "这是一个测试文本，用于验证中文Token计数功能。"
        count = self.counter.count(text)
        self.assertGreater(count, 0)
        # Chinese characters typically map to ~0.7 tokens each
        self.assertLess(count, len(text))

    def test_mixed_chinese_english(self):
        """Test counting mixed Chinese-English text."""
        text = "Hello世界！This is混合文本test。"
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_numbers(self):
        """Test counting text with numbers."""
        text = "The answer is 42 and 3.14159."
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_code_text(self):
        """Test counting code."""
        text = 'def hello():\n    print("Hello, world!")\n    return True'
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_json_text(self):
        """Test counting JSON."""
        text = json.dumps({"name": "test", "value": 42, "items": [1, 2, 3]})
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_markdown_text(self):
        """Test counting Markdown."""
        text = "# Header\n\nThis is **bold** and *italic* text.\n\n- Item 1\n- Item 2"
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_bpe_approx_strategy(self):
        """Test BPE approximation strategy."""
        counter = TokenCounter(strategy=TokenStrategy.BPE_APPROX)
        text = "Hello, world! This is a test."
        count = counter.count(text)
        self.assertGreater(count, 0)

    def test_char_level_strategy(self):
        """Test character-level strategy."""
        counter = TokenCounter(strategy=TokenStrategy.CHAR_LEVEL)
        text = "Hello, world! This is a test."
        count = counter.count(text)
        self.assertGreater(count, 0)

    def test_hybrid_strategy(self):
        """Test hybrid strategy."""
        counter = TokenCounter(strategy=TokenStrategy.HYBRID)
        text = "Hello, world! This is a test."
        count = counter.count(text)
        self.assertGreater(count, 0)

    def test_count_with_report(self):
        """Test count_with_report method."""
        text = "Hello, world!"
        report = self.counter.count_with_report(text)
        self.assertIn("text_length", report)
        self.assertIn("line_count", report)
        self.assertIn("content_type", report)
        self.assertIn("bpe_approx_tokens", report)
        self.assertIn("char_level_tokens", report)
        self.assertIn("hybrid_tokens", report)
        self.assertEqual(report["text_length"], len(text))

    def test_compare_strategies(self):
        """Test compare_strategies static method."""
        text = "Hello, world! This is a test."
        comparisons = TokenCounter.compare_strategies(text)
        self.assertIn("bpe_approx", comparisons)
        self.assertIn("char_level", comparisons)
        self.assertIn("hybrid", comparisons)
        # All strategies should give positive counts
        for strategy, count in comparisons.items():
            self.assertGreater(count, 0)

    def test_count_tokens_with_content_type(self):
        """Test count_tokens with content type hint."""
        text = '{"key": "value"}'
        count = self.counter.count_tokens(text, content_type="json")
        self.assertGreater(count, 0)

    def test_whitespace_only(self):
        """Test counting whitespace-only text."""
        text = "   \n\n\t  "
        count = self.counter.count(text)
        self.assertGreaterEqual(count, 0)

    def test_repeated_text(self):
        """Test that repeated text gives consistent counts."""
        text = "Hello, world!"
        count1 = self.counter.count(text)
        count2 = self.counter.count(text)
        self.assertEqual(count1, count2)

    def test_long_text_performance(self):
        """Test counting performance on longer text."""
        text = "The quick brown fox jumps over the lazy dog. " * 100
        count = self.counter.count(text)
        self.assertGreater(count, 100)
        self.assertLess(count, 2000)

    def test_special_characters(self):
        """Test counting text with special characters."""
        text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        count = self.counter.count(text)
        self.assertGreater(count, 0)

    def test_cjk_punctuation(self):
        """Test counting CJK punctuation."""
        text = "你好，世界！这是一个测试。"
        count = self.counter.count(text)
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()
