# scraper_pipeline.py

from backend.scraper.description_scraper import get_description
from backend.scraper.seller_scraper import get_seller_info
from backend.scraper.reviews_scraper import get_reviews
from backend.scraper.question_scraper import get_questions

def scrape_all_info(url):

    return {
        "description": get_description(url),
        "reviews": get_reviews(url),    
        "seller": get_seller_info(url),
        "questions": get_questions(url)
    }
