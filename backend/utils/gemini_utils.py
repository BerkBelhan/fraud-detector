# In: backend/utils/gemini_utils.py

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Load environment variables from your .env file
load_dotenv()

# Get the API key from the environment
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable in your .env file.")

# Configure the genai library with your API key
genai.configure(api_key=api_key)


# --- MODEL CREATION (This is the line that was missing) ---
# Create a single, reusable model instance for the app
model = genai.GenerativeModel("gemini-1.5-flash-latest")


# --- HELPER FUNCTION (With debugging prints) ---
def call_gemini(prompt: str) -> dict:
    """
    Calls Gemini with the given prompt and returns the parsed JSON response.
    """
    print("------------------------------------------")
    print(f"DEBUG: Sending this prompt to Gemini:\n{prompt}")
    print("------------------------------------------")
    
    try:
        response = model.generate_content(prompt)
        
        print(f"DEBUG: Full Gemini response object:\n{response}")
        print("------------------------------------------")

        text = response.text.strip()
        print(f"DEBUG: Extracted text from response:\n'{text}'")
        print("------------------------------------------")

        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print("DEBUG: ERROR - No JSON object was found in the text.")
            return {"error": "No JSON found in Gemini response."}

        json_str = match.group()
        print(f"DEBUG: Successfully found JSON string:\n{json_str}")
        print("------------------------------------------")
        
        return json.loads(json_str)
    except Exception as e:
        print(f"DEBUG: An exception occurred: {e}")
        return {"error": str(e)}
    