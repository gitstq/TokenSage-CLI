"""TokenSage HTTP Proxy Server - Drop-in proxy for AI agent integration."""

import json
from typing import Optional

from tokensage.compress import compress, CompressionResult


def run_proxy(port: int = 8787) -> None:
    """Run TokenSage as an HTTP proxy server.
    
    This provides a drop-in proxy that intercepts LLM API calls
    and compresses the request body before forwarding.
    """
    try:
        import uvicorn
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse, Response
        from starlette.routing import Route
        import httpx
    except ImportError:
        raise ImportError(
            "Proxy dependencies not installed. Run: pip install 'tokensage[proxy]'"
        )

    async def healthcheck(request):
        return JSONResponse({
            "status": "ok",
            "service": "tokensage-proxy",
            "version": "1.0.0",
            "port": port,
        })

    async def compress_endpoint(request):
        """Compress text via HTTP POST."""
        body = await request.json()
        text = body.get("text", "")
        content_type = body.get("type")

        result = compress(text=text, content_type=content_type)
        return JSONResponse(result.to_dict())

    async def proxy_chat(request):
        """Intercept chat completion requests and compress them."""
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)

        messages = body.get("messages", [])
        compressed_count = 0
        total_original = 0
        total_compressed = 0

        for msg in messages:
            if isinstance(msg.get("content"), str) and msg["content"]:
                result = compress(msg["content"])
                total_original += result.original_tokens
                total_compressed += result.compressed_tokens
                if result.compressed_tokens < result.original_tokens:
                    msg["content"] = result.compressed_text
                    compressed_count += 1

        # Add compression metadata
        body["_tokensage"] = {
            "original_tokens": total_original,
            "compressed_tokens": total_compressed,
            "savings_percent": round(
                (1 - total_compressed / max(total_original, 1)) * 100, 1
            ),
            "messages_compressed": compressed_count,
        }

        return JSONResponse(body)

    app = Starlette(debug=False, routes=[
        Route("/", endpoint=healthcheck),
        Route("/health", endpoint=healthcheck),
        Route("/compress", endpoint=compress_endpoint, methods=["POST"]),
        Route("/v1/chat/completions", endpoint=proxy_chat, methods=["POST"]),
        Route("/v1/chat/completions", endpoint=proxy_chat, methods=["POST"]),
    ])

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_proxy()