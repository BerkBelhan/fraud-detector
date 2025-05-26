import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)




class Crawl4AIAgent:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.cleaned_text = None
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def fetch_html(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            self.html = response.text
            return True
        except Exception as e:
            print(f"❌ Failed to fetch HTML: {e}")
            return False

    def extract_visible_text(self):
        try:
            soup = BeautifulSoup(self.html, "html.parser")

            # Remove script/style
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()

            # Extract visible text
            self.cleaned_text = soup.get_text(separator=" ", strip=True)
            return True
        except Exception as e:
            print(f"❌ Error cleaning text: {e}")
            return False

    def extract_product_info(self):
        if not self.cleaned_text:
            print("❌ No cleaned HTML to analyze.")
            return None

        prompt = f"""
Given the raw text content of an e-commerce product page, extract structured product information.

Then generate:
1. A short and **localized Akakçe search query** using **Turkish words**.
   - Do **not include** product codes (e.g., MW0W3TU/A), RAM size, SSD size, or colors unless essential.
   - Always use "**inç**" instead of "inch"/"inc".
   - Make sure it’s 3 to 6 words max. Example: "macbook air 13 inç m3"
   - Avoid model years unless necessary.
   - PT is "Pozitif Teknoloji". 

2. A clean seller name to be used as an Ekşi Sözlük query:
   - If the seller has two words, use a space.
   - If it’s one word like “shopvoyant”, strip generic words (“shop”, “store”) → just “voyant”.
   - If the store is Voyant Apparel, drop the Apparel and just use voyant.

Return your response in the following JSON format:

{{
  "title": "...",
  "price": "...",
  "merchant": "...",
  "rating": "...",
  "snippet": "...",
  "eksi_query": "...",
  "akakce_query": "..."
}}

Raw product content:
\"\"\"
{self.cleaned_text[:8000]}
\"\"\"
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"❌ Gemini extraction error: {e}")
            return None


# ✅ Test standalone
if __name__ == "__main__":
    url = input("🔗 Enter product URL: ").strip()
    agent = Crawl4AIAgent(url)

    if agent.fetch_html() and agent.extract_visible_text():
        result = agent.extract_product_info()
        print("\n🧠 Extracted Product Info:\n", result)
    else:
        print("❌ Failed to process URL.")