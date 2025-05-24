import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# 3. Prompt template
def evaluate_comments(comments):
    joined_comments = "\n".join(comments)
    prompt = f"""
You are an e-commerce fraud detection agent.

Analyze the following user comments and decide whether the product is a scam, suspicious, or safe. Be very cautious of repeated reviews, mentions of wrong items, fake quality, or refund issues. But do not be so harsh. If the majority of comments are positive, consider it safe. If the majority are negative, consider it suspicious. If there are many repeated reviews or mentions of refund issues, consider it a scam.

Return your output in this JSON format:
{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "short explanation here"
}}

User comments:
{joined_comments}
"""

    response = model.generate_content(prompt)
    return response.text