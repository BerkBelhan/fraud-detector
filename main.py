from backend.scraper.product_comments import launch_driver as launch_product_driver
from backend.scraper.product_comments import navigate_to_full_comments, extract_product_reviews

from backend.scraper.seller import launch_driver as launch_seller_driver
from backend.scraper.seller import get_seller_url_from_product, fetch_seller_reviews, extract_seller_info_and_reviews

from backend.agents.investigators.product_investigator import evaluate_product_comments
from backend.agents.investigators.seller_investigator import evaluate_seller_comments
from backend.agents.investigators.final_verdict_agent import evaluate_overall_verdict

from backend.agents.controllers.product_controller import classify_product_analysis
from backend.agents.controllers.seller_controller import classify_seller_analysis


def run_product_analysis(product_url):
    driver = launch_product_driver()
    success = navigate_to_full_comments(driver, product_url)
    if not success:
        driver.quit()
        return None, "❌ Product review extraction failed."

    data = extract_product_reviews(driver)
    driver.quit()

    comments = data["comments"]
    feedback = evaluate_product_comments(comments)

    ##added below 2 
    product_classification = classify_product_analysis(feedback)
    print(f"Product Classification: {product_classification}")
    return feedback, data


def run_seller_analysis(product_url):
    driver = launch_seller_driver()
    seller_url = get_seller_url_from_product(driver, product_url)
    if not seller_url:
        driver.quit()
        return None, "❌ Seller extraction failed."

    if not fetch_seller_reviews(driver, seller_url):
        driver.quit()
        return None, "❌ Seller review page navigation failed."

    seller_data = extract_seller_info_and_reviews(driver)
    driver.quit()

    comments = seller_data["reviews"]
    feedback = evaluate_seller_comments(comments)

    ##added below 2
    seller_classification = classify_seller_analysis(feedback)
    print(f"Seller Classification: {seller_classification}")
    return feedback, seller_data


if __name__ == "__main__":
    product_url = input("🔗 Enter Trendyol PRODUCT URL: ").strip()

    print("\n🔍 Running Product Review Evaluation...")
    product_feedback, product_data = run_product_analysis(product_url)
    if isinstance(product_feedback, str):
        print(product_feedback)
    else:
        print(f"\n🧠 Gemini Product Agent Feedback:\n{product_feedback}")

    print("\n🔍 Running Seller Review Evaluation...")
    seller_feedback, seller_data = run_seller_analysis(product_url)
    if isinstance(seller_feedback, str):
        print(seller_feedback)
    else:
        print(f"\n🧠 Gemini Seller Agent Feedback:\n{seller_feedback}")

    if isinstance(product_feedback, dict) and isinstance(seller_feedback, dict):
        print("\n🔍 Running Final Verdict Evaluation...")
        overall_result = evaluate_overall_verdict(product_feedback, seller_feedback)
        print(f"\n🚦 Final Verdict: {overall_result['final_verdict']}")
        print(f"📌 Reason: {overall_result['reason']}")