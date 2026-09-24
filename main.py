import logging
import json
import sys
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from src.fetch import fetch_rss, fetch_hackernews, deduplicate
from src.summarize import summarize_and_categorize
from src.format_email import generate_html_email
from src.send import send_email

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

STATE_FILE = "sent_articles.json"

def main():
    logger.info("Starting Daily AI Digest Pipeline...")
    
    logger.info("Fetching articles...")
    rss_articles = fetch_rss()
    hn_articles = fetch_hackernews()
    all_articles = rss_articles + hn_articles
    
    logger.info(f"Fetched total {len(all_articles)} articles.")
    
    new_articles, all_sent_urls = deduplicate(all_articles, STATE_FILE)
    logger.info(f"Found {len(new_articles)} new articles after deduplication.")
    
    if not new_articles:
        logger.info("No new articles to process. Exiting.")
        sys.exit(0)
        
    logger.info("Summarizing and categorizing via LLM...")
    processed_articles = summarize_and_categorize(new_articles)
    
    final_articles = [art for art in processed_articles if "summary" in art]
    
    if not final_articles:
        logger.warning("No articles were successfully summarized. Exiting.")
        sys.exit(0)
        
    logger.info("Formatting email...")
    html_content = generate_html_email(final_articles)
    
    logger.info("Sending email...")
    success = send_email(html_content)
    
    if success:
        logger.info("Updating state file...")
        sent_urls = set(all_sent_urls)
        for art in final_articles:
            sent_urls.add(art["url"])
            
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_urls), f, indent=2)
        logger.info("Pipeline completed successfully.")
    else:
        logger.error("Failed to send email. State file not updated.")
        sys.exit(1)

if __name__ == "__main__":
    main()
