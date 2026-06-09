"""Token counting engine for TokenSage-CLI.

Implements multiple token estimation strategies without external dependencies.
Provides BPE-approximate, character-level, and hybrid counting methods
optimized for both English and Chinese text.
"""

import json
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple

from tokensage.exceptions import TokenCountError
from tokensage.utils import detect_content_type


class TokenStrategy(Enum):
    """Token estimation strategies."""

    BPE_APPROX = "bpe_approx"
    CHAR_LEVEL = "char_level"
    HYBRID = "hybrid"


class TokenCounter:
    """Token counting engine with multiple estimation strategies.

    This module provides token estimation without requiring tiktoken or
    other external tokenizers. It uses a BPE-inspired approximation that
    handles both English and Chinese text with reasonable accuracy.

    The BPE approximation is based on common subword patterns observed in
    popular tokenizers like cl100k_base (used by GPT-4/GPT-3.5).
    """

    # Common English words that typically map to single tokens
    COMMON_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "just", "because", "but", "and", "or", "if", "while", "that", "this",
        "these", "those", "it", "its", "he", "she", "they", "we", "you", "i",
        "me", "him", "her", "us", "them", "my", "your", "his", "our", "their",
        "what", "which", "who", "whom", "up", "about", "also", "new", "like",
        "time", "way", "may", "people", "take", "year", "your", "good", "get",
        "make", "know", "come", "think", "look", "want", "give", "use", "find",
        "tell", "ask", "work", "seem", "feel", "try", "leave", "call", "keep",
        "let", "begin", "show", "hear", "play", "run", "move", "live", "true",
        "change", "help", "turn", "start", "might", "show", "much", "place",
        "well", "long", "right", "still", "own", "old", "thing", "hand",
        "high", "last", "school", "part", "real", "left", "end", "point",
        "home", "small", "number", "different", "next", "water", "night",
        "large", "open", "world", "city", "back", "group", "country", "side",
        "problem", "power", "money", "great", "man", "woman", "day", "head",
        "house", "life", "name", "line", "boy", "girl", "state", "book",
        "face", "form", "case", "week", "system", "game", "program", "team",
        "plan", "table", "class", "idea", "family", "fact", "story", "body",
        "data", "word", "business", "issue", "today", "area", "market",
        "company", "best", "first", "second", "third", "last", "many",
    }

    # Common 2-3 character subword units
    COMMON_SUBWORDS = {
        "ing", "tion", "ment", "ness", "able", "ible", "ful", "less", "ous",
        "ive", "al", "er", "ed", "ly", "ity", "ent", "ance", "ence", "ism",
        "ist", "ize", "ise", "fy", "ous", "ic", "ical", "ial", "ual",
        "th", "wh", "ch", "sh", "ph", "gh", "ck", "ng", "qu", "kn", "wr",
        "tion", "sion", "ment", "ness", "ence", "ance", "able", "ible",
        "pre", "re", "un", "dis", "mis", "over", "out", "sub", "inter",
        "trans", "super", "anti", "semi", "multi", "auto", "bio", "geo",
        "tele", "micro", "macro", "meta", "para", "poly", "syn", "sym",
    }

    # Regex pattern for BPE-like token splitting
    # This mimics how tokenizers split text into subword units
    _BPE_PATTERN = re.compile(
        r"""'s|'t|'re|'ve|'m|'ll|'d| ?\w+| ?\d+| ?[^\s\w\d]+|\s+(?!\S)|\s+""",
        re.UNICODE,
    )

    def __init__(self, strategy: TokenStrategy = TokenStrategy.HYBRID):
        """Initialize the token counter.

        Args:
            strategy: The token estimation strategy to use.
        """
        self.strategy = strategy
        self._bpe_cache: Dict[str, int] = {}

    def count(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: The text to count tokens for.

        Returns:
            Estimated token count.

        Raises:
            TokenCountError: If counting fails.
        """
        if not text:
            return 0

        try:
            if self.strategy == TokenStrategy.BPE_APPROX:
                return self._count_bpe_approx(text)
            elif self.strategy == TokenStrategy.CHAR_LEVEL:
                return self._count_char_level(text)
            else:  # HYBRID
                return self._count_hybrid(text)
        except Exception as e:
            raise TokenCountError(f"Token counting failed: {e}") from e

    def count_with_report(self, text: str) -> Dict:
        """Count tokens and return a detailed report.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary with token count and analysis details.
        """
        content_type = detect_content_type(text)
        bpe_count = self._count_bpe_approx(text)
        char_count = self._count_char_level(text)
        hybrid_count = self._count_hybrid(text)

        return {
            "text_length": len(text),
            "line_count": text.count("\n") + 1,
            "content_type": content_type,
            "bpe_approx_tokens": bpe_count,
            "char_level_tokens": char_count,
            "hybrid_tokens": hybrid_count,
            "recommended_estimate": hybrid_count,
            "strategy_used": self.strategy.value,
        }

    def _count_bpe_approx(self, text: str) -> int:
        """BPE-approximate token counting.

        Splits text using regex patterns similar to how BPE tokenizers work,
        then estimates token counts based on subword unit lengths and
        common word/subword lookups.

        Args:
            text: The text to count.

        Returns:
            Estimated token count.
        """
        # Split text into word-like units
        units = self._BPE_PATTERN.findall(text)
        token_count = 0

        for unit in units:
            # Check cache first
            if unit in self._bpe_cache:
                token_count += self._bpe_cache[unit]
                continue

            tokens = self._estimate_unit_tokens(unit)
            self._bpe_cache[unit] = tokens
            token_count += tokens

        return token_count

    def _estimate_unit_tokens(self, unit: str) -> int:
        """Estimate tokens for a single word-like unit.

        Args:
            unit: A word-like unit from BPE splitting.

        Returns:
            Estimated token count for this unit.
        """
        stripped = unit.strip()

        # Empty or whitespace-only
        if not stripped:
            return 1 if unit else 0

        # Pure whitespace
        if not stripped:
            return 1

        # Numbers: typically 1 token per number (up to ~3-4 digits)
        if stripped.isdigit():
            return 1 if len(stripped) <= 4 else (len(stripped) + 2) // 3

        # Punctuation/symbols: typically 1 token each
        if all(not c.isalnum() and not c.isspace() for c in stripped):
            return 1

        # Check if it's a common word (single token)
        lower = stripped.lower()
        if lower in self.COMMON_WORDS:
            return 1

        # CJK characters: each character is typically 1-2 tokens
        cjk_count = 0
        non_cjk = ""
        for char in stripped:
            cp = ord(char)
            if (
                (0x4E00 <= cp <= 0x9FFF)
                or (0x3400 <= cp <= 0x4DBF)
                or (0xF900 <= cp <= 0xFAFF)
                or (0xFF00 <= cp <= 0xFFEF)
                or (0x3000 <= cp <= 0x303F)
            ):
                cjk_count += 1
            else:
                non_cjk += char

        if cjk_count > 0 and not non_cjk:
            # Pure CJK: ~1.5 tokens per character on average
            return max(1, int(cjk_count * 0.7))

        if cjk_count > 0 and non_cjk:
            # Mixed CJK + Latin
            cjk_tokens = max(1, int(cjk_count * 0.7))
            latin_tokens = self._estimate_latin_tokens(non_cjk)
            return cjk_tokens + latin_tokens

        # Latin word: estimate based on length and common subwords
        return self._estimate_latin_tokens(stripped)

    def _estimate_latin_tokens(self, word: str) -> int:
        """Estimate tokens for a Latin/English word.

        Uses word length and common subword patterns to estimate
        how many BPE tokens a word would be split into.

        Args:
            word: A Latin/English word.

        Returns:
            Estimated token count.
        """
        if not word:
            return 0

        length = len(word)
        lower = word.lower()

        # Short words are usually 1 token
        if length <= 3:
            return 1

        # Common words are 1 token
        if lower in self.COMMON_WORDS:
            return 1

        # Check for common prefixes and suffixes
        has_common_subword = False
        for subword in self.COMMON_SUBWORDS:
            if subword in lower:
                has_common_subword = True
                break

        # Estimate based on character count
        # Average token length is ~4 characters for English
        if has_common_subword:
            # Words with common subwords tend to tokenize more efficiently
            return max(1, int(length / 5) + 1)
        else:
            # Uncommon/long words get split more
            return max(1, int(length / 4) + 1)

    def _count_char_level(self, text: str) -> int:
        """Character-level token estimation.

        Uses character-level heuristics: ~4 chars per token for English,
        ~1.5 chars per token for CJK, whitespace is roughly 1 token per
        3-4 spaces.

        Args:
            text: The text to count.

        Returns:
            Estimated token count.
        """
        if not text:
            return 0

        cjk_count = 0
        latin_count = 0
        digit_count = 0
        space_count = 0
        punctuation_count = 0

        for char in text:
            cp = ord(char)
            if char.isspace():
                space_count += 1
            elif char.isdigit():
                digit_count += 1
            elif (
                (0x4E00 <= cp <= 0x9FFF)
                or (0x3400 <= cp <= 0x4DBF)
                or (0xF900 <= cp <= 0xFAFF)
                or (0xFF00 <= cp <= 0xFFEF)
                or (0x3000 <= cp <= 0x303F)
            ):
                cjk_count += 1
            elif char.isalpha():
                latin_count += 1
            else:
                punctuation_count += 1

        # Estimate tokens per category
        cjk_tokens = int(cjk_count / 1.5)
        latin_tokens = int(latin_count / 4.0)
        digit_tokens = int(digit_count / 3.5) + (1 if digit_count > 0 else 0)
        space_tokens = int(space_count / 3.5) + (1 if space_count > 0 else 0)
        punct_tokens = punctuation_count

        return cjk_tokens + latin_tokens + digit_tokens + space_tokens + punct_tokens

    def _count_hybrid(self, text: str) -> int:
        """Hybrid token estimation combining BPE and char-level.

        Uses BPE approximation for structured content (JSON, code)
        and a weighted average for plain text.

        Args:
            text: The text to count.

        Returns:
            Estimated token count.
        """
        if not text:
            return 0

        content_type = detect_content_type(text)

        if content_type == "json":
            return self._count_json(text)
        elif content_type == "code":
            return self._count_code(text)
        else:
            # Weighted average of BPE and char-level for text/markdown
            bpe = self._count_bpe_approx(text)
            char = self._count_char_level(text)
            # BPE approximation is generally more accurate, weight it higher
            return int(bpe * 0.65 + char * 0.35)

    def _count_json(self, text: str) -> int:
        """Token counting optimized for JSON content.

        JSON has predictable structure: keys, values, punctuation.
        Accounts for the overhead of JSON syntax.

        Args:
            text: JSON string.

        Returns:
            Estimated token count.
        """
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            # Fall back to general BPE if not valid JSON
            return self._count_bpe_approx(text)

        # Count tokens for the stringified representation
        # JSON syntax (braces, colons, commas, quotes) adds overhead
        json_text = json.dumps(data, ensure_ascii=False, separators=(", ", ": "))

        # Estimate: structural tokens + value tokens
        structural_chars = sum(
            1 for c in json_text if c in '{}[],:"'
        )
        value_text = json_text.replace("{}", "").replace("[]", "")
        value_text = re.sub(r'[,:\[\]{}"]', "", value_text)

        structural_tokens = max(1, structural_chars // 3)
        value_tokens = self._count_bpe_approx(value_text)

        return structural_tokens + value_tokens

    def _count_code(self, text: str) -> int:
        """Token counting optimized for code content.

        Code has many short tokens (keywords, operators, identifiers).
        Accounts for code-specific patterns.

        Args:
            text: Code string.

        Returns:
            Estimated token count.
        """
        lines = text.split("\n")

        code_tokens = 0
        for line in lines:
            stripped = line.strip()

            # Empty lines: ~0 tokens (or 1 for newline)
            if not stripped:
                continue

            # Comment lines: estimate as text
            if stripped.startswith("#") or stripped.startswith("//"):
                code_tokens += self._count_bpe_approx(stripped[2:].lstrip())
                continue

            if stripped.startswith("/*") or stripped.startswith("*"):
                code_tokens += self._count_bpe_approx(stripped)
                continue

            # Code line: split by common delimiters
            # Keywords and operators are typically 1 token each
            parts = re.split(r'([{}()\[\];,.=+\-*/<>!&|^~%?:])', stripped)
            parts = [p for p in parts if p.strip()]

            for part in parts:
                if len(part) <= 2:
                    code_tokens += 1  # Operators, short tokens
                elif part.strip().strip('"\'').strip('"\'') == part.strip():
                    # String literal
                    code_tokens += self._count_bpe_approx(part)
                else:
                    # Identifier or keyword
                    code_tokens += self._estimate_latin_tokens(part.strip())

        return code_tokens

    def count_tokens(
        self,
        text: str,
        content_type: Optional[str] = None,
    ) -> int:
        """Public API for counting tokens with optional content type hint.

        Args:
            text: The text to count tokens for.
            content_type: Optional content type hint ('json', 'code', 'markdown', 'text').

        Returns:
            Estimated token count.
        """
        if not text:
            return 0

        if content_type == "json":
            return self._count_json(text)
        elif content_type == "code":
            return self._count_code(text)
        else:
            return self.count(text)

    @staticmethod
    def compare_strategies(text: str) -> Dict[str, int]:
        """Compare token counts from all strategies.

        Args:
            text: The text to analyze.

        Returns:
            Dictionary mapping strategy names to token counts.
        """
        counter = TokenCounter()
        return {
            "bpe_approx": counter._count_bpe_approx(text),
            "char_level": counter._count_char_level(text),
            "hybrid": counter._count_hybrid(text),
        }
