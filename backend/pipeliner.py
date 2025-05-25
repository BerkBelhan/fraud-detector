# C:\SENG472\MainProje\fraud-detector\backend\pipeliner.py

from backend.scraper.scraper_pipeline import scrape_all_info
from backend.agents.investigators.product_investigator import ProductReviewInvestigator # UPDATED
from backend.agents.investigators.seller_investigator import evaluate_seller_comments
# from backend.agents.controllers.product_controller import classify_product_analysis # REMOVED
from backend.agents.controllers.seller_controller import classify_seller_analysis
from backend.agents.final_judge import final_verdict_with_reasoning

# Instantiate the powerful investigator once
product_agent = ProductReviewInvestigator()

def run_analysis_pipeline(product_url):
    # Step 1: Scrape all data
    scraped_data = scrape_all_info(product_url)

    # Extract data for agents
    product_comments = scraped_data.get("reviews", [])
    seller_info = scraped_data.get("seller", {})

    # Step 2: Run Investigators
    # The new Product Investigator directly produces the JSON, making the controller redundant.
    product_json = product_agent.evaluate_reviews(product_comments)
    
    # The Seller Investigator still produces a paragraph for the controller
    seller_paragraph = evaluate_seller_comments(seller_info)
    seller_json = classify_seller_analysis(seller_paragraph)

    # Step 3: Final Judge
    final_output = final_verdict_with_reasoning(product_json, seller_json)

    # Return final output and a dictionary of all intermediate steps for debugging
    return final_output, {
        "Scraped Product Comments": product_comments,
        "Scraped Seller Info": seller_info,
        "Seller Investigator Paragraph": seller_paragraph,
        "Product Analysis JSON": product_json,
        "Seller Analysis JSON": seller_json,
        "Scraped Description Info": scraped_data.get("description", [])
    }