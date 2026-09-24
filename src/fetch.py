import feedparser
import requests
import json
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "arXiv cs.AI": "http://export.arxiv.org/rss/cs.AI",
    "arXiv cs.LG": "http://export.arxiv.org/rss/cs.LG",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "r/MachineLearning": "https://www.reddit.com/r/MachineLearning/.rss",
    "World News": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
}

def fetch_rss() -> List[Dict]:
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            # Take top 5 recent entries per feed
            for entry in feed.entries[:5]:
                link = entry.get('link', '')
                if not link:
                    continue
                articles.append({
                    "url": link,
                    "title": entry.get('title', ''),
                    "source": source,
                    "content": entry.get('description', '')[:500]
                })
        except Exception as e:
            logger.error(f"Error fetching from {source}: {e}")
    return articles

def fetch_hackernews() -> List[Dict]:
    articles = []
    try:
        # Get current front page for quality top stories
        url = "http://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=10"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for hit in data.get('hits', []):
            link = hit.get('url') or hit.get('story_url')
            if not link:
                continue
            articles.append({
                "url": link,
                "title": hit.get('title', ''),
                "source": "Hacker News",
                "content": ""
            })
    except Exception as e:
        logger.error(f"Error fetching Hacker News: {e}")
    return articles

def deduplicate(articles: List[Dict], state_file: str) -> Tuple[List[Dict], List[str]]:
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            sent_urls = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sent_urls = []
        
    sent_set = set(sent_urls)
    new_articles = []
    seen_in_batch = set()
    
    for article in articles:
        url = article["url"]
        if url not in sent_set and url not in seen_in_batch:
            new_articles.append(article)
            seen_in_batch.add(url)
            
    return new_articles, sent_urls
