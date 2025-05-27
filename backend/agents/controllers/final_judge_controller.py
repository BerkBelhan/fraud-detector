from google.genai import types
import time
from pydantic import BaseModel

def evaluate_final_judge_analysis(content, thinking_placeholder, base_html, top_k=50, top_p=0.95, temperature=0.3):

    from backend.utils.gemini_utils import client  # or however you're loading Gemini

    ins = """
## Task

You are an agent who controls an overall product and seller analysis is correctly written or not.
Your decision will change the parameters of the analysis agent.
In analysis, you have to check logical consistency, grammar, and whether the analysis is informative.
If the analysis is not correctly written, the agent will be asked to rewrite it and you will decide topK, topP and temperature parameters of the agent.
Be careful while making your decision, because it will affect the final decision of the product.

## Input

You will get an overall analysis of product and seller written in both Turkish and English and the current agent parameters.

## Output

You will return a boolean value indicating whether the analysis is correctly written or not.
If the analysis is not correctly written, you will return topK, topP and temperature parameters of the agent.
"""

    investigator = "Controlling the final judge"
    text = ""
    for char in investigator:
        text += char
        thinking_placeholder.markdown(base_html.format(text), unsafe_allow_html=True)
        time.sleep(0.00003)

    class FinalController(BaseModel):
        is_correct: bool
        top_k: int
        top_p: float
        temperature: float

    agent_data = """

### Agent Parameters
TopK: {top_k}
TopP: {top_p}
Temperature: {temperature}
""".format(top_k=top_k, top_p=top_p, temperature=temperature)

    content += agent_data

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=content,
        config=types.GenerateContentConfig(
            system_instruction=ins,
            temperature=0.3,
            max_output_tokens=100,
            top_p=0.95,
            top_k=50,
            seed=42,
            responseSchema=FinalController,
            responseMimeType='application/json'
        ),
    )
    
    response: FinalController = response.parsed

    is_correct = response.is_correct
    if is_correct:
        return True, None, None, None
    else:
        top_k = response.top_k
        top_p = response.top_p
        temperature = response.temperature
        return False, top_k, top_p, temperature