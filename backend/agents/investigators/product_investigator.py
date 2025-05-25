# C:\SENG472\MainProje\fraud-detector\backend\agents\investigators\product_investigator.py

import google.generativeai as genai
import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file or environment.")
    genai.configure(api_key=GOOGLE_API_KEY)
except (ImportError, ValueError) as e:
    print(f"CRITICAL ERROR: {e}")
    exit()

class ProductReviewInvestigator:
    """
    An agent that specializes in analyzing product reviews to detect signs of fraud.
    """

    def __init__(self, model_name="gemini-1.5-flash-latest"):
        self.generation_config = genai.GenerationConfig(response_mime_type="application/json")
        self.model = genai.GenerativeModel(
            model_name,
            generation_config=self.generation_config
        )
        # print(f"✅ ProductReviewInvestigator initialized with model '{model_name}' and JSON output mode.") # You can uncomment for terminal debugging

    def evaluate_reviews(self, reviews: list[str]) -> dict:
        if not reviews: # This is a Python-level check. If the list is truly empty.
            return {"verdict": "Safe", "reason": "No reviews were provided to the Python function."}
        
        # --- Critical f-string formatting ---
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
        {" ".join(reviews)}
        ---
        *SECTION 6: OUTPUT FORMAT AND JUSTIFICATION*
        Return analysis as JSON: {{"verdict": "...", "reason": "..."}}.
        * *If you followed PATH A, B, or C (due to 0, 1, or 2 reviews):* Your reason MUST explicitly state that the analysis was based on this specific low number of reviews, detail the nature of those reviews (Positive, N1, N2, N3), and how that directly led to the verdict as per the instructions in Section 0 for that Path. Do not refer to review majorities, percentages applicable to larger sets, or patterns from Section 1.
        * *If you followed PATH D (3 or more reviews):* Your reason MUST explicitly state how positive patterns, Authenticity Flags (A-D), and the proportion/severity of Negative Review Categories (N1, N2, N3) influenced the verdict, detailing the balance of evidence.
        """
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text) # Gemini is configured for JSON output
            if "verdict" not in result or "reason" not in result:
                raise KeyError("The model's JSON response is missing 'verdict' or 'reason' key.")
            
            valid_verdicts = ["Safe", "Suspicious", "Likely Scam", "Error"]
            if result.get("verdict") not in valid_verdicts:
                print(f"Warning: Model returned an unexpected verdict: {result.get('verdict')}.")
                return {"verdict": "Suspicious", "reason": f"Model returned an invalid verdict. Please review manually."}
            return result
        except Exception as e:
            print(f"An unexpected error occurred during product review AI call: {e}")
            return {"verdict": "Error", "reason": f"Failed to get a valid analysis from the AI model. Error: {e}"}