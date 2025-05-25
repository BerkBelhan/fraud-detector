from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests

def fetch_with_selenium(url, driver=False, close=True, wait_for=False):
    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    if driver:
        pass
    else:
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
    if close:
        driver.quit()
    return html, driver

def fetch(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except:
        return 0
    return response.text

def extract_seller_link(html_with_driver):
        html, driver = html_with_driver
        soup = BeautifulSoup(html, 'html.parser')
        seller_link = soup.find('a', attrs={'class':'seller-name-text'})["href"]
        seller_split = seller_link.split('/')
        id = seller_split[-1]
        seller_link = f"https://www.trendyol.com/magaza/profil/{id}"
        return fetch_with_selenium(seller_link, driver, True, wait_for="product-review-section__review-count")

def extract_seller_info(html):
    try:
        html, driver = html
        soup = BeautifulSoup(html, 'html.parser')
        containers = soup.find_all('div', class_='seller-info-container__wrapper__text-container')
        seller_dictionary = dict()
        for container in containers:
            spans = container.find_all('span')
            key = spans[0].text
            value = spans[1].text
            seller_dictionary[key] = value
        containers = soup.find_all('div', class_='seller-metrics-container__wrapper')
        for container in containers:
            spans = container.find_all('span')
            key = spans[0].text
            value = spans[1].text
            seller_dictionary[key] = value
        rating = soup.find('span', class_='product-review-section-wrapper__wrapper__rating_wrapper_left__rating_value').text
        reviews = soup.find_all('span', class_='product-review-section__review-count')
        review_count = reviews[0].text
        comment_count = reviews[1].text
        
        seller_dictionary['Rating'] = rating
        seller_dictionary['Değerlendirme sayısı'] = review_count
        seller_dictionary['Yorum sayısı'] = comment_count

        return seller_dictionary
    except:
        return 1

def format_seller_info(seller_info):
    if seller_info == 0:
        return "Linke erişilemiyor"
    if seller_info == 1:
        return "Satıcı bilgileri bulunamadı, site değişmiş olabilir."
    
    formatted_text = "Satıcı Bilgileri:\n\n"
    for key, value in seller_info.items():
        formatted_text += f"{key}: {value}\n"
    
    return formatted_text

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

def get_seller_info(url):
    url = link_parse(url)
    html_with_driver = fetch_with_selenium(url, False, False, wait_for="seller-container")
    if html_with_driver == 0:
        return "Linke erişilemiyor"
    html_with_seller_link = extract_seller_link(html_with_driver)
    seller_info = extract_seller_info(html_with_seller_link)
    return format_seller_info(seller_info)

if __name__ == "__main__":
    url = input("🔗 Enter Trendyol product URL: ")
    print(get_seller_info(url))