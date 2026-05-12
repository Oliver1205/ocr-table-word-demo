"""Command line entrypoint for OCR table to Word conversion."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_LOG_DIR,
    DEFAULT_OCR_LANG,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_TITLE,
)
from .logger import setup_logger
from .ocr_engine import OCREngine
from .preprocess import preprocess_image
from .table_parser import parse_table_from_ocr
from .utils import check_file_exists, ensure_dir
from .word_writer import write_table_to_docx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a table image into an editable Word .docx table."
    )
    parser.add_argument("--input", required=True, help="Input image path, for example input/sample.jpg")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output Word path, default: output/result.docx",
    )
    parser.add_argument(
        "--conf-threshold",
        type=float,
        default=DEFAULT_CONF_THRESHOLD,
        help="Low confidence threshold, default: 0.70",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save preprocessing debug images under logs/debug",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    ensure_dir(DEFAULT_LOG_DIR)
    logger = setup_logger(level=logging.INFO)

    logger.info("OCR table to Word process started")
    logger.info("Input image: %s", args.input)
    logger.info("Output docx: %s", args.output)
    logger.info("Low confidence threshold: %.2f", args.conf_threshold)

    try:
        input_path = check_file_exists(args.input)

        preprocess_result = preprocess_image(str(input_path), debug=args.debug)
        if preprocess_result.get("success"):
            logger.info("Image preprocessing completed")
            if args.debug:
                logger.info("Debug images: %s", preprocess_result.get("debug_paths", {}))
        else:
            logger.warning(
                "Image preprocessing failed, fallback to original image. Reason: %s",
                preprocess_result.get("error"),
            )

        ocr_results: list[dict] = []
        try:
            ocr_engine = OCREngine(lang=DEFAULT_OCR_LANG, use_angle_cls=True)
            ocr_results = ocr_engine.recognize(str(input_path))
            logger.info("OCR recognized %d text boxes", len(ocr_results))
        except Exception as exc:
            logger.error("OCR step failed: %s", exc)
            logger.warning(
                "Fallback to empty table output. The Word file will still be generated."
            )

        low_confidence_items = [
            item for item in ocr_results if item.get("confidence", 0.0) < args.conf_threshold
        ]
        for item in low_confidence_items:
            logger.warning(
                "Low confidence text: %.3f | %s",
                item.get("confidence", 0.0),
                item.get("text", ""),
            )

        table_data = parse_table_from_ocr(
            ocr_results,
            conf_threshold=args.conf_threshold,
            mark_low_confidence=True,
        )
        logger.info(
            "Table matrix generated: %d rows x %d columns",
            len(table_data),
            max((len(row) for row in table_data), default=0),
        )

        write_table_to_docx(table_data, args.output, title=DEFAULT_TITLE)
        logger.info("Word file generated: %s", Path(args.output).resolve())
        logger.info("OCR table to Word process finished")
        return 0

    except Exception as exc:
        logger.error("Process failed: %s", exc)
        logger.debug("Debug traceback", exc_info=True)
        return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
