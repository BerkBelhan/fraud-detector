from google.genai import types
import time

def evaluate_product_comments(comments, thinking_placeholder, base_html, top_k=50, top_p=0.95, temperature=0.3):
    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    instruction = """
## Task

You are an agent who analyzes user comments and reviews about a product. 
Your response will be used to determine the product is scam and whether to proceed with the purchase or not.
There will be many agents like you and they will analyze different parts of the product such as seller informations, product description etc...

## Key Points

Provide valueable insights about the comments, for instance, give some example from fraud related comments.
Return good results for products that have good comments.
You will see average rating from 1 to 5, where 1 is the worst and 5 is the best. You have to analyze this rating and give your insights about it.
You will see comments count and reviews count. It's another metric you should analyze.

## Input Prompy

Comments will be written in Turkish, so you should understand Turkish.


## Output Format

Some products may have no comments at all, in this case, you should return a message saying that there are no comments to analyze.
Your output have to be in English and formal.
Your output have to be less then 400 words

## Example Structure

**Brief Summary**
**Analysis of reviews and comments count and average rating**
**Analysis of comments**
**Some good and bad comments as examples**
"""

    investigator = "Investigating the product reviews and comments"
    text = ""
    for char in investigator:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=comments,
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=temperature,
            max_output_tokens=670,
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
