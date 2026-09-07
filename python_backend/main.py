"""
Main Orchestration Script for Resume Scraper
Processes resumes from dump folder and generates segregated multi-sheet Excel file.
"""

import os
import sys
import glob
from datetime import datetime
from typing import List, Dict, Any
from tqdm import tqdm
import pandas as pd

from config import DUMP_DIR, FALLBACK_INPUT_DIR, OUTPUT_DIR
from extractor import extract_text_from_file
from parser import parse_resume
from excel_exporter import export_to_excel


def discover_resume_files() -> List[str]:
    """Finds all supported resume files in dump and input folders."""
    valid_exts = {".docx", ".doc", ".pdf", ".txt", ".rtf"}
    files = []

    # Check dump_resumes_here
    if os.path.exists(DUMP_DIR):
        for root, _, filenames in os.walk(DUMP_DIR):
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_exts and not f.startswith("~$"):
                    files.append(os.path.join(root, f))

    # Also check input_resumes if dump_resumes_here has few or none
    if os.path.exists(FALLBACK_INPUT_DIR):
        for root, _, filenames in os.walk(FALLBACK_INPUT_DIR):
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in valid_exts and not f.startswith("~$"):
                    full_p = os.path.join(root, f)
                    if full_p not in files:
                        files.append(full_p)

    return sorted(list(set(files)))


def detect_duplicates(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flags duplicate candidate submissions based on matching email or phone."""
    seen_emails = set()
    seen_phones = set()

    for rec in records:
        email = rec.get("Email", "").strip().lower()
        phone = rec.get("Phone", "").strip()

        is_dup = False
        if email and email not in ["not found", "n/a"]:
            if email in seen_emails:
                is_dup = True
            else:
                seen_emails.add(email)

        if phone and phone not in ["not found", "n/a"]:
            digits = "".join(filter(str.isdigit, phone))
            if len(digits) >= 10:
                if digits in seen_phones:
                    is_dup = True
                else:
                    seen_phones.add(digits)

        if is_dup:
            rec["Candidate Status"] = "On Hold"
            rec["Recruiter Notes"] = "⚠️ Duplicate profile detected (matching contact)"

    return records


def run_scraping_pipeline(auto_open: bool = False) -> str:
    """Runs the extraction, parsing, category segregation, and Excel export."""
    print("=" * 65)
    print("        RESUME SCRAPER & ATS TALENT PIPELINE")
    print("=" * 65)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DUMP_DIR, exist_ok=True)

    resume_files = discover_resume_files()
    if not resume_files:
        print(f"\n[!] No resumes found in: {DUMP_DIR}")
        print("    Please drop your .docx, .doc, or .pdf resumes into 'dump_resumes_here' and run again.")
        return ""

    print(f"\n[*] Found {len(resume_files)} resume file(s) to process.")
    print("[*] Extracting candidate details, location, company, and skills...\n")

    parsed_records: List[Dict[str, Any]] = []

    # Process files with progress bar
    for file_path in tqdm(resume_files, desc="Processing CVs", unit="file"):
        filename = os.path.basename(file_path)
        try:
            raw_text = extract_text_from_file(file_path)
            record = parse_resume(file_path, raw_text)
            parsed_records.append(record)
        except Exception as err:
            parsed_records.append({
                "Candidate Name": os.path.splitext(filename)[0],
                "Category": "General_and_Others",
                "Designation": "Error during parsing",
                "Current Company": "Not Specified",
                "Location": "Not Specified",
                "Experience": "N/A",
                "Education": "N/A",
                "Top Skills": "N/A",
                "All Skills": "N/A",
                "Email": "N/A",
                "Phone": "N/A",
                "Candidate Status": "New",
                "Recruiter Notes": f"Parse Error: {str(err)}",
                "File Name": filename,
                "File Path": os.path.abspath(file_path),
                "Status": "Error"
            })

    # Flag duplicate submissions
    parsed_records = detect_duplicates(parsed_records)

    # Generate timestamped Excel file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Resume_Scraping_Report_{timestamp}.xlsx"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    print("\n[*] Creating ATS Excel workbook with sheet navigation & status dropdowns...")
    export_to_excel(parsed_records, output_path)

    # Also save clean CSV backup
    csv_filename = f"Resume_Scraping_Report_{timestamp}.csv"
    csv_path = os.path.join(OUTPUT_DIR, csv_filename)
    df_csv = pd.DataFrame(parsed_records)
    if "File Path" in df_csv.columns:
        df_csv.drop(columns=["File Path"], inplace=True)
    df_csv.to_csv(csv_path, index=False)

    # Print summary breakdown to console
    print("\n" + "=" * 65)
    print("                     PROCESSING COMPLETE")
    print("=" * 65)
    print(f"[+] Excel Report : {output_path}")
    print(f"[+] CSV Backup   : {csv_path}")
    print(f"[+] Total CVs    : {len(parsed_records)}")

    # Category summary
    cat_counts = {}
    for r in parsed_records:
        cat = r.get("Category", "General_and_Others").replace("_", " ")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("\nCandidates per Domain:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat:<32} : {count} candidate(s)")

    print("=" * 65)

    if auto_open:
        try:
            os.startfile(output_path)
        except Exception as e:
            print(f"[!] Could not automatically open Excel: {e}")

    return output_path


if __name__ == "__main__":
    should_open = "--open" in sys.argv
    run_scraping_pipeline(auto_open=should_open)
