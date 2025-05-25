import sys
import os
import json

# This ensures the script can find the 'backend' module
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- All Backend Imports ---
from backend.scraper.product_comments import launch_driver as launch_product_driver, navigate_to_full_comments, extract_product_reviews
from backend.scraper.seller import launch_driver as launch_seller_driver, get_seller_url_from_product, fetch_seller_reviews, extract_seller_info_and_reviews
# --- FIX: Import the CLASS, not the non-existent function ---
from backend.agents.investigators.product_investigator import ProductReviewInvestigator
from backend.agents.investigators.seller_investigator import evaluate_seller_comments
# from backend.agents.investigators.final_verdict_agent import evaluate_overall_verdict # Disabled
from backend.agents.controllers.product_controller import classify_product_analysis
from backend.agents.controllers.seller_controller import classify_seller_analysis


def run_product_analysis(product_url, product_agent):
    """Runs the full product analysis using the provided agent instance."""
    print("--- 1. PRODUCT ANALYSIS ---")
    driver = launch_product_driver()
    success = navigate_to_full_comments(driver, product_url)
    if not success:
        driver.quit()
        return "❌ Product review extraction failed."

    data = extract_product_reviews(driver)
    driver.quit()

    comments = data.get("comments", [])
    if not comments:
        return {"verdict": "Warning", "reason": "Scraper could not find any product comments."}

    # --- FIX: Call the correct method on the agent instance ---
    feedback = product_agent.evaluate_reviews(comments)
    
    # Pass the dictionary to the controller
    classified_feedback = classify_product_analysis(feedback)
    return classified_feedback


def run_seller_analysis(product_url):
    """Runs the full seller analysis."""
    print("\n--- 2. SELLER ANALYSIS ---")
    driver = launch_seller_driver()
    seller_url = get_seller_url_from_product(driver, product_url)
    if not seller_url:
        driver.quit()
        return "❌ Seller URL extraction failed."

    if not fetch_seller_reviews(driver, seller_url):
        driver.quit()
        return "❌ Seller review page navigation failed."

    seller_data = extract_seller_info_and_reviews(driver)
    driver.quit()
    
    comments = seller_data.get("reviews", [])
    if not comments:
        return {"verdict": "Warning", "reason": "Scraper could not find any seller comments."}

    feedback = evaluate_seller_comments(comments)
    classified_feedback = classify_seller_analysis(feedback)
    return classified_feedback


if __name__ == "__main__":
    # --- FIX: Initialize the agent once at the start ---
    print("Initializing AI agents...")
    product_review_agent = ProductReviewInvestigator()
    print("-" * 30)

    product_url = input("🔗 Enter Trendyol PRODUCT URL: ").strip()

    # Run Product Analysis
    product_result = run_product_analysis(product_url, product_review_agent)
    print("\n🧠 Product Agent Final Result:")
    # Use json.dumps for pretty printing the dictionary
    print(json.dumps(product_result, indent=2, ensure_ascii=False))

    # Run Seller Analysis
    seller_result = run_seller_analysis(product_url)
    print("\n🧠 Seller Agent Final Result:")
    print(json.dumps(seller_result, indent=2, ensure_ascii=False))
    
    # Final verdict logic would go here once the agent is ready
    # print("\n--- 3. FINAL VERDICT (DISABLED) ---")
    # if isinstance(product_result, dict) and isinstance(seller_result, dict):
    #     overall_result = evaluate_overall_verdict(product_result, seller_result)
    #     print(f"\n🚦 Final Verdict: {overall_result['final_verdict']}")
    #     print(f"📌 Reason: {overall_result['reason']}")