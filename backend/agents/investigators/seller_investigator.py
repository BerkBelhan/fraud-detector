from google.genai import types
import time

def evaluate_seller_info(info, thinking_placeholder, base_html, top_k=50, top_p=0.95, temperature=0.3):
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
Your output have to be in English and formal.
Your output have to be less then 150 words


## Example Structure

**Brief Summary**
**Analysis of seller information**
**Some good and bad parts of the seller information as examples**
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
            temperature=temperature,
            max_output_tokens=250,
            top_p=top_p,
            top_k=top_k,
            seed=42
        ),
    ).text

    base_response = response[:300]
    text += "<br>"
    for char in base_response:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    return response

