"""Chinese text optimization module for TokenSage-CLI.

Provides specialized optimization for Chinese and CJK text content,
including word segmentation awareness, redundant expression removal,
and mixed-language token optimization.
"""

import re
from typing import Dict, List, Optional, Tuple


class ChineseWordSegmenter:
    """Simple Chinese word segmentation using dictionary-based forward matching.

    This is a basic segmenter that handles common Chinese words and patterns.
    It is not a full NLP segmenter (like jieba) but provides reasonable
    results for compression optimization purposes.
    """

    # Common Chinese words (2-4 characters) for segmentation
    COMMON_WORDS = {
        # Common verbs
        "可以", "需要", "应该", "能够", "已经", "正在", "将要", "可能",
        "希望", "认为", "觉得", "知道", "了解", "理解", "相信", "发现",
        "表示", "说明", "指出", "强调", "提出", "进行", "开展", "实施",
        "完成", "实现", "达到", "超过", "包括", "包含", "涉及", "关于",
        "根据", "按照", "通过", "利用", "使用", "采用", "选择", "决定",
        # Common nouns
        "问题", "方法", "系统", "技术", "数据", "信息", "内容", "功能",
        "服务", "平台", "应用", "项目", "方案", "结果", "效果", "影响",
        "情况", "条件", "原因", "目的", "意义", "作用", "关系", "区别",
        "特点", "优势", "不足", "挑战", "机会", "发展", "变化", "趋势",
        "模型", "算法", "网络", "程序", "设计", "开发", "测试", "部署",
        "用户", "客户", "企业", "市场", "行业", "领域", "方向", "标准",
        "管理", "运营", "维护", "优化", "改进", "提升", "降低", "控制",
        "分析", "评估", "验证", "检查", "处理", "解决", "支持", "保障",
        # Common adjectives
        "重要", "关键", "基本", "主要", "核心", "有效", "合理", "必要",
        "充分", "详细", "具体", "明确", "简单", "复杂", "高效", "稳定",
        "安全", "可靠", "准确", "精确", "快速", "灵活", "强大", "丰富",
        # Common adverbs/conjunctions
        "因此", "所以", "但是", "然而", "虽然", "尽管", "如果", "假设",
        "并且", "而且", "或者", "以及", "同时", "另外", "此外", "其中",
        "首先", "其次", "最后", "总之", "综上", "例如", "比如", "即",
        "也就是说", "换句话说", "事实上", "实际上", "基本上", "本质上",
        # Common measure words + nouns
        "一个", "一种", "一些", "这个", "那个", "这些", "那些", "每个",
        "所有", "任何", "某些", "当前", "目前", "现有", "最新", "相关",
    }

    # Common redundant Chinese expressions
    REDUNDANT_EXPRESSIONS = {
        # Verbose -> concise mappings
        "进行一个": "进行",
        "做一个": "做",
        "起到一个": "起到",
        "对于这个问题": "对此",
        "在这种情况下": "此时",
        "在某种程度上": "某种程度上",
        "从某种意义上来说": "从某种意义说",
        "众所周知": "已知",
        "毫无疑问": "无疑",
        "不可否认": "诚然",
        "总而言之": "总之",
        "换句话说": "即",
        "也就是说": "即",
        "事实上": "实际上",
        "基本上": "基本",
        "在一定程度上": "一定程度上",
        "与此同时": "同时",
        "除此之外": "此外",
        "在这种情况下": "此时",
        "在这样的情况下": "此时",
        "需要注意的是": "注意",
        "需要指出的是": "指出",
        "需要强调的是": "强调",
        "需要说明的是": "说明",
        "众所周知的是": "已知",
        "从宏观角度来看": "宏观上",
        "从整体上来看": "整体上",
        "从实际情况来看": "实际上",
        "根据相关数据显示": "数据显示",
        "根据相关统计": "据统计",
        "通过以上分析可以看出": "综上",
        "经过上述分析": "综上",
        "综合以上分析": "综上",
        "基于上述原因": "因此",
        "由于上述原因": "因此",
        "为了能够": "为",
        "以便能够": "以便",
        "以达到": "以达",
        "来进行": "进行",
        "来实现": "实现",
        "来完成": "完成",
        "来处理": "处理",
        "来解决": "解决",
        "来提高": "提高",
        "来降低": "降低",
        "来优化": "优化",
        "来改进": "改进",
    }

    # Chinese punctuation that can be compressed
    PUNCTUATION_MAP = {
        "……": "...",
        "——": "-",
        "＊": "*",
        "＃": "#",
        "＠": "@",
        "＆": "&",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "｛": "{",
        "｝": "}",
        "，": ",",
        "。": ".",
        "：": ":",
        "；": ";",
        "？": "?",
        "！": "!",
    }

    def __init__(self):
        """Initialize the Chinese word segmenter."""
        self._max_word_len = max(len(w) for w in self.COMMON_WORDS) if self.COMMON_WORDS else 4

    def segment(self, text: str) -> List[str]:
        """Segment Chinese text into words.

        Uses forward maximum matching with the built-in dictionary.

        Args:
            text: Chinese text to segment.

        Returns:
            List of word/token strings.
        """
        if not text:
            return []

        tokens = []
        i = 0
        text_len = len(text)

        while i < text_len:
            # Try maximum length match first
            matched = False
            for length in range(min(self._max_word_len, text_len - i), 1, -1):
                substr = text[i : i + length]
                if substr in self.COMMON_WORDS:
                    tokens.append(substr)
                    i += length
                    matched = True
                    break

            if not matched:
                char = text[i]
                # Non-CJK characters are returned as-is
                cp = ord(char)
                if not (
                    (0x4E00 <= cp <= 0x9FFF)
                    or (0x3400 <= cp <= 0x4DBF)
                    or (0xF900 <= cp <= 0xFAFF)
                ):
                    # Collect consecutive non-CJK characters
                    j = i + 1
                    while j < text_len:
                        cp_j = ord(text[j])
                        if (
                            (0x4E00 <= cp_j <= 0x9FFF)
                            or (0x3400 <= cp_j <= 0x4DBF)
                            or (0xF900 <= cp_j <= 0xFAFF)
                        ):
                            break
                        j += 1
                    tokens.append(text[i:j])
                    i = j
                else:
                    tokens.append(char)
                    i += 1

        return tokens

    def is_cjk(self, char: str) -> bool:
        """Check if a character is a CJK character.

        Args:
            char: A single character.

        Returns:
            True if the character is CJK.
        """
        cp = ord(char)
        return (
            (0x4E00 <= cp <= 0x9FFF)
            or (0x3400 <= cp <= 0x4DBF)
            or (0xF900 <= cp <= 0xFAFF)
            or (0x20000 <= cp <= 0x2A6DF)
            or (0x3000 <= cp <= 0x303F)
            or (0xFF00 <= cp <= 0xFFEF)
        )


class ChineseOptimizer:
    """Chinese text optimizer for token reduction.

    Provides various optimization strategies specific to Chinese text,
    including redundant expression removal, punctuation normalization,
    and mixed-language optimization.
    """

    def __init__(self):
        """Initialize the Chinese optimizer."""
        self._segmenter = ChineseWordSegmenter()

    def optimize(self, text: str, level: str = "medium") -> str:
        """Optimize Chinese text for token efficiency.

        Args:
            text: Chinese text to optimize.
            level: Optimization level ('mild', 'medium', 'aggressive').

        Returns:
            Optimized text.
        """
        if not text:
            return text

        # Normalize fullwidth punctuation
        text = self._normalize_punctuation(text)

        # Remove redundant expressions
        if level in ("medium", "aggressive"):
            text = self._remove_redundant_expressions(text)

        # Compress whitespace
        text = self._compress_whitespace(text, level)

        # Optimize mixed Chinese-English text
        if level == "aggressive":
            text = self._optimize_mixed_text(text)

        # Remove filler words in aggressive mode
        if level == "aggressive":
            text = self._remove_filler_words(text)

        return text

    def optimize_code_comment(self, comment: str) -> str:
        """Optimize Chinese code comments.

        Args:
            comment: A code comment string (may include comment markers).

        Returns:
            Optimized comment.
        """
        # Strip comment markers
        stripped = comment.strip()
        for marker in ("#", "//", "/*", "*/", "*"):
            if stripped.startswith(marker):
                stripped = stripped[len(marker):].strip()
            if stripped.endswith(marker):
                stripped = stripped[: -len(marker)].strip()

        # Optimize the comment text
        optimized = self.optimize(stripped, level="medium")

        # Re-add comment marker
        if comment.strip().startswith("#"):
            return "# " + optimized
        elif comment.strip().startswith("//"):
            return "// " + optimized
        return optimized

    def _normalize_punctuation(self, text: str) -> str:
        """Normalize fullwidth punctuation to halfwidth.

        Fullwidth punctuation takes more tokens in most tokenizers.

        Args:
            text: Text to normalize.

        Returns:
            Text with normalized punctuation.
        """
        for fullwidth, halfwidth in self._segmenter.PUNCTUATION_MAP.items():
            text = text.replace(fullwidth, halfwidth)
        return text

    def _remove_redundant_expressions(self, text: str) -> str:
        """Remove common redundant Chinese expressions.

        Args:
            text: Text to process.

        Returns:
            Text with redundant expressions removed.
        """
        for verbose, concise in self._segmenter.REDUNDANT_EXPRESSIONS.items():
            text = text.replace(verbose, concise)
        return text

    def _compress_whitespace(self, text: str, level: str) -> str:
        """Compress whitespace in Chinese text.

        Chinese text typically doesn't need spaces between characters.

        Args:
            text: Text to compress.
            level: Compression level.

        Returns:
            Text with compressed whitespace.
        """
        # Remove spaces between CJK characters
        text = re.sub(r"([\u4e00-\u9fff])\s+([\u4e00-\u9fff])", r"\1\2", text)

        # Remove spaces after CJK punctuation
        text = re.sub(r"([\u4e00-\u9fff\u3000-\u303f])\s+", r"\1", text)

        # Collapse multiple spaces
        text = re.sub(r" {2,}", " ", text)

        # Collapse multiple newlines
        if level == "aggressive":
            text = re.sub(r"\n{3,}", "\n", text)
        else:
            text = re.sub(r"\n{3,}", "\n\n", text)

        return text

    def _optimize_mixed_text(self, text: str) -> str:
        """Optimize mixed Chinese-English text.

        Removes unnecessary spaces around English words embedded in
        Chinese text.

        Args:
            text: Mixed-language text.

        Returns:
            Optimized text.
        """
        # Remove space before English word after CJK character
        text = re.sub(
            r"([\u4e00-\u9fff])\s+([a-zA-Z])",
            r"\1\2",
            text,
        )
        # Remove space after English word before CJK character
        text = re.sub(
            r"([a-zA-Z])\s+([\u4e00-\u9fff])",
            r"\1\2",
            text,
        )
        return text

    def _remove_filler_words(self, text: str) -> str:
        """Remove common Chinese filler words.

        Args:
            text: Text to process.

        Returns:
            Text with filler words removed.
        """
        filler_patterns = [
            r"\b的话\b",  #的话
            r"\b的话\b",
            r"嗯[，,]?\s*",
            r"啊[，,]?\s*",
            r"哦[，,]?\s*",
            r"呀[，,]?\s*",
            r"呢[，,]?\s*",
        ]
        for pattern in filler_patterns:
            text = re.sub(pattern, "", text)

        return text

    def get_optimization_stats(self, original: str, optimized: str) -> Dict:
        """Get statistics about the optimization.

        Args:
            original: Original text.
            optimized: Optimized text.

        Returns:
            Dictionary with optimization statistics.
        """
        from tokensage.token_counter import TokenCounter

        counter = TokenCounter()
        original_tokens = counter.count(original)
        optimized_tokens = counter.count(optimized)

        return {
            "original_length": len(original),
            "optimized_length": len(optimized),
            "length_reduction": len(original) - len(optimized),
            "length_reduction_percent": (
                (len(original) - len(optimized)) / len(original) * 100
                if len(original) > 0
                else 0
            ),
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_savings": original_tokens - optimized_tokens,
            "token_savings_percent": (
                (original_tokens - optimized_tokens) / original_tokens * 100
                if original_tokens > 0
                else 0
            ),
        }
