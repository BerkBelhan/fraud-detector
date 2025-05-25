from backend.utils.gemini_utils import model

def final_verdict_with_reasoning(product_json, seller_json):
    prompt = f"""
    You are the final decision-making agent in a multi-agent fraud detection system for e-commerce products and sellers.

    Two controller agents provided these evaluations:

    - Product Controller: {product_json}
    - Seller Controller: {seller_json}

    Your job is to:

    1. Integrate both analyses and provide an overall trust verdict for the product-seller.
    2. Give the verdict as ONE WORD ONLY, in uppercase, choosing from exactly these:

    - SAFE
    - PROCEED WITH CAUTION
    - LIKELY SCAM

    3. Then, on a new line, provide a concise, human-like explanation of your verdict in plain text.
    4. Do NOT output JSON or any other formatting—just the verdict word on the first line, then the explanation on the next line(s).
    5. Keep the explanation simple, clear, and focused on the key points from both controllers.
    6. Avoid lengthy or overly technical explanations.

    ---

    What to consider in your decision:

    - Look for suspicious review patterns, fake or incentivized reviews.
    - Check seller reputation, ratings, and user comments.
    - Do not over-penalize minor complaints or isolated negative comments.
    - Balance product and seller signals carefully.

    ---

    Example output:

    SAFE
    The product has mostly genuine reviews with balanced opinions, and the seller has a strong positive reputation with many verified purchases.

    ---
    """
    response = model.generate_content(prompt)
    return response.text


