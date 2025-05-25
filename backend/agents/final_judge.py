from backend.utils.gemini_utils import model


def final_verdict_with_reasoning(product_json, seller_json):
    prompt = f"""
    You're the final decision agent for a fraud detection system.

    Two controller agents provided these evaluations:

    - Product Controller: {product_json}
    - Seller Controller: {seller_json}

    Your job is to determine the overall trust score using these rules:
    - If both are Safe → "Green"
    - If one is Suspicious and the other Safe → "Orange"
    - If one is Likely Scam → "Red"
    - If both are Suspicious → "Red"

    Return your decision as a JSON:
    {{
        "final_verdict": "Green" | "Orange" | "Red",
        "score": 1 to 100,
        "reason": "Summarize reasoning clearly."
    }}
    """

    response = model.generate_content(prompt)
    return response.text
