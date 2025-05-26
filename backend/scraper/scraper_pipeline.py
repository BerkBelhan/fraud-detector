# scraper_pipeline.py

from backend.scraper.description_scraper import get_description
from backend.scraper.seller_scraper import get_seller_info
from backend.scraper.reviews_scraper import get_reviews
from backend.scraper.question_scraper import get_questions
import time


def scrape_all_info(url, thinking_placeholder=None, base_html=None):

    fetch = "Fetching {} data"
    text = ""
    desc_fetch = fetch.format("description")
    for char in desc_fetch:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)
    description = get_description(url)

    base_desc = description[:200]
    text += "<br>"
    for char in base_desc:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    rews_fetch = fetch.format("reviews")
    text = ""
    for char in rews_fetch:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    reviews = get_reviews(url)
    base_reviews = reviews[:200]

    text += "<br>"
    for char in base_reviews:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    seller_fetch = fetch.format("seller")
    text = ""
    for char in seller_fetch:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    seller_info = get_seller_info(url)
    base_seller_info = seller_info[:200]

    text += "<br>"
    for char in base_seller_info:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    """questions_fetch = fetch.format("questions")
    text = ""
    for char in questions_fetch:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)
    
    questions = get_questions(url)
    base_questions = questions[:200]
    
    text += "<br>"
    for char in base_questions:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)"""

    return {
        "description": description,
        "reviews": reviews,    
        "seller": seller_info,
        "questions": ""
    }
