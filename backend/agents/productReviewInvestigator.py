# productReviewInvestigator.py (Version 2.0 - Refined for Robustness)

import google.generativeai as genai
import os
import json

# --- Configuration & Security ---
# As per SRS security requirement 3.2, API keys are stored securely in environment
# variables and not in the code itself[cite: 52].
try:
    from dotenv import load_dotenv
    load_dotenv() # Loads variables from a .env file into the environment
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment.")
    genai.configure(api_key=GOOGLE_API_KEY)
except (ImportError, ValueError) as e:
    print(f"CRITICAL ERROR: {e}")
    print("Please ensure you have a .env file in the same directory with the line: GOOGLE_API_KEY='YOUR_API_KEY'")
    exit() # Exit if the API key is not configured


# --- Agent Definition ---

class ProductReviewInvestigator:
    """
    An agent that specializes in analyzing product reviews to detect signs of fraud.
    It uses Gemini with a guaranteed JSON output for reliable, structured analysis,
    aligning with the multi-agent system architecture[cite: 22, 69].
    """

    def __init__(self, model_name="gemini-1.5-flash-latest"):
        """
        Initializes the agent and configures the generative model for JSON output.
        """
        # This configuration forces the model to output a response in the JSON MIME type.
        # This is more reliable than asking for JSON in the prompt.
        self.generation_config = genai.GenerationConfig(response_mime_type="application/json")
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=self.generation_config
        )
        print(f"✅ ProductReviewInvestigator initialized with model '{model_name}' and JSON output mode.")

    def evaluate_reviews(self, reviews: list[str]) -> dict:
        """
        Analyzes a list of product reviews and returns a structured JSON analysis.

        Args:
            reviews: A list of strings, where each string is a customer review.

        Returns:
            A dictionary with the verdict and a brief explanation, or an error message.
        """
        if not reviews:
            return {"verdict": "Safe", "reason": "No reviews were provided for analysis."}

        # The prompt focuses on the analytical task. The model's configuration
        # handles the JSON formatting automatically.
       # Inside the evaluate_reviews method in productReviewInvestigator.py

     # In productReviewInvestigator.py, replace the whole prompt with this one.

        prompt = f"""
        You are an expert e-commerce fraud detection agent specializing in analyzing Turkish or English product reviews. Your task is to analyze the following user comments and decide if the product is a scam, suspicious, or safe.

        ---
        ### Good Example (Safe Verdict)
        Reviews: "ürün harika alın aldırın. çok beğendim. kargo da hızlıydı."
        Reasoning: These are common, enthusiastic Turkish phrases. While short, they are typical of real users and not inherently suspicious.
        ---
        ### Bad Example (Suspicious Verdict)
        Reviews: "Great product buy now. Fast shipping good quality. Amazing item works perfect."
        Reasoning: These reviews are generic, use oddly structured English, and appear robotic, suggesting they are likely fake or bot-generated.
        ---

        Based on these examples, perform your analysis on the following real reviews. Be very careful not to misinterpret common Turkish enthusiasm as spam.

        Real Reviews to Analyze:
        ---
        {" ".join(reviews)}
        ---

        Return your final analysis ONLY as a JSON object with two keys: "verdict" (either "Safe", "Suspicious", or "Likely Scam") and "reason".
        """
        try:
            response = self.model.generate_content(prompt)
            
            # The API guarantees the response.text is a valid JSON string,
            # so we can parse it directly without manual cleaning.
            result = json.loads(response.text)

            # Additional validation to ensure the JSON contains the keys we need.
            if "verdict" not in result or "reason" not in result:
                raise KeyError("The model's JSON response is missing 'verdict' or 'reason' key.")
            
            return result

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing model output: {e}")
            return {"verdict": "Error", "reason": f"Failed to get a valid analysis. Error: {e}"}
        except Exception as e:
            print(f"An unexpected error occurred during the API call: {e}")
            return {"verdict": "Error", "reason": "An unexpected error occurred."}

# --- Example Usage (for testing the agent independently) ---
if __name__ == "__main__":
    # Initialize the investigator agent
    review_agent = ProductReviewInvestigator()

    # --- Test Case 1: Suspicious Reviews (Generic and repetitive) ---
    print("\n--- Testing with Suspicious Reviews ---")
    suspicious_reviews = [
        "Wow, great product, 5 stars!",
        "Excellent purchase, would buy again. A++",
        "Very good quality, just as described. Perfect.",
        "I love it! Amazing product, highly recommend to everyone.",
    ]
    analysis_suspicious = review_agent.evaluate_reviews(suspicious_reviews)
    print(json.dumps(analysis_suspicious, indent=2))

    # --- Test Case 2: Legit Reviews (Detailed and balanced) ---
    print("\n--- Testing with Legit-Looking Reviews ---")
    legit_reviews = [
        "The shipping was faster than expected. The t-shirt's fabric is soft, but it runs a bit smaller than the size chart suggested. I'd recommend ordering one size up.",
        "I've been using this coffee maker for about two weeks. It brews quickly and is easy to clean. My only complaint is that the power cord is a little short.",
    ]
    analysis_legit = review_agent.evaluate_reviews(legit_reviews)
    print(json.dumps(analysis_legit, indent=2))

    # --- Test Case 3: Scam-Indicating Reviews (Clear red flags) ---
    print("\n--- Testing with Scam-Indicating Reviews ---")
    scam_reviews = [
        "Total scam. Never received the item and the seller won't respond to my messages.",
        "This is a piece of junk. It looks nothing like the picture and broke the first day.",
    ]
    analysis_scam = review_agent.evaluate_reviews(scam_reviews)
    print(json.dumps(analysis_scam, indent=2))