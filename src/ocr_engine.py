"""PaddleOCR adapter."""

from __future__ import annotations

from typing import Any


class OCREngine:
    """Small wrapper that converts PaddleOCR output into a stable structure."""

    def __init__(self, lang: str = "ch", use_angle_cls: bool = True) -> None:
        self.lang = lang
        self.use_angle_cls = use_angle_cls

        try:
            from paddleocr import PaddleOCR

            self.ocr = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=lang,
                show_log=False,
            )
        except Exception as exc:
            raise RuntimeError(
                "PaddleOCR initialization failed. Please check that "
                "paddleocr and paddlepaddle are installed correctly. "
                f"Original error: {exc}"
            ) from exc

    def recognize(self, image_path: str) -> list[dict]:
        """Run OCR and return text, confidence and quadrilateral boxes."""
        try:
            raw_result = self.ocr.ocr(image_path, cls=self.use_angle_cls)
        except Exception as exc:
            raise RuntimeError(f"OCR recognition failed for {image_path}: {exc}") from exc

        lines = self._flatten_raw_result(raw_result)
        normalized: list[dict] = []

        for item in lines:
            parsed = self._parse_line(item)
            if parsed is not None:
                normalized.append(parsed)

        return normalized

    @staticmethod
    def _looks_like_line(item: Any) -> bool:
        return (
            isinstance(item, (list, tuple))
            and len(item) >= 2
            and isinstance(item[0], (list, tuple))
            and isinstance(item[1], (list, tuple))
            and len(item[1]) >= 2
        )

    @classmethod
    def _flatten_raw_result(cls, raw_result: Any) -> list:
        """Support common PaddleOCR 2.x single-image output variants."""
        if not raw_result:
            return []

        if cls._looks_like_line(raw_result[0]):
            return list(raw_result)

        if len(raw_result) == 1 and isinstance(raw_result[0], list):
            page = raw_result[0]
            if not page:
                return []
            if cls._looks_like_line(page[0]):
                return list(page)

        lines = []
        for page in raw_result:
            if isinstance(page, list):
                lines.extend(item for item in page if cls._looks_like_line(item))
        return lines

    @staticmethod
    def _parse_line(item: Any) -> dict | None:
        try:
            box = [[float(point[0]), float(point[1])] for point in item[0]]
            text = str(item[1][0]).strip()
            confidence = float(item[1][1])
        except Exception:
            return None

        if not text:
            return None

        return {
            "text": text,
            "confidence": confidence,
            "box": box,
        }
