import hashlib
from datetime import datetime
import feedparser
from pymongo import MongoClient

# -------------------------------------------------------------
# DATABASE INITIALIZATION (Layer 02)
# -------------------------------------------------------------
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["mental_health_research"]
collection = db["reddit_posts"]

def generate_author_hash(author_url):
    """Extracts the author username from the RSS profile link and hashes it

    to comply with ethical PII scrub requirements.
    """
    if not author_url:
        return "anonymous_or_deleted"
    
    # Reddit RSS author links usually look like: https://www.reddit.com/user/username
    author_name = author_url.split("/user/")[-1] if "/user/" in author_url else "anonymous"
    
    salt = "MIT_MH_NLP_2026"
    return hashlib.sha256((author_name + salt).encode("utf-8")).hexdigest()

def scrape_subreddit_rss(subreddit_name):
    """Fetches public hot posts via the public RSS feed endpoint."""
    url = f"https://www.reddit.com/r/{subreddit_name}/hot/.rss"
    print(f"[*] Fallback activated: Extracting data from {url} ...")
    
    # Parse the RSS feed structure directly
    feed = feedparser.parse(url)
    
    if feed.bozo:
        print("[!] Failed to parse RSS feed. It's possible Reddit is throttling requests.")
        return

    batch_records = []
    
    for entry in feed.entries:
        # Avoid empty content records
        raw_content = entry.get("summary", "") or entry.get("title", "")
        if not raw_content:
            continue
            
        # Extract post identifier from the standard RSS ID link
        raw_id = entry.get("id", "").split("/")[-1] if "/" in entry.get("id", "") else entry.get("id")

        # Map cleanly to your Project's Unified Schema
        post_doc = {
            "post_id": f"reddit_rss_{raw_id}",
            "platform": "Reddit",
            "timestamp": datetime.now(), # RSS feeds default to live system streaming metadata
            "author_hash": generate_author_hash(entry.get("author_detail", {}).get("href", "")),
            "parent_id": None, # RSS pulls submissions, which act as root nodes
            "raw_text": f"{entry.get('title')}\n{raw_content}",
            "platform_specific_metadata": {
                "subreddit": subreddit_name,
                "via_source": "Public RSS Feed",
                "permalink": entry.get("link", "")
            }
        }
        batch_records.append(post_doc)

    # Database Write Transaction
    if batch_records:
        print(f"[+] Inserting {len(batch_records)} public RSS records into MongoDB...")
        for record in batch_records:
            collection.update_one(
                {"post_id": record["post_id"]}, {"$set": record}, upsert=True
            )
        print("[✔] Layer 01 & 02 complete. Data securely stored via RSS workaround!")
    else:
        print("[-] No valid text content retrieved on this pass.")

if __name__ == "__main__":
    scrape_subreddit_rss("mentalhealth")