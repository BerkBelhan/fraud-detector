from google.genai import types

def evaluate_seller_info(info):
    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    instruction = """
You are an agent who analyzes seller informations for a product. 
Your response will be used to determine the product is scam and whether to proceed with the purchase or not.
There will be many agents like you and they will analyze different parts of the product such as product comments, product description etc...
If the input is an error message, you should return a message saying that there is no seller information to analyze.
Try to provide valueable insights about the seller informations.
Try to provide bad parts and good parts of the seller informations.
The language of the seller information is Turkish, so you should understand Turkish.
"""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=info,
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

