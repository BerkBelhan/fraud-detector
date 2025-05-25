from backend.scraper.product_comments import launch_driver as launch_product_driver
from backend.scraper.product_comments import navigate_to_full_comments, extract_product_reviews

from backend.scraper.seller import launch_driver as launch_seller_driver
from backend.scraper.seller import get_seller_url_from_product, fetch_seller_reviews, extract_seller_info_and_reviews

from backend.agents.investigators.comment_Investigator import evaluate_comments

from backend.agents.investigators.rating_investigator import evaluate_ratings


from backend.agents.controllers.seller_controller import seller_investigator_controller

from backend.agents.controllers.rating_controller import controller_agent as rating_controller_agent
from backend.agents.finalJudge import evaluate_overall_verdict as final_judge_agent


def run_product_analysis(product_url):
    driver = launch_product_driver()
    success = navigate_to_full_comments(driver, product_url)
    if not success:
        driver.quit()
        return None, "❌ Product review extraction failed."

    data = extract_product_reviews(driver)
    driver.quit()

    comments = data["comments"]
    feedback = evaluate_comments(comments)
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
    feedback = seller_investigator_controller(comments)
    return feedback, seller_data

def run_ratings_analysis(product_url):
    driver = launch_seller_driver()
    seller_url = get_seller_url_from_product(driver, product_url)
    if not seller_url:
        driver.quit()
        return None, "❌ Ratings extraction failed."

    if not fetch_seller_reviews(driver, seller_url):
        driver.quit()
        return None, "❌ Seller ratings navigation failed."

    seller_data = extract_seller_info_and_reviews(driver)
    driver.quit()

    comments = seller_data["reviews"]
    product_rating_count = seller_data.get("product_rating_count", 0)
    seller_rating = seller_data.get("seller_rating", 0)
    seller_rating_count = seller_data.get("seller_rating_count", 0)

    feedback = evaluate_ratings(comments, product_rating_count, seller_rating, seller_rating_count)
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

    """
    print("\n🔍 Running Ratings Evaluation...")
    ratings_investigator_feedback, ratings_data = run_ratings_analysis(product_url)

    if isinstance(ratings_investigator_feedback, str):
        print(ratings_investigator_feedback)
        ratings_final_feedback = None
    else:
        # Extract ratings info from seller_data or product_data as needed
        product_rating = ratings_data.get("product_rating", 0)
        product_rating_count = ratings_data.get("product_rating_count", 0)
        seller_rating = ratings_data.get("seller_rating", 0)
        seller_rating_count = ratings_data.get("seller_rating_count", 0)

    # Run controller on investigator output
    ratings_final_feedback = rating_controller_agent(
        product_rating=product_rating,
        product_rating_count=product_rating_count,
        seller_rating=seller_rating,
        seller_rating_count=seller_rating_count,
        r_investigator_output=ratings_investigator_feedback,
        
    )

    # Convert controller response to dict if JSON or structured string
    import json
    try:
        ratings_feedback = json.loads(ratings_final_feedback)
    except Exception as e:
        print("Failed to parse controller feedback:", e)
        ratings_feedback = None

    print(f"\n🧠 Gemini Ratings Controller Feedback:\n{ratings_feedback}")
    """



    # Collect all agent outputs in a dict
    agent_outputs = {}

    # Assuming product_feedback and seller_feedback are dicts that contain 'confidence' or similar
    if isinstance(product_feedback, dict) and "confidence" in product_feedback:
        agent_outputs["product_agent"] = product_feedback["confidence"]
    if isinstance(seller_feedback, dict) and "confidence" in seller_feedback:
        agent_outputs["seller_agent"] = seller_feedback["confidence"]
    #if isinstance(ratings_feedback, dict) and "confidence" in ratings_feedback:
    #agent_outputs["ratings_agent"] = ratings_feedback["confidence"]

    REQUIRED_SIZE = 2
    if len(agent_outputs) >= REQUIRED_SIZE:
        # Once you have enough agents' outputs, call the final judge
        final_result = final_judge_agent(agent_outputs)
        print(f"\n🚦 Final Verdict: {final_result['verdict']}")
        print(f"📌 Reason: {final_result['reason']}")
        print(f"🔍 Agent Outputs: {agent_outputs}")
        #sys.exit(0)
    else:
        print(f"\n⚠️ Waiting for more agents... Current: {len(agent_outputs)}, Required: {REQUIRED_SIZE}")
