def evaluate_overall_verdict(product_feedback, seller_feedback):
    product_verdict = product_feedback.get("verdict", "").lower()
    seller_verdict = seller_feedback.get("verdict", "").lower()

    if "suspicious" in product_verdict or "suspicious" in seller_verdict:
        return {
            "final_verdict": "Red",
            "reason": "One or both agents marked the source as suspicious."
        }

    if "inconclusive" in product_verdict or "inconclusive" in seller_verdict:
        return {
            "final_verdict": "Orange",
            "reason": "One or both agents returned inconclusive results. Needs manual review."
        }

    return {
        "final_verdict": "Green",
        "reason": "Both agents evaluated the product and seller as trustworthy."
    }