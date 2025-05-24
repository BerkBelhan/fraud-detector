import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def final_judge(agent_confidences: dict):
    prompt = f"""
You are the final decision agent in a multi-agent fraud detection system.

You are given a dictionary of confidence scores from up to 7 specialized agents. Each agent assesses a different fraud metric for an online product. The confidence values range from 0.0 (very unsafe) to 1.0 (very safe).

These agents may or may not all be present. Your job is to weigh their inputs based on their relevance and come to a final verdict: "Safe", "Risky", or "Scam".

**Guidelines**:
- If most scores are above 0.7 and critical metrics like "comment_analysis" and "rating_consistency" are high, lean toward **Safe**.
- If most scores fall between 0.4 and 0.7, especially for key trust metrics, lean toward **Risky**.
- If several scores are below 0.4, especially for "price_anomaly", "duplicate_listing", or "comment_analysis", it's likely a **Scam**.
- Be robust: don’t require all metrics to be present. Do the best with what you have.

Return your judgment in the following JSON format:
{{
  "verdict": "Safe" | "Risky" | "Scam",
  "reason": "short explanation that mentions which inputs influenced the decision"
}}

Input received:
{agent_confidences}
"""

    response = model.generate_content(prompt)
    return response.text

result = final_judge({
    "comment_analysis": 0.32,
    "rating_consistency": 0.48,
    "price_anomaly": 0.12,
    "shipping_estimate": 0.82,
    "description_quality": 0.55
})
print(result)

