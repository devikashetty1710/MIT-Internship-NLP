import hashlib
import re
import time
import urllib.request
from datetime import datetime
import feedparser
import pandas as pd
from pymongo import MongoClient

class RedditRSSScraper:
    def __init__(self, mongodb_uri="mongodb://localhost:27017/"):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client["mental_health_research"]
        self.collection = self.db["reddit_posts"]
        # Custom headers to emulate browser requests and prevent 403 / throttling blocks
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def generate_author_hash(self, author_url):
        if not author_url:
            return "anonymous_or_deleted"
        author_name = author_url.split("/user/")[-1] if "/user/" in author_url else "anonymous"
        salt = "MIT_MH_NLP_2026"
        return hashlib.sha256((author_name + salt).encode("utf-8")).hexdigest()

    def fetch_feed_data(self, rss_url):
        posts = []
        try:
            req = urllib.request.Request(rss_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                feed = feedparser.parse(xml_data)
                
                for entry in feed.entries:
                    raw_content = entry.get("summary", "") or entry.get("title", "")
                    if not raw_content:
                        continue
                    
                    raw_id = entry.get("id", "").split("/")[-1] if "/" in entry.get("id", "") else entry.get("id")
                    
                    # Extract subreddit name from link
                    link = entry.get("link", "")
                    sub_match = re.search(r'/r/([^/\n?#]+)', link, re.IGNORECASE)
                    sub_name = sub_match.group(1).lower() if sub_match else "unknown"

                    post_doc = {
                        "post_id": f"reddit_rss_{raw_id}",
                        "platform": "Reddit",
                        "timestamp": datetime.now(),
                        "author_hash": self.generate_author_hash(entry.get("author_detail", {}).get("href", "")),
                        "parent_id": None,
                        "raw_text": f"{entry.get('title')}\n{raw_content}",
                        "platform_specific_metadata": {
                            "subreddit": sub_name,
                            "via_source": "Public RSS Feed",
                            "permalink": link
                        }
                    }
                    posts.append(post_doc)
        except Exception as e:
            print(f"  [!] Failed to pull {rss_url}: {e}")
        return posts

    def save_to_mongodb(self, posts):
        if not posts:
            return 0
        saved_count = 0
        for record in posts:
            result = self.collection.update_one(
                {"post_id": record["post_id"]},
                {"$set": record},
                upsert=True
            )
            if result.upserted_id or result.modified_count:
                saved_count += 1
        return len(posts)

def main():
    MONGODB_URI = "mongodb://localhost:27017/"
    scraper = RedditRSSScraper(mongodb_uri=MONGODB_URI)
    
    # 15 distinct subreddits
    target_subreddits = [
        "mentalhealth", "anxiety", "depression", "selfhelp", 
        "psychology", "offmychest", "advice", "jobs", 
        "college", "suicidewatch", "lonely", "stress", 
        "emotionalintelligence", "trauma", "socialanxiety"
    ]
    
    # Multiple endpoints per subreddit to bypass the 25-post limit per feed
    feed_types = ["hot/.rss", "new/.rss", "top/.rss?t=month", "top/.rss?t=year"]
    
    print(f"[*] Starting multi-feed scraping pipeline across {len(target_subreddits)} subreddits...")
    total_ingested = 0
    
    for sub in target_subreddits:
        print(f"\n---> Ingesting r/{sub} ...")
        for feed in feed_types:
            rss_url = f"https://www.reddit.com/r/{sub}/{feed}"
            posts = scraper.fetch_feed_data(rss_url)
            if posts:
                count = scraper.save_to_mongodb(posts)
                total_ingested += count
                print(f"  [+] Ingested {len(posts)} posts from /{feed}")
            time.sleep(1.5)  # Pause to avoid rate limits
            
    total_db_count = scraper.collection.count_documents({})
    print(f"\n[✔] Multi-subreddit scraping complete!")
    print(f"[✔] Total documents in MongoDB collection 'reddit_posts': {total_db_count}")

if __name__ == "__main__":
    main()