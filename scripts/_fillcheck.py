"""
_fillcheck.py — PDF fill measurement using lowest text Y coordinate.

Usage:
    python _fillcheck.py <path_to_pdf>

Output:
    PAGE_COUNT=<n>
    PAGE_SIZE=<w>x<h>pts
    PAGE_1_FILL=<float>
    PAGE_LAST_FILL=<float>
    PAGE_LAST_NUM=<n>
    STATUS=OK | WARN_FILL_LOW | WARN_LAST_PAGE_LOW
    VERDICT=<human readable>

Exit codes:
    0 — pass
    1 — fill below threshold
    2 — file error
"""

import sys

try:
    import fitz  # PyMuPDF
    _BACKEND = "fitz"
except ImportError:
    fitz = None
    _BACKEND = "none"

SINGLE_PAGE_MIN_FILL = 98.0
LAST_PAGE_MIN_FILL   = 75.0


def measure_fill_fitz(doc, page_index: int) -> tuple[float, float, float]:
    """Return (width_pts, height_pts, fill_pct) using PyMuPDF block bounding boxes."""
    pg = doc[page_index]
    rect = pg.rect
    w, h = rect.width, rect.height
    if h == 0:
        return w, h, 0.0
    blocks = pg.get_text("blocks")
    ys = [b[3] for b in blocks if b[4].strip()]  # b[3] = y1 (bottom of block, Y↓)
    if not ys:
        return w, h, 0.0
    last_y = max(ys)
    return w, h, round(last_y / h * 100.0, 2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python _fillcheck.py <path_to_pdf>")
        sys.exit(2)

    if _BACKEND == "none":
        print("ERROR: PyMuPDF (fitz) not installed. Run: pip install pymupdf")
        sys.exit(2)

    pdf_path = sys.argv[1]

    try:
        doc = fitz.open(pdf_path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Could not open PDF: {e}")
        sys.exit(2)

    page_count = len(doc)
    page_width, page_height, page1_fill = measure_fill_fitz(doc, 0)
    last_fill = measure_fill_fitz(doc, page_count - 1)[2] if page_count > 1 else page1_fill

    print(f"PAGE_COUNT={page_count}")
    print(f"PAGE_SIZE={page_width:.0f}x{page_height:.0f}pts ({page_width/72:.2f}\"x{page_height/72:.2f}\")")
    print(f"PAGE_1_FILL={page1_fill}")
    print(f"PAGE_LAST_FILL={last_fill}")
    print(f"PAGE_LAST_NUM={page_count}")

    if page_count == 1:
        if page1_fill >= SINGLE_PAGE_MIN_FILL:
            status    = "OK"
            verdict   = f"1-page resume: {page1_fill}% filled — PASS (>= {SINGLE_PAGE_MIN_FILL}%)"
            exit_code = 0
        else:
            gap_pts   = (SINGLE_PAGE_MIN_FILL / 100 - page1_fill / 100) * page_height
            status    = "WARN_FILL_LOW"
            verdict   = f"1-page resume: {page1_fill}% filled — FAIL (need >= {SINGLE_PAGE_MIN_FILL}%, add ~{gap_pts:.1f}pts of content)"
            exit_code = 1
    else:
        if last_fill >= LAST_PAGE_MIN_FILL:
            status    = "OK"
            verdict   = f"{page_count}-page resume: last page {last_fill}% filled — PASS (>= {LAST_PAGE_MIN_FILL}%)"
            exit_code = 0
        else:
            status    = "WARN_LAST_PAGE_LOW"
            verdict   = f"{page_count}-page resume: last page {last_fill}% filled — FAIL (need >= {LAST_PAGE_MIN_FILL}%, trim to {page_count - 1} page(s))"
            exit_code = 1

    print(f"STATUS={status}")
    print(f"VERDICT={verdict}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()