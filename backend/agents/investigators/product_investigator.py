# C:\SENG472\MainProje\fraud-detector\backend\agents\investigators\product_investigator.py

import google.generativeai as genai
import json
from backend.utils.gemini_utils import model # Using the shared model instance

class ProductReviewInvestigator:
    """
    An agent that performs a detailed analysis of product reviews and returns a structured JSON verdict.
    It now acts as both the investigator and controller for product reviews.
    """
    def __init__(self, model_name="gemini-1.5-flash-latest"):
        """
        Initializes the agent with a specific Gemini model configured for JSON output.
        """
        try:
            self.generation_config = genai.GenerationConfig(response_mime_type="application/json")
            self.model = genai.GenerativeModel(
                model_name,
                generation_config=self.generation_config
            )
        except Exception as e:
            print(f"❌ Failed to initialize ProductReviewInvestigator: {e}")
            # Fallback to the globally defined model if specific initialization fails
            self.model = model
            print("✅ Falling back to global model instance.")

    def evaluate_reviews(self, reviews: list[str]) -> dict:
        """
        Evaluates a list of product reviews based on a detailed multi-path prompt.
        """
        if not reviews:
            return {"verdict": "Warning", "reason": "No reviews were provided for analysis.", "score": 50}

        # Flatten the list of reviews, as the scraper provides nested data
        flat_comments = []
        for item in reviews:
            if isinstance(item, list):
                flat_comments.extend(item)
            elif isinstance(item, str):
                flat_comments.append(item)
        
        # We only need the actual comments, not the rating/count headers for the AI
        actual_comments = [c for c in flat_comments if not c.replace('.','',1).isdigit() and len(c) > 10]

        if not actual_comments:
            return {"verdict": "Warning", "reason": "Review data was present, but no actual comment text could be extracted for analysis.", "score": 40}

        prompt = f"""
        You are an expert e-commerce fraud detection agent. Your goal is to determine if a product is "Safe", "Suspicious", or a "Likely Scam" based on the provided reviews.

        Follow these steps precisely:
        1.  **Review Analysis**: Analyze the reviews provided in the "Real Reviews to Analyze" section.
        2.  **Verdict Determination**: Based on your analysis, choose a verdict: "Safe", "Suspicious", or "Likely Scam".
        3.  **Reasoning**: Write a 1-2 sentence summary explaining the key factors that led to your verdict.
        4.  **Scoring**: Provide a numerical trustworthiness score from 0 (definite scam) to 100 (perfectly safe).

        CRITERIA:
        - **Safe**: Mostly positive, genuine-sounding reviews. Minor or subjective complaints are acceptable. Score: 75-100.
        - **Suspicious**: A mix of very positive and very negative reviews (polarized). Presence of potentially fake reviews (e.g., repetitive, generic praise). Multiple credible complaints about quality or misrepresentation. Score: 25-74.
        - **Likely Scam**: Numerous, credible reports of non-delivery, receiving fake items, or serious safety issues. Score: 0-24.

        OUTPUT FORMAT:
        You must return your analysis *only* in the following JSON format:
        {{
          "verdict": "...",
          "reason": "...",
          "score": ...
        }}

        ---
        Real Reviews to Analyze:
        ---
        {" ".join(actual_comments)}
        ---
        """
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            if not all(k in result for k in ["verdict", "reason", "score"]):
                raise KeyError("Response missing required keys.")
            
            return result
        except Exception as e:
            print(f"An error occurred during product review AI call: {e}")
            return {"verdict": "Error", "reason": f"Failed to get a valid analysis from the AI model. Error: {e}", "score": 0}