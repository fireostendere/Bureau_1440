"""Filesystem-related helper utilities."""

import os
import re
from pathlib import Path
from typing import Optional

from config import get_app_config


def get_env(key: str, default: Optional[str]) -> Optional[str]:
    """Fetch environment variable value with optional default."""
    value = os.getenv(key, default)
    return value


def safe_filename(text: str) -> str:
    """Convert arbitrary text into a filesystem-safe filename."""
    sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", text)
    return sanitized


def ensure_dir(path: Path) -> Path:
    """Create directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_artifact_path(artifact_type: str) -> Path:
    """Return path under artifacts directory for the requested type."""
    config = get_app_config(None)
    artifact_path = config.artifacts_dir / artifact_type
    return artifact_path


def get_baseline_path(filename: str) -> Path:
    """Resolve baseline asset path with environment overrides."""
    primary_root = Path(get_env("BASELINE_ROOT", "tests/baselines"))
    candidate = primary_root / filename
    if candidate.exists():
        return candidate

    fallback_root = Path(get_env("BASELINE_FALLBACK_ROOT", "src"))
    return fallback_root / filename
