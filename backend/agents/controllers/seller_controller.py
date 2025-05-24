import json

def seller_investigator_controller(investigator_output: str) -> dict:
    """
    Processes the output from the seller investigator and returns a structured response.

    Returns:
        dict: A dictionary containing the verdict and reason extracted from the investigator output.
    """

    try:
        parsed = json.loads(investigator_output)
        verdict = parsed.get("verdict", "").lower()
        reason = parsed.get("reason", "")
        user_friendly_reason = parsed.get("user_friendly_reason", "")

        if verdict not in ["safe", "suspicious", "likely scam"]:
            raise ValueError("Invalid verdict value. Must be one of 'safe', 'suspicious', or 'likely scam'.")
        
        risk_score = {
            "safe": 0,
            "suspicious": 50,
            "likely scam": 90
        }
        score = risk_score[verdict]

        return {
            "agent": "sellerInvestigator",
            "verdict": verdict,
            "reasoning": reason,
            "user_friendly_reason": user_friendly_reason,
            "score": score,
            "flagged": verdict != "safe",
            "source": "seller_reviews"
        }
    
    except json.JSONDecodeError:
        return{
            "error": "Invalid JSON format in investigator output.",
            "raw_output": investigator_output #returns the raw output for debugging we dont occasioanlly need this.
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "raw_output": investigator_output  # for debugging
        }