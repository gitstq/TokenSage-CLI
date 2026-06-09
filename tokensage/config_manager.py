"""Configuration management for TokenSage-CLI.

Manages application configuration with support for YAML and JSON formats.
Handles default settings, custom pricing, proxy configuration, and
auto-generation of configuration files.
"""

import json
import os
from typing import Any, Dict, List, Optional

from tokensage.exceptions import ConfigurationError
from tokensage.utils import get_config_dir, read_file_safe, write_file_safe


# Default configuration template
DEFAULT_CONFIG = {
    "version": "0.1.0",
    "compression": {
        "default_level": "medium",
        "default_strategy": "auto",
        "preserve_structure": True,
        "reversible": False,
        "max_output_tokens": None,
        "language_hint": "auto",
    },
    "token_counter": {
        "default_strategy": "hybrid",
    },
    "cost_calculator": {
        "default_model": "gpt-4o",
        "currency": "USD",
    },
    "proxy": {
        "host": "127.0.0.1",
        "port": 8080,
        "target_host": "api.openai.com",
        "target_port": 443,
        "compression_level": "medium",
        "enabled_paths": [
            "/v1/chat/completions",
            "/v1/completions",
            "/v1/embeddings",
        ],
    },
    "custom_pricing": {},
    "history": {
        "enabled": True,
        "max_records": 1000,
    },
    "dashboard": {
        "history_limit": 20,
        "chart_width": 50,
    },
}


class ConfigManager:
    """Manages TokenSage configuration.

    Handles loading, saving, and validating configuration.
    Supports both JSON and YAML formats (YAML is optional).
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self._config_path = config_path or os.path.join(
            get_config_dir(), "config.json"
        )
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from file, falling back to defaults."""
        if os.path.exists(self._config_path):
            try:
                content = read_file_safe(self._config_path)
                self._config = json.loads(content)
                # Merge with defaults for any missing keys
                self._config = self._merge_with_defaults(self._config)
            except (json.JSONDecodeError, IOError) as e:
                self._config = dict(DEFAULT_CONFIG)
        else:
            self._config = dict(DEFAULT_CONFIG)

    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults to fill missing keys.

        Args:
            config: User configuration dictionary.

        Returns:
            Merged configuration dictionary.
        """
        result = dict(DEFAULT_CONFIG)
        for key, value in config.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = {**result[key], **value}
            else:
                result[key] = value
        return result

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            write_file_safe(
                self._config_path,
                json.dumps(self._config, indent=2, ensure_ascii=False),
            )
        except IOError as e:
            raise ConfigurationError(f"Failed to save config: {e}") from e

    def generate_default_config(self, path: Optional[str] = None) -> str:
        """Generate a default configuration file.

        Args:
            path: Path to write the config file. If None, uses default path.

        Returns:
            Path to the generated config file.
        """
        output_path = path or self._config_path
        content = json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False)

        # Add comments (as JSON doesn't support comments, add a header)
        header = (
            "# TokenSage-CLI Configuration File\n"
            "# Generated automatically - edit as needed\n"
            "# All values have sensible defaults\n\n"
        )
        write_file_safe(output_path, header + content)
        return output_path

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports dot notation).

        Args:
            key: Configuration key, supporting dot notation (e.g., 'compression.default_level').
            default: Default value if key not found.

        Returns:
            Configuration value.
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value (supports dot notation).

        Args:
            key: Configuration key with dot notation.
            value: Value to set.
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section.

        Args:
            section: Section name.

        Returns:
            Section dictionary, or empty dict if not found.
        """
        return self._config.get(section, {})

    def set_section(self, section: str, values: Dict[str, Any]) -> None:
        """Set an entire configuration section.

        Args:
            section: Section name.
            values: Dictionary of values to set.
        """
        self._config[section] = values

    def add_custom_pricing(
        self, model_name: str, input_price: float, output_price: float
    ) -> None:
        """Add custom model pricing.

        Args:
            model_name: Model name.
            input_price: Input price per 1K tokens.
            output_price: Output price per 1K tokens.
        """
        if "custom_pricing" not in self._config:
            self._config["custom_pricing"] = {}
        self._config["custom_pricing"][model_name] = {
            "input_price": input_price,
            "output_price": output_price,
        }

    def remove_custom_pricing(self, model_name: str) -> bool:
        """Remove custom model pricing.

        Args:
            model_name: Model name to remove.

        Returns:
            True if the model was found and removed.
        """
        if "custom_pricing" in self._config:
            if model_name in self._config["custom_pricing"]:
                del self._config["custom_pricing"][model_name]
                return True
        return False

    def get_custom_pricing(self) -> Dict[str, Dict[str, float]]:
        """Get all custom pricing configurations.

        Returns:
            Dictionary of custom pricing models.
        """
        return self._config.get("custom_pricing", {})

    def validate(self) -> List[str]:
        """Validate the current configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors = []

        # Validate compression level
        level = self.get("compression.default_level", "")
        if level not in ("mild", "medium", "aggressive"):
            errors.append(f"Invalid compression level: {level}")

        # Validate token counter strategy
        strategy = self.get("token_counter.default_strategy", "")
        if strategy not in ("bpe_approx", "char_level", "hybrid"):
            errors.append(f"Invalid token counter strategy: {strategy}")

        # Validate proxy settings
        port = self.get("proxy.port")
        if port is not None and (not isinstance(port, int) or port < 1 or port > 65535):
            errors.append(f"Invalid proxy port: {port}")

        host = self.get("proxy.host", "")
        if not host:
            errors.append("Proxy host cannot be empty")

        # Validate history settings
        max_records = self.get("history.max_records")
        if max_records is not None and (not isinstance(max_records, int) or max_records < 0):
            errors.append(f"Invalid max_records: {max_records}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Export the full configuration as a dictionary.

        Returns:
            Configuration dictionary.
        """
        return dict(self._config)

    @property
    def config_path(self) -> str:
        """Path to the configuration file."""
        return self._config_path

    def __repr__(self) -> str:
        """String representation."""
        return f"ConfigManager(path={self._config_path})"
