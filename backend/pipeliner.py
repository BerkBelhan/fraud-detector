# C:\SENG472\MainProje\fraud-detector\backend\pipeliner.py

from backend.scraper.scraper_pipeline import scrape_all_info
from backend.agents.investigators.reviews_investigator import evaluate_product_comments
from backend.agents.investigators.seller_investigator import evaluate_seller_info
from backend.agents.investigators.description_investigator import evaluate_product_description
from backend.agents.final_judge import final_verdict_with_reasoning
from backend.agents.controllers.description_controller import evaluate_description_analysis
from backend.agents.controllers.seller_controller import evaluate_seller_analysis
from backend.agents.controllers.reviews_controller import evaluate_reviews_analysis
from backend.agents.controllers.final_judge_controller import evaluate_final_judge_analysis

def run_analysis_pipeline(product_url, thinking_placeholder, base_html):
    # Step 1: Scrape all data
    all_data = scrape_all_info(product_url, thinking_placeholder, base_html)

    product_comments = all_data["reviews"]
    seller_info = all_data["seller"]
    description = all_data["description"]

    # Step 2: Investigators (pass directly to the functions)
    description_paragraph = evaluate_product_description(description, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    product_paragraph = evaluate_product_comments(product_comments, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    seller_paragraph = evaluate_seller_info(seller_info, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)

    decription_controller_content = f"""
### Data

{description}

### Analysis

{description_paragraph}
"""
    
    is_correct, top_k, top_p, temperature = evaluate_description_analysis(decription_controller_content, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    print("\n\nBefore Description Paragraph:", description_paragraph)
    print("\n\nDescription Analysis:", is_correct, top_k, top_p, temperature)
    if not is_correct:
        description_paragraph = evaluate_product_description(description, thinking_placeholder, base_html, top_k=top_k, top_p=top_p, temperature=temperature)
        print("\n\nAfter Description Paragraph:", description_paragraph)
    product_controller_content = f"""
### Data

{product_comments}

### Analysis

{product_paragraph}
"""
    is_correct, top_k, top_p, temperature = evaluate_seller_analysis(product_controller_content, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    print("\n\nBefore Product Paragraph:", product_paragraph)
    print("\n\nProduct Controller Analysis:", is_correct, top_k, top_p, temperature)
    if not is_correct:
        product_paragraph = evaluate_product_comments(product_comments, thinking_placeholder, base_html, top_k=top_k, top_p=top_p, temperature=temperature)
        print("\n\nAfter Product Paragraph:", product_paragraph)
    seller_controller_content = f"""
### Data

{seller_info}

### Analysis

{seller_paragraph}
"""
    is_correct, top_k, top_p, temperature = evaluate_description_analysis(seller_controller_content, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    print("\n\nBefore Seller Paragraph:", seller_paragraph)
    print("\n\nSeller Controller Analysis:", is_correct, top_k, top_p, temperature)
    if not is_correct:
        seller_paragraph = evaluate_seller_info(seller_info, thinking_placeholder, base_html, top_k=top_k, top_p=top_p, temperature=temperature)
        print("\n\nAfter Seller Paragraph:", seller_paragraph)
    

    # Step 4: Final Judge
    final_output = final_verdict_with_reasoning(product_paragraph, seller_paragraph, description_paragraph, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    print("\n\nBefore Final Judge Analysis:", final_output)
    is_correct, top_k, top_p, temperature = evaluate_final_judge_analysis(final_output, thinking_placeholder, base_html, top_k=50, top_p=0.9, temperature=.7)
    print("\n\nFinal Judge Analysis:", is_correct, top_k, top_p, temperature)
    if not is_correct:
        final_output = final_verdict_with_reasoning(product_paragraph, seller_paragraph, description_paragraph, thinking_placeholder, base_html, top_k=top_k, top_p=top_p, temperature=temperature)
        print("\n\nAfter Final Judge Analysis:", final_output)

    # Return final output and a dictionary of all intermediate steps for debugging
    return final_output, {
        "Product Description": description,
        "Product Comments": product_comments,
        "Seller Informations": seller_info
    }, {
        "Description Analysis": description_paragraph,
        "Reviews Analysis": product_paragraph,
        "Seller Analysis": seller_paragraph,
    }