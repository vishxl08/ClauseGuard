import pdfplumber
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io
import re
import os


# ── Tesseract path for Windows ────────────────────────────────
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(pdf_path: str):
    """Try normal text extraction first. If empty/scanned, use OCR."""
    text = _try_normal_extraction(pdf_path)

    if _is_good_text(text):
        return text.strip(), "digital"

    print("Normal extraction failed — switching to OCR...")
    text = _ocr_pdf(pdf_path)

    if not text.strip():
        raise ValueError(
            "Could not extract text from this document. "
            "Make sure the scan is clear and not too dark/blurry."
        )

    return text.strip(), "scanned"


def _try_normal_extraction(pdf_path: str) -> str:
    """Extract text normally using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass
    return text


def _is_good_text(text: str) -> bool:
    """Check if extracted text is real and usable."""
    if not text or len(text.strip()) < 100:
        return False
    words = text.split()
    if len(words) < 20:
        return False
    return True


def _ocr_pdf(pdf_path: str) -> str:
    """Convert each PDF page to image and run Tesseract OCR."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            page_text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
            text += page_text + "\n"
        doc.close()
    except Exception as e:
        raise ValueError(f"OCR failed: {str(e)}")
    return text


def extract_text_from_image(image_path: str):
    """Extract text directly from a scanned image file (JPG/PNG)."""
    try:
        img = Image.open(image_path)
        img = img.convert("L")  # grayscale for better OCR
        text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
        if not text.strip() or len(text.strip()) < 50:
            raise ValueError(
                "Could not read text from image. "
                "Make sure the image is clear, well-lit and not blurry."
            )
        return text.strip(), "image_ocr"
    except Exception as e:
        raise ValueError(f"Image OCR failed: {str(e)}")


def extract_text(file_path: str):
    """
    Master function — handles ALL file types:
    - Digital PDF  → normal extraction
    - Scanned PDF  → auto OCR
    - Image file   → direct OCR
    Returns: (extracted_text, source_type)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Upload PDF or image (JPG/PNG).")


def detect_doc_type(text: str) -> str:
    """Detect document type from text keywords."""
    text_lower = text.lower()

    rent_keywords = ["rent", "tenant", "landlord", "lease", "premises", "monthly rent", "security deposit", "tenancy"]
    loan_keywords = ["loan", "borrower", "lender", "repayment", "emi", "interest rate", "principal", "disbursement"]
    nda_keywords = ["confidential", "non-disclosure", "proprietary", "trade secret", "nda", "disclose"]
    job_keywords = ["employment", "employee", "employer", "salary", "designation", "probation", "notice period", "joining"]

    scores = {
        "rent_agreement": sum(1 for k in rent_keywords if k in text_lower),
        "loan_agreement": sum(1 for k in loan_keywords if k in text_lower),
        "nda": sum(1 for k in nda_keywords if k in text_lower),
        "job_offer": sum(1 for k in job_keywords if k in text_lower),
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "general_agreement"
    return best


def split_into_clauses(text: str) -> list[dict]:
    """Split document text into individual clauses."""
    clauses = []

    pattern = r'(?:(?:^|\n)(?:Clause\s+\d+|Section\s+\d+|\d+\.)\s+.+?)(?=(?:\n(?:Clause\s+\d+|Section\s+\d+|\d+\.)\s)|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    if matches and len(matches) >= 3:
        for i, match in enumerate(matches):
            clean = match.strip()
            if len(clean) > 20:
                clauses.append({
                    "index": i + 1,
                    "text": clean[:800]
                })
    else:
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        for i, para in enumerate(paragraphs[:15]):
            clauses.append({
                "index": i + 1,
                "text": para[:800]
            })

    return clauses