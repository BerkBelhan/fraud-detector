from backend.utils.gemini_utils import model

#   SCORE EKLENECEK JSON A "score": "A numerical score from 0 to 100 indicating trustworthiness."
def classify_product_analysis(paragraph):
    """
    Given a paragraph analysis from product_investigator, classify the product's trust level.
    Return a JSON verdict and short reason.
    """
    prompt = f"""
    You are a controller agent for e-commerce fraud detection.

    Given the following paragraph analysis of product reviews, classify the product as:
    - "Safe" if the product has mostly positive reviews with minor complaints.
    - "Suspicious" if there are repeated complaints, but not enough to confirm a scam.
    - "Likely Scam" if many users report serious issues like fake items, refund refusal, or safety hazards.

    Your job is to convert this paragraph into the following JSON format:
    {{
      "verdict": "Safe" | "Suspicious" | "Likely Scam",
      "reason": "A short, clear summary (1-2 sentences) extracted from the analysis."
    }}
    

    Do not make up information. Just summarize and classify based on what is actually said.

    --- 
    Investigator Paragraph:
    {paragraph}
    """
    response = model.generate_content(prompt)
    return response.text
