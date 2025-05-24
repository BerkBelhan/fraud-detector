import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def evaluate_overall_verdict(agent_confidences: dict) -> dict:
    """
    agent_confidences: dict of {agent_name: confidence_score (float 0-1)}

    Calls the LLM to evaluate all confidences and outputs a final verdict.
    """

    prompt = f"""
You are a Final Judge AI agent that receives confidence scores from multiple evaluation agents analyzing an e-commerce product/seller.

Input:
Agent confidences (name: confidence between 0 and 1):
{json.dumps(agent_confidences, indent=2)}

Your task:
- Assess the overall trustworthiness based on the agent confidence values.
- Consider the agent names and their typical reliability.
- Provide a final JSON verdict with:
  - "verdict": one of "Safe", "Suspicious", "Likely Scam"
  - "reason": brief explanation of your final judgment

Output ONLY the JSON object below, no additional text:

{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "your concise reasoning here"
}}
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
      return json.loads(raw_output)
    except json.JSONDecodeError:
      return {
        "verdict": "Suspicious",
        "reason": "Could not parse model output.Defaulting to Suspicious."
    }
    
"""
agent_confidences = {
    "comment_investigator": 0.92,
    "seller_investigator": 0.85,
    "rating_controller": 0.88,
    "behavioral_analysis_agent": 0.81,
    "metadata_consistency_agent": 0.79
}

print(evaluate_overall_verdict(agent_confidences))
"""
