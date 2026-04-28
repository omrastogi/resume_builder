import sys
import os

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf")
    sys.exit(1)

def check_pdf(filename):
    if not os.path.exists(filename):
        print(f"ERROR: File not found: {filename}")
        sys.exit(1)

    r = PdfReader(filename)
    pages = len(r.pages)
    print(f"Pages: {pages}")
    print(f"File: {filename}")
    print("-" * 50)

    for i, page in enumerate(r.pages):
        text = page.extract_text() or ""
        text = text.strip()
        lines = [l for l in text.splitlines() if l.strip()]
        chars = len(text)
        words = len(text.split())
        print(f"  Page {i+1}: {len(lines)} lines | {words} words | {chars} chars")

    if pages > 1:
        first_text = (r.pages[0].extract_text() or "").strip()
        last_text  = (r.pages[-1].extract_text() or "").strip()
        first_chars = len(first_text)
        last_chars  = len(last_text)
        fill = (last_chars / first_chars * 100) if first_chars > 0 else 0
        print("-" * 50)
        print(f"Last page fill vs page 1: {fill:.0f}%")
        if fill < 75:
            print("ACTION: Last page is under 75% full — trim content to fit on fewer pages.")
        else:
            print("OK: Last page is 75%+ full — keep the extra page.")
        print("\nLast page preview (first 400 chars):")
        print(last_text[:400])
    else:
        print("Single page — no fill check needed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        pdfs = [f for f in os.listdir(".") if f.endswith(".pdf")]
        if not pdfs:
            print("No PDF files found in current directory.")
            sys.exit(1)
        if len(pdfs) == 1:
            check_pdf(pdfs[0])
        else:
            print("Multiple PDFs found. Pass filename as argument.")
            for p in pdfs:
                print(f"  {p}")
    else:
        check_pdf(sys.argv[1])
