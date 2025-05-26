# C:/SENG472/MainProje/fraud-detector/frontend/ui_config.py
import re
import json

# Path to the genie/scaminator image asset
GENIE_IMAGE_PATH = "frontend/assets/genie.png" 

# Dialogue lines for the Scaminator persona
GENIE_PERSONA_DIALOGUE = {
    "welcome": "Greetings, Master. I am the Scaminator. Present me a product URL, and I shall unveil its secrets.",
    "thinking": "The mists of the marketplace swirl... I am consulting the digital spirits...",
    "final_verdict": "I have returned. The threads of data have been woven into a final judgment."
}

def extract_json_from_response(text_response):
    """
    Finds and parses a JSON block from a string, handling various formats.
    """
    # If it's already a dictionary, return it directly.
    if isinstance(text_response, dict):
        return text_response
    
    # Ensure the input is a string before proceeding
    if not isinstance(text_response, str):
        return {"verdict": "Error", "reason": "Invalid data type for JSON extraction.", "score": 0}

    # First, try to find a Markdown JSON block
    match = re.search(r"```json\s*(\{.*?\})\s*```", text_response, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return {"verdict": "Error", "reason": "Malformed JSON found inside code block.", "score": 0}

    # If no Markdown block, try parsing the whole string as JSON
    try:
        return json.loads(text_response)
    except json.JSONDecodeError:
        # If all parsing fails, return a structured error
        return {"verdict": "Error", "reason": "Could not parse JSON from the agent's raw text response.", "score": 0}