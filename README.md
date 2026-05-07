---
title: ClauseGuard
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🛡️ ClauseGuard

> Upload any legal document — get instant risk audit, missing clause detection & plain English summary.

Built with Python, FastAPI, HTML/JS/CSS, LangChain, ChromaDB & Groq (free LLM).

---

## 🚀 Features

- **🔴 Clause Risk Scorer** — Every clause scored 1–10 for risk with reason and suggestion
- **❌ Missing Clause Detector** — Finds important clauses absent from your document
- **📄 Plain English Summary** — Explains what you're agreeing to in simple language
- **💬 Ask Anything (RAG Chat)** — Ask questions, AI answers from YOUR document

### Supported Document Types
- Rent / Lease Agreements
- Loan Agreements
- NDAs (Non-Disclosure Agreements)
- Job Offer Letters
- General Agreements
- **Scanned PDFs & Images** (JPG/PNG) via Tesseract OCR

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript (Vanilla Web) |
| Backend | FastAPI |
| LLM | Groq API — llama-3.3-70b (FREE) |
| Embeddings | sentence-transformers (local, FREE) |
| Vector DB | ChromaDB (local, FREE) |
| PDF Parsing | pdfplumber |
| RAG Framework | LangChain |

**Total API cost = ₹0**

---

## ⚙️ Setup & Installation (Windows)

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/clauseguard-ai.git
cd clauseguard-ai
```

### Step 2 — Install Tesseract OCR (Windows)
1. Download from [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install it to the default path: `C:\Program Files\Tesseract-OCR\`
3. Make sure to check **✅ Add to PATH** during installation.

### Step 3 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Get your FREE Groq API key
1. Go to [groq.com](https://groq.com)
2. Sign up (free)
3. Go to API Keys → Create new key
4. Copy the key

### Step 6 — Set up environment variables
Open `.env` file and replace with your key:
```
GROQ_API_KEY=your_actual_key_here
```

### Step 7 — Run the backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
Keep this terminal open.

### Step 8 — Run the frontend (new terminal)
```bash
cd frontend-web
python -m http.server 3000
```

### Step 9 — Open in browser
Go to: `http://localhost:3000`

---

## 📁 Project Structure

```
clauseguard-ai/
├── backend/
│   ├── main.py                  # FastAPI app — all API routes
│   ├── pdf_parser.py            # PDF text extraction + doc type detection
│   ├── rag_pipeline.py          # ChromaDB + embeddings + RAG retrieval
│   ├── risk_scorer.py           # ENGINE 1: clause risk scoring
│   ├── missing_clause.py        # ENGINE 2: missing clause detection
│   ├── summary_generator.py     # ENGINE 3: plain English summary
│   ├── groq_client.py           # Groq API wrapper
│   └── checklists/              # JSON checklists per document type
│       ├── rent_agreement.json
│       ├── loan_agreement.json
│       ├── nda.json
│       └── general_agreement.json
├── frontend-web/
│   ├── index.html               # Main UI layout
│   ├── styles.css               # Styling
│   └── script.js                # Frontend logic & API calls
├── .env                         # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🌐 Deployment

### Deploy Backend → Render.com (FREE)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set root directory to `backend`
5. Build command: `pip install -r ../requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
7. Add environment variable: `GROQ_API_KEY = your_key`

### Deploy Frontend → Vercel / GitHub Pages / Netlify (FREE)
1. Connect your GitHub repo to a static hosting provider like Vercel.
2. Set the root/publish directory to `frontend-web`.
3. Update the `BACKEND_URL` in `frontend-web/script.js` to match your Render backend URL.

---

## ⚠️ Disclaimer

ClauseGuard is for educational and informational purposes only.
It is NOT a substitute for professional legal advice.
Always consult a qualified lawyer before signing legal documents.

---

## 👨‍💻 Author

Built as a Final Year B.Tech CSE (AI) project.
```
