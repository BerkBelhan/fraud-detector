from backend.utils.gemini_utils import client
from google.genai import types
from pydantic import BaseModel
import time

def final_verdict_with_reasoning(product_response, seller_response, description_response, thinking_placeholder=None, base_html=None, top_k=50, top_p=0.95, temperature=0.3):
    ins = """
## Task

You are the final decision-making agent in a multi-agent fraud detection system for e-commerce products and sellers.

There are many agents that you will get data from, and they are:

- Product Description Investigator
- Product Reviews Investigator
- Seller Information Investigator

Your job is to:

1. Integrate both analyses and provide an overall trust verdict for the product-seller.
2. Give a trustworthy score between 0 and 100, where 0 is completely untrustworthy and 100 is completely trustworthy. Don't hesitate to give low points if you see big threats.
3. Provide a concise explanation of your verdict, focusing on key points from both analyses.
4. Always give examples for your reasoning, such as specific comments or seller behaviors that influenced your decision.


## Key Points

Be as objective as possible, but also consider the overall context of the product and seller.
You should return a brief summary of your analysis, an overall score with review, and a list of reasonings ( at least 7 reasons ) with examples that led to your decision.
Reasonings should be sorted from the most important to the least important which represents the score accurately.
Your overall score review should be related with agents' analyses.
You have to provide a small suggestion by agents for the users who wants to buy this product.

## Input Prompt

Your input will be pure English excluding Turkish comments and seller information.

## Output Format

Your output should be well formatted and easy to understand.
Your output have to be in English.
Be formal and professional in your tone.

## Rule

Don't mention the agents and their names in your response
"""

    prompt = f"""
### Product Description Investigator Analysis:

{description_response}

### Product Reviews Investigator Analysis:

{product_response}

### Seller Information Investigator Analysis:

{seller_response}
"""

    class OverallResult(BaseModel):
        summary: str
        overall_score: int
        overall_score_review: str
        reasonings_with_examples: list[str]
        suggestion: str


    final_judge = "Final evaluations"
    text = ""
    for char in final_judge:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=ins,
            temperature=temperature,
            max_output_tokens=1000,
            top_p=top_p,
            top_k=top_k,
            seed=42,
            responseSchema=OverallResult,
            responseMimeType='application/json'
        ),
    )

    response: OverallResult = response.parsed

    overall_score = response.overall_score
    if overall_score <= 24:
        verdict = "Likely Scam"
    elif overall_score <= 49:
        verdict = "Suspicious"
    elif overall_score <= 74:
        verdict = "Likely Safe"
    else:
        verdict = "Very Safe"

    base_summary = response.summary[:300]
    text += "<br>"
    for char in base_summary:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    reasonings = response.reasonings_with_examples
    reasonings_text = ""
    for i in range(len(reasonings)):
        reasonings_text += f"**{i + 1}.** {reasonings[i]}\n\n"

    formatted_text = f"""

### Summary of Analysis

{response.summary}

### {verdict}

### Overall Trustworthy Score: {response.overall_score}/100

### Overall Score Review

{response.overall_score_review}

### Reasonings

{reasonings_text}

### Additional Suggestions for Users

{response.suggestion}

"""

    return formatted_text


