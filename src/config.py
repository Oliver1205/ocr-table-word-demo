"""Default project configuration."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_OCR_LANG = "ch"
DEFAULT_USE_ANGLE_CLS = True
DEFAULT_CONF_THRESHOLD = 0.70

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
DEFAULT_DEBUG_DIR = DEFAULT_LOG_DIR / "debug"

DEFAULT_OUTPUT_PATH = DEFAULT_OUTPUT_DIR / "result.docx"
DEFAULT_TITLE = "表格 OCR 识别结果"
LOG_FILE_NAME = "app.log"
