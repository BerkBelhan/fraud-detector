from backend.scraper.scraper_pipeline import scrape_all_info
from backend.agents.investigators.product_investigator import evaluate_product_comments
from backend.agents.investigators.seller_investigator import evaluate_seller_comments
from backend.agents.controllers.product_controller import classify_product_analysis
from backend.agents.controllers.seller_controller import classify_seller_analysis
from backend.agents.final_judge import final_verdict_with_reasoning

def run_analysis_pipeline(product_url_or_text):
    # Step 1: Scrape everything in one call
    all_data = scrape_all_info(product_url_or_text)

    # Handle errors (optional)
    if all_data["reviews"] in [0, 1, 2] or all_data["seller"] in [0, 1]:
        return {"status": "error", "message": "Scraping failed or incomplete    "}, all_data

    product_comments = all_data["reviews"]
    seller_info = all_data["seller"]

    # Step 2: Investigators (pass directly to the functions)
    product_paragraph = evaluate_product_comments(product_comments)
    seller_paragraph = evaluate_seller_comments(seller_info)


    # Step 3: Controllers
    product_json = classify_product_analysis(product_paragraph)
    seller_json = classify_seller_analysis(seller_paragraph)

    # Step 4: Final Judge
    final_output = final_verdict_with_reasoning(product_json, seller_json)

    return final_output, {
        "Product Comments": product_comments,
        "Seller Info": seller_info,
        "Product Paragraph": product_paragraph,
        "Seller Paragraph": seller_paragraph,
        "Product JSON": product_json,
        "Seller JSON": seller_json,
        "Description Info": all_data["description"] 
    }
