# product_investigator.py
from backend.utils.gemini_utils import model

def evaluate_product_comments(comments):
    from backend.utils.gemini_utils import model  # or however you're loading Gemini

    # Flatten nested lists
    flat_comments = []
    for item in comments:
        if isinstance(item, list):
            flat_comments.extend(item)
        elif isinstance(item, str):
            flat_comments.append(item)

    joined_comments = "\n".join(flat_comments)

    prompt = f"""
    You are an agent analyzing product reviews. Here are some recent reviews:\n
    {joined_comments}\n
    Summarize the tone, spot suspicious patterns (like fake reviews), and generate a short paragraph summary.
    """

    response = model.generate_content(prompt)
    return response.text
