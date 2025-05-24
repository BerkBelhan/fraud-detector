# gemini_utils.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")
