# C:\SENG472\MainProje\fraud-detector\backend\pipeliner.py

from backend.scraper.scraper_pipeline import scrape_all_info
from backend.agents.investigators.reviews_investigator import evaluate_product_comments
from backend.agents.investigators.seller_investigator import evaluate_seller_info
from backend.agents.investigators.description_investigator import evaluate_product_description
from backend.agents.controllers.product_controller import classify_product_analysis
from backend.agents.controllers.seller_controller import classify_seller_analysis
from backend.agents.final_judge import final_verdict_with_reasoning


def run_analysis_pipeline(product_url):
    # Step 1: Scrape all data
    all_data = scrape_all_info(product_url)

    product_comments = all_data["reviews"]
    seller_info = all_data["seller"]
    questions = all_data["questions"]
    description = all_data["description"]

    # Step 2: Investigators (pass directly to the functions)
    product_paragraph = evaluate_product_comments(product_comments)
    seller_paragraph = evaluate_seller_info(seller_info)
    description_paragraph = evaluate_product_description(description)


    # Step 3: Controllers
    #product_json = classify_product_analysis(product_paragraph)
    #seller_json = classify_seller_analysis(seller_paragraph)

    # Step 4: Final Judge
    final_output = final_verdict_with_reasoning(product_paragraph, seller_paragraph, description_paragraph)

    # Return final output and a dictionary of all intermediate steps for debugging
    return final_output, {
        "Product Comments": product_comments,
        "Seller Info": seller_info,
        "Product Paragraph": product_paragraph,
        "Seller Paragraph": seller_paragraph,
        "Product JSON": dict(),
        "Seller JSON": dict(),
        "Description Info": all_data["description"] 
    }