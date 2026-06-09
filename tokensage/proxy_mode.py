"""HTTP proxy mode for TokenSage-CLI.

Implements a transparent HTTP proxy server that intercepts LLM API requests,
automatically compresses the request body context, and decompresses responses.
Supports OpenAI-compatible API format.
"""

import json
import re
import socket
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, Optional, Tuple
from urllib.request import Request, urlopen, HTTPError
from urllib.error import URLError

from tokensage.compressor import Compressor
from tokensage.config_manager import ConfigManager
from tokensage.exceptions import ProxyError
from tokensage.models.compression import CompressionConfig, CompressionLevel
from tokensage.token_counter import TokenCounter


class CompressionProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler that compresses LLM API requests.

    Intercepts requests to LLM API endpoints, compresses the messages/context
    in the request body, forwards the compressed request, and returns
    the response transparently.
    """

    # API endpoints to intercept (OpenAI-compatible format)
    INTERCEPT_PATHS = {
        "/v1/chat/completions",
        "/v1/completions",
        "/v1/embeddings",
        "/chat/completions",
        "/completions",
    }

    # Target API base URLs (default: OpenAI)
    DEFAULT_TARGET_HOST = "api.openai.com"
    DEFAULT_TARGET_PORT = 443

    def __init__(self, *args, compressor: Optional[Compressor] = None, **kwargs):
        """Initialize the proxy handler.

        Args:
            compressor: Compressor instance for request compression.
        """
        self._compressor = compressor or Compressor(
            CompressionConfig(level=CompressionLevel.MEDIUM)
        )
        self._counter = TokenCounter()
        self._stats = {
            "requests_proxied": 0,
            "tokens_saved": 0,
            "requests_compressed": 0,
            "total_original_tokens": 0,
            "total_compressed_tokens": 0,
        }
        super().__init__(*args, **kwargs)

    def do_CONNECT(self) -> None:
        """Handle HTTPS CONNECT requests (SSL tunneling)."""
        # Parse target host and port
        host_port = self.path.split(":")
        target_host = host_port[0]
        target_port = int(host_port[1]) if len(host_port) > 1 else 443

        try:
            # Connect to target server
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((target_host, target_port))

            # Send 200 Connection Established
            self.send_response(200)
            self.send_header("Connection", "established")
            self.end_headers()

            # Tunnel data between client and remote
            self._tunnel_data(self.connection, remote_socket)
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")

    def do_POST(self) -> None:
        """Handle POST requests - intercept and compress API calls."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._forward_request()
            return

        # Read request body
        body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")

        # Check if this is an API request we should intercept
        if self._should_intercept(content_type):
            self._handle_api_request(body)
        else:
            self._forward_request(body=body)

    def do_GET(self) -> None:
        """Handle GET requests - forward directly."""
        self._forward_request()

    def _should_intercept(self, content_type: str) -> bool:
        """Check if the request should be intercepted for compression.

        Args:
            content_type: Request content type header.

        Returns:
            True if the request should be intercepted.
        """
        # Check path
        for path in self.INTERCEPT_PATHS:
            if self.path.endswith(path) or self.path == path:
                return True

        # Check content type
        if "application/json" in content_type:
            return True

        return False

    def _handle_api_request(self, body: bytes) -> None:
        """Handle an intercepted API request.

        Args:
            body: Raw request body bytes.
        """
        try:
            # Parse JSON body
            data = json.loads(body.decode("utf-8"))

            # Compress messages if present
            if "messages" in data:
                original_body = json.dumps(data, ensure_ascii=False)
                original_tokens = self._counter.count(original_body)

                data = self._compress_messages(data)
                compressed_body = json.dumps(data, ensure_ascii=False)
                compressed_tokens = self._counter.count(compressed_body)

                tokens_saved = original_tokens - compressed_tokens
                self._stats["tokens_saved"] += tokens_saved
                self._stats["requests_compressed"] += 1
                self._stats["total_original_tokens"] += original_tokens
                self._stats["total_compressed_tokens"] += compressed_tokens

                # Update Content-Length
                body = compressed_body.encode("utf-8")
                self.headers["Content-Length"] = str(len(body))

                # Log compression info
                self._log_compression(original_tokens, compressed_tokens)

            self._stats["requests_proxied"] += 1
            self._forward_request(body=body)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If we can't parse/process, forward as-is
            self._forward_request(body=body)

    def _compress_messages(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress messages in the API request data.

        Args:
            data: API request data with 'messages' field.

        Returns:
            Data with compressed messages.
        """
        compressed_messages = []
        for message in data.get("messages", []):
            if isinstance(message, dict) and "content" in message:
                content = message["content"]
                if isinstance(content, str) and len(content) > 100:
                    result = self._compressor.compress(content)
                    if result.tokens_saved > 0:
                        message = dict(message)
                        message["content"] = result.compressed_text
                        # Add metadata header (optional)
                        message["_ts_compressed"] = True
            compressed_messages.append(message)

        data = dict(data)
        data["messages"] = compressed_messages
        return data

    def _forward_request(self, body: Optional[bytes] = None) -> None:
        """Forward the request to the target server.

        Args:
            body: Optional request body.
        """
        try:
            # Build target URL
            target_url = f"https://{self.DEFAULT_TARGET_HOST}{self.path}"

            # Build headers
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in (
                    "host",
                    "connection",
                    "transfer-encoding",
                    "content-length",
                ):
                    headers[key] = value
            headers["Host"] = self.DEFAULT_TARGET_HOST

            # Create and send request
            req = Request(target_url, data=body, headers=headers, method=self.command)

            try:
                response = urlopen(req, timeout=30)
                response_body = response.read()

                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response_body)

            except HTTPError as e:
                self.send_response(e.code)
                for key, value in e.headers.items():
                    if key.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(e.read())

        except (URLError, OSError) as e:
            self.send_error(502, f"Bad Gateway: {e}")

    def _tunnel_data(self, client_socket: socket.socket, remote_socket: socket.socket) -> None:
        """Tunnel data between client and remote sockets.

        Args:
            client_socket: Client socket.
            remote_socket: Remote server socket.
        """
        client_socket.setblocking(False)
        remote_socket.setblocking(False)

        sockets = [client_socket, remote_socket]
        try:
            while True:
                import select

                readable, _, _ = select.select(sockets, [], [], 60)
                if not readable:
                    break

                for s in readable:
                    try:
                        data = s.recv(8192)
                        if not data:
                            raise ConnectionError("Connection closed")
                        if s is client_socket:
                            remote_socket.sendall(data)
                        else:
                            client_socket.sendall(data)
                    except (ConnectionError, OSError):
                        return
        except Exception:
            pass
        finally:
            remote_socket.close()

    def _log_compression(self, original_tokens: int, compressed_tokens: int) -> None:
        """Log compression statistics.

        Args:
            original_tokens: Original token count.
            compressed_tokens: Compressed token count.
        """
        savings = original_tokens - compressed_tokens
        ratio = (savings / original_tokens * 100) if original_tokens > 0 else 0
        # Use server logger
        self.log_message(
            "TokenSage: Compressed %d -> %d tokens (saved %d, %.1f%%)",
            original_tokens,
            compressed_tokens,
            savings,
            ratio,
        )

    def log_message(self, format: str, *args: Any) -> None:
        """Override to add TokenSage prefix to log messages."""
        sys_module = __import__("sys")
        sys_module.stderr.write(
            f"[TokenSage Proxy] {format % args}\n"
        )


class ProxyServer:
    """HTTP proxy server with automatic LLM API compression.

    Starts a local HTTP proxy that intercepts LLM API requests and
    compresses the context/messages before forwarding to the target API.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        target_host: Optional[str] = None,
        target_port: Optional[int] = None,
        compression_level: str = "medium",
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the proxy server.

        Args:
            host: Local bind address.
            port: Local bind port.
            target_host: Target API host (default: api.openai.com).
            target_port: Target API port (default: 443).
            compression_level: Compression level for intercepted requests.
            config: Additional configuration dictionary.
        """
        self.host = host
        self.port = port
        self.target_host = target_host or "api.openai.com"
        self.target_port = target_port or 443
        self.compression_level = compression_level
        self.config = config or {}
        self._server: Optional[HTTPServer] = None
        self._running = False

    def start(self, blocking: bool = True) -> None:
        """Start the proxy server.

        Args:
            blocking: If True, blocks the current thread. If False, runs in background.
        """
        level = CompressionLevel(self.compression_level)
        compressor = Compressor(CompressionConfig(level=level))

        # Create handler class with compressor
        handler_class = type(
            "TSProxyHandler",
            (CompressionProxyHandler,),
            {
                "DEFAULT_TARGET_HOST": self.target_host,
                "DEFAULT_TARGET_PORT": self.target_port,
            },
        )

        # Patch handler init to accept compressor
        original_init = handler_class.__init__

        def patched_init(self_handler, *args, **kwargs):
            kwargs["compressor"] = compressor
            original_init(self_handler, *args, **kwargs)

        handler_class.__init__ = patched_init

        self._server = HTTPServer((self.host, self.port), handler_class)
        self._running = True

        print(f"[TokenSage Proxy] Starting proxy on {self.host}:{self.port}")
        print(f"[TokenSage Proxy] Target: {self.target_host}:{self.target_port}")
        print(f"[TokenSage Proxy] Compression level: {self.compression_level}")
        print(f"[TokenSage Proxy] Configure your LLM client to use http://{self.host}:{self.port} as proxy")
        print(f"[TokenSage Proxy] Press Ctrl+C to stop")

        if blocking:
            try:
                self._server.serve_forever()
            except KeyboardInterrupt:
                print("\n[TokenSage Proxy] Shutting down...")
                self.stop()
        else:
            thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            thread.start()

    def stop(self) -> None:
        """Stop the proxy server."""
        self._running = False
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        print("[TokenSage Proxy] Stopped.")

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics.

        Returns:
            Dictionary with proxy statistics.
        """
        if self._server and hasattr(self._server, "stats"):
            return self._server.stats
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "target": f"{self.target_host}:{self.target_port}",
        }
