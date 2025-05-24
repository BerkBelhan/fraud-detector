import streamlit as st
from backend.agents.investigators.comment_Investigator import evaluate_comments
from backend.agents.investigators.seller_Investigator import evaluate_seller_comments
from backend.agents.investigators.final_verdict_agent import evaluate_overall_verdict

from backend.scraper.product_comments import (
    launch_driver as launch_product_driver,
    navigate_to_full_comments,
    extract_product_reviews
)

from backend.scraper.seller import (
    launch_driver as launch_seller_driver,
    get_seller_url_from_product,
    fetch_seller_reviews,
    extract_seller_info_and_reviews
)

# ---------------- Page Configuration ---------------- #
st.set_page_config(
    page_title="🛡️ E-Commerce Fraud Detector",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("<h1 style='text-align: center;'>🛍️ Trendyol Fraud Detector</h1>", unsafe_allow_html=True)
st.markdown("Analyze Trendyol product and seller to detect potential fraud risks using AI 🤖")

# ---------------- URL Input ---------------- #
product_url = st.text_input("🔗 Enter Trendyol Product URL", placeholder="https://www.trendyol.com/...")

if st.button("🔍 Analyze"):
    if not product_url.startswith("https://www.trendyol.com"):
        st.error("❌ Please enter a valid Trendyol product URL.")
    else:
        try:
            # ------------- Product Review Analysis ------------- #
            st.subheader("🛒 Step 1: Analyzing Product Reviews")
            with st.spinner("Scraping and analyzing product reviews..."):
                product_driver = launch_product_driver()
                if not navigate_to_full_comments(product_driver, product_url):
                    st.error("❌ Failed to load product reviews.")
                    product_driver.quit()
                    st.stop()

                product_data = extract_product_reviews(product_driver)
                product_driver.quit()
                comments = product_data["comments"]
                product_feedback = evaluate_comments(comments)

            with st.expander("📃 View Product Review Evaluation"):
                st.json(product_feedback)

            st.success("✅ Product reviews analyzed.")

            # ------------- Seller Review Analysis ------------- #
            st.subheader("🏪 Step 2: Analyzing Seller Reviews")
            with st.spinner("Scraping and analyzing seller reviews..."):
                seller_driver = launch_seller_driver()
                seller_url = get_seller_url_from_product(seller_driver, product_url)

                if not seller_url or not fetch_seller_reviews(seller_driver, seller_url):
                    st.error("❌ Failed to extract seller reviews.")
                    seller_driver.quit()
                    st.stop()

                seller_data = extract_seller_info_and_reviews(seller_driver)
                seller_driver.quit()
                seller_comments = seller_data["reviews"]
                seller_feedback = evaluate_seller_comments(seller_comments)

            with st.expander("📃 View Seller Review Evaluation"):
                st.json(seller_feedback)

            st.success("✅ Seller reviews analyzed.")

            # ------------- Final Verdict ------------- #
            st.subheader("🔍 Step 3: Final Verdict")
            with st.spinner("Evaluating overall fraud risk..."):
                final_result = evaluate_overall_verdict(product_feedback, seller_feedback)

            st.markdown("---")
            st.markdown(f"""
                <div style="background-color:#f9f9f9;padding:20px;border-radius:10px;border:1px solid #ddd;">
                    <h2 style="text-align:center;">🚦 Final Verdict: {final_result["final_verdict"]}</h2>
                    <p style="text-align:center;font-size:16px;">📌 <b>Reason:</b> {final_result["reason"]}</p>
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"🚨 An error occurred: {e}")
