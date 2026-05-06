import json
from groq_client import ask_groq


def score_clauses(clauses: list[dict], doc_type: str, api_key: str = None) -> list[dict]:
    """Score each clause for risk level using Groq LLM."""
    scored = []

    # Only score first 8 clauses to avoid rate limits
    clauses_to_score = clauses[:8]

    for clause in clauses_to_score:
        prompt = f"""Analyze this clause from a {doc_type.replace('_', ' ')} for risk to the signing party (tenant/borrower/employee).

Clause:
{clause['text']}

Return ONLY a valid JSON object:
{{
  "score": <number 1-10, where 10 is highest risk>,
  "favors": "landlord/tenant/neutral/lender/borrower/employer/employee",
  "risk_reason": "one sentence explaining why this is risky or safe",
  "suggestion": "one sentence on what to negotiate or watch out for (or 'No action needed' if safe)"
}}

Score guide: 1-3 = safe, 4-6 = moderate risk, 7-10 = high risk
Return ONLY the JSON, no extra text."""

        response = ask_groq(prompt, max_tokens=300, api_key=api_key)

        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            result = json.loads(clean.strip())
            scored.append({
                "clause_index": clause["index"],
                "clause_text": clause["text"][:400],
                "score": int(result.get("score", 5)),
                "favors": result.get("favors", "neutral"),
                "risk_reason": result.get("risk_reason", ""),
                "suggestion": result.get("suggestion", "")
            })
        except Exception:
            # If parse fails, add with default score
            scored.append({
                "clause_index": clause["index"],
                "clause_text": clause["text"][:400],
                "score": 5,
                "favors": "neutral",
                "risk_reason": "Could not analyze this clause automatically.",
                "suggestion": "Review manually."
            })

    # Sort by risk score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def get_risk_label(score: int) -> str:
    """Convert numeric score to risk label."""
    if score >= 7:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"
