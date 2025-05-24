import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
from backend.agents.investigators.seller_investigator import evaluate_seller_comments

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def seller_investigator_controller(comments, scores_dict=None) -> dict:
    """
    Processes the natural language output from the seller investigator and returns a structured response.

    Args:
        investigator_output (str): Text output from the investigator agent.
        scores_dict (dict, optional): A shared dictionary to which the final score will be appended.

    Returns:
        dict: A dictionary containing the verdict, reasoning, user_friendly_reason, score, and flag.
    """

    investigator_output = evaluate_seller_comments(comments)

    controller_prompt = f"""
You are a controller AI. You receive raw analysis text from a review investigation agent.

Based on the content of the analysis, output a structured JSON object using the following schema:

{{
  "verdict": "safe" | "suspicious" | "likely scam",
  "reason": "short internal explanation",
  "user_friendly_reason": "short explanation for general users",
  "confidence": float  # between 0 and 1
}}

Now process this investigator report:
\"\"\"
{investigator_output}
\"\"\"
"""

    response = model.generate_content(controller_prompt)
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
