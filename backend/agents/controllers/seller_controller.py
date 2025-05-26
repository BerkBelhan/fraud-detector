

def classify_seller_analysis(paragraph):
    """
    Given a paragraph analysis from seller_investigator, classify the seller's trust level.
    Return a JSON verdict and short reason.
    """
    prompt = f"""
    You are a controller agent for e-commerce fraud detection.

    Based on the following paragraph that summarizes user comments about a **seller**, classify the seller as:
    - "Safe" if users mostly trust them and complaints are minor (e.g. wrong color).
    - "Suspicious" if there are multiple complaints or worrying patterns, but it's not clearly a scam.
    - "Likely Scam" if there's strong indication of fraud, scam, or undelivered orders.

    Return a structured JSON object like this:
    {{
      "verdict": "Safe" | "Suspicious" | "Likely Scam",
      "reason": "A brief explanation extracted from the paragraph."
    }}

    Only use the given paragraph — do not invent new insights.

    ---
    Seller Analysis Paragraph:
    {paragraph}
    """
    response = model.generate_content(prompt)
    return response.text
