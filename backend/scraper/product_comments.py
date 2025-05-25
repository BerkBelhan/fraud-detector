# File: backend/scraper/product_comments.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def launch_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("log-level=3") 
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def navigate_to_full_comments(driver, product_url):
    driver.get(product_url)
    time.sleep(2) 

    try:
        # Using a more general selector that finds the link to all reviews
        all_reviews_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/yorumlar']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", all_reviews_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", all_reviews_button)
        print("✅ Navigated to all reviews page.")
        return True
    except Exception:
        print("⚠️ Could not navigate to a separate reviews page. Will scrape comments from the main product page.")
        # This is not a failure; we can still proceed.
        return True

def extract_product_reviews(driver):
    
    # --- FIX: ADDING AN INTELLIGENT WAIT ---
    # Instead of a fixed sleep, we will wait up to 10 seconds for the
    # first comment element to appear in the HTML.
    # We use your original 'div.comment-text' selector here.
    try:
        print("Waiting for review comments to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.comment-text"))
        )
        print("✅ Comments loaded successfully.")
    except Exception:
        # If after 10 seconds nothing is found, we print a clear message.
        print("❌ Timed out waiting for comments to load. The page may have no reviews or the layout has changed.")
        return {'comments': []} # Return empty list to be handled gracefully

    # Now that we know the comments are present, we can safely parse the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    comment_elements = soup.find_all('div', class_='comment-text')
    comments = [c.get_text(strip=True) for c in comment_elements]
    
    print(f"✅ Found {len(comments)} product comments.")

    return {
        'comments': comments[:20] 
    }