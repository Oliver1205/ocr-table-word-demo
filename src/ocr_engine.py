"""OCR engine wrapper based on RapidOCR + ONNXRuntime.

This version replaces EasyOCR with RapidOCR because RapidOCR is more suitable
for Chinese document/table OCR and does not depend on paddlepaddle runtime.

Output format stays compatible with the rest of the project:
[
    {
        "text": "...",
        "confidence": 0.98,
        "box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
]
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("ocr_table_word_demo")


class OCREngine:
    """RapidOCR-based OCR engine."""

    def __init__(self, lang: str = "ch", use_angle_cls: bool = True) -> None:
        self.lang = lang
        self.use_angle_cls = use_angle_cls

        try:
            from rapidocr_onnxruntime import RapidOCR
        except Exception as exc:
            raise RuntimeError(
                "Failed to import RapidOCR. Please check rapidocr-onnxruntime installation."
            ) from exc

        try:
            logger.info("Initializing RapidOCR ONNXRuntime engine")
            self.engine = RapidOCR()
            logger.info("RapidOCR engine initialized successfully")
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize RapidOCR engine: {exc}") from exc

    def recognize(self, image_path: str) -> list[dict[str, Any]]:
        """Recognize text from an image."""
        try:
            result, _ = self.engine(image_path)
        except Exception as exc:
            raise RuntimeError(f"RapidOCR recognition failed: {exc}") from exc

        normalized_results: list[dict[str, Any]] = []

        if not result:
            logger.warning("RapidOCR returned no text boxes")
            return normalized_results

        for item in result:
            try:
                box, text, confidence = item
                text = str(text).strip()
                confidence = float(confidence)

                # Filter extremely low-confidence noise.
                if not text:
                    continue

                if confidence < 0.05:
                    continue

                if confidence < 0.12 and len(text) <= 2:
                    continue

                normalized_box = [
                    [float(point[0]), float(point[1])]
                    for point in box
                ]

                normalized_results.append(
                    {
                        "text": text,
                        "confidence": confidence,
                        "box": normalized_box,
                    }
                )
            except Exception as exc:
                logger.warning("Skipped invalid OCR item: %s | reason: %s", item, exc)

        normalized_results.sort(
            key=lambda item: (
                min(point[1] for point in item["box"]),
                min(point[0] for point in item["box"]),
            )
        )

        return normalized_results
