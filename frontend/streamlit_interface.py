import streamlit as st
from annotated_text import annotated_text
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.pipeliner import run_analysis_pipeline

# Sidebar
st.sidebar.title("🛡️ E-Commerce Fraud Detector")
page = st.sidebar.radio("Menu", ["Home", "Run Analysis", "About"])

def show_final_verdict(final_output):
    #annotated_text(final_output)
    st.markdown(final_output)


if page == "Home":
    st.title("Welcome to the E-Commerce Fraud Detection System")
    st.write("Use the menu to get started.")

elif page == "Run Analysis":
    st.title("Run Fraud Check")
    user_input = st.text_area("Paste product/seller reviews or link:")

    if st.button("Analyze"):
        with st.spinner("Running analysis with agents..."):
            final_output, all_intermediate_data = run_analysis_pipeline(user_input)

        # Display intermediate steps (optional, for dev)
        with st.expander("🔍 Agent Responses (Developer Mode)", expanded=False):
            for key, value in all_intermediate_data.items():
                st.markdown(f"**{key}**:\n```json\n{value}\n```")

        # Final result
        st.subheader("🧠 Final Verdict")
        show_final_verdict(final_output)

elif page == "About":
    st.title("About this Project")
    st.write("Multi-agent fraud detection system using Gemini LLM.")
