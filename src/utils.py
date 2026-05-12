"""Shared utility helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def normalize_path(path: str | Path) -> Path:
    """Return a normalized Path without forcing it to exist."""
    return Path(path).expanduser()


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if it does not already exist."""
    directory = normalize_path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def ensure_parent_dir(path: str | Path) -> Path:
    """Create parent directory for a file path."""
    file_path = normalize_path(path)
    ensure_dir(file_path.parent)
    return file_path


def check_file_exists(path: str | Path) -> Path:
    """Validate that a file exists and return its normalized path."""
    file_path = normalize_path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    return file_path


def safe_filename(name: str) -> str:
    """Convert arbitrary text to a simple filesystem-friendly filename."""
    base = Path(name).stem.strip() or "file"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", base)


def save_debug_image(image: Any, output_path: str | Path) -> Path:
    """Save an OpenCV image and raise a clear error when writing fails."""
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is not installed. Please run: pip install -r requirements.txt"
        ) from exc

    path = ensure_parent_dir(output_path)
    ok = cv2.imwrite(str(path), image)
    if not ok:
        raise IOError(f"Failed to save debug image: {path}")
    return path
