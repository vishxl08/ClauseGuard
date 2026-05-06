import os
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import auth
from auth import get_current_user

from pdf_parser import extract_text, detect_doc_type, split_into_clauses
from summary_generator import generate_summary
from missing_clause import detect_missing_clauses
from risk_scorer import score_clauses, get_risk_label
from rag_pipeline import build_rag_index, answer_question

app = FastAPI(title="ClauseGuard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


class ChatRequest(BaseModel):
    question: str
    session_id: str


@app.get("/")
def root():
    return {"status": "ClauseGuard AI backend is running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Upload PDF or scanned image.
    Auto-detects if scanned → runs OCR automatically.
    """
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload PDF or image (JPG, PNG, TIFF, BMP, WEBP)."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Step 1: Extract text (auto handles digital/scanned/image)
        text, source_type = extract_text(tmp_path)

        # Step 2: Detect doc type
        doc_type = detect_doc_type(text)

        # Step 3: Split into clauses
        clauses = split_into_clauses(text)

        user_api_key = current_user.get("api_key")

        # Step 4: Run all 3 engines
        summary = generate_summary(text, doc_type, api_key=user_api_key)
        missing = detect_missing_clauses(text, doc_type)
        risks = score_clauses(clauses, doc_type, api_key=user_api_key)

        # Step 5: Build RAG index
        session_id = str(uuid.uuid4()).replace("-", "")[:16]
        build_rag_index(text, session_id)

        return {
            "session_id": session_id,
            "doc_type": doc_type,
            "filename": filename,
            "source_type": source_type,
            "summary": summary,
            "missing_clauses": missing,
            "risk_scores": [
                {**r, "risk_label": get_risk_label(r["score"])} for r in risks
            ],
            "total_clauses_found": len(clauses)
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.post("/chat")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Answer a question about the uploaded document using RAG."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = answer_question(request.question, request.session_id, api_key=current_user.get("api_key"))
    return result