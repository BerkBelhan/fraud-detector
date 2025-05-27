# nottrendyol/fraud_pipeline.py
import json
import re
import os
from dotenv import load_dotenv
from .eksi import get_social_sentiment_eksi
from .crawl4ai_agent import Crawl4AIAgent
from .akakce_scraper import scrape_prices
import google.generativeai as genai

# --- CONFIGURATION (Ensure this uses GOOGLE_API_KEY for consistency if possible) ---
load_dotenv()
# Consider standardizing your API key name across the project, e.g., GOOGLE_API_KEY
API_KEY = os.getenv("GOOGLE_API_KEY") # Or GOOGLE_API_KEY if you standardize
if not API_KEY:
    raise ValueError("API key for nottrendyol pipeline not found. Please set GEMINI_API_KEY (or GOOGLE_API_KEY if standardized).")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash") # Using a consistent model name

INPUT_COST_PER_M = 0.035
OUTPUT_COST_PER_M = 0.070
total_cost_usd = 0.0

# --- HELPER FUNCTIONS ---
def compute_cost(input_tokens, output_tokens):
    return round(
        (input_tokens * INPUT_COST_PER_M + output_tokens * OUTPUT_COST_PER_M) / 1_000_000,
        6
    )

def run_gemini_agent(label, prompt):
    global total_cost_usd
    response = model.generate_content(prompt)
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count
    output_tokens = usage.candidates_token_count
    cost = compute_cost(input_tokens, output_tokens)
    total_cost_usd += cost
    print(f"🧾 (External Pipeline) Gemini Agent: {label} - Cost: ${cost:.6f}") # Kept for console logging
    return response.text

def extract_json_from_gemini_response(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        print(f"❌ (External Pipeline) Could not extract JSON from Gemini response: {text[:300]}...")
        return {"level": "Error", "reason": "Could not extract JSON structure from AI response."}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print(f"❌ (External Pipeline) JSON parsing failed: {e}")
        print(f"↪ Extracted: {match.group(0)}")
        return {"level": "Error", "reason": f"AI response was not valid JSON: {match.group(0)[:100]}..."}

# --- GEMINI AGENT WRAPPERS (Unchanged, they return dicts) ---
def evaluate_with_comments(comments):
    joined = "\n".join(comments)
    prompt = f"""
You are a scam detection agent.
You are given user comments about a seller. Your job is to analyze whether the seller appears to be a scam (e.g., fake products, bait-and-switch, misleading listings, no delivery).
💡 Important:
- Do not treat negative cargo/delivery delays alone as scam signals.
- If comments are mostly about shipping or delivery time, state that the seller is likely not a scam, but mention the cargo problems in your reason.
Respond in this format:
{{
  "level": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "..."
}}
User comments:
\"\"\"{joined}\"\"\"
"""
    text = run_gemini_agent("evaluate_with_comments", prompt)
    return extract_json_from_gemini_response(text)

def evaluate_with_price_gap(product_price, akakce_prices):
    prompt = f"""
You are a scam detection agent.
Compare this product's price with similar listings. You're checking for suspicious pricing behaviors.
🔍 Guidelines:
- Only treat large price gaps as scam signals if the seller is unknown or suspicious.
- For fashion items (e.g., şort, t-shirt, hırka, kaban, sweatshirt), ignore price differences unless:
  - The item costs more than 10,000 TL, and
  - The seller has no reliable reputation.
- Focus on unreasonably low prices, not just high ones.
Product price: {product_price}
Other prices:
{json.dumps(akakce_prices, indent=2, ensure_ascii=False)}
Return a JSON verdict like:
{{
  "level": "Safe" | "Suspicious" | "Likely Scam",
  "reason": "..."
}}
"""
    text = run_gemini_agent("evaluate_with_price_gap", prompt)
    return extract_json_from_gemini_response(text)

def combine_verdicts(comment_verdict, price_verdict):
    prompt = f"""
You are a final fraud detection agent.
You are given:
1. A sentiment-based verdict about the seller
2. A price-based verdict about the product
🎯 Your goal is to decide if the listing is truly a scam.
⚖️ Judgment Policy:
- Give higher weight to user comments.
- If users describe the seller as trustworthy, do not mark as scam even if there's a price difference.
- Do not penalize fashion products (like şort, kaban, elbise, sweatshirt) for price gaps unless the product is expensive (>10.000 TL) AND seller has red flags.
- If cargo/shipping delays are mentioned, they are NOT scam indicators.
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
    text = run_gemini_agent("combine_verdicts", prompt)
    return extract_json_from_gemini_response(text)

# --- MAIN PIPELINE ---
def main(url=None):
    global total_cost_usd # Reset cost for each run
    total_cost_usd = 0.0

    if not url:
        # This part is for command-line execution, Streamlit will pass the URL
        url = input("🔗 Enter product URL: ").strip()
    
    results = {
        "product_title": "N/A",
        "product_price": "N/A",
        "seller_name": "N/A",
        "comment_verdict": {"level": "Error", "reason": "Pipeline did not complete."},
        "price_verdict": {"level": "Error", "reason": "Pipeline did not complete."},
        "final_verdict": {"final_level": "Error", "summary_reason": "Pipeline did not complete."},
        "api_cost": 0.0
    }

    agent = Crawl4AIAgent(url)
    if not agent.fetch_html() or not agent.extract_visible_text():
        results["final_verdict"]["summary_reason"] = "Failed to extract product info from URL."
        return results

    product_raw = agent.extract_product_info()
    data = extract_json_from_gemini_response(product_raw)
    if not data or data.get("level") == "Error":
        results["final_verdict"]["summary_reason"] = data.get("reason", "Failed to parse initial product data.") if data else "Failed to parse initial product data."
        return results

    results["product_title"] = data.get("title", "N/A")
    results["product_price"] = data.get("price", "N/A")
    results["seller_name"] = data.get("merchant", "N/A")
    akakce_query = data.get("akakce_query")
    eksi_query = data.get("eksi_query")

    comments = get_social_sentiment_eksi(eksi_query, limit=5)
    if comments:
        results["comment_verdict"] = evaluate_with_comments(comments)
    else:
        results["comment_verdict"] = {
            "level": "Unknown",
            "reason": "No user comments found on Ekşi Sözlük."
        }

    akakce_data = scrape_prices(akakce_query, limit=5, headless=True)
    results["price_verdict"] = evaluate_with_price_gap(results["product_price"], akakce_data)
    
    results["final_verdict"] = combine_verdicts(results["comment_verdict"], results["price_verdict"])
    results["api_cost"] = round(total_cost_usd, 6)
    
    # Instead of printing, we return the dictionary
    return results

if __name__ == "__main__":
    # This allows the script to still be run from the command line for testing
    run_results = main()
    print("\n📣 Final Scam Verdict (from command line):\n", json.dumps(run_results.get("final_verdict"), indent=2, ensure_ascii=False))
    print(f"\n💸 Total Gemini API Cost for this run: ${run_results.get('api_cost'):.6f}")