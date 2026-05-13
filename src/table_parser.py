"""Simplified table reconstruction from OCR text boxes."""

from __future__ import annotations

from statistics import mean

from .config import DEFAULT_CONF_THRESHOLD


def get_box_bounds(box: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in box]
    ys = [point[1] for point in box]
    return min(xs), min(ys), max(xs), max(ys)


def get_box_center(box: list[list[float]]) -> tuple[float, float]:
    left, top, right, bottom = get_box_bounds(box)
    return (left + right) / 2, (top + bottom) / 2


def get_box_height(box: list[list[float]]) -> float:
    _, top, _, bottom = get_box_bounds(box)
    return max(1.0, bottom - top)


def get_box_width(box: list[list[float]]) -> float:
    left, _, right, _ = get_box_bounds(box)
    return max(1.0, right - left)


def group_by_rows(results: list[dict], row_threshold: float | None = None) -> list[list[dict]]:
    """Cluster OCR boxes into rows by y-center distance."""
    if not results:
        return []

    heights = [get_box_height(item["box"]) for item in results if item.get("box")]
    threshold = row_threshold or max(10.0, mean(heights) * 0.8 if heights else 12.0)

    rows: list[dict] = []
    for item in sorted(results, key=lambda r: get_box_center(r["box"])[1]):
        _, center_y = get_box_center(item["box"])
        matched_row = None

        for row in rows:
            if abs(center_y - row["center_y"]) <= threshold:
                matched_row = row
                break

        if matched_row is None:
            rows.append({"center_y": center_y, "items": [item]})
        else:
            matched_row["items"].append(item)
            matched_row["center_y"] = mean(get_box_center(x["box"])[1] for x in matched_row["items"])

    return [row["items"] for row in rows]


def infer_columns(rows: list[list[dict]]) -> list[float]:
    """Infer global column centers from OCR box x-centers."""
    items = [item for row in rows for item in row]
    if not items:
        return []

    widths = [get_box_width(item["box"]) for item in items]
    threshold = max(20.0, mean(widths) * 0.75 if widths else 25.0)

    clusters: list[dict] = []
    for item in sorted(items, key=lambda r: get_box_center(r["box"])[0]):
        center_x, _ = get_box_center(item["box"])
        matched = None

        for cluster in clusters:
            if abs(center_x - cluster["center_x"]) <= threshold:
                matched = cluster
                break

        if matched is None:
            clusters.append({"center_x": center_x, "values": [center_x]})
        else:
            matched["values"].append(center_x)
            matched["center_x"] = mean(matched["values"])

    return [cluster["center_x"] for cluster in clusters]


def normalize_matrix(rows: list[list[dict]], columns: list[float]) -> list[list[str]]:
    """Align row items to inferred columns and fill missing cells with empty strings."""
    if not rows:
        return []

    if not columns:
        return [
            [item.get("display_text", item.get("text", "")) for item in sorted(row, key=lambda r: get_box_center(r["box"])[0])]
            for row in rows
        ]

    matrix: list[list[str]] = []
    for row in rows:
        cells = [""] * len(columns)
        for item in sorted(row, key=lambda r: get_box_center(r["box"])[0]):
            center_x, _ = get_box_center(item["box"])
            column_index = min(range(len(columns)), key=lambda idx: abs(center_x - columns[idx]))
            text = item.get("display_text", item.get("text", ""))
            cells[column_index] = f"{cells[column_index]} {text}".strip() if cells[column_index] else text
        matrix.append(cells)

    return matrix


def parse_table_from_ocr(
    ocr_results: list[dict],
    conf_threshold: float = DEFAULT_CONF_THRESHOLD,
    mark_low_confidence: bool = True,
) -> list[list[str]]:
    """Convert OCR results into a simple 2D matrix.

    MVP strategy: cluster boxes into rows by y coordinate, infer columns by
    x coordinate, and place text into the nearest column. Complex merged cells
    are intentionally left for later versions.
    """
    if not ocr_results:
        return []

    prepared: list[dict] = []
    for item in ocr_results:
        text = str(item.get("text", "")).strip()
        box = item.get("box")
        if not text or not box:
            continue

        copied = dict(item)
        if mark_low_confidence and float(item.get("confidence", 0.0)) < conf_threshold:
            copied["display_text"] = f"[浣庣疆淇″害] {text}"
        else:
            copied["display_text"] = text
        prepared.append(copied)

    rows = group_by_rows(prepared)
    columns = infer_columns(rows)
    return normalize_matrix(rows, columns)

