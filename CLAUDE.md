# Resume Tailoring Workflow

## Project Structure

```
Resumes/
├── CLAUDE.md
├── Reference/
│   ├── linkinedin_profile.txt
│   ├── Om_Resume_AI_Extended.zip
│   ├── Om_Resume_Data_Engineering.zip
│   ├── Om_Resume_Computer_Vision.zip
│   ├── Om_Resume_AI_Strategy.zip
│   ├── Resume_Data_Scientist.zip
│   └── Resume_Edge_AI.zip
├── jobs/
│   └── *.txt
├── output/
│   └── <company_job>/
│       ├── Resume_Om.tex
│       ├── *.cls
│       └── Resume_Om.pdf
└── scripts/
    ├── _fillcheck.py
    └── _pagecheck.py
```

---

## Batch Mode

If multiple `.txt` files exist in `jobs/`, run the full pipeline below for each one sequentially. Print a summary at the end: JD filename, base variant used, output path, page count, fill %, status.

---

## Step 1 — Parse Job Description

Read the `.txt` file from `jobs/`. Extract:

- Role title and company name
- Key requirements and preferred qualifications
- Tech stack and tools mentioned
- Specific keywords and phrasing to mirror

**Output:** a mental map of what to emphasize, what to de-emphasize, and which terms to adopt verbatim where truthful.

---

## Step 2 — Select Base Variant

Scan `Reference/` for all `.zip` files. Available variants: AI Extended, Data Engineering, Computer Vision, AI Strategy, Data Scientist, Edge AI.

Pick the closest match to the JD. Never create a new `.tex` from scratch — always start from an existing variant.

---

## Step 3 — Set Up Output Directory

1. Create `output/<company_job>/` (lowercase, underscores, e.g. `output/google_cv_engineer/`)
2. Extract the selected `.zip` — copy both the `.tex` and `.cls` files into that directory
3. Rename the `.tex` to `Resume_Om.tex`

---

## Step 4 — Tailor Content

Read `Reference/linkinedin_profile.txt` for full context on experience, projects, skills, and education.

Apply the following edits to `Resume_Om.tex`:

- Reorder and re-emphasize bullet points to match the JD
- Mirror JD terminology where truthful (e.g. "foundation models" instead of "LLMs" if that's what the JD says)
- Reorder the skills section to front-load what the JD asks for
- Do not fabricate experience, metrics, or skills not present in `linkinedin_profile.txt` or the source `.tex`
- Do not remove sections (Education, Experience, Projects, Skills) — only reorder and adjust emphasis within them

---

## Step 5 — Compile

Run:
```
cmd.exe /c "cd /d E:\Om\Resumes\output\<company_job> && pdflatex -interaction=nonstopmode Resume_Om.tex"
```

### Compilation Loop

```
attempt = 1
while compilation fails:
    read the .log file
    fix the specific error in Resume_Om.tex
    recompile
    attempt += 1
    if attempt > 3:
        stop and tell the user what failed — do not guess further
```

Run twice on success if references need resolving (e.g. `Rerun to get cross-references right` appears in log).

---

## Step 6 — Content Verification Loop

Run:
```
cmd.exe /c "cd /d E:\Om\Resumes\output\<company_job> && pdftotext Resume_Om.pdf -"
```

Check that:
- All expected sections are present (Education, Experience, Projects, Skills)
- No bullets are visibly truncated or dropped
- No garbled text or encoding artifacts

```
while content looks wrong:
    identify what is missing or broken in the .tex
    fix it
    recompile (go back to Step 5 compilation loop)
    re-run pdftotext
```

Ignore FontAwesome ligature warnings — they are harmless.

---

## Step 7 — Page Count and Fill Check

Run:
```
cmd.exe /c "cd /d E:\Om\Resumes\output\<company_job> && python ..\..\scripts\_fillcheck.py Resume_Om.pdf"
```

Parse the output:
- `PAGE_COUNT` — number of pages
- `PAGE_1_FILL` — fill % of page 1
- `PAGE_LAST_FILL` — fill % of last page
- `STATUS` — OK / WARN_FILL_LOW / WARN_LAST_PAGE_LOW
- `VERDICT` — human readable summary

Then follow the correct loop below based on role type.

---

### 7a — Internship Roles (1-page hard requirement)

#### Fill Loop

```
while PAGE_1_FILL < 98%:
    if PAGE_COUNT > 1:
        trim content (follow trimming order below) until it fits on 1 page
    else:
        if fill < 98%:
            add content from linkinedin_profile.txt (priority: strongest quantified results > relevant projects > certifications > additional skills)
    recompile
    re-run _fillcheck.py
```

Exit when: `PAGE_COUNT == 1` AND `PAGE_1_FILL >= 98%`

---

### 7b — Full-time and Research Roles

#### Page Count Loop

```
while PAGE_COUNT > desired AND PAGE_LAST_FILL < 75%:
    trim content (follow trimming order below)
    recompile
    re-run _fillcheck.py
```

Exit when: `PAGE_LAST_FILL >= 75%` or the resume fits cleanly on fewer pages.

If `PAGE_LAST_FILL >= 75%` — keep it. The last page is sufficiently full.

---

### Trimming Order

Apply in this order. Stop as soon as the check passes. Do not apply all at once.

1. Cut or shorten the weakest bullets for this specific JD
2. Tighten wording — reduce verbose bullets to single concise lines
3. Reduce vertical spacing — small `\vspace` adjustments only (e.g. `\vspace{-2pt}`)
4. Reduce space between sections slightly

**Never:** change font size, change margins below template defaults, remove entire sections, or make the resume look cramped. An ugly 1-pager is worse than a clean 2-pager.

---

## Step 8 — Orphan Line Loop

Run:
```
cmd.exe /c "cd /d E:\Om\Resumes\output\<company_job> && pdftotext -layout Resume_Om.pdf -"
```

Scan for orphan lines: any line with fewer than 5 words that is a continuation of the previous bullet.

```
while orphan lines exist:
    for each orphan:
        option A: shorten the bullet so it fits on one fewer line
        option B: extend the bullet so the last line is at least half the column width
    recompile
    re-run pdftotext -layout
    if no clean fix is possible after 2 attempts on a bullet: leave it and move on
```

---

## Step 9 — Final Output

Verify:
- `output/<company_job>/Resume_Om.pdf` exists and opens cleanly
- Page count and fill are within spec
- No orphan lines
- Content matches the tailored version

Done. If running batch mode, move to the next JD.