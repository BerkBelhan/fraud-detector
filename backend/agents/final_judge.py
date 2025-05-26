# In: backend/agents/final_judge.py
# --- FINAL CORRECTED VERSION ---

import time
from pydantic import BaseModel, ValidationError
from typing import List # <--- CHANGE 1: Added this import

# We import our single, reliable function for calling the Gemini API
from backend.utils.gemini_utils import call_gemini


def final_verdict_with_reasoning(product_response, seller_response, description_response, thinking_placeholder=None, base_html=None):
    """
    Integrates analyses from other agents, calls Gemini for a final verdict,
    and formats the response string for display.
    """

    # --- START OF CHANGES ---

    # 2. NEW: Define a Pydantic model for a single reasoning item
    class ReasoningItem(BaseModel):
        reason: str

    # 3. Update the main model to expect a list of ReasoningItem objects
    class OverallResult(BaseModel):
        summary: str
        overall_score: int
        overall_score_review: str
        reasonings_with_examples: List[ReasoningItem] # This line was changed from list[str]
        suggestion: str

    # --- END OF CHANGES ---

    prompt = f"""
You are the final decision-making agent in a multi-agent fraud detection system.
Your job is to integrate the following analyses, provide an overall trust verdict, a score from 0-100,
and a detailed explanation with examples. Your response must be in English.

Your output MUST be a single JSON object that strictly adheres to this schema:
{{
    "summary": "A brief summary of your analysis.",
    "overall_score": "An integer score between 0 and 100.",
    "overall_score_review": "A short review explaining the score.",
    "reasonings_with_examples": [
        {{"reason": "Reasoning point with an example."}},
        {{"reason": "Another reasoning point with an example."}}
    ],
    "suggestion": "A small suggestion for users who want to buy this product."
}}

--- START OF DATA FOR ANALYSIS ---

### Product Description Investigator Analysis:
{description_response}

### Product Reviews Investigator Analysis:
{product_response}

### Seller Information Investigator Analysis:
{seller_response}

--- END OF DATA FOR ANALYSIS ---

Now, provide your final verdict as a single, clean JSON object with no other text before or after it.
"""

    if thinking_placeholder and base_html:
        final_judge_text = "Finalizing verdict..."
        animated_text = ""
        for char in final_judge_text:
            animated_text += char
            thinking_placeholder.markdown(base_html.format(animated_text), unsafe_allow_html=True)
            time.sleep(0.05)

    result_json = call_gemini(prompt)

    if "error" in result_json:
        return f"An error occurred during final analysis: {result_json['error']}"

    try:
        response = OverallResult(**result_json)

        # --- START OF CHANGES ---

        # 4. Update the formatting loop to access the .reason attribute from each item
        reasonings_text = ""
        for i, item in enumerate(response.reasonings_with_examples):
            reasonings_text += f"**{i + 1}.** {item.reason}\n\n" # Changed from `reason` to `item.reason`

        # --- END OF CHANGES ---

        formatted_text = f"""
### Summary of Analysis
{response.summary}

### Overall Trustworthy Score: {response.overall_score}/100

### Overall Score Review
{response.overall_score_review}

### Reasonings
{reasonings_text}

### Additional Suggestions for Users
{response.suggestion}
"""
        return formatted_text

    except ValidationError as e:
        return f"Error: The AI response was not in the expected format.\n\nDetails: {e}\n\nRaw AI Response: {result_json}"
    except Exception as e:
        return f"An unexpected error occurred while processing the final verdict: {e}"