import json
import re
from eksi import get_social_sentiment_eksi
from crawl4ai_agent import Crawl4AIAgent
from akakce_scraper import scrape_prices
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ────────────────────────────────────────────────────────────────
# Utility Functions
# ────────────────────────────────────────────────────────────────

def extract_json_from_gemini_response(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        print("❌ Could not extract JSON from Gemini response.")
        print(text)
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        print("↪ Extracted:", match.group(0))
        return None

# ────────────────────────────────────────────────────────────────
# Individual Agents
# ────────────────────────────────────────────────────────────────

def evaluate_with_comments(comments):
    joined = "\n".join(comments)
    prompt = f"""
You are a scam detection agent.

You are given user comments about a seller. Your job is to **analyze whether the seller appears to be a scam** (e.g., fake products, bait-and-switch, misleading listings, no delivery).

💡 Important:
- Do **not** treat negative cargo/delivery delays alone as scam signals.
- If comments are mostly about shipping or delivery time, state that **the seller is likely not a scam**, but **mention the cargo problems** in your reason.

Respond in this format:
{{
  "level": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "..."
}}

User comments:
\"\"\"{joined}\"\"\"
"""
    response = model.generate_content(prompt)
    return extract_json_from_gemini_response(response.text)

def evaluate_with_price_gap(product_price, akakce_prices):
    prompt = f"""
You are a scam detection agent.

Compare this product's price with similar listings. You're checking for suspicious pricing behaviors.

🔍 Guidelines:
- Only treat large price gaps as scam signals **if the seller is unknown or suspicious**.
- For **fashion items** (e.g., şort, t-shirt, hırka, kaban, sweatshirt), ignore price differences **unless**:
  - The item costs more than 10,000 TL, **and**
  - The seller has no reliable reputation.
- Focus on **unreasonably low prices**, not just high ones.



Product price: {product_price}

Other prices:
{json.dumps(akakce_prices, indent=2, ensure_ascii=False)}

Return a JSON verdict like:
{{
  "level": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "..."
}}
"""
    response = model.generate_content(prompt)
    return extract_json_from_gemini_response(response.text)

def combine_verdicts(comment_verdict, price_verdict):
    prompt = f"""
You are a final fraud detection agent.

You are given:
1. A sentiment-based verdict about the seller
2. A price-based verdict about the product

🎯 Your goal is to decide if the listing is truly a scam.

⚖️ Judgment Policy:
- **Give higher weight to user comments.**
- If users describe the seller as trustworthy, **do not mark as scam** even if there's a price difference.
- **Do not penalize fashion products** (like şort, kaban, elbise, sweatshirt) for price gaps unless the product is expensive (>10.000 TL) AND seller has red flags.
- If cargo/shipping delays are mentioned, **they are NOT scam indicators**.

Respond in JSON:
{{
  "final_level": "Safe" | "Suspicious" | "Likely Scam",
  "summary_reason": "..."
}}


1. User Comment Verdict:
{json.dumps(comment_verdict, indent=2, ensure_ascii=False)}

2. Price Comparison Verdict:
{json.dumps(price_verdict, indent=2, ensure_ascii=False)}

Based on both, return a final risk verdict in JSON:
{{
  "final_level": "Safe" | "Suspicious" | "Likely Scam",
  "summary_reason": "..."
}}
"""
    response = model.generate_content(prompt)
    return extract_json_from_gemini_response(response.text)

# ────────────────────────────────────────────────────────────────
# Main Pipeline
# ────────────────────────────────────────────────────────────────

def main():
    url = input("🔗 Enter product URL: ").strip()
    agent = Crawl4AIAgent(url)

    if not agent.fetch_html() or not agent.extract_visible_text():
        print("❌ Failed to extract product info.")
        return

    print("🧠 Extracting product info and search queries...")
    product_raw = agent.extract_product_info()

    data = extract_json_from_gemini_response(product_raw)
    if not data:
        return

    title = data.get("title")
    price = data.get("price")
    seller = data.get("merchant")
    akakce_query = data.get("akakce_query")
    eksi_query = data.get("eksi_query")

    print(f"\n🧠 Title: {title}\n💰 Price: {price}\n🏬 Seller: {seller}")
    print(f"🔎 Ekşi Query: {eksi_query}\n🔍 Akakçe Query: {akakce_query}\n")

    # 🗣 Evaluate Ekşi comments
    comments = get_social_sentiment_eksi(eksi_query, limit=5)
    if comments:
        print("🗣️ Evaluating Ekşi Sözlük sentiment...\n")
        comment_verdict = evaluate_with_comments(comments)
    else:
        comment_verdict = {
            "level": "Unknown",
            "reason": "No user comments found on Ekşi Sözlük."
        }

    # 💰 Evaluate price comparison
    print("💰 Checking Akakçe for price comparison...\n")
    akakce_data = scrape_prices(akakce_query, limit=5, headless=True)
    price_verdict = evaluate_with_price_gap(price, akakce_data)

    # 🧠 Final decision agent
    final_verdict = combine_verdicts(comment_verdict, price_verdict)

    print("\n📣 Final Scam Verdict:\n", json.dumps(final_verdict, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
