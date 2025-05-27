from google.genai import types
import time

def evaluate_product_description(description, thinking_placeholder, base_html, top_k=50, top_p=0.95, temperature=0.3):
    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    instruction = """
## Task

You are an agent who analyzes product description.
Your response will be used to determine the product is scam and whether to proceed with the purchase or not.
There will be many agents like you and they will analyze different parts of the product such as seller informations, product reviews etc...

## Key Points

Try to provide valueable insights about the description.
Do you think the description is well written? 
Does it contain any suspicious or scam-related phrases?
Does it provide enough information about the product?

## Input Prompt

The language of the product description is Turkish, so you should understand Turkish.

## Output Format

Some products may return error message, in this case, you should return a message saying that there are no description to analyze.
Your output have to be in English.
Your output have to be formal and professional.
Your output have to be less then 200 words

## Example Structure

**Brief Summary**
**Analysis of description**
**Some good and bad parts of the description as examples**
"""

    investigator = "Investigating the product description"
    text = ""
    for char in investigator:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=description,
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=temperature,
            max_output_tokens=340,
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
