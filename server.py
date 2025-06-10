# C:\SENG472\MainProje\fraud-detector\server.py
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Path Setup ---
# Add the project root to the Python path to allow imports from backend/ and nottrendyol/
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Backend Imports ---
# Import your two main pipeline functions
from backend.trendyol_pipeline import run_trendyol_analysis
from backend.global_pipeline import run_global_analysis

# --- Flask App Initialization ---
app = Flask(__name__)
# CORS is needed to allow your extension (on chrome-extension://...)
# to make requests to this server (on http://127.0.0.1:5000)
CORS(app) 

# --- API Endpoint ---
@app.route("/evaluate", methods=["POST"])
def evaluate_url():
    print("--- SERVER: Received a request on /evaluate ---")
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "No URL provided"}), 400

    url = data["url"]
    print(f"--- SERVER: Analyzing URL: {url} ---")
    
    final_output_data = None
    intermediate_data_dict = {}
    pipeline_type_used = ""

    try:
        # We pass None for the UI elements because the server has no access to the extension's UI
        # The animation logic for the backend needs to be disabled or conditional
        # For now, we will pass None and modify the backend functions to handle it
        if url.strip().lower().startswith("https://www.trendyol.com"):
            pipeline_type_used = "trendyol"
            # Note: We pass 'None' for the UI elements as the server can't access them
            final_output_data, intermediate_data_dict = run_trendyol_analysis(url, None, None, None)
        else:
            pipeline_type_used = "global"
            # Note: We pass 'None' for the UI elements as the server can't access them
            final_output_data, intermediate_data_dict = run_global_analysis(url, None, None, None)

        response_data = {
            "pipeline_type": pipeline_type_used,
            "final_verdict_data": final_output_data,
            "intermediate_data": intermediate_data_dict
        }

        print("--- SERVER: Analysis complete. Sending response. ---")
        return jsonify(response_data)

    except Exception as e:
        print(f"--- SERVER: An error occurred during pipeline execution: {e} ---")
        return jsonify({"error": str(e)}), 500


# --- Run the Server ---
if __name__ == "__main__":
    # Note: Use port 5000 for Flask, as 8501 is the default for Streamlit
    app.run(host="127.0.0.1", port=5000, debug=True)