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
    # options.add_argument("--headless")  # Enable headless if needed
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def navigate_to_full_comments(driver, product_url):
    driver.get(product_url)
    wait = WebDriverWait(driver, 10)
    time.sleep(1)

    # Incrementally scroll to make sure button loads
    print("🔽 Scrolling to find 'Tüm Yorumları Göster' button...")
    button = None
    scroll_y = 500
    while scroll_y < 5000:
        driver.execute_script(f"window.scrollTo(0, {scroll_y});")
        time.sleep(0.5)
        try:
            button = driver.find_element(By.CSS_SELECTOR, "button.navigate-all-reviews-btn")
            if button.is_displayed():
                break
        except:
            pass
        scroll_y += 300

    if button:
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", button)
            print("✅ Clicked 'Tüm Yorumları Göster'")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Failed to click the button: {e}")
    else:
        print("⚠️ Button not found after scrolling.")

    return False

def extract_product_reviews(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    try:
        rating = soup.find('div', class_='ps-ratings__count-text').get_text(strip=True)
    except:
        rating = 'Rating not found'

    try:
        counts = soup.find_all('div', class_='ps-ratings__count')
        review_count = counts[0].get_text(strip=True) if len(counts) > 0 else 'Review count not found'
        comment_count = counts[1].get_text(strip=True) if len(counts) > 1 else 'Comment count not found'
    except:
        review_count = 'Review count not found'
        comment_count = 'Comment count not found'

    comment_elements = soup.find_all('div', class_='comment-text')
    comments = [c.get_text(strip=True) for c in comment_elements]

    return {
        'rating': rating,
        'review_count': review_count,
        'comment_count': comment_count,
        'comments': comments[:10]  # limit to top 10
    }

if __name__ == "__main__":
    product_url = input("🔗 Enter Trendyol product URL: ").strip()
    driver = launch_driver()

    success = navigate_to_full_comments(driver, product_url)
    if success:
        result = extract_product_reviews(driver)
        driver.quit()

        print(f"\n⭐ Product Rating: {result['rating']}")
        print(f"📊 Total Reviews: {result['review_count']} | Total Comments: {result['comment_count']}")
        print("📝 Top 10 Product Comments:")
        for i, comment in enumerate(result['comments'], 1):
            print(f"{i}. {comment}")

        # Run Gemini if needed
        from backend.agents.investigators.comment_Investigator import evaluate_comments
        response = evaluate_comments(result['comments'])
        print("\n🧠 Gemini Evaluation Result:\n", response)
    else:
        print("❌ Could not complete process.")
        driver.quit()