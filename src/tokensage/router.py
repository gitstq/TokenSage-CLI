"""
Content type routing for TokenSage.
Detects whether input is code, JSON, log, or prose.
"""

import re
from typing import Optional


def route_content(text: str) -> str:
    """Detect the content type of the given text.
    
    Returns one of: "code", "json", "text", "log"
    """
    if not text or not text.strip():
        return "text"

    text_stripped = text.strip()

    # JSON detection
    if text_stripped.startswith("{") or text_stripped.startswith("["):
        try:
            import json
            json.loads(text_stripped[:10000])  # Parse first 10K chars
            return "json"
        except (json.JSONDecodeError, ValueError):
            pass

    # Log detection
    log_patterns = [
        r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',  # ISO timestamp
        r'^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',  # syslog timestamp
        r'^\[?\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}',  # Apache log
        r'^(ERROR|WARN|INFO|DEBUG|TRACE)\s',  # Log level at start
    ]
    first_lines = text_stripped.split("\n")[:5]
    for line in first_lines:
        for pattern in log_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return "log"

    # Code detection
    code_indicators = 0
    # Python
    if re.search(r'^(def |class |import |from |@|async def|if __name__)', text_stripped, re.MULTILINE):
        code_indicators += 2
    # JavaScript/TypeScript
    if re.search(r'^(function |const |let |var |import\s+|export\s+|interface |type |=>)', text_stripped, re.MULTILINE):
        code_indicators += 2
    # Common code patterns
    if re.search(r'[{};]\s*$', text_stripped, re.MULTILINE):
        code_indicators += 1
    if re.search(r'^\s*(if|for|while|try|switch|return|pass|break|continue|raise|yield|print)\s', text_stripped, re.MULTILINE):
        code_indicators += 1
    # Python: lines ending with colon (def/class/if/for/while/try/except/finally/with/elif/else)
    if re.search(r':\s*$', text_stripped, re.MULTILINE):
        if re.search(r'^\s*(def |class |if |for |while |try |except |finally |with |elif |else |async )', text_stripped, re.MULTILINE):
            code_indicators += 1
    if re.search(r'^\s*#\s*(include|define|pragma)', text_stripped, re.MULTILINE):
        code_indicators += 2

    if code_indicators >= 3:
        return "code"

    # Table/delimited data check
    if re.search(r'^\|.+\|$', text_stripped, re.MULTILINE):
        if text_stripped.count("|") > 10:
            return "text"  # tables compress like text

    return "text"