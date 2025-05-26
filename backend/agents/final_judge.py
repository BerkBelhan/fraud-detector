from backend.utils.gemini_utils import client
from google.genai import types
from pydantic import BaseModel
import time

def final_verdict_with_reasoning(product_response, seller_response, description_response, thinking_placeholder=None, base_html=None):
    ins = """
You are the final decision-making agent in a multi-agent fraud detection system for e-commerce products and sellers.

There are two agents:

- Product Description Investigator
- Product Reviews Investigator
- Seller Information Investigator

Your job is to:

1. Integrate both analyses and provide an overall trust verdict for the product-seller.
2. Give a trustworthy score between 0 and 100, where 0 is completely untrustworthy and 100 is completely trustworthy. Don't hesitate to give low points if you see big threats.
3. Provide a concise explanation of your verdict, focusing on key points from both analyses.
4. Always give examples for your reasoning, such as specific comments or seller behaviors that influenced your decision.

Be as objective as possible, but also consider the overall context of the product and seller.
Your output should be well formatted and easy to understand.
Your output have to be in English.
Your input will be pure English excluding Turkish comments and seller information.
Be formal and professional in your tone.

In the end, you should return a brief summary of your analysis, an overall score with review, and a list of reasonings ( at least 7 reasons ) with examples that led to your decision.
Your overall score review should be related with agents' analyses.

In addition, you have to provide a small suggestion by agents for the users who wants to buy this product.

Don't mention the agents and their names in your response
Reasonings should be sorted from the most important to the least important which represents the score accurately.
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
            temperature=0.1,
            max_output_tokens=2000,
            top_p=0.8,
            top_k=3,
            seed=42,
            responseSchema=OverallResult,
            responseMimeType='application/json'
        ),
    )

    response: OverallResult = response.parsed

    base_summary = response.summary[:200]
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

### Overall Trustworthy Score: {response.overall_score}/100

### Overall Score Review

{response.overall_score_review}

### Reasonings

{reasonings_text}

### Additional Suggestions for Users

{response.suggestion}

"""

    return formatted_text


