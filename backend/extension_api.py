import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import both pipelines
from backend.pipeliner import run_analysis_pipeline
from nottrendyol.fraud_pipeline import main as run_nottrendyol_pipeline

# Dummy placeholder for non-Streamlit execution
class DummyPlaceholder:
    def markdown(self, *args, **kwargs):
        pass  # Ignore any visual output

# --- FastAPI setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate")
async def evaluate(request: Request):
    body = await request.json()
    url = body.get("url", "").strip()

    if not url:
        return {
            "final_verdict": {
                "final_level": "Error",
                "summary_reason": "No URL provided."
            }
        }

    if "trendyol.com/" in url:
        try:
            dummy_placeholder = DummyPlaceholder()
            base_html = "<div>{}</div>"

            final_output, raw_data, intermediate_data = run_analysis_pipeline(
                url, dummy_placeholder, base_html
            )

            return {
                "final_verdict": {
                    "final_level": "Analyzed",
                    "summary_reason": final_output
                },
                "raw_data": raw_data,
                "intermediate_analysis": intermediate_data
            }

        except Exception as e:
            return {
                "final_verdict": {
                    "final_level": "Error",
                    "summary_reason": f"Trendyol pipeline failed: {str(e)}"
                }
            }

    else:
        try:
            result = run_nottrendyol_pipeline(url)
            verdict = result.get("final_verdict") or {}
            return {
                "final_verdict": {
                    "final_level": verdict.get("final_level", "Error"),
                    "summary_reason": verdict.get("summary_reason", "No explanation provided.")
                },
                "full_result": result
            }

        except Exception as e:
            return {
                "final_verdict": {
                    "final_level": "Error",
                    "summary_reason": f"External pipeline failed: {str(e)}"
                }
            }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)