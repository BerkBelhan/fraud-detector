import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash-latest")

def evaluate_image_vs_name(image_path, product_name):
    with open(image_path, "rb") as f:
        image_data = f.read()

    response = model.generate_content([
        {"inline_data": {"mime_type": "image/jpeg", "data": image_data}},
        {"text": f"""
You are an e-commerce fraud detection AI.

Given the product name "{product_name}" and the attached product image:
- Does the image accurately represent the product?
- Is the image quality acceptable?
- Return a JSON like this:
{{
  "match": "Yes" | "No" | "Uncertain",
  "quality": "Good" | "Poor" | "Average",
  "reason": "Short explanation"
}}
"""}
    ])

    return response.text

# Example usage
if __name__ == "__main__":
    image_path = "D:/ScamDetector/fraud-detector/earbudsly.jpg"
    product_name = "Wireless Earbuds"
    result = evaluate_image_vs_name(image_path, product_name)
    print(result)
