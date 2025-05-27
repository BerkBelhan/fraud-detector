from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def fetch_with_selenium(url, wait_for=False):
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        if wait_for:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, wait_for))
            )
        else:
            time.sleep(4)
        html = driver.page_source
    except:
        driver.quit()
        return 0
    driver.quit()
    return html

def extract_review(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        rating = soup.find('div', attrs={'class': 'ps-ratings__count-text'}).text
        reviews = soup.find_all('div', attrs={'class': 'ps-ratings__count'})
        review_count = reviews[0].text 
        comment_count = reviews[1].text
        desc = soup.find('div', attrs={'class': 'reviews'})
        reviews = soup.find_all('div', attrs={'class': 'comment-text'})
        if len(reviews) == 0:
            return 1
        return [[rating, review_count, comment_count]] + [review.text for review in reviews]
    except:
        return 2

def link_parse(url):
    new_url = ""
    if url.startswith("https://"):
        new_url += "https://"
        url = url[8:]
        
    url = url.split('/')
    for i in range(3):
        if i == 2:
            new_url += url[i].split('?')[0]
        else:
            new_url += url[i] + "/"
    return new_url

def scrape_reviews(url):
    html = fetch_with_selenium(url, wait_for='reviews-content')
    if html == 0:
        return 0
    if html == 1:
        return 1
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
            formatted_text += f"Ürün Ratingi: {review[0]}, Değerlendirme sayısı: {review[1]}, Yorum sayısı: {review[2]}\n\nYorumlar:\n"
            continue
        formatted_text += f"{index}. {review}\n"
    
    return formatted_text

def get_reviews(url):
    url = process_url(link_parse(url))
    reviews = scrape_reviews(url)
    return format_reviews(reviews)

if __name__ == "__main__":
    url = input("Enter the URL: ")
    print(get_reviews(url))