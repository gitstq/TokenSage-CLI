"""Custom exceptions for TokenSage-CLI."""


class TokenSageError(Exception):
    """Base exception for all TokenSage errors."""

    def __init__(self, message: str = "", code: int = 0):
        self.message = message
        self.code = code
        super().__init__(self.message)


class TokenCountError(TokenSageError):
    """Error during token counting operations."""

    pass


class CompressionError(TokenSageError):
    """Error during compression operations."""

    pass


class DecompressionError(TokenSageError):
    """Error during decompression operations."""

    pass


class CostCalculationError(TokenSageError):
    """Error during cost calculation."""

    pass


class ConfigurationError(TokenSageError):
    """Error in configuration loading or validation."""

    pass


class ProxyError(TokenSageError):
    """Error in proxy mode operations."""

    pass


class ModelNotFoundError(TokenSageError):
    """Requested pricing model not found."""

    pass


class UnsupportedContentTypeError(TokenSageError):
    """Content type is not supported for the operation."""

    pass


class FileReadError(TokenSageError):
    """Error reading a file."""

    pass


class FileWriteError(TokenSageError):
    """Error writing a file."""

    pass
