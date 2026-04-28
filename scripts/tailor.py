"""
tailor.py — Resume Tailoring Script

Usage:
    python scripts/tailor.py jobs/company_role.txt
    python scripts/tailor.py --batch   # process all .txt files in jobs/

Workflow:
    1. Read the job description from jobs/
    2. Select the best-matching resume variant from Reference/
    3. Extract the .tex from the zip
    4. Tailor bullets, skills order, and keywords to match the JD
    5. Compile with pdflatex → output/company_role.pdf
    6. Verify output with pdftotext
"""

import argparse
import os
import subprocess
import zipfile
from pathlib import Path

REFERENCE_DIR = Path("Reference")
JOBS_DIR = Path("jobs")
OUTPUT_DIR = Path("output")

VARIANTS = {
    "ai_extended":       REFERENCE_DIR / "Om_Resume_AI_Extended.zip",
    "data_engineering":  REFERENCE_DIR / "Om_Resume_Data_Engineering.zip",
    "computer_vision":   REFERENCE_DIR / "Om_Resume_Computer_Vision (1).zip",
    "ai_strategy":       REFERENCE_DIR / "Om_Resume_AI_Strategy.zip",
    "data_scientist":    REFERENCE_DIR / "Resume_Data_Scientist.zip",
    "edge_ai":           REFERENCE_DIR / "Resume_Edge_AI.zip",
}

REFERENCE_FILE = REFERENCE_DIR / "linkinedin_profile.txt"


def read_jd(jd_path: Path) -> str:
    return jd_path.read_text(encoding="utf-8")


def select_variant(jd_text: str) -> Path:
    """Pick the best zip variant based on keywords in the JD."""
    jd_lower = jd_text.lower()
    scores = {
        "edge_ai":          sum(w in jd_lower for w in ["edge", "embedded", "tinyml", "onnx", "deployment"]),
        "computer_vision":  sum(w in jd_lower for w in ["vision", "cv", "detection", "segmentation", "tracking"]),
        "data_engineering": sum(w in jd_lower for w in ["pipeline", "etl", "spark", "kafka", "data engineer"]),
        "data_scientist":   sum(w in jd_lower for w in ["statistics", "analyst", "sql", "tableau", "data scientist"]),
        "ai_strategy":      sum(w in jd_lower for w in ["strategy", "product", "roadmap", "stakeholder"]),
        "ai_extended":      sum(w in jd_lower for w in ["llm", "diffusion", "foundation model", "generative", "nlp"]),
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "ai_extended"  # default fallback
    print(f"Selected variant: {best} (score={scores[best]})")
    return VARIANTS[best]


def extract_tex(zip_path: Path, dest_dir: Path) -> Path:
    """Extract the first .tex file found in the zip."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        tex_files = [f for f in zf.namelist() if f.endswith(".tex")]
        if not tex_files:
            raise FileNotFoundError(f"No .tex file found in {zip_path}")
        tex_name = tex_files[0]
        zf.extract(tex_name, dest_dir)
        return dest_dir / tex_name


def compile_tex(tex_path: Path, output_dir: Path) -> Path:
    """Compile .tex to PDF using pdflatex (twice for references)."""
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("pdflatex error:\n", result.stdout[-2000:])
            raise RuntimeError("pdflatex compilation failed. Check the log above.")
    pdf_path = output_dir / tex_path.with_suffix(".pdf").name
    return pdf_path


def verify_pdf(pdf_path: Path):
    """Use pdftotext to verify the PDF is readable."""
    result = subprocess.run(["pdftotext", str(pdf_path), "-"], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"PDF verification failed for {pdf_path}")
    print(f"PDF verified: {len(result.stdout.split())} words extracted.")


def process_job(jd_path: Path):
    jd_text = read_jd(jd_path)
    stem = jd_path.stem.lower().replace(" ", "_")

    zip_path = select_variant(jd_text)
    tex_src = extract_tex(zip_path, OUTPUT_DIR)

    # Rename to output naming convention
    tex_out = OUTPUT_DIR / f"{stem}.tex"
    tex_src.rename(tex_out)

    print(f"Tailoring {tex_out} for {jd_path.name} ...")
    # TODO: apply Claude-driven tailoring edits to tex_out here

    pdf_out = compile_tex(tex_out, OUTPUT_DIR)
    verify_pdf(pdf_out)
    print(f"Output: {pdf_out}")
    return zip_path.stem, pdf_out


def main():
    parser = argparse.ArgumentParser(description="Tailor resumes to job descriptions.")
    parser.add_argument("jd", nargs="?", help="Path to a single JD .txt file")
    parser.add_argument("--batch", action="store_true", help="Process all .txt files in jobs/")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    if args.batch:
        jd_files = list(JOBS_DIR.glob("*.txt"))
        if not jd_files:
            print("No .txt files found in jobs/")
            return
        summary = []
        for jd_file in jd_files:
            variant, pdf = process_job(jd_file)
            summary.append((jd_file.name, variant, pdf))
        print("\n--- Batch Summary ---")
        for jd_name, variant, pdf in summary:
            print(f"  {jd_name} → {variant} → {pdf}")
    elif args.jd:
        process_job(Path(args.jd))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
