"""OCR engine wrapper.

Current Docker delivery version uses EasyOCR as a compatibility fallback.

Reason:
- The original design used PaddleOCR.
- In the current Windows Docker Desktop / WSL environment, paddlepaddle crashed
  at import time with segmentation fault / input-output errors.
- To keep the MVP deliverable runnable, this module keeps the same OCREngine
  interface but switches the backend to EasyOCR.

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
    """EasyOCR-based OCR engine.

    The class name and recognize() output are kept stable so main.py and
    table_parser.py do not need to change.
    """

    def __init__(self, lang: str = "ch", use_angle_cls: bool = True) -> None:
        """Initialize EasyOCR reader.

        Args:
            lang: Kept for compatibility with the old PaddleOCR interface.
            use_angle_cls: Kept for compatibility. EasyOCR does not use this flag.
        """
        self.lang = lang
        self.use_angle_cls = use_angle_cls

        try:
            import easyocr
        except Exception as exc:
            raise RuntimeError(
                "Failed to import EasyOCR. Please check whether easyocr is installed."
            ) from exc

        try:
            # ch_sim: Simplified Chinese
            # en: English / digits / common symbols
            # gpu=False keeps the Docker CPU version more stable.
            logger.info("Initializing EasyOCR reader with languages: ch_sim, en")
            self.reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize EasyOCR reader: {exc}") from exc

    def recognize(self, image_path: str) -> list[dict[str, Any]]:
        """Recognize text from an image.

        Args:
            image_path: Image path inside local environment or Docker container.

        Returns:
            A list of normalized OCR items:
            [
                {
                    "text": str,
                    "confidence": float,
                    "box": [[x, y], [x, y], [x, y], [x, y]]
                }
            ]
        """
        try:
            raw_results = self.reader.readtext(image_path, detail=1, paragraph=False)
        except Exception as exc:
            raise RuntimeError(f"EasyOCR recognition failed: {exc}") from exc

        normalized_results: list[dict[str, Any]] = []

        if not raw_results:
            logger.warning("EasyOCR returned no text boxes")
            return normalized_results

        for item in raw_results:
            try:
                box, text, confidence = item

                normalized_box = [
                    [float(point[0]), float(point[1])]
                    for point in box
                ]

                normalized_results.append(
                    {
                        "text": str(text).strip(),
                        "confidence": float(confidence),
                        "box": normalized_box,
                    }
                )
            except Exception as exc:
                logger.warning("Skipped invalid OCR item: %s | reason: %s", item, exc)

        return normalized_results