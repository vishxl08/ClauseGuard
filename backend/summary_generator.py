import json
from groq_client import ask_groq


def generate_summary(text: str, doc_type: str, api_key: str = None) -> dict:
    """Generate a plain English summary of the document."""

    prompt = f"""You are analyzing a {doc_type.replace('_', ' ')} document.

Document text:
{text[:3000]}

Task: Summarize this document in plain simple English for a common person who has no legal knowledge.

Return ONLY a valid JSON object with this exact structure:
{{
  "doc_title": "short title for this document",
  "doc_type": "{doc_type}",
  "key_details": [
    {{"label": "detail name", "value": "detail value"}}
  ],
  "top_risks": [
    {{"risk": "risk description", "severity": "high/medium/low"}}
  ],
  "plain_summary": "2-3 sentence plain English summary of what this document means for the signer"
}}

Rules:
- key_details: extract 5-7 important facts (parties, amounts, dates, durations)
- top_risks: list top 3 risks FOR THE PERSON SIGNING (tenant/borrower/employee)
- plain_summary: write like explaining to a friend, no legal jargon
- Return ONLY the JSON, no extra text"""

    response = ask_groq(prompt, max_tokens=1000, api_key=api_key)

    try:
        # Clean response in case model adds markdown
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean.strip())
        return result
    except Exception:
        # Fallback if JSON parse fails
        return {
            "doc_title": f"{doc_type.replace('_', ' ').title()}",
            "doc_type": doc_type,
            "key_details": [{"label": "Note", "value": "Could not extract details automatically"}],
            "top_risks": [{"risk": "Please review document manually", "severity": "medium"}],
            "plain_summary": response[:500] if response else "Summary unavailable."
        }
