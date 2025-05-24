import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Loads .env

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def evaluate_ratings(product_rating, product_rating_count, seller_rating, seller_rating_count):
    prompt = f"""
You are an e-commerce fraud detection agent.

Evaluate the trustworthiness of a product and its seller based on the following rating metrics:

- A high rating with a **very low number of ratings** could be suspicious (possibly manipulated).
- A low rating with **many reviews** indicates poor quality or service.
- Don't rely solely on the number of reviews; consider the **balance** between product and seller ratings.
- A product with a relatively low number of reviews may still be trustworthy if the seller hasn't received many complaints.
- Balanced ratings (e.g., 4.2/5 from 30+ users) are typically more trustworthy.
- Be cautious of both extremes and look for patterns that may suggest fraud, such as:
  - New sellers with perfect scores but few reviews
  - Products with high ratings but lots of complaints in comments
  - Large gaps between seller and product ratings

Be fair but cautious. Give a reasoned judgment.

Return your output in this JSON format:
{{
  "verdict": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "short explanation here"
}}

Data:
- Product Rating: {product_rating} stars from {product_rating_count} reviews
- Seller Rating: {seller_rating} stars from {seller_rating_count} reviews
"""

    response = model.generate_content(prompt)
    return response.text

print(evaluate_ratings(
    product_rating=4.8,
    product_rating_count=750,
    seller_rating=4.9,
    seller_rating_count=2600
))

