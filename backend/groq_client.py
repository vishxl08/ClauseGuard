import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

def ask_groq(prompt: str, system: str = "You are a helpful legal document analysis assistant.", max_tokens: int = 1024, api_key: str = None) -> str:
    """Send a prompt to Groq and return the response text using the user's API key."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return "ERROR: Missing Groq API Key. Please update your profile."
        
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"
