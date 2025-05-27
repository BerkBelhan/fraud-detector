from google.genai import types
import time

def evaluate_seller_info(info, thinking_placeholder, base_html):
    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    instruction = """
## Task

You are an agent who analyzes seller informations for a product. 
Your response will be used to determine the product is scam and whether to proceed with the purchase or not.
There will be many agents like you and they will analyze different parts of the product such as product comments, product description etc...

## Key Points

Provide valueable insights about the seller informations.
Provide bad parts and good parts of the seller informations.

## Input Prompt

The language of the seller information is Turkish, so you should understand Turkish.

## Output Format

If the input is an error message, you should return a message saying that there is no seller information to analyze.
Your output have to be in English excluding Turkish seller information and it should be formal and professional.
"""

    investigator = "Investigating the seller information"
    text = ""
    for char in investigator:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=info,
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=0.3,
            max_output_tokens=150,
            top_p=0.95,
            top_k=50,
            seed=42
        ),
    ).text

    base_response = response[:200]
    text += "<br>"
    for char in base_response:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    return response

