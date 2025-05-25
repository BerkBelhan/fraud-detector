# scraper_pipeline.py

from backend.scraper.description_scraper import scrape_descriptions
from backend.scraper.seller_scraper import extract_seller_info, extract_seller_link, fetch_with_selenium
from backend.scraper.reviews_scraper import scrape_reviews, process_url

def scrape_all_info(url):
    # 1. Description
    desc_data = scrape_descriptions(url)

    # 2. Reviews
    review_url = process_url(url)
    review_data = scrape_reviews(review_url)

    # 3. Seller Info
    html_with_driver = fetch_with_selenium(url, False, False)
    if html_with_driver == 0:
        seller_data = 0
    else:
        html_with_seller_link = extract_seller_link(html_with_driver)
        seller_data = extract_seller_info(html_with_seller_link)

    return {
        "description": desc_data,  # [desc_dict, tech_dict] or 0/1
        "reviews": review_data,    # [rating, review_count, comment_count, list of reviews] or 0/1/2
        "seller": seller_data      # dict or 0/1
    }
