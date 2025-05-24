# product_investigator.py
from backend.utils.gemini_utils import model

def evaluate_product_comments(comments):
    joined_comments = "\n".join(comments)
    prompt = f"""
    You are a product fraud detection assistant.

    Your job is to analyze user comments about a specific product and assess whether there are signs of fraud or low product quality.

    Read the following comments carefully and provide a clear and concise paragraph summary.

    If users mention repeated complaints (fake product, refund issues, wrong items, dangerous items), mention this and warn the user.

    If comments are mostly positive but have a few minor complaints (delays, packaging issues), note that too and recommend they proceed with caution.

    In the end, suggest:
    - Proceed
    - Proceed with caution
    - Avoid

    ---
    User Comments:
    {joined_comments}
    """

    response = model.generate_content(prompt)
    return response.text
