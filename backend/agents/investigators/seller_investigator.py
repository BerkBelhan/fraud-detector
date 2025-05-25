from backend.utils.gemini_utils import model

def evaluate_seller_comments(comments):
    """
    Evaluates seller comments to determine trustworthiness.
    Args:
        comments (list): List of seller review comments.
    Returns:
        str: A concise evaluation paragraph summarizing trustworthiness, delivery issues, scams, and patterns in complaints.   
    """
    joined_comments = "\n".join(comments)
    prompt = f"""
    Analyze the following user comments about a seller. Focus on trustworthiness, delivery issues, scams, and patterns in complaints. Do **not** return a JSON. Instead, write a concise and clear paragraph summarizing your evaluation.

    Be honest, but cautious. If the comments seem mostly harmless (e.g., wrong color or minor delays), say that it's likely a good seller but minor mistakes occurred.

    Include a suggestion for the user: whether to proceed, proceed with caution, or avoid.
    ---
    Seller reviews:
    {joined_comments}
    """
    response = model.generate_content(prompt)
    return response.text

