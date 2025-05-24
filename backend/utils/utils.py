import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash-latest")

def call_gemini(prompt: str) -> dict:
    """
    Calls Gemini with the given prompt and returns the parsed JSON response.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return {"error": "No JSON found in Gemini response."}

        return json.loads(match.group())
    except Exception as e:
        return {"error": str(e)}