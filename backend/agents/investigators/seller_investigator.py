import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def evaluate_seller_comments(comments, scores_dict=None):
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
