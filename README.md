# Scaminator

E-Commerce Fraud Detector  
SENG 472 LLM Term Project

---

## Overview

Fraud Detector is a multi-agent, LLM-powered system designed to assess the trustworthiness of e-commerce products and sellers. By analyzing product descriptions, reviews, and seller information, the system provides an overall verdict, a trust score, and actionable insights for users to make safer online purchases.

---

## Features

- **Multi-Agent Analysis:**  
  Separate agents investigate product descriptions, reviews, and seller profiles.

- **LLM-Powered Reasoning:**  
  Uses Google Gemini and custom logic to generate human-like, explainable verdicts.

- **Comprehensive Output:**  
  Provides a summary, trust score (0-100), detailed reasoning, and user suggestions.

- **Modular Design:**  
  Easily extendable for new data sources or analysis agents.

---

## Project Structure

```
fraud-detector/
│
├── backend/
│   ├── agents/
│   │   └── final_judge.py
│   ├── investigators/
│   │   └── comment_Investigator.py
│   ├── scraper/
│   │   └── product_comments.py
│   └── utils/
│       └── gemini_utils.py
│
├── frontend/
│   └── ... (UI code, e.g., Streamlit app)
│
├── requirements.txt
└── README.md
```

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/fraud-detector.git
   cd fraud-detector
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up API keys:**
   - Place your Google Gemini API key and any other required credentials in a `.env` file or as environment variables as needed by `gemini_utils.py`.

---

## Usage

### Backend

Run the backend analysis (example for product comments):

```sh
cd backend
python scraper/product_comments.py
```

Run the final judge agent:

```sh
python -m agents.final_judge
```

### Frontend

If using Streamlit or another UI, run:

```sh
streamlit run frontend/app.py
```

---

## How It Works

1. **Scraping:**  
   Product and seller data are scraped from e-commerce platforms.

2. **Agent Analysis:**  
   - **Product Description Investigator:** Analyzes the product description for suspicious patterns.
   - **Product Reviews Investigator:** Evaluates user reviews for authenticity and red flags.
   - **Seller Information Investigator:** Checks seller reputation and behavior.

3. **Final Judge:**  
   Aggregates all agent outputs, generates a trust score, and provides a detailed, explainable verdict.

---

## Example Output

```
### Summary of Analysis

The product description contains inconsistencies and several negative reviews mention non-delivery. The seller has a low reputation score.

# Likely Scam

### Overall Trustworthy Score: 18/100

### Overall Score Review

The product and seller both exhibit multiple red flags, including fake reviews and suspicious seller activity.

### Reasonings

**1.** Multiple reviews report non-delivery.  
**2.** Seller has only been active for 1 month.  
**3.** Product description contains grammatical errors.  
...

### Additional Suggestions for Users

Avoid purchasing from this seller. Look for verified sellers with a longer history and positive reviews.
```

---
## License

This project is for academic use only. See [LICENSE](LICENSE) for details.

---

## Authors

- [Your Name]
- [Team Members]

---

## Acknowledgements

- Google Gemini API
- Streamlit
- Pydantic
- SENG 472, TED University
