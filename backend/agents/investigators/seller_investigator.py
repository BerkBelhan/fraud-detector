# In: backend/agents/investigators/seller_investigator.py

# 1. Import our one, reliable function for calling the API
from backend.utils.gemini_utils import call_gemini

def evaluate_seller_info(info, thinking_placeholder=None, base_html=None):
    """
    Analyzes seller information by calling the unified Gemini helper function.
    """
    # 2. Create a clear prompt for this specific agent's task, asking for a JSON output.
    prompt = f"""
    You are an e-commerce analysis agent. Your task is to analyze the following seller information, which is in Turkish.
    Consider the seller's score, shipment success rate, and typical response time. Note any red flags.
    Your output MUST be a single JSON object with one key: "summary". Your summary must be in English.

    Example:
    {{
        "summary": "The seller has a high rating and a good shipping success rate, indicating reliability. No significant red flags were found in their profile information."
    }}

    --- SELLER INFO DATA ---
    {info}
    --- END OF DATA ---

    Now, provide your analysis as a single JSON object.
    """

    # 3. Call the unified Gemini function
    result_dict = call_gemini(prompt)

    # 4. Handle the response and return ONLY the summary paragraph
    if "error" in result_dict:
        return f"Error during seller analysis: {result_dict['error']}"

    return result_dict.get("summary", "Could not generate a summary for the seller information.")