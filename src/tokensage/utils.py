"""TokenSage utility functions."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any


def get_config_dir() -> Path:
    """Get the TokenSage configuration directory."""
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    config_dir = Path(xdg) / "tokensage"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_cache_dir() -> Path:
    """Get the TokenSage cache directory."""
    xdg = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    cache_dir = Path(xdg) / "tokensage"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def load_config() -> Dict[str, Any]:
    """Load TokenSage configuration."""
    config_file = get_config_dir() / "config.json"
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save TokenSage configuration."""
    config_file = get_config_dir() / "config.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"