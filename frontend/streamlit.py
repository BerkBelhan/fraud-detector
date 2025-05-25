# C:\SENG472\MainProje\fraud-detector\frontend\streamlit.py

import sys
import os
import streamlit as st
import time
# Note: json and re are now used within ui_config.py for extract_json_from_response

# --- This block adds the project root to the Python path ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -----------------------------------------------------------

# --- Import from our new UI configuration file ---
from frontend.ui_config import GENIE_IMAGE_PATH, GENIE_PERSONA_DIALOGUE, extract_json_from_response

# --- All Backend Imports ---
from backend.agents.investigators.product_investigator import ProductReviewInvestigator
from backend.agents.investigators.seller_investigator import evaluate_seller_comments
from backend.agents.controllers.product_controller import classify_product_analysis
from backend.agents.controllers.seller_controller import classify_seller_analysis
from backend.scraper.product_comments import launch_driver as launch_product_driver, navigate_to_full_comments, extract_product_reviews
from backend.scraper.seller import launch_driver as launch_seller_driver, get_seller_url_from_product, fetch_seller_reviews, extract_seller_info_and_reviews

# ----------------- STREAMLIT PAGE CONFIG ----------------- #
st.set_page_config(
    page_title="Scaminator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLES & UI HELPER FUNCTIONS (that use st commands) ---
def load_external_css(css_file_path):
    """Reads a CSS file and injects its content into the Streamlit app."""
    try:
        with open(css_file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Error: The CSS file was not found at {css_file_path}")


def stream_speech(container, speech_text):
    """Simulates a typewriter effect inside a specific container."""
    with container:
        bubble_placeholder = st.empty()
        full_speech = ""
        for chunk in speech_text.split():
            full_speech += chunk + " "
            time.sleep(0.08)
            bubble_placeholder.markdown(
                f'<div class="speech-bubble"><p class="genie-speech">{full_speech}</p></div>',
                unsafe_allow_html=True
            )
        time.sleep(0.5)

def display_finding(icon, title, feedback_dict):
    """Creates a styled box to present a single agent's findings with verdict-based colors."""
    verdict = feedback_dict.get("verdict", "Unknown")
    reason = feedback_dict.get("reason", "No reasoning was provided.")

    # Determine CSS class based on verdict keyword
    verdict_lower = verdict.lower()
    if "safe" in verdict_lower:
        verdict_class = "safe"
    elif "suspicious" in verdict_lower or "warning" in verdict_lower:
        verdict_class = "suspicious"
    elif "scam" in verdict_lower:
        verdict_class = "scam"
    else:
        verdict_class = "unknown" # Default case

    st.markdown(f"<h4>{icon} {title}</h4>", unsafe_allow_html=True)
    # Apply the dynamic class to both the box and the verdict text
    st.markdown(
        f'<div class="finding-box {verdict_class}">'
        f'  <p class="verdict {verdict_class}">{verdict}</p>'
        f'  <p class="reason">{reason}</p>'
        f'</div>',
        unsafe_allow_html=True
    )


# ----------------- BACKEND ORCHESTRATOR ----------------- #
@st.cache_resource
def get_agents():
    print("Initializing AI Agents...")
    product_agent = ProductReviewInvestigator()
    return product_agent

def run_full_analysis(product_url):
    product_agent = get_agents()
    
    st.info("Scaminator is analyzing product data...")
    product_driver = launch_product_driver()
    if not navigate_to_full_comments(product_driver, product_url):
        product_driver.quit()
        raise Exception("Failed to load product reviews page.")
    product_data = extract_product_reviews(product_driver)
    product_driver.quit()
    
    product_comments_raw = product_data.get("comments", [])

    if not product_comments_raw:
        product_feedback = {
            "verdict": "Warning - No Reviews Found",
            "reason": "The Scaminator could not find any product reviews on the page. This might mean the product is new and has no comments, or there was a temporary issue loading them."
        }
    else:
        product_feedback_raw_ai = product_agent.evaluate_reviews(product_comments_raw)
        classified_product_feedback_raw = classify_product_analysis(product_feedback_raw_ai)
        product_feedback = extract_json_from_response(classified_product_feedback_raw) # Now imported
    
    st.info("Scaminator is now investigating the seller...")
    seller_driver = launch_seller_driver()
    seller_url = get_seller_url_from_product(seller_driver, product_url)
    if not seller_url:
        seller_driver.quit()
        raise Exception("Failed to find seller URL from product page.")
    if not fetch_seller_reviews(seller_driver, seller_url):
        seller_driver.quit()
        raise Exception("Failed to load seller reviews page.")
    seller_data = extract_seller_info_and_reviews(seller_driver)
    seller_driver.quit()

    seller_reviews_raw = seller_data.get("reviews", [])

    if not seller_reviews_raw:
        seller_feedback = {
            "verdict": "Warning - No Seller Reviews Found",
            "reason": "The Scaminator could not find any seller reviews. The seller might be new or have no feedback."
        }
    else:
        seller_feedback_raw_ai = evaluate_seller_comments(seller_reviews_raw)
        classified_seller_feedback_raw = classify_seller_analysis(seller_feedback_raw_ai)
        seller_feedback = extract_json_from_response(classified_seller_feedback_raw) # Now imported
    
    return product_feedback, seller_feedback, product_comments_raw, seller_reviews_raw

# ----------------- STREAMLIT APP LAYOUT (Using Session State) ----------------- #

# Initialize session state variables
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'product_feedback' not in st.session_state:
    st.session_state.product_feedback = {}
if 'seller_feedback' not in st.session_state:
    st.session_state.seller_feedback = {}
if 'raw_product_comments' not in st.session_state:
    st.session_state.raw_product_comments = []
if 'raw_seller_reviews' not in st.session_state:
    st.session_state.raw_seller_reviews = []

load_external_css("frontend/styles.css") # Load CSS from external file

st.markdown("<h1 class='main-title'>Scaminator</h1>", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1.5], gap="large")

if not st.session_state.analysis_done:
    with left_col:
        st.markdown('<div class="genie-column">', unsafe_allow_html=True)
        st.image(GENIE_IMAGE_PATH, use_container_width=True) # Use imported constant
        st.markdown('</div>', unsafe_allow_html=True)
    
    with right_col:
        st.markdown(f"<p class='genie-speech'>{GENIE_PERSONA_DIALOGUE['welcome']}</p>", unsafe_allow_html=True) # Use imported dict
        product_url = st.text_input(" ", placeholder="Paste the Trendyol Product URL here...", label_visibility="collapsed")
        
        if st.button("Unveil the Truth!", use_container_width=True):
            if not product_url.strip().startswith("https://www.trendyol.com"):
                st.error("A valid Trendyol product URL is required.")
            else:
                with st.spinner(GENIE_PERSONA_DIALOGUE["thinking"]): # Use imported dict
                    try:
                        p_feedback, s_feedback, raw_p_comments, raw_s_reviews = run_full_analysis(product_url.strip())
                        st.session_state.product_feedback = p_feedback
                        st.session_state.seller_feedback = s_feedback
                        st.session_state.raw_product_comments = raw_p_comments
                        st.session_state.raw_seller_reviews = raw_s_reviews
                        st.session_state.analysis_done = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"An unexpected disturbance occurred: {e}")
                        st.session_state.analysis_done = False 

else: # This is the results view
    with left_col:
        st.markdown('<div class="genie-column">', unsafe_allow_html=True)
        st.image(GENIE_IMAGE_PATH, use_container_width=True) # Use imported constant
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Analyze Another", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.product_feedback = {}
            st.session_state.seller_feedback = {}
            st.session_state.raw_product_comments = []
            st.session_state.raw_seller_reviews = []
            st.rerun()

    with right_col:
        stream_speech(right_col, GENIE_PERSONA_DIALOGUE["done_no_verdict"]) # Use imported dict
        display_finding("Product", "Product Findings", st.session_state.product_feedback)
        display_finding("Seller", "Seller Findings", st.session_state.seller_feedback)

        with st.expander("Show Raw Data Analyzed by Scaminator"):
            st.markdown("---")
            st.subheader("Raw Product Comments Submitted:")
            if st.session_state.raw_product_comments:
                for i, comment in enumerate(st.session_state.raw_product_comments):
                    st.text(f"{i+1}. {comment}")
            else:
                st.info("No raw product comments were processed or available for display.")
            
            st.markdown("---")
            st.subheader("Raw Seller Reviews Submitted:")
            if st.session_state.raw_seller_reviews:
                for i, review in enumerate(st.session_state.raw_seller_reviews):
                    st.text(f"{i+1}. {review}")
            else:
                st.info("No raw seller reviews were processed or available for display.")