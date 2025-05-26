# In: backend/agents/investigators/reviews_investigator.py

# 1. Import our one, reliable function for calling the API
from backend.utils.gemini_utils import call_gemini

def evaluate_product_comments(comments, thinking_placeholder=None, base_html=None):
    """
    Analyzes product comments by calling the unified Gemini helper function.
    """
    # 2. Create a clear prompt for this specific agent's task, asking for a JSON output.
    prompt = f"""
    You are an e-commerce analysis agent. Your task is to analyze the following product reviews, which are in Turkish.
    Look for patterns like fake reviews (repetitive, generic praise), significant complaints about product quality, or non-delivery.
    Your output MUST be a single JSON object with one key: "summary". Your summary must be in English.

    Example:
    {{
        "summary": "Analysis of user reviews shows a high number of positive but generic comments, suggesting a potential fake review campaign. There are also several credible complaints about the item not matching the description."
    }}

    --- PRODUCT REVIEW DATA ---
    {comments}
    --- END OF DATA ---

    Now, provide your analysis as a single JSON object.
    """

    # 3. Call the unified Gemini function
    result_dict = call_gemini(prompt)

    # 4. Handle the response and return ONLY the summary paragraph
    if "error" in result_dict:
        return f"Error during review analysis: {result_dict['error']}"

    return result_dict.get("summary", "Could not generate a summary for the product reviews.")