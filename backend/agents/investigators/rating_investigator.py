import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def evaluate_ratings(product_rating, product_rating_count, seller_rating, seller_rating_count):
    prompt = f"""
You are a senior fraud detection agent working in an e-commerce integrity unit. Your job is to assess the **trustworthiness** of a product listing and the associated seller based solely on their **numerical rating scores** and **rating counts**.

## Objective
Evaluate the **risk** or **suspicion** of manipulation, fraud, or artificial boosting based on discrepancies, imbalances, and contextual red flags. Deliver a **verdict** and a **concise, human-readable explanation** for your judgment. Your decision is advisory, but should lean toward **consumer protection** in unclear or borderline cases.

## Knowledge Base
You are aware of the following common fraud or manipulation patterns in e-commerce:

- **Ratings inflation:** Products or sellers with extremely high scores but very few reviews are often boosted using fake reviews or bots.
- **Asymmetric credibility:** A high-rated product paired with a poorly rated seller, or vice versa, signals inconsistency that may warrant skepticism.
- **Volume-weighted signals:** A 4.2/5 rating from 2,000 users is more reliable than a 4.9/5 from just 5.
- **New sellers with perfect metrics** are a common tactic used by scammers before they get caught.
- **Low product scores with high seller ratings** may mean fake or dropshipped items handled well logistically.
- **Seller ratings below 3.5** with hundreds of reviews are strong red flags.

## Behavioral Directives
- Be **cautiously skeptical** — lean toward consumer safety in ambiguous cases.
- Avoid overconfidence in any metric with insufficient data.
- Consider not just the raw rating, but the **trustworthiness of its volume**.
- Avoid false positives: Do not penalize genuinely small businesses with decent reviews.
- Be concise. Don't repeat the numbers back in your explanation — interpret them.

## Output Specification (Very Important)
Your final output **must strictly** follow this JSON structure with no deviations:

```json
{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "short, 1-2 sentence explanation of your judgment"
}}


Data:
- Product Rating: {product_rating} stars from {product_rating_count} reviews
- Seller Rating: {seller_rating} stars from {seller_rating_count} reviews
"""

    response = model.generate_content(prompt)
    return response.text


investigator_output = evaluate_ratings(
    product_rating=4.8,
    product_rating_count=1860,
    seller_rating=4.9,
    seller_rating_count=2600
)

#print(r_investigator_output)


