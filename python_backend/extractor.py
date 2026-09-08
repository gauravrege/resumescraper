"""
Text Extraction Module for Resume Scraper
Supports .docx, .doc, and .pdf formats
"""

import os
import re
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Extractor")


def extract_text_from_docx(file_path: str) -> str:
    """Extracts text from modern Word .docx documents including tables."""
    text_chunks = []
    try:
        import docx
        doc = docx.Document(file_path)
        # Extract headers if present
        for section in doc.sections:
            if section.header:
                for hp in section.header.paragraphs:
                    if hp.text.strip():
                        text_chunks.append(hp.text.strip())

        # Extract regular paragraphs
        for p in doc.paragraphs:
            if p.text.strip():
                text_chunks.append(p.text.strip())

        # Extract tables content
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text_chunks.append(" | ".join(row_text))

        extracted = "\n".join(text_chunks)
        if extracted.strip():
            return extracted
    except Exception as e:
        logger.warning(f"python-docx failed on {os.path.basename(file_path)}: {e}. Trying docx2txt fallback.")

    # Fallback to docx2txt
    try:
        import docx2txt
        text = docx2txt.process(file_path)
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.error(f"docx2txt also failed on {os.path.basename(file_path)}: {e}")

    return ""


def extract_text_from_doc(file_path: str) -> str:
    """Extracts text from legacy .doc Word files using win32com or binary extraction fallback."""
    abs_path = os.path.abspath(file_path)
    
    # Try Word COM automation if on Windows
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        doc = word.Documents.Open(abs_path, ReadOnly=True)
        text = doc.Range().Text
        doc.Close(False)
        word.Quit()
        pythoncom.CoUninitialize()
        if text and text.strip():
            return text.strip()
    except Exception as e:
        logger.info(f"Word COM automation not available or failed on {os.path.basename(file_path)}: {e}. Using binary stream fallback.")

    # Fallback: Extract printable ASCII & Unicode strings from binary .doc stream
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        # Find continuous sequences of readable characters
        matches = re.findall(rb'[\x20-\x7E]{4,}', content)
        decoded = [m.decode('latin1', errors='ignore') for m in matches]
        filtered = [s.strip() for s in decoded if len(s.strip()) > 3 and not s.startswith(("\\", "!", "%"))]
        return "\n".join(filtered)
    except Exception as e:
        logger.error(f"Binary fallback failed on {os.path.basename(file_path)}: {e}")
        return ""


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from PDF documents using pdfplumber with pypdf and OCR fallbacks."""
    text_chunks = []
    extracted_text = ""
    
    # 1. Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True) or page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
                
                # Check tables on page
                tables = page.extract_tables()
                for tbl in tables:
                    for row in tbl:
                        row_vals = [str(c).strip() for c in row if c and str(c).strip()]
                        if row_vals:
                            text_chunks.append(" | ".join(row_vals))

        combined = "\n".join(text_chunks).strip()
        if combined:
            extracted_text = combined
    except Exception as e:
        logger.warning(f"pdfplumber failed on {os.path.basename(file_path)}: {e}")

    # 2. Fallback to pypdf if pdfplumber extracted nothing
    if len(extracted_text) < 50:
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            chunks = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    chunks.append(t)
            
            pypdf_text = "\n".join(chunks).strip()
            if len(pypdf_text) > len(extracted_text):
                extracted_text = pypdf_text
        except Exception as e:
            logger.warning(f"pypdf failed on {os.path.basename(file_path)}: {e}")

    # 3. Fallback to OCR if text is still empty or very short (likely scanned image)
    if len(extracted_text) < 50:
        logger.info(f"Little or no text extracted for {os.path.basename(file_path)}, attempting OCR...")
        try:
            import pypdfium2 as pdfium
            from rapidocr_onnxruntime import RapidOCR
            
            ocr = RapidOCR()
            pdf = pdfium.PdfDocument(file_path)
            ocr_text = []
            
            for i in range(len(pdf)):
                page = pdf[i]
                # Render to PIL Image, then convert to numpy array for OCR
                pil_img = page.render(scale=2).to_pil()
                import numpy as np
                image = np.array(pil_img)
                
                # result is a list of [box, text, confidence]
                result, _ = ocr(image)
                if result:
                    page_text = "\n".join([line[1] for line in result])
                    ocr_text.append(page_text)
            
            if ocr_text:
                extracted_text = "\n".join(ocr_text).strip()
                logger.info(f"OCR successfully extracted text for {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"OCR failed on {os.path.basename(file_path)}: {e}")

    return extracted_text


def extract_text_from_file(file_path: str) -> str:
    """Dispatches extraction based on file extension."""
    if not os.path.exists(file_path):
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".doc":
        return extract_text_from_doc(file_path)
    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".txt", ".rtf"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""
    else:
        logger.warning(f"Unsupported file format: {ext} for {file_path}")
        return ""
