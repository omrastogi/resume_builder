"""Render the PDF with pdf2image/Pillow and measure bottom whitespace."""
import sys
import os

fname = sys.argv[1] if len(sys.argv) > 1 else "revspring_data_engineering_coop.pdf"

try:
    from pdf2image import convert_from_path
    pages = convert_from_path(fname, dpi=150)
    img = pages[0].convert("L")  # grayscale
    width, height = img.size
    pixels = img.load()

    # Scan rows from bottom; a row is "blank" if all pixels are >= 250 (near-white)
    blank_rows = 0
    for y in range(height - 1, -1, -1):
        row_pixels = [pixels[x, y] for x in range(width)]
        if all(p >= 245 for p in row_pixels):
            blank_rows += 1
        else:
            break

    fill_pct = (1.0 - blank_rows / height) * 100
    print(f"Image: {width}x{height} px at 150 dpi")
    print(f"Blank rows at bottom: {blank_rows} ({blank_rows/height*100:.1f}% of page)")
    print(f"Fill estimate: {fill_pct:.1f}%")
    if fill_pct < 98:
        gap_pts = blank_rows / 150 * 72  # convert px to pts (72pt = 1 inch)
        print(f"ACTION: Under 98% — approx {gap_pts:.0f}pt gap at bottom, add content to fill.")
    else:
        print("OK: 98%+ filled")

except ImportError:
    print("pdf2image not available, trying pypdf approach...")
    from pypdf import PdfReader
    r = PdfReader(fname)
    pg = r.pages[0]
    text = pg.extract_text() or ""
    chars = len(text.strip())
    # Rough heuristic: a dense 1-page DE resume at 7pt has ~3500+ chars
    print(f"Characters on page: {chars}")
    if chars >= 3200:
        print("Heuristic OK: content density looks sufficient for 98% fill")
    else:
        print(f"Heuristic WARNING: only {chars} chars — may be under-filled")
