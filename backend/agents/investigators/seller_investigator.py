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
    Evaluates seller comments to determine trustworthiness and appends confidence to agent_outputs dict.

    Args:
        comments (list): List of seller review comments.
        agent_outputs (dict, optional): Shared dict to append confidence score.

    Returns:
        dict: Parsed JSON response including verdict, reason, user_friendly_reason, and confidence.

    You are a seller trust evaluator. 

    Analyze these reviews and return a structured JSON response.

    Response format:
    {{
      "verdict": "Safe" | "Suspicious" | "Likely Scam",
      "reason": "short explanation",
      "user_friendly_reason": "Explanation understandable by a normal user (e.g., 'Some users received the wrong color or size, which may not be a scam but requires caution.')",
      "confidence": 0.0  # Provide a confidence score between 0 and 1 based on your analysis
    }}

    Seller reviews:
    {joined_comments}
    """
    response = model.generate_content(prompt)
    
    return response.text.strip()

