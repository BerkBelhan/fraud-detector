from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def fetch_with_selenium(url):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()
    return html

def extract_review(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    rating = soup.find('div', attrs={'class': 'ps-ratings__count-text'}).text
    reviews = soup.find_all('div', attrs={'class': 'ps-ratings__count'})
    review_count = reviews[0].text 
    comment_count = reviews[1].text
    desc = soup.find('div', attrs={'class': 'reviews'})
    reviews = soup.find_all('div', attrs={'class': 'comment-text'})
    if desc:
        return [[rating, review_count, comment_count]] + [review.text for review in reviews]
    return None

def scrape_reviews(urls):
    reviews = []
    for url in urls:
        html = fetch_with_selenium(url)
        reviews.append(extract_review(html))
    return reviews

if __name__ == "__main__":
    url = input("Enter the URL: ")
    urls = [url]
    reviews = scrape_reviews(urls)
    for index, url in enumerate(reviews):
        for index2, comment in enumerate(url):
            if index2 == 0:
                print(f"{comment[0]} , {comment[1]} , {comment[2]}")
                continue
            print(f"{index2}. {comment}")