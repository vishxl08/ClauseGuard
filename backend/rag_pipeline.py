import os
import chromadb
from sentence_transformers import SentenceTransformer
from groq_client import ask_groq

# Load embedding model once at startup
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB client — stores data locally in ./chroma_db folder
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def build_rag_index(text: str, session_id: str) -> None:
    """Chunk text, embed, and store in ChromaDB under session_id."""
    # Delete existing collection for this session if it exists
    try:
        chroma_client.delete_collection(name=session_id)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=session_id)

    # Split text into chunks of ~400 chars with 50 char overlap
    chunks = chunk_text(text, chunk_size=400, overlap=50)

    if not chunks:
        return

    # Embed all chunks
    embeddings = embedder.encode(chunks).tolist()

    # Store in ChromaDB
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap

    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 30:
            chunks.append(chunk.strip())

    return chunks


def answer_question(question: str, session_id: str, api_key: str = None) -> dict:
    """Retrieve relevant chunks and answer question using Groq."""
    try:
        collection = chroma_client.get_collection(name=session_id)
    except Exception:
        return {
            "answer": "No document loaded. Please upload a document first.",
            "source": ""
        }

    # Embed the question
    question_embedding = embedder.encode([question]).tolist()[0]

    # Retrieve top 3 most relevant chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(3, collection.count())
    )

    if not results["documents"] or not results["documents"][0]:
        return {
            "answer": "Could not find relevant information in the document.",
            "source": ""
        }

    relevant_chunks = results["documents"][0]
    context = "\n\n---\n\n".join(relevant_chunks)

    prompt = f"""You are a legal document assistant. Answer the user's question based ONLY on the document excerpts below.

Document excerpts:
{context}

User question: {question}

Rules:
- Answer in simple, plain English — no legal jargon
- If the answer is not in the excerpts, say "This information is not mentioned in the document."
- Keep answer under 150 words"""

    answer = ask_groq(prompt, max_tokens=400, api_key=api_key)

    return {
        "answer": answer,
        "source": relevant_chunks[0][:200] + "..." if relevant_chunks else ""
    }
