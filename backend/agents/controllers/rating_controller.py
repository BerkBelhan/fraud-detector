import json
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

def controller_agent(
    product_rating,
    product_rating_count,
    seller_rating,
    seller_rating_count,
    investigator_output,
    scores_dict  # shared dictionary
):

    investigator_output = json.loads(investigator_output)

    prompt = f"""
You are a meta-evaluation AI called the **Rating Controller Agent**.

Your job is to evaluate the performance of a subordinate agent who assessed an e-commerce product and seller based on rating metadata.

You are provided:
- Original input data used by the investigator
- The JSON output returned by the investigator

Your task is to:
1. **Validate** the investigator's verdict based on the input metadata
2. **Evaluate** the quality and alignment of their reasoning
3. **Score** how well their judgment aligns with known heuristics
4. **Ensure** the JSON format was followed properly

## Known Heuristics:
- High ratings (4.5+) with **high review counts (500+)** are generally trustworthy.
- Perfect or near-perfect scores with **low review counts (<20)** may be suspicious.
- Low product rating (<3.5) with **many reviews** = usually low quality.
- Major gaps (e.g. 2-star seller but 5-star product) should trigger caution.
- Consistent high ratings (e.g. 4.7–4.9) across both product and seller with high volume are likely safe.

## Output Requirements:
Return your evaluation in valid JSON format:
```json
{{
  "verdict": "Correct" | "Inconsistent" | "Invalid",
  "score": float
}}

Be strict. Only mark the agent as "Correct" with a score > 0.85 if its reasoning and judgment are clearly aligned with the input.

Investigator Output:
{json.dumps(investigator_output, indent=2)}

Original Input:
Product Rating: {product_rating} stars from {product_rating_count} reviews
Seller Rating: {seller_rating} stars from {seller_rating_count} reviews

Give your final evaluation below in raw JSON only:
"""

    response = model.generate_content(prompt)

    try:
        eval_output = json.loads(response.text)
    except Exception:
        eval_output = {"verdict": "Invalid", "score": 0.0}

    # Append this controller's score into the shared dictionary under its unique key
    scores_dict["rating_controller"] = eval_output.get("score", 0.0)

    # Return the updated dictionary (can also return the eval_output if needed)
    return scores_dict


investigator_json_output = {
"verdict": "Safe",
"reason": "Both product and seller have high ratings with significant review volumes, indicating overall trustworthiness."
}

"""
print(controller_agent(
product_rating=4.8,
product_rating_count=1860,
seller_rating=4.9,
seller_rating_count=2600,
investigator_output=investigator_json_output
))
"""
