# Resume Tailoring System

A Claude Code-powered pipeline that picks the right resume variant for a job, rewrites bullets to match the JD, compiles a clean PDF, and runs fill/page checks automatically.

---

## How It Works

1. You drop a job description into `jobs/`
2. Claude picks the best-matching resume variant from `Reference/`
3. It tailors the LaTeX: reorders bullets, mirrors JD keywords, tightens wording
4. Compiles via `pdflatex`, then loops on fill and page-count checks until the resume meets spec

---

## Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| `pdflatex` | Compile `.tex` to PDF | MiKTeX (Windows) or TeX Live (Mac/Linux) |
| `pdftotext` | Verify PDF content | Poppler — `brew install poppler` |
| Python 3.9+ | Run helper scripts | python.org |

```bash
pip install pymupdf pypdf pdf2image
```

---

## Folder Structure

```
resume_builder/
├── CLAUDE.md                    # Workflow rules — Claude reads this automatically
├── Reference/
│   ├── profile.txt              # Your full experience dump (the source of truth)
│   └── *.zip                    # One zip per resume track (each contains a .tex + .cls)
├── jobs/
│   └── company_role.txt         # Paste job descriptions here
├── output/
│   └── company_role/            # Generated resumes land here
└── scripts/
    ├── _fillcheck.py
    ├── _pagecheck.py
    └── tailor.py
```

---

## First-Time Setup

**After cloning, run this single prompt in Claude Code before anything else:**

```
Read CLAUDE.md. I am setting up this resume builder for the first time.

My name is [Your Name].
My resume tracks are: [e.g. Software Engineering, Machine Learning, Data Engineering, Product Management]

Do the following:
1. Ask me to paste my full work history and experience (roles, bullets, metrics, projects,
   skills, certifications — everything). Save it as Reference/profile.txt.
2. Update the VARIANTS dict in scripts/tailor.py to reflect my tracks, using placeholder
   zip names in the format [YourName]_Resume_[Track].zip.
3. Update CLAUDE.md to replace any hardcoded paths or names with my name and correct OS paths.
4. Update the output file naming convention throughout CLAUDE.md and tailor.py to use my name.
5. Confirm what zip files I need to create and place in Reference/ before I can run the pipeline.
```

Claude will walk you through the rest interactively. By the end you will know exactly which zip files to create and where to put them.

---

## Reference Zips

Each zip is one resume track. It must contain a `.tex` file and its `.cls` class file.

Create one zip per domain you apply to. Name them consistently, for example:

```
Reference/
├── Jane_Resume_Software_Engineering.zip
├── Jane_Resume_Machine_Learning.zip
└── Jane_Resume_Product.zip
```

The selection logic in `scripts/tailor.py` scans the JD for keywords and picks the closest match. After the first-time setup prompt, Claude will have updated this to match your tracks.

---

## Daily Use

Once setup is done, the workflow is:

1. Save the job description as a `.txt` file in `jobs/`, named after the company and role
2. Open Claude Code in the project root
3. Run:

```
Tailor my resume for jobs/company_role.txt. Follow all steps in CLAUDE.md.
```

For multiple jobs at once:

```
Run the CLAUDE.md pipeline in batch mode for all files in jobs/.
```

---

## Fill Check Thresholds

Defined at the top of `scripts/_fillcheck.py`:

```python
SINGLE_PAGE_MIN_FILL = 98.0   # 1-page resumes must be >= 98% filled
LAST_PAGE_MIN_FILL   = 75.0   # Multi-page: last page must be >= 75% filled
```

Internship roles target 1 page at 98%+. Full-time and research roles allow 2 pages as long as the last page clears 75%.

---

## Troubleshooting

**`pdflatex` not found** — Install MiKTeX (miktex.org) on Windows or run `brew install --cask mactex` on Mac.

**`fitz` import error** — Run `pip install pymupdf`.

**Compilation fails** — Claude reads the `.log` automatically and fixes the error. If it fails after 3 attempts it will stop and show you the raw log.

**Fill stuck below threshold** — Add more bullets to `Reference/profile.txt`. Claude pulls from there when it needs to add content.