from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def launch_driver():
    options = Options()
    # Uncomment to run headless
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_seller_url_from_product(driver, product_url):
    driver.get(product_url)
    wait = WebDriverWait(driver, 10)

    try:
        # ✅ Corrected CSS selector from screenshot
        seller_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.seller-name-text")))
        seller_url = seller_link.get_attribute("href")
        print(f"✅ Found seller link: {seller_url}")
        return seller_url
    except Exception as e:
        print(f"❌ Could not find seller link on product page: {e}")
        return None

def fetch_seller_reviews(driver, seller_url):
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(seller_url)

        profile_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "seller_profile_button")))
        driver.execute_script("arguments[0].click();", profile_button)
        print("✅ Clicked 'Satıcı Profili'")
        time.sleep(3)

        seller_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//span[contains(text(), "Satıcı Değerlendirmeleri")]')
        ))
        driver.execute_script("arguments[0].click();", seller_tab)
        print("✅ Clicked 'Satıcı Değerlendirmeleri'")
        time.sleep(3)

        return True
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        return False

def extract_seller_info_and_reviews(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="seller-review"]'))
        )
    except:
        print("⚠️ No seller reviews found.")
        return {
            'seller': 'Unknown',
            'rating': 'Unknown',
            'reviews': []
        }

    try:
        seller_name = driver.find_element(By.CLASS_NAME, "seller-store__name").text.strip()
    except:
        seller_name = 'Seller name not found'

    try:
        rating = driver.find_element(By.CLASS_NAME, "seller-store__score").text.strip()
    except:
        rating = 'Rating not found'

    review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="seller-review"]')
    comments = [r.text.strip() for r in review_elements[:10]]

    return {
        'seller': seller_name,
        'rating': rating,
        'reviews': comments
    }

if __name__ == "__main__":
    product_url = input("Enter Trendyol product URL: ").strip()
    driver = launch_driver()

    seller_url = get_seller_url_from_product(driver, product_url)
    if seller_url and fetch_seller_reviews(driver, seller_url):
        result = extract_seller_info_and_reviews(driver)
        driver.quit()

        print(f"\n🛍️ Seller: {result['seller']}")
        print(f"⭐ Rating: {result['rating']}")
        print("📝 Top 10 Seller Reviews:")
        for i, review in enumerate(result['reviews'], 1):
            print(f"{i}. {review}")
    else:
        print("❌ Could not complete process.")
        driver.quit()