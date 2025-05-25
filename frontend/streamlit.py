# C:\SENG472\MainProje\fraud-detector\frontend\streamlit.py

import sys
import os
import streamlit as st
import time
import json
import re

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Frontend & Backend Imports ---
from ui_config import GENIE_IMAGE_PATH, GENIE_PERSONA_DIALOGUE, extract_json_from_response
from backend.pipeliner import run_analysis_pipeline # Assuming this is the pipeliner.py you confirmed

# --- Page Config ---
st.set_page_config(
    page_title="Scaminator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- UI Helper Functions ---
def load_external_css(css_file_path):
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found at {css_file_path}")

def display_finding(icon, title, feedback_dict):
    verdict = feedback_dict.get("verdict", "Unknown")
    reason = feedback_dict.get("reason", "No reasoning was provided.")
    score = feedback_dict.get("score", "N/A")

    verdict_lower = str(verdict).lower()
    if "safe" in verdict_lower: verdict_class = "safe"
    elif "suspicious" in verdict_lower or "warning" in verdict_lower: verdict_class = "suspicious"
    elif "scam" in verdict_lower or "error" in verdict_lower: verdict_class = "scam"
    else: verdict_class = "unknown"

    st.markdown(
        f'<div class="finding-box {verdict_class}">'
        f'  <p class="finding-title">{icon} {title}</p>'
        f'  <p class="verdict {verdict_class}">{verdict} (Score: {score})</p>'
        f'  <p class="reason">{reason}</p>'
        f'</div>', unsafe_allow_html=True)

def display_final_verdict(final_verdict_str):
    try:
        verdict, reason = final_verdict_str.split('\n', 1)
    except (ValueError, AttributeError):
        verdict = "Analysis Error"
        reason = "The final verdict could not be parsed correctly."

    verdict_lower = verdict.lower()
    if "safe" in verdict_lower: verdict_class = "safe"
    elif "caution" in verdict_lower: verdict_class = "suspicious"
    elif "scam" in verdict_lower or "error" in verdict_lower: verdict_class = "scam"
    else: verdict_class = "unknown"

    st.markdown(
        f'<div class="final-verdict-box {verdict_class}">'
        f'  <p class="final-verdict-title">Final Verdict</p>'
        f'  <p class="final-verdict-text {verdict_class}">{verdict.strip().upper()}</p>'
        f'  <p class="final-reason">{reason.strip()}</p>'
        f'</div>', unsafe_allow_html=True)

# --- Main App Logic ---

if 'view' not in st.session_state:
    st.session_state.view = 'input'
if 'results' not in st.session_state:
    st.session_state.results = {}

load_external_css(os.path.join(script_dir, "styles.css"))
st.markdown("<h1 class='main-title'>Scaminator</h1>", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.image(GENIE_IMAGE_PATH, use_container_width=True)
    if st.session_state.view == 'results':
        if st.button("Analyze Another Product", use_container_width=True):
            st.session_state.view = 'input'
            st.session_state.results = {}
            st.rerun()

with right_col:
    if st.session_state.view == 'input':
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['welcome']}</p>", unsafe_allow_html=True)
        product_url = st.text_input(" ", placeholder="Paste the Trendyol Product URL here...", label_visibility="collapsed")

        if st.button("Unveil the Truth!", use_container_width=True):
            if not product_url.strip().startswith("https://www.trendyol.com"):
                st.error("A valid Trendyol product URL is required.")
            else:
                st.session_state.product_url = product_url.strip()
                st.session_state.view = 'processing'
                st.rerun()

    elif st.session_state.view == 'processing':
        # --- Letter-by-letter "Deep Thinking" Animation ---
        thinking_placeholder = st.empty()
        thinking_steps = [
            "Initializing cosmic scrapers...",
            "Probing product page for review emanations...",
            "Scrutinizing seller's ethereal presence...",
            "Transmitting data to the investigator spirits...",
            "Product spirit is weaving a summary...",
            "Seller spirit is discerning patterns...",
            "Consulting controller entities for classification...",
            "Finalizing spectral reports...",
            "Summoning the final judge for the ultimate decree..."
        ]
        full_thought_process = "\n".join(f"• {step}" for step in thinking_steps)
        displayed_text = ""
        base_html = '<div class="thinking-bar"><pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{}</code></pre></div>'
        
        for char_index, char in enumerate(full_thought_process):
            displayed_text += char
            cursor = "▌" if char_index % 2 == 0 else " " 
            thinking_placeholder.markdown(base_html.format(displayed_text + cursor), unsafe_allow_html=True)
            time.sleep(0.015) 

        thinking_placeholder.markdown(base_html.format(displayed_text), unsafe_allow_html=True) # Final text
        time.sleep(0.5) # Pause after animation before clearing
        thinking_placeholder.empty() # Clear the animation placeholder

        # Now show the spinner for the actual pipeline execution
        with st.spinner(GENIE_PERSONA_DIALOGUE['thinking']): 
            try:
                final_output, intermediate_data = run_analysis_pipeline(st.session_state.product_url)
                st.session_state.results['final_verdict_str'] = final_output
                
                # --- KEY CORRECTION HERE ---
                # Using keys that match your confirmed pipeliner.py output
                st.session_state.results['product_json'] = extract_json_from_response(intermediate_data.get("Product Analysis JSON", {}))
                st.session_state.results['seller_json'] = extract_json_from_response(intermediate_data.get("Seller Analysis JSON", {}))
                # --- END KEY CORRECTION ---

                st.session_state.results['raw_data'] = intermediate_data
                st.session_state.view = 'results'
                st.rerun()
            except Exception as e:
                st.error(f"A critical error occurred during pipeline execution: {e}")
                st.session_state.view = 'input'
                st.rerun()

    elif st.session_state.view == 'results':
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['final_verdict']}</p>", unsafe_allow_html=True)
        display_final_verdict(st.session_state.results['final_verdict_str'])

        with st.expander("Show Detailed Investigator Findings & Raw Data"):
            st.markdown("---")
            st.subheader("Intermediate Controller Findings")
            display_finding("Product", "Product Review Analysis", st.session_state.results['product_json'])
            display_finding("Seller", "Seller Review Analysis", st.session_state.results['seller_json'])
            st.markdown("---")
            st.subheader("Raw Data Collected by Scrapers")
            st.json(st.session_state.results['raw_data'])