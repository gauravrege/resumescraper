# Resume Scraper & Category Segregator

An automated resume extraction and segregation system that processes Word (`.docx`, `.doc`) and PDF (`.pdf`) resumes from a dump folder and generates an organized, multi-tab Excel report.

---

## Quick Start (One-Click)

1. **Drop Resumes**: Copy or drag-and-drop your `.docx`, `.doc`, or `.pdf` CVs into the **`dump_resumes_here`** folder.
2. **Double-Click**: Run **`run_scraper.bat`**.
3. **View Results**: The scraper will process all resumes, show a progress bar in the console, and automatically open the newly generated Excel report in the **`output/`** folder.

---

## Folder Structure

```
resumescraper/
├── dump_resumes_here/      <-- DUMP YOUR RESUMES HERE (.docx, .doc, .pdf)
├── output/                 <-- Extracted Excel reports saved here
├── run_scraper.bat         <-- Double-click to execute scraper
├── main.py                 <-- Main orchestration script
├── parser.py               <-- Attribute extraction & category classification logic
├── extractor.py            <-- File reader for Word (.docx, .doc) & PDF (.pdf)
├── excel_exporter.py       <-- Multi-tab Excel generator with corporate styling
├── config.py               <-- Category taxonomy, skills dictionary, degrees
├── requirements.txt        <-- Dependencies
└── .venv/                  <-- Python virtual environment
```

---

## What Gets Extracted?

For every resume processed, the scraper extracts:
- **Candidate Name**: Detected from document headers and clean filename heuristics.
- **Category**: Segregated into dedicated domain categories (Software Engineering, Data Science & AI, Finance & Accounting, Sales & Marketing, Human Resources, Operations, Design, Legal, etc.).
- **Current / Target Designation**: Software Engineer, Data Scientist, Accountant, HR Manager, etc.
- **Email Address**: Clean email regex extraction.
- **Phone Number**: International and standard domestic phone numbers.
- **Total Experience**: Explicit years mentioned (e.g. `5+ Years`) or estimated from career date spans.
- **Education / Degrees**: Standardized degrees (B.Tech, MBA, M.Tech, B.Com, CA, CFA, etc.).
- **Key Skills**: Matches against industry skills dictionary.
- **Summary Snippet**: First 2 lines of executive profile summary.
- **File Name & Clickable Source Link**: Direct file link to open the original CV with one click.

---

## Excel Output Layout

The generated Excel workbook includes:
1. **Summary Dashboard**: Overall counts (total CVs scanned, success/fail counters) and breakdown count per category.
2. **All Candidates**: Master table containing all parsed candidates with filterable headers and hyperlinks.
3. **Segregated Category Tabs**: Separate sheets for each category (e.g., `Software Engineering`, `Data Science & AI`, `Finance & Accounting`, `Human Resources`, `Sales & Marketing`).

---

## Customization

To add or modify categories and skills:
- Open `config.py` in any text editor.
- Update `CATEGORIES` dictionary to add new domain keywords.
- Update `SKILLS_LIST` to include specific niche tools or frameworks.
