import re
import json

GENIE_IMAGE_PATH = "frontend/assets/genie.png" 

GENIE_PERSONA_DIALOGUE = {
    "welcome": "Greetings, Master. I am the Scaminator. Present me a product URL, and I shall consult the spirits of Product and Seller for you.",
    "thinking": "The mists of the marketplace swirl... I am analyzing the separate spirits...",
    "done_no_verdict": "I have returned with my findings from the two realms. Examine them carefully."
}

def extract_json_from_response(text_response):
    """
    Finds and parses a JSON block from a string, even if it's surrounded by other text.
    """
    if not isinstance(text_response, str): 
        return text_response # Already a dict, or not a string

    # Try to find JSON within ```json ... ```
    match = re.search(r"```json\s*(\{.*?\})\s*```", text_response, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            # If parsing this specific block fails, it's a problem with this block
            return {"error": "Malformed JSON block found within ```json ```.", "raw_text": json_string}

    # Fallback: if no ```json``` block, try to parse the whole string or find first/last braces
    # This is less reliable but can catch cases where the agent doesn't use backticks
    try:
        # Attempt to parse the whole string if it looks like JSON
        if text_response.strip().startswith("{") and text_response.strip().endswith("}"):
            return json.loads(text_response)
    except json.JSONDecodeError:
        pass # Continue to next fallback

    try: # Fallback to find first '{' and last '}'
        start = text_response.find('{')
        end = text_response.rfind('}') + 1
        if start != -1 and end != 0 and start < end : # Ensure valid slice
            potential_json = text_response[start:end]
            return json.loads(potential_json)
    except json.JSONDecodeError:
        pass # Ignore if this fails too

    # If all else fails, return an error object with the raw text
    return {"error": "Could not find or parse a valid JSON object in the agent's response.", "raw_response": text_response}