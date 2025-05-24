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

    def _init_(self, model_name="gemini-1.5-flash-latest"):
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
        Handles reviews in Turkish, English, or a mix of both.

        Args:
            reviews: A list of strings, where each string is a customer review.

        Returns:
            A dictionary with the verdict and a brief explanation, or an error message.
        """
        if not reviews:
            return {"verdict": "Safe", "reason": "No reviews were provided for analysis."}

        # productReviewInvestigator.py (Inside the evaluate_reviews method)

        # This refined prompt is optimized for handling both Turkish and English reviews,
        # including mixed-language inputs, with better nuance for Turkish enthusiastic patterns.
        # productReviewInvestigator.py (Inside the evaluate_reviews method)

        # REINFORCED PROMPT v3 - Extremely Directive for Turkish Enthusiasm
        # productReviewInvestigator.py (Inside the evaluate_reviews method)
        # productReviewInvestigator.py (Inside the evaluate_reviews method)

        # productReviewInvestigator.py (Inside the evaluate_reviews method)

        # PROMPT VERSION 4.3 - AGGRESSIVE FIX for Low Review Counts Hallucination
        prompt = f"""
        You are an expert e-commerce fraud detection agent. Your primary mission is to accurately assess product reviews. Your goal is to determine if the product/seller is "Safe", "Suspicious", or a "Likely Scam".

        *SECTION 0: CRITICAL FIRST STEP - DETERMINE REVIEW COUNT AND EXECUTE PATH*

        *Carefully examine the "Real Reviews to Analyze" section provided at the end of this entire prompt. Based ONLY on what you observe there, choose ONE of the following paths (A, B, C, or D) and follow its instructions precisely.*

        * *PATH A: No Reviews Provided*
            * If the "Real Reviews to Analyze" section is empty or clearly contains no actual review text:
                * Your verdict is "Error".
                * Your reason is "No reviews were provided for analysis."
                * *YOU MUST STOP HERE. Do not proceed to any other sections or paths. Output this verdict and reason immediately.*

        * *PATH B: Exactly One Review Provided*
            * If the "Real Reviews to Analyze" section visibly contains text for EXACTLY ONE review:
                * *DISREGARD ALL OTHER SECTIONS of this prompt (Sections 1, 2, 3, 4, and any examples in Section 5 that refer to multiple reviews). Your entire analysis will be based SOLELY on this single review and the categorization rules in Section 2.2 (Negative Review Content Analysis) provided further down, which you should refer to ONLY for N-category definitions.*
                * Categorize this SINGLE review as 'Positive' or, if negative, determine its N-Category (N1, N2, or N3) using the definitions from Section 2.2.
                * Based on this single review's categorization:
                    * If N1 (Scam-Indicative): Verdict="Likely Scam". Reason must cite specific N1 indicators from this one review.
                    * If N2 (Serious Quality/Misrepresentation): Verdict="Suspicious". Reason must cite specific N2 indicators from this one review.
                    * If N3 (Subjective/Minor): Verdict="Safe". Reason: "Based on a single review reporting only a minor issue (Category N3)."
                    * If Positive: Verdict="Safe". Reason: "Based on a single positive review."
                * *YOU MUST STOP HERE. Do not proceed to any other sections. Output the determined verdict and reason, ensuring the reason clearly states it's based on the analysis of only one review.*

        * *PATH C: Exactly Two Reviews Provided*
            * If the "Real Reviews to Analyze" section visibly contains text for EXACTLY TWO reviews:
                * *DISREGARD Sections 1, 3, 4, and any multi-review examples in Section 5. Your analysis is based SOLELY on these two reviews and Section 2.2 for N-category definitions.*
                * Analyze both reviews individually (categorize as Positive, N1, N2, N3 using definitions from Section 2.2).
                * If ANY review is N1: Verdict="Likely Scam".
                * If BOTH are N2 OR if one is N2 and the other is N1: Verdict="Suspicious" (or "Likely Scam" if N1 is present and N2 is severe).
                * If ONE is N2 and the other is Positive or N3: Verdict="Suspicious".
                * If BOTH are N3 OR (one N3 and one Positive) OR BOTH are Positive: Verdict="Safe".
                * Your reason must summarize the findings for these two reviews and justify the verdict accordingly.
                * *YOU MUST STOP HERE. Do not proceed to any other sections. Output the determined verdict and reason.*

        * *PATH D: Three or More Reviews Provided*
            * If the "Real Reviews to Analyze" section visibly contains text for THREE OR MORE distinct reviews:
                * *You are now on PATH D. You MUST proceed to and meticulously follow Sections 1, 2, 3, and 4. The examples in Section 5 are also relevant for this path.*

        ---
        *(THE FOLLOWING SECTIONS (1-5) APPLY ONLY IF YOU HAVE DETERMINED YOU ARE ON PATH D: Three or More Reviews, as per Section 0)*
        ---

        *SECTION 1: IDENTIFYING POSITIVE REVIEW PATTERNS (PATH D ONLY)*
        * *Turkish Enthusiastic Pattern:* Look for high volumes of reviews that are short, highly enthusiastic (using common Turkish praise like "harika," "süper," "çok beğendim," etc.), similar in phrasing, lack deep unique detail, and are overwhelmingly positive. If reviews are natural-sounding idiomatic Turkish, this pattern is generally a positive sign.
        * *Detailed Positive Reviews (Any Language):* Look for reviews with specific, credible positive details.

        *SECTION 2: IDENTIFYING RED FLAGS & ANALYZING NEGATIVE REVIEW CONTENT (Definitions in 2.2 are used by PATH B & C for categorization; all of Section 2 is used by PATH D)*

        *SUB-SECTION 2.1: REVIEW AUTHENTICITY & MANIPULATION FLAGS (Primarily for PATH D; can lead to "Suspicious")*
        * *Flag A (Verbatim Copies):* Multiple reviews are exact word-for-word copies (full sentences/longer).
        * *Flag B (Demonstrably Unnatural Phrasing):* Language used contains clear errors suggesting bot/poor translation.
        * *Flag C (Internal Contradictions/Nonsense in Positive-Seeming Reviews):* Praise mixed with illogical statements.
        * *Flag D (Highly Unusual Repetition of Unique/Complex Sentences):* Multiple reviews repeat the exact same unique, complex positive phrasing.

        *SUB-SECTION 2.2: NEGATIVE REVIEW CONTENT ANALYSIS (Severity-Based Categorization - Definitions used by PATHS B, C, and D)*
        Categorize all negative reviews.
        * *Category N1: Scam-Indicative Negative Reviews (High Severity)*
            * *Definition:* Credible, specific reviews alleging: Non-delivery + unresponsive seller; fakes/counterfeits; receiving completely different, low-value item; clear seller deception/fraudulent financial practices.
        * *Category N2: Serious Product Quality or Gross Misrepresentation Issues (Medium-High Severity)*
            * *Definition:* Credible reviews (pattern, not isolated) reporting: Product breaks quickly/non-functional (systemic poor manufacturing); grossly misrepresented core specs/features/materials.
        * *Category N3: Subjective Dissatisfaction, Minor Issues, or Isolated Defects (Low Severity)*
            * *Definition:* Reviews expressing: Subjective dislike; minor inconveniences (slight shipping delay, received okay); single, isolated defects; issues from user error.

        *SECTION 3: FINAL VERDICT DETERMINATION (PATH D ONLY)*
        The final verdict depends on the balance of positive evidence, authenticity flags, and the proportion/severity of categorized negative reviews.
        * *"Safe":* Positive reviews form a clear and substantial majority (>70-75%) AND appear genuine. NO N1 reviews. N2 reviews are a small, isolated minority (<10-15%) clearly outweighed. N3s don't negate positive majority. NO significant Flags A-D.
        * *"Suspicious":* Flags A-D present. Some credible N1 reviews exist (~5-25%). N2 reviews are a significant portion (~20-50% or a clear pattern), indicating consistently poor/misrepresented product (this includes "half N2 bad, half good"). High polarization. Excessively high N3s with weak positive sentiment.
        * *"Likely Scam":* N1 reviews are numerous, credible, and form a consistent pattern of fraud (>25-30% N1, or fewer if exceptionally severe/detailed).

        *SECTION 4: ENGLISH REVIEW NUANCE (PATH D ONLY, if reviews are English)*
        Be more critical of generic, repetitive positive English reviews. Apply N1-N3 and ratio analysis.

        *SECTION 5: EXAMPLES (Illustrative for PATH D; PATH B & C have their logic defined in Section 0)*
        (Ensure all examples here imply a context of 3+ reviews for PATH D)
        ### Example (PATH D): "Safe" (Turkish Enthusiasm + Minor N3 Negatives)
        Reviews: 10 reviews total. 8 positive Turkish ("harika"). 2 N3: "Kargo kutusu ezikti."
        Reasoning: 'Safe'. Substantial positive majority. N3s minor. No N1/N2 or Flags A-D.
        ---
        ### Example (PATH D): "Suspicious" (Half N2, Half Positive)
        Reviews: 10 reviews total. 5 positive. 5 specific N2s: "Ürün 3 gün sonra bozuldu."
        Reasoning: 'Suspicious'. 50% are N2, indicating serious quality/misrepresentation issues.
        ---
        (Other relevant examples for N1, Flags A-D for PATH D)

        ---
        *"Real Reviews to Analyze":*
        ---
        {{" ".join(reviews)}}
        ---

        *SECTION 6: OUTPUT FORMAT AND JUSTIFICATION*
        Return analysis as JSON: {{"verdict": "...", "reason": "..."}}.
        * *If you followed PATH A, B, or C (due to 0, 1, or 2 reviews):* Your reason MUST explicitly state that the analysis was based on this specific low number of reviews, detail the nature of those reviews (Positive, N1, N2, N3), and how that directly led to the verdict as per the instructions in Section 0 for that Path. Do not refer to review majorities, percentages applicable to larger sets, or patterns from Section 1.
        * *If you followed PATH D (3 or more reviews):* Your reason MUST explicitly state how positive patterns, Authenticity Flags (A-D), and the proportion/severity of Negative Review Categories (N1, N2, N3) influenced the verdict, detailing the balance of evidence.
        """
        try:
            response = self.model.generate_content(prompt)
            
            # The API guarantees the response.text is a valid JSON string,
            # so we can parse it directly without manual cleaning.
            result = json.loads(response.text)

            # Additional validation to ensure the JSON contains the keys we need.
            if "verdict" not in result or "reason" not in result:
                raise KeyError("The model's JSON response is missing 'verdict' or 'reason' key.")
            
            # Validate verdict value
            valid_verdicts = ["Safe", "Suspicious", "Likely Scam"]
            if result.get("verdict") not in valid_verdicts:
                print(f"Warning: Model returned an unexpected verdict: {result.get('verdict')}. Forcing to 'Suspicious'. Original reason: {result.get('reason')}")
                # Fallback or re-classification logic could be more sophisticated
                return {"verdict": "Suspicious", "reason": f"Model returned an invalid verdict ('{result.get('verdict')}'). Original reason: {result.get('reason')}. Please review manually."}

            return result

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing model output: {e}")
            return {"verdict": "Error", "reason": f"Failed to get a valid analysis. Error: {e}"}
        except Exception as e: # Catching more general google.generativeai.core.generation_types.BlockedPromptException or other API errors
            # It's good practice to log the full error for debugging
            # For example, using the logging module: logging.error(f"API call failed: {e}", exc_info=True)
            print(f"An unexpected error occurred during the API call or processing: {type(e)._name_} - {e}")
            # Check if the error has response parts that might indicate blocking
            error_details = "An unexpected error occurred."
            if hasattr(e, 'message'): # General exception message
                error_details = e.message
            
            # For Generative AI specific errors, sometimes they have more structured info
            # This part is a bit speculative as the exact error structure can vary.
            # If you're using response = self.model.generate_content(prompt), errors might be raised directly
            # or response.prompt_feedback might contain block reasons.
            # Since we are in an exception block for generate_content, we might not have a response object here in all cases.
            # However, some API errors might be caught by the generic Exception.
            
            # If the model's response itself indicated an issue (e.g. safety filters)
            # This would typically be checked on the 'response' object if the call didn't raise an exception.
            # For example: if response.prompt_feedback.block_reason:
            #    error_details = f"Content blocked due to: {response.prompt_feedback.block_reason}"

            return {"verdict": "Error", "reason": error_details}



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