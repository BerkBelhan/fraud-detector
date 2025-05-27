from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ✅ 1. Launch Driver
def launch_driver():

    options = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    
    options.add_argument(f'user-agent={user_agent}')




    
    # Uncomment for headless mode
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ 2. Search and click first Ekşi Sözlük topic
def search_topic(driver, topic):
    wait = WebDriverWait(driver, 5)
    try:
        driver.get("https://eksisozluk.com")
        time.sleep(2)

        # Accept cookies if needed
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='kabul et']")))
            cookie_btn.click()
            time.sleep(1)
        except:
            pass

        # Type in search box
        search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='başlık, #entry, @yazar']")))
        search_box.clear()
        search_box.send_keys(topic)

        # Click the search button (the magnifying glass)
        search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'][aria-label='getir']")))
        search_btn.click()

        # Wait for results page to load
        time.sleep(3)

        return True

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False

# ✅ 3. Extract entry contents
def extract_entries(driver, limit=5):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".content")))
        entry_elements = driver.find_elements(By.CSS_SELECTOR, ".content")[:limit]
        return [e.text.strip() for e in entry_elements]
    except Exception as e:
        print(f"⚠️ Could not extract entries: {e}")
        return []

# ✅ 4. Wrap it all
def get_social_sentiment_eksi(topic, limit=5):
    driver = launch_driver()
    try:
        if search_topic(driver, topic):
            entries = extract_entries(driver, limit)
            return entries
        else:
            return []
    finally:
        driver.quit()

# ✅ 5. Run for testing
if __name__ == "__main__":
    topic = input("🔍 Enter search topic (e.g., voyant, trendyol airpods pro): ").strip()
    entries = get_social_sentiment_eksi(topic)

    if entries:
        print(f"\n📢 Top {len(entries)} Ekşi Sözlük entries for '{topic}':\n")
        for i, entry in enumerate(entries, 1):
            print(f"{i}. {entry}\n")
    else:
        print("❌ No entries found or scraping failed.")