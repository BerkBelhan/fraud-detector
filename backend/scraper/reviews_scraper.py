from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

def fetch_with_selenium(url):
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        html = driver.page_source
    except:
        driver.quit()
        return 0
    driver.quit()
    return html

def extract_review(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    rating = soup.find('div', attrs={'class': 'ps-ratings__count-text'}).text
    reviews = soup.find_all('div', attrs={'class': 'ps-ratings__count'})
    review_count = reviews[0].text 
    comment_count = reviews[1].text
    
    comments = soup.find_all('div', attrs={'class': 'comment-text'})
    
    if len(comments) == 0:
        return 1
    
    summary = f"Rating: {rating}, Review Count: {review_count}, Comment Count: {comment_count}"
    return [summary] + [comment.text.strip() for comment in comments]


def scrape_reviews(url):
    html = fetch_with_selenium(url)
    if html == 0:
        return 0
    return extract_review(html)

def process_url(url):
    split_url = url.split('?')
    return split_url[0] + "/yorumlar"

def format_reviews(reviews):
    if reviews == 0:
        return "Linke erişilemiyor"
    if reviews == 1:
        return "Yorum bulunamadı"
    if reviews == 2:
        return "Yorumlar yüklenemedi, site değişmiş olabilir."

    formatted_text = ""
    for index, review in enumerate(reviews):
        if index == 0:
            formatted_text += f"Rating: {review[0]}, Değerlendirme sayısı: {review[1]}, Yorum sayısı: {review[2]}\n\nYorumlar:\n"
            continue
        formatted_text += f"{index}. {review}\n"
    
    return formatted_text

def get_reviews(url):
    reviews = scrape_reviews(process_url(url))
    return format_reviews(reviews)

if __name__ == "__main__":
    url = input("Enter the URL: ")
    reviews = scrape_reviews(process_url(url))
    formatted_reviews = format_reviews(reviews)
    print(formatted_reviews)