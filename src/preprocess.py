"""Image preprocessing utilities based on OpenCV."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import DEFAULT_DEBUG_DIR
from .utils import check_file_exists, ensure_dir, safe_filename, save_debug_image


def _load_cv2():
    try:
        import cv2

        return cv2
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is not installed. Please run: pip install -r requirements.txt"
        ) from exc


def enhance_table_lines(binary_image: Any) -> Any:
    """Enhance horizontal and vertical table lines for debug/extension use.

    The MVP still uses OCR boxes as the primary table parser input. This helper
    keeps a practical hook for future line-based cell detection.
    """
    cv2 = _load_cv2()
    height, width = binary_image.shape[:2]
    inverted = 255 - binary_image

    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (max(10, width // 30), 1)
    )
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (1, max(10, height // 30))
    )

    horizontal = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, horizontal_kernel)
    vertical = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, vertical_kernel)
    lines = cv2.add(horizontal, vertical)
    return 255 - lines


def preprocess_image(image_path: str, debug: bool = False) -> dict:
    """Read and preprocess an input image.

    PaddleOCR often performs best on the original image, so preprocessing is
    non-blocking: if it fails, the caller can still continue with the source
    file path.
    """
    source_path = check_file_exists(image_path)
    result: dict[str, Any] = {
        "original_path": str(source_path),
        "source_path": str(source_path),
        "ocr_image_path": str(source_path),
        "processed_path": None,
        "debug_paths": {},
        "success": False,
        "error": None,
    }

    try:
        cv2 = _load_cv2()
        image = cv2.imread(str(source_path))
        if image is None:
            raise ValueError(f"OpenCV failed to read image: {source_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15,
        )
        table_lines = enhance_table_lines(binary)

        result.update(
            {
                "original_image": image,
                "gray_image": gray,
                "denoised_image": denoised,
                "binary_image": binary,
                "table_lines_image": table_lines,
                "success": True,
            }
        )

        if debug:
            debug_dir = ensure_dir(DEFAULT_DEBUG_DIR)
            prefix = safe_filename(Path(source_path).name)
            debug_paths = {
                "gray": save_debug_image(gray, debug_dir / f"{prefix}_gray.png"),
                "denoised": save_debug_image(denoised, debug_dir / f"{prefix}_denoised.png"),
                "binary": save_debug_image(binary, debug_dir / f"{prefix}_binary.png"),
                "table_lines": save_debug_image(table_lines, debug_dir / f"{prefix}_table_lines.png"),
            }
            result["processed_path"] = str(debug_paths["binary"])
            result["debug_paths"] = {key: str(value) for key, value in debug_paths.items()}

    except Exception as exc:  # Keep the main OCR flow alive whenever possible.
        result["error"] = str(exc)

    return result
