import sys
from pathlib import Path

import cv2
import numpy as np


def enhance_image(input_path: str, output_path: str) -> None:
    img = cv2.imread(input_path)

    if img is None:
        raise RuntimeError(f"Failed to read image: {input_path}")

    # 1. Enlarge image: OCR works better when text is larger.
    enlarged = cv2.resize(
        img,
        None,
        fx=2.5,
        fy=2.5,
        interpolation=cv2.INTER_CUBIC,
    )

    # 2. Convert to grayscale.
    gray = cv2.cvtColor(enlarged, cv2.COLOR_BGR2GRAY)

    # 3. Improve local contrast.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    # 4. Sharpen text edges.
    blur = cv2.GaussianBlur(contrast, (0, 0), 1.2)
    sharp = cv2.addWeighted(contrast, 1.6, blur, -0.6, 0)

    # 5. Save enhanced grayscale image.
    cv2.imwrite(output_path, sharp)

    # Also save a binary version for backup testing.
    binary_path = str(Path(output_path).with_name(Path(output_path).stem + "_binary.png"))
    binary = cv2.adaptiveThreshold(
        sharp,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    cv2.imwrite(binary_path, binary)

    print(f"Saved enhanced image: {output_path}")
    print(f"Saved binary image: {binary_path}")


if __name__ == "__main__":
    enhance_image(sys.argv[1], sys.argv[2])
