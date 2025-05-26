from google.genai import types

def evaluate_product_comments(comments):
    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    instruction = """
You are an agent who analyzes user comments and reviews about a product. 
Your response will be used to determine the product is scam and whether to proceed with the purchase or not.
There will be many agents like you and they will analyze different parts of the product such as seller informations, product description etc...
Some products may have no comments at all, in this case, you should return a message saying that there are no comments to analyze.
Provide valueable insights about the comments, for instance, give some example from fraud related comments.
Also return good results for products that have good comments.
You will see average rating from 1 to 5, where 1 is the worst and 5 is the best. You have to analyze this rating and give your insights about it.
Comments will be written in Turkish, so you should understand Turkish.
You will see comments count and reviews count. It's another metric you should analyze.
"""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=comments,
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=0.3,
            max_output_tokens=1000,
            top_p=0.5,
            top_k=5,
            seed=42
        ),
    )
    return response.text
