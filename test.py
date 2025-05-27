import json
# Import the specific functions and classes from your existing files
from backend.scraper.scraper import scrape_reviews
from backend.agents.productReviewInvestigator import ProductReviewInvestigator

def main():
    """
    Orchestrates the end-to-end test of the scraper and review agent.
    """
    # --- Step 1: Initialize the Investigator Agent ---
    # This creates an instance of your agent, ready to analyze.
    print("Initializing the Product Review Investigator Agent...")
    review_agent = ProductReviewInvestigator()
    print("-" * 30)

    # --- Step 2: Get URL from the User ---
    product_url = input("Enter the e-commerce product URL to investigate: ")
    if not product_url:
        print("No URL entered. Exiting.")
        return
    
    # --- Step 3: Use the Scraper to Get Reviews ---
    print("\nScraping reviews from the URL... (This may take a moment)")
    try:
        # The scrape_reviews function expects a list of URLs, so we wrap it.
        # The result will look like: [[[metadata], "comment 1", "comment 2", ...]]
        scraped_data_list = scrape_reviews([product_url])
        
        if not scraped_data_list or not scraped_data_list[0]:
            print("❌ Scraping failed. Could not retrieve any reviews from the page.")
            return
            
        # Extract the review list for the first (and only) URL
        scraped_reviews_with_metadata = scraped_data_list[0]
        
    except Exception as e:
        print(f"❌ An error occurred during scraping: {e}")
        return

    # --- Step 4: Prepare the Data for the Agent ---
    # Your agent's evaluate_reviews method expects a clean list of comment strings.
    # The first item from the scraper is metadata ([rating, review_count, ...]),
    # so we take everything *after* the first item.
    actual_comments = scraped_reviews_with_metadata[1:]

    if not actual_comments:
        print("✅ Scraping was successful, but no individual comments were found on the page.")
        return

    print(f"✅ Successfully scraped {len(actual_comments)} comments.")
    print("-" * 30)

    # --- Step 5: Send Reviews to the Agent for Analysis ---
    print("\nSending comments to the agent for analysis...")
    analysis_result = review_agent.evaluate_reviews(actual_comments)

    # --- Step 6: Display the Final Verdict ---
    print("\n--- AGENT's FINAL VERDICT ---")
    # Use json.dumps for a clean, readable print of the dictionary
    print(json.dumps(analysis_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()