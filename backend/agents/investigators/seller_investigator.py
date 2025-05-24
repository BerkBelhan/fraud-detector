import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
def evaluate_seller_comments(comments):
    """
    Evaluates seller comments to determine trustworthiness.
    Args:
        comments (list): List of seller review comments.
    Returns:
        str: JSON response with verdict and reason.
    """
    joined_comments = "\n".join(comments)
    prompt = f"""
    You are a seller trust evaluator. 

    Analyze these reviews and return a structured JSON response.

    Response format:
    {{
      "verdict": "Safe" | "Suspicious" | "Likely Scam",
      "reason": "short explanation"
      "user_friendly_reason": "Explanation understandable by a normal user (e.g., 'Some users received the wrong color or size, which may not be a scam but requires caution.')"
    }}

    Seller reviews:
    {joined_comments}
    """
    response = model.generate_content(prompt)
    return response.text