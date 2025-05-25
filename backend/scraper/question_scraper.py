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
        return 1
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

def extract_questions(html):
    try:
        html, driver = html
        soup = BeautifulSoup(html, 'html.parser')
        questions = soup.find_all('div', class_='qna-item')
        for i,question in enumerate(questions):
            question_dict = dict()
            question_text = question.find('h4').text
            answer_text = question.find('h5').text
            question_dict[question_text] = answer_text
            questions[i] = question_dict
        return questions
    except:
        return 1

def format_questions(questions):
    if questions == 0:
        return "Linke erişilemiyor"
    if questions == 1:
        return "Soru bulunamadı"
    
    formatted_text = "Sorular:\n\n"
    for question in questions:
        for question_text, answer_text in question.items():
            formatted_text += f"Soru: {question_text}\nCevap: {answer_text}\n\n"
    
    return formatted_text

def link_parse(url):
    new_url = ""
    if url.startswith("https://"):
        new_url += "https://"
        url = url[8:]
        
    urls = url.split('/')
    for i in range(3):
        if i == 2:
            new_url += urls[i].split('?')[0]
        else:
            new_url += urls[i] + "/"
    merchant_id = url.split("merchantId=")[1].split('&')[0]
    new_url += "/saticiya-sor?" + "merchantId=" + merchant_id + "&showSelectedSeller=true"
    return new_url

def get_questions(url):
    url = link_parse(url)
    html_with_driver = fetch_with_selenium(url, False, True, wait_for="qna-item")
    if html_with_driver == 0:
        return "Linke erişilemiyor"
    questions = extract_questions(html_with_driver)
    return format_questions(questions)

if __name__ == "__main__":
    url = input("🔗 Enter Trendyol product URL: ")
    print(get_questions(url))