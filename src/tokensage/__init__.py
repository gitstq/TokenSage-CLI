"""
TokenSage - 轻量级LLM上下文令牌优化引擎
Lightweight LLM Context Token Optimization Engine
"""

__version__ = "1.0.0"
__author__ = "TokenSage Team"
__license__ = "MIT"

# Re-export main API
from tokensage.compress import compress, CompressionResult
from tokensage.router import route_content

__all__ = [
    "compress",
    "CompressionResult",
    "ContentType",
    "route_content",
]