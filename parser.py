"""
Resume Parsing and Entity Extraction Module
Extracts Candidate Name, Contact Info, Skills, Education, Experience,
Designation, and Classifies into Domain Categories.
"""

import os
import re
from typing import Dict, Any, List
from datetime import datetime

from config import (
    CATEGORIES,
    DEFAULT_CATEGORY,
    SKILLS_LIST,
    DEGREES,
    DESIGNATION_KEYWORDS,
    EMAIL_PATTERN,
    LOCATIONS,
    KNOWN_COMPANIES
)


def extract_email(text: str) -> str:
    """Finds first valid email in resume text."""
    matches = EMAIL_PATTERN.findall(text)
    for email in matches:
        clean = email.strip(".,;:()")
        # Disregard obvious false positives
        if not any(clean.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".pdf", ".docx"]):
            return clean
    return "Not Found"


def extract_phone(text: str) -> str:
    """Finds mobile / telephone numbers from text."""
    # Pattern for 10-digit numbers with optional country code (+91, 0, +1, etc.) and spaces/hyphens
    pattern = re.compile(r'(?:(?:\+|00)\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?[6-9]\d{4}[\s.-]?\d{4,5}\b')
    matches = pattern.findall(text)
    
    # Generic fallback pattern if no Indian/international standard mobile found
    if not matches:
        generic_pattern = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        matches = generic_pattern.findall(text)

    for phone in matches:
        clean = phone.strip(".,;:() ")
        # Exclude common number sequences like years or zip codes
        digits_only = re.sub(r'\D', '', clean)
        if 10 <= len(digits_only) <= 13:
            return clean

    return "Not Found"


def extract_name(text: str, filename: str) -> str:
    """
    Infers candidate name using document header analysis and filename fallback.
    """
    # 1. Inspect first 10 non-empty lines of text
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    invalid_keywords = {
        "resume", "curriculum", "vitae", "cv", "profile", "bio", "summary",
        "contact", "phone", "email", "education", "experience", "skills",
        "objective", "address", "page", "personal", "details", "declaration",
        "professional", "overview", "employment", "history", "career", "background",
        "qualifications", "core", "highlights", "competencies", "strengths",
        "teacher", "instructor", "lecturer", "professor", "manager", "engineer",
        "developer", "analyst", "specialist", "coordinator", "consultant",
        "executive", "associate", "officer", "accountant", "administrator",
        "representative", "worker", "technician", "intern", "supervisor", "lead", "assistant"
    }

    for line in lines[:10]:
        # Filter line: length, word count, no digits/special chars
        cleaned_line = re.sub(r'[^a-zA-Z\s.]', '', line).strip()
        words = cleaned_line.split()
        if 2 <= len(words) <= 4:
            # Check if all words start with capital letter or uppercase
            if all(w.istitle() or w.isupper() for w in words):
                if not any(w.lower() in invalid_keywords for w in words):
                    return " ".join(w.title() for w in words)

    # 2. Heuristic from filename (e.g. John_Doe_Resume.pdf -> John Doe or 10504237.pdf -> Candidate #10504237)
    base_name = os.path.splitext(filename)[0]
    if base_name.isdigit():
        return f"Candidate #{base_name}"

    cleaned_name = re.sub(r'(?i)[_-]?(resume|cv|biodata|profile|updated|latest|\d+)', '', base_name)
    cleaned_name = re.sub(r'[_\W]+', ' ', cleaned_name).strip()
    words = cleaned_name.split()
    if 2 <= len(words) <= 4:
        return " ".join(w.title() for w in words)
    elif len(words) == 1 and len(words[0]) >= 3:
        return words[0].title()

    return f"Candidate ({base_name})"


def extract_skills(text: str) -> List[str]:
    """Identifies matching skills from SKILLS_LIST using regex boundaries."""
    found_skills = set()
    text_lower = text.lower()

    for skill in SKILLS_LIST:
        # Match word boundaries carefully, escape C++, .NET, etc.
        escaped = re.escape(skill.lower())
        pattern = rf'(?<![\w#+]){escaped}(?![\w#+])'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # Sort alphabetically for consistency
    return sorted(list(found_skills))


def extract_experience(text: str) -> str:
    """Extracts explicit years of experience or estimates from date ranges."""
    # 1. Explicit years (e.g., "5+ years of experience", "3.5 years experience", "Total Experience: 4 Years")
    exp_regexes = [
        r'(?:total\s+)?experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years|yrs)',
        r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years|yrs)\s+(?:of\s+)?experience'
    ]
    for r in exp_regexes:
        m = re.search(r, text, re.IGNORECASE)
        if m:
            years = m.group(1)
            return f"{years} Years"

    # 2. Scan for year ranges (e.g., 2018 - 2024, 2019 to Present)
    year_range_pattern = re.findall(r'\b(19\d{2}|20\d{2})\s*(?:-|–|to)\s*(19\d{2}|20\d{2}|present|current)\b', text, re.IGNORECASE)
    if year_range_pattern:
        current_year = datetime.now().year
        total_span = 0
        spans = []
        for start_str, end_str in year_range_pattern:
            start_yr = int(start_str)
            if end_str.lower() in ["present", "current"]:
                end_yr = current_year
            else:
                end_yr = int(end_str)
            if 0 <= (end_yr - start_yr) <= 40:
                spans.append((start_yr, end_yr))

        if spans:
            earliest_yr = min(s[0] for s in spans)
            latest_yr = max(s[1] for s in spans)
            span_years = latest_yr - earliest_yr
            if 0 < span_years <= 40:
                return f"~{span_years} Years (Est: {earliest_yr}-{latest_yr})"

    return "Not Specified"


def extract_education(text: str) -> str:
    """Finds qualifying education degrees and maps them to canonical names."""
    canonical_map = {
        "bachelor of technology": "B.Tech",
        "b.tech": "B.Tech",
        "btech": "B.Tech",
        "master of technology": "M.Tech",
        "m.tech": "M.Tech",
        "mtech": "M.Tech",
        "bachelor of engineering": "B.E.",
        "b.e.": "B.E.",
        "chartered accountant": "Chartered Accountant (CA)",
        "ca": "Chartered Accountant (CA)",
        "cfa": "CFA",
        "cpa": "CPA",
        "bachelor of commerce": "B.Com",
        "b.com": "B.Com",
        "bcom": "B.Com",
        "master of commerce": "M.Com",
        "m.com": "M.Com",
        "master of business administration": "MBA",
        "mba": "MBA",
        "pgdm": "PGDM",
        "bachelor of business administration": "BBA",
        "bba": "BBA",
        "master of computer applications": "MCA",
        "mca": "MCA",
        "bachelor of computer applications": "BCA",
        "bca": "BCA",
        "b.sc": "B.Sc",
        "bsc": "B.Sc",
        "m.sc": "M.Sc",
        "msc": "M.Sc",
        "ph.d": "Ph.D",
        "doctorate": "Doctorate",
        "ll.b": "LL.B",
        "ll.m": "LL.M"
    }

    found_degrees = []
    found_canonicals = set()

    for deg_pattern in DEGREES:
        matches = re.findall(deg_pattern, text, re.IGNORECASE)
        if matches:
            raw = matches[0].strip().rstrip(".")
            cleaned = re.sub(r'[\.\s]+', '', raw).lower()
            raw_low = raw.lower()

            # Find matching canonical
            canonical = canonical_map.get(raw_low) or canonical_map.get(cleaned) or raw.title()
            if canonical not in found_canonicals:
                found_canonicals.add(canonical)
                found_degrees.append(canonical)

    if found_degrees:
        return ", ".join(found_degrees[:4])
    return "Not Specified"


def extract_designation(text: str) -> str:
    """Finds current or target job designation/title, checking header first."""
    lines = [re.sub(r'[^a-zA-Z\s/]', '', l).strip() for l in text.split("\n") if l.strip()][:5]
    for line in lines:
        for des in DESIGNATION_KEYWORDS:
            if des.lower() == line.lower() or line.lower().startswith(des.lower()):
                return des

    for des in DESIGNATION_KEYWORDS:
        escaped = re.escape(des)
        pattern = rf'\b{escaped}\b'
        if re.search(pattern, text, re.IGNORECASE):
            return des
    return "Not Specified"


def classify_category(text: str, designation: str, skills: List[str]) -> str:
    """
    Classifies resume into domain category based on weighted keyword scoring.
    """
    text_lower = text.lower()
    scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORIES}

    # 1. Match category keywords in full text
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            # Word boundary search
            escaped = re.escape(kw.lower())
            count = len(re.findall(rf'\b{escaped}\b', text_lower))
            if count > 0:
                scores[cat] += count * 1.5

    # 2. Boost score if designation matches a category's keywords
    des_lower = designation.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in des_lower:
                scores[cat] += 10.0

    # 3. Boost score based on detected skills
    for skill in skills:
        skill_lower = skill.lower()
        for cat, keywords in CATEGORIES.items():
            if any(kw in skill_lower for kw in keywords):
                scores[cat] += 2.0

    # Determine best category
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] >= 2.0:
        return best_cat
    return DEFAULT_CATEGORY


def extract_location(text: str) -> str:
    """Detects candidate location / city from resume text."""
    text_lower = text.lower()
    aliases = {
        "bengaluru": "Bangalore",
        "gurugram": "Gurgaon",
        "delhi ncr": "Delhi NCR",
        "new delhi": "Delhi",
        "trivandrum": "Thiruvananthapuram"
    }

    # 1. Search in header (first 15 lines) where location is usually stated
    header_text = "\n".join(text.split("\n")[:15]).lower()
    for loc in LOCATIONS:
        pattern = rf'\b{re.escape(loc.lower())}\b'
        if re.search(pattern, header_text):
            return aliases.get(loc.lower(), loc)

    # 2. Fallback to full document
    for loc in LOCATIONS:
        pattern = rf'\b{re.escape(loc.lower())}\b'
        if re.search(pattern, text_lower):
            return aliases.get(loc.lower(), loc)

    return "Not Specified"


def extract_company(text: str) -> str:
    """Identifies current or prominent past employer from resume text."""
    text_lower = text.lower()

    # Tools/skills that contain company names but shouldn't count as employer unless independent
    tech_tools = {
        "google": ["google apps", "google applications", "google classroom", "google docs", "google drive", "google suite", "google ads", "google analytics"],
        "microsoft": ["microsoft office", "microsoft word", "microsoft excel", "microsoft powerpoint", "microsoft teams", "microsoft suite", "microsoft certified", "ms office"],
        "amazon": ["amazon web services", "aws"],
        "oracle": ["oracle sql", "oracle database"],
        "adobe": ["adobe creative", "adobe suite", "adobe photoshop", "adobe illustrator"]
    }

    # 1. Check against known prominent companies
    for comp in KNOWN_COMPANIES:
        c_low = comp.lower()
        if c_low in tech_tools:
            # Check if mentions are merely tool names
            tool_phrases = tech_tools[c_low]
            mentions = len(re.findall(rf'\b{re.escape(c_low)}\b', text_lower))
            tool_matches = sum(len(re.findall(rf'\b{re.escape(tp)}\b', text_lower)) for tp in tool_phrases)
            if mentions <= tool_matches:
                continue

        pattern = rf'\b{re.escape(c_low)}\b'
        if re.search(pattern, text_lower):
            return comp

    # 2. Heuristic patterns (corporate & educational institutions)
    company_patterns = [
        r'(?:at|with)\s+([A-Z][a-zA-Z0-9&.\s]{2,30}?(?:School District|High School|Elementary School|Middle School|Public Schools|Academy|University|College|Technologies|Solutions|Tech|Corp|Corporation|Inc|LLC|Ltd|Limited|Labs|Services|Systems|Consulting|Media|India))\b',
        r'(?:Company|Employer|Organization|School|District)\s*[:\-]\s*([A-Z][a-zA-Z0-9&.\s]{2,25})\b'
    ]
    for cp in company_patterns:
        m = re.search(cp, text)
        if m:
            clean_comp = m.group(1).strip()
            if len(clean_comp.split()) <= 4 and clean_comp.lower() not in ["name", "city", "state"]:
                return clean_comp

    return "Not Specified"


def extract_summary_snippet(text: str) -> str:
    """Extracts first meaningful lines for quick preview."""
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 25]
    # Filter out email/phone lines
    clean_lines = [l for l in lines if "@" not in l and not re.search(r'\d{10}', l)]
    if clean_lines:
        snippet = " ".join(clean_lines[:2])
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        return snippet
    return "N/A"


def parse_resume(file_path: str, extracted_text: str) -> Dict[str, Any]:
    """
    Main parser orchestrator returning structured dictionary of resume data.
    """
    filename = os.path.basename(file_path)
    file_ext = os.path.splitext(filename)[1].lower()
    abs_path = os.path.abspath(file_path)

    if not extracted_text or not extracted_text.strip():
        return {
            "Candidate Name": extract_name("", filename),
            "Category": DEFAULT_CATEGORY,
            "Designation": "Not Specified",
            "Current Company": "Not Specified",
            "Location": "Not Specified",
            "Experience": "Not Specified",
            "Education": "Not Specified",
            "Top Skills": "None Detected",
            "All Skills": "None Detected",
            "Email": "Not Found",
            "Phone": "Not Found",
            "Candidate Status": "New",
            "Recruiter Notes": "",
            "File Name": filename,
            "File Path": abs_path,
            "Status": "Failed / Empty"
        }

    # Extract all components
    name = extract_name(extracted_text, filename)
    email = extract_email(extracted_text)
    phone = extract_phone(extracted_text)
    skills = extract_skills(extracted_text)
    exp = extract_experience(extracted_text)
    edu = extract_education(extracted_text)
    des = extract_designation(extracted_text)
    loc = extract_location(extracted_text)
    comp = extract_company(extracted_text)
    category = classify_category(extracted_text, des, skills)

    # Clean top skills (take top 6 for clean visual layout)
    top_skills_str = ", ".join(skills[:6]) if skills else "None Detected"
    all_skills_str = ", ".join(skills) if skills else "None Detected"

    return {
        "Candidate Name": name,
        "Category": category,
        "Designation": des,
        "Current Company": comp,
        "Location": loc,
        "Experience": exp,
        "Education": edu,
        "Top Skills": top_skills_str,
        "All Skills": all_skills_str,
        "Email": email,
        "Phone": phone,
        "Candidate Status": "New",
        "Recruiter Notes": "",
        "File Name": filename,
        "File Path": abs_path,
        "Status": "Processed"
    }

