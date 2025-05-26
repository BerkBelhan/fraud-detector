# C:\SENG472\MainProje\fraud-detector\frontend\streamlit.py

import sys
import os
import streamlit as st
import time # Keep time if other parts of your original streamlit file used it.
# import json # No longer needed directly here if all parsing is in backend
# import re   # No longer needed directly here

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Frontend & Backend Imports ---
from ui_config import GENIE_IMAGE_PATH, GENIE_PERSONA_DIALOGUE
# Removed extract_json_from_response as nottrendyol handles its own JSON now
from backend.pipeliner import run_analysis_pipeline
# Import the main function correctly
from nottrendyol.fraud_pipeline import main as nottrendyol_main_pipeline


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
    # This function expects "verdict", "reason", "score"
    # We will adapt the nottrendyol data to fit this if possible
    # For nottrendyol, 'level' maps to 'verdict'
    verdict = feedback_dict.get("level", feedback_dict.get("verdict", "Unknown"))
    reason = feedback_dict.get("reason", "No reasoning was provided.")
    score = feedback_dict.get("score", "N/A") # nottrendyol doesn't provide a score for these intermediate steps

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

def display_summary_finding(icon, title, summary_text):
    st.markdown(
        f'<div class="finding-box unknown">'
        f'  <p class="finding-title">{icon} {title}</p>'
        f'  <p class="reason">{summary_text}</p>'
        f'</div>', unsafe_allow_html=True)

def display_final_verdict(final_verdict_content, is_external_pipeline=False):
    title = "Final Verdict"
    text_to_display = ""
    verdict_class_override = None

    if is_external_pipeline:
        # For the external pipeline, final_verdict_content is a dictionary
        level = final_verdict_content.get("final_level", "Error")
        reason = final_verdict_content.get("summary_reason", "Analysis failed.")
        text_to_display = f"{level} - {reason}"
        
        level_lower = str(level).lower()
        if "safe" in level_lower: verdict_class_override = "safe"
        elif "suspicious" in level_lower: verdict_class_override = "suspicious"
        elif "scam" in level_lower or "error" in level_lower: verdict_class_override = "scam"
        else: verdict_class_override = "unknown"

    else:
        # For the internal pipeline, it's a pre-formatted string
        text_to_display = final_verdict_content


    html_class = f"final-verdict-box {verdict_class_override if verdict_class_override else ''}"
    st.markdown(
        f'<div class="{html_class.strip()}">' # Apply color class if available
        f'  <p class="final-verdict-title">{title}</p>'
        f'  <p class="final-verdict-text">{text_to_display}</p>'
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
    if st.session_state.view in ['results', 'nottrendyol_results']: # Unified button logic
        if st.button("Analyze Another Product", use_container_width=True):
            st.session_state.view = 'input'
            st.session_state.results = {}
            st.rerun()

with right_col:
    if st.session_state.view == 'input':
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['welcome']}</p>", unsafe_allow_html=True)
        product_url = st.text_input(" ", placeholder="Paste Product URL here...", label_visibility="collapsed")

        if st.button("Unveil the Truth!", use_container_width=True):
            product_url = product_url.strip()
            if "trendyol.com/" in product_url:
                st.session_state.product_url = product_url
                st.session_state.view = 'processing_trendyol' # Specific view for trendyol
                st.rerun()
            else:
                st.session_state.product_url = product_url # Store URL for external
                st.session_state.view = 'processing_external' # Specific view for external
                st.rerun()

    elif st.session_state.view == 'processing_trendyol':
        thinking_placeholder = st.empty()
        base_html = '<div class="thinking-bar">{}</div>'
        with st.spinner(GENIE_PERSONA_DIALOGUE['thinking']):
            try:
                final_output, intermediate_data = run_analysis_pipeline(st.session_state.product_url, thinking_placeholder, base_html)
                st.session_state.results['final_verdict_str'] = final_output
                st.session_state.results['raw_data'] = intermediate_data
                st.session_state.view = 'results'
                st.rerun()
            except Exception as e:
                st.error(f"A critical error occurred during Trendyol pipeline execution: {e}")
                st.session_state.view = 'input'
                st.rerun()
    
    elif st.session_state.view == 'processing_external':
        with st.spinner("Running external analysis... This might take a moment."):
            try:
                # Call the modified nottrendyol_main_pipeline and store its dict output
                nottrendyol_results_data = nottrendyol_main_pipeline(url=st.session_state.product_url)
                st.session_state.results['nottrendyol_data'] = nottrendyol_results_data
                st.session_state.view = 'nottrendyol_results' # New view for external results
                st.rerun()
            except Exception as e:
                st.error(f"External fraud pipeline failed: {e}")
                st.session_state.view = 'input'
                st.rerun()

    elif st.session_state.view == 'results': # For Trendyol pipeline results
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['final_verdict']}</p>", unsafe_allow_html=True)
        display_final_verdict(st.session_state.results['final_verdict_str'])

        with st.expander("Show Detailed Investigator Findings & Raw Data (Trendyol)"):
            st.markdown("---")
            st.subheader("Investigator Summaries")
            raw_data = st.session_state.results.get('raw_data', {})
            display_summary_finding("📝", "Description Analysis", raw_data.get("Description Info", "Analysis not available."))
            display_summary_finding("💬", "Product Review Analysis", raw_data.get("Product Paragraph", "Analysis not available."))
            display_summary_finding("📦", "Seller Information Analysis", raw_data.get("Seller Paragraph", "Analysis not available."))
            st.markdown("---")
            st.subheader("Raw Scraper Data")
            st.json(st.session_state.results.get('raw_data', {}))

    elif st.session_state.view == 'nottrendyol_results': # New view for external pipeline results
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['final_verdict']}</p>", unsafe_allow_html=True)
        data = st.session_state.results.get('nottrendyol_data', {})
        
        # Display the final verdict from external pipeline
        display_final_verdict(data.get("final_verdict", {"final_level": "Error", "summary_reason": "No final verdict."}), is_external_pipeline=True)

        with st.expander("Show Detailed Findings (External Site)"):
            st.markdown("---")
            st.subheader("Product & Seller Information")
            st.markdown(f"**Title:** {data.get('product_title', 'N/A')}")
            st.markdown(f"**Price:** {data.get('product_price', 'N/A')}")
            st.markdown(f"**Seller:** {data.get('seller_name', 'N/A')}")
            st.markdown("---")
            st.subheader("Analysis Components")
            display_finding("🗣️", "Comment Analysis Verdict", data.get("comment_verdict", {}))
            display_finding("💰", "Price Comparison Verdict", data.get("price_verdict", {}))
            st.markdown("---")
            st.markdown(f"**Estimated API Cost for this analysis:** ${data.get('api_cost', 0.0):.6f}")