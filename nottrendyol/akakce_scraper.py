"""
Akakçe Price & Seller Scraper
─────────────────────────────
• Opens Akakçe, searches for a product, waits for results,
  and extracts the first N (price, seller) pairs it finds.

• Works in GUI mode by default so you can watch what it does.
  Set headless=True in scrape_prices() for CI / servers.

Requires: selenium, webdriver-manager
"""

from __future__ import annotations

import json
import sys
import time
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ────────────────────────────────────────────────────────────────────────────────
# Core scraper
# ────────────────────────────────────────────────────────────────────────────────
def scrape_prices(
    term: str,
    limit: int = 40,
    headless: bool = False,
    wait_seconds: int = 20,
) -> List[Dict[str, str]]:
    """
    Return a list like:
    [
        {'seller': 'trendyol',   'price': '39.495,94 TL'},
        {'seller': 'MediaMarkt', 'price': '39.999,00 TL'},
        ...
    ]
    """
    # 1. Chrome driver setup
    opts = Options()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    opts.add_argument(f'user-agent={user_agent}')
 
    if headless:
        opts.add_argument("--headless=new")           # Chrome ≥ 109
    opts.add_experimental_option("detach", True)      # keep window open in GUI mode
    opts.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )

    out: List[Dict[str, str]] = []

    try:
        # 2. Open Akakçe & run the search
        driver.get("https://www.akakce.com")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "q"))
        ).send_keys(term, Keys.RETURN)

        # 3. Wait until *any* price label appears
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.pt_v8"))
        )

        # Optionally scroll once to trigger lazy-loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

        # 4. Grab the first <limit> price spans
        price_spans = driver.find_elements(By.CSS_SELECTOR, "span.pt_v8")[:limit]

        for span in price_spans:
            price_text = span.text.strip()
            if not price_text:
                continue

            # ▶ find the nearest ancestor <div> that also contains a seller logo
            try:
                row = span.find_element(
                    By.XPATH,
                    "./ancestor::div[.//img[@alt]][1]"
                )
                seller = row.find_element(By.XPATH, ".//img[@alt][1]") \
                             .get_attribute("alt").strip()
            except Exception:
                # Something unexpected: record price but mark seller unknown
                seller = "Unknown"

            out.append({"seller": seller, "price": price_text})

    finally:
        # keep browser open in GUI mode for inspection; close only in headless runs
        if headless:
            driver.quit()

    # Deduplicate while preserving order
    seen = set()
    uniq = [
        item for item in out
        if (t := (item["seller"], item["price"])) not in seen and not seen.add(t)
    ]
    return uniq


# ────────────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or input("🔍 Product to search on Akakçe: ")
    results = scrape_prices(query, limit=5, headless=True)

    if results:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("❌ No prices found.")