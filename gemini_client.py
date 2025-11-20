import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

# Configure Gemini
genai.configure(api_key=api_key)

def generate_text(prompt: str) -> str:
    """
    Sends text to Gemini and returns the response.
    """
    # Use a current model (2.x) – 1.5 series is retired
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return (response.text or "").strip()