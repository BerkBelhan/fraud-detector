# In: backend/agents/investigators/description_investigator.py

# 1. Import our one, reliable function for calling the API
from backend.utils.gemini_utils import call_gemini

def evaluate_product_description(description, thinking_placeholder=None, base_html=None):
    """
    Analyzes the product description by calling the unified Gemini helper function.
    """
    # 2. Create a clear prompt for this specific agent's task, asking for a JSON output.
    prompt = f"""
    You are an e-commerce analysis agent. Your task is to analyze the following product description, which is in Turkish.
    Focus on its clarity, professionalism, and any suspicious language (e.g., exaggerated claims, pressure tactics).
    Your output MUST be a single JSON object with one key: "summary". Your summary must be in English.

    Example:
    {{
        "summary": "The product description is clear and professional, providing adequate detail about the product's features without using suspicious marketing tactics."
    }}

    --- PRODUCT DESCRIPTION DATA ---
    {description}
    --- END OF DATA ---

    Now, provide your analysis as a single JSON object.
    """

    # 3. Call the unified Gemini function
    result_dict = call_gemini(prompt)

    # 4. Handle the response and return ONLY the summary paragraph
    if "error" in result_dict:
        return f"Error during description analysis: {result_dict['error']}"

    return result_dict.get("summary", "Could not generate a summary for the product description.")