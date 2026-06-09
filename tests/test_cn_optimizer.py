"""Unit tests for cn_optimizer module."""

import unittest

from tokensage.cn_optimizer import ChineseOptimizer, ChineseWordSegmenter


class TestChineseWordSegmenter(unittest.TestCase):
    """Tests for the ChineseWordSegmenter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.segmenter = ChineseWordSegmenter()

    def test_empty_string(self):
        """Test segmenting empty string."""
        result = self.segmenter.segment("")
        self.assertEqual(result, [])

    def test_pure_chinese(self):
        """Test segmenting pure Chinese text."""
        text = "这是一个测试"
        result = self.segmenter.segment(text)
        self.assertGreater(len(result), 0)
        # Should contain some multi-character words
        has_multi_char = any(len(t) > 1 for t in result)
        self.assertTrue(has_multi_char)

    def test_mixed_text(self):
        """Test segmenting mixed Chinese-English text."""
        text = "Hello世界test测试"
        result = self.segmenter.segment(text)
        self.assertGreater(len(result), 0)

    def test_is_cjk(self):
        """Test CJK character detection."""
        self.assertTrue(self.segmenter.is_cjk("中"))
        self.assertTrue(self.segmenter.is_cjk("国"))
        self.assertFalse(self.segmenter.is_cjk("a"))
        self.assertFalse(self.segmenter.is_cjk("1"))
        self.assertFalse(self.segmenter.is_cjk(" "))

    def test_common_words_detection(self):
        """Test that common words are detected."""
        text = "问题方法系统技术"
        result = self.segmenter.segment(text)
        # Should detect some 2-char words
        has_two_char = any(len(t) == 2 for t in result)
        self.assertTrue(has_two_char)


class TestChineseOptimizer(unittest.TestCase):
    """Tests for the ChineseOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = ChineseOptimizer()

    def test_empty_string(self):
        """Test optimizing empty string."""
        result = self.optimizer.optimize("")
        self.assertEqual(result, "")

    def test_punctuation_normalization(self):
        """Test fullwidth to halfwidth punctuation conversion."""
        text = "你好，世界！这是一个测试。"
        result = self.optimizer.optimize(text, level="medium")
        # Fullwidth comma and period should be converted
        self.assertNotIn("，", result)
        self.assertNotIn("。", result)

    def test_redundant_expression_removal(self):
        """Test redundant expression removal."""
        text = "众所周知，这个问题需要进行一个深入的分析。"
        result = self.optimizer.optimize(text, level="medium")
        # "众所周知" should be shortened to "已知"
        self.assertNotIn("众所周知", result)

    def test_whitespace_compression(self):
        """Test whitespace compression between CJK characters."""
        text = "你 好 世 界 测 试"
        result = self.optimizer.optimize(text, level="medium")
        # Spaces between CJK characters should be removed
        self.assertNotIn("你 好", result)

    def test_mixed_text_optimization(self):
        """Test mixed Chinese-English text optimization."""
        text = "使用 Python 进行 数据 分析"
        result = self.optimizer.optimize(text, level="aggressive")
        # Spaces between CJK and English should be removed in aggressive mode
        self.assertNotIn("进行 数据", result)

    def test_code_comment_optimization(self):
        """Test code comment optimization."""
        comment = "# 这是一个很长的注释，用于说明代码的功能和实现细节"
        result = self.optimizer.optimize_code_comment(comment)
        self.assertIn("#", result)
        self.assertLessEqual(len(result), len(comment))

    def test_mild_level_preserves_more(self):
        """Test that mild level preserves more text."""
        text = "众所周知，这个问题需要进行一个深入的分析。"
        mild_result = self.optimizer.optimize(text, level="mild")
        medium_result = self.optimizer.optimize(text, level="medium")
        # Mild should generally be longer or equal to medium
        self.assertGreaterEqual(len(mild_result), len(medium_result))

    def test_aggressive_level_more_compression(self):
        """Test that aggressive level compresses more."""
        text = "众所周知，从宏观角度来看，这个问题需要进行一个深入的分析。"
        medium_result = self.optimizer.optimize(text, level="medium")
        aggressive_result = self.optimizer.optimize(text, level="aggressive")
        # Aggressive should generally be shorter or equal to medium
        self.assertLessEqual(len(aggressive_result), len(medium_result))

    def test_optimization_stats(self):
        """Test optimization statistics."""
        original = "众所周知，这个问题需要进行一个深入的分析。"
        optimized = self.optimizer.optimize(original, level="medium")
        stats = self.optimizer.get_optimization_stats(original, optimized)
        self.assertIn("original_length", stats)
        self.assertIn("optimized_length", stats)
        self.assertIn("original_tokens", stats)
        self.assertIn("optimized_tokens", stats)
        self.assertGreater(stats["original_length"], 0)
        self.assertGreater(stats["original_tokens"], 0)

    def test_long_chinese_text(self):
        """Test optimizing longer Chinese text."""
        text = (
            "在当前的情况下，我们需要对这个问题进行一个全面的、深入的、系统的分析。"
            "从宏观的角度来看，这个问题的本质是相当复杂的。"
            "综上所述，我们需要采取有效的措施来解决这个问题。"
        )
        result = self.optimizer.optimize(text, level="medium")
        self.assertGreater(len(result), 0)
        # Should be shorter than original
        self.assertLess(len(result), len(text))


if __name__ == "__main__":
    unittest.main()
