import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def evaluate_comments(comments, scores_dict=None):
    joined_comments = "\n".join(comments)
    prompt = f"""
You are an e-commerce fraud detection agent.

Analyze the following user comments and decide whether the product is a scam, suspicious, or safe. Be very cautious of repeated reviews, mentions of wrong items, fake quality, or refund issues. But do not be so harsh. If the majority of comments are positive, consider it safe. If the majority are negative, consider it suspicious. If there are many repeated reviews or mentions of refund issues, consider it a scam.

Respond ONLY with the JSON object. Do NOT add any explanations or extra text.
{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "short explanation here",
  "confidence": float  # confidence score from 0 to 1
}}

User comments:
{joined_comments}
"""

    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Remove markdown code fences if present
    if raw_output.startswith("```") and raw_output.endswith("```"):
      lines = raw_output.split("\n")
      #Remove the first line (e.g. ```json) and the last line (```)
      lines = lines[1:-1]
      raw_output = "\n".join(lines).strip()

    try:
      feedback = json.loads(raw_output)
    except json.JSONDecodeError:
      feedback = {
        "verdict": "Suspicious",
        "reason": "Could not parse model output.",
        "confidence": 0.5
    }

    # If confidence is missing, provide a default heuristic
    confidence = feedback.get("confidence", None)
    if confidence is None:
        # Simple heuristic: assign confidence based on verdict
        verdict_confidence_map = {
            "Safe": 0.9,
            "Suspicious": 0.6,
            "Likely Scam": 0.95
        }
        confidence = verdict_confidence_map.get(feedback.get("verdict", "Suspicious"), 0.5)
        feedback["confidence"] = confidence

    # Append confidence score to the shared dictionary if provided
    if scores_dict is not None:
        scores_dict["comments_agent"] = confidence

    return feedback