import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
def evaluate_seller_comments(comments):
    joined_comments = "\n".join(comments)
    prompt = f"""
You are a seller trust evaluator.

Analyze these reviews and return:

{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "short explanation"
}}

Seller reviews:
{joined_comments}
"""
    response = model.generate_content(prompt)
    return response.text