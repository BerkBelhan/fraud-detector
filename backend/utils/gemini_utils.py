# gemini_utils.py
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
