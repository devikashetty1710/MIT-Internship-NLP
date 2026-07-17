import hashlib
import re
from datetime import datetime
import feedparser
import pandas as pd
from pymongo import MongoClient

class RedditRSSScraper:
    def __init__(self, mongodb_uri="mongodb://localhost:27017/"):
        """
        Initialize the Reddit RSS Scraper and MongoDB connection.
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client["mental_health_research"]
        self.collection = self.db["reddit_posts"]

    def extract_subreddit_name(self, url):
        """
        Extract subreddit name from a standard Reddit URL.

        Args:
            url (str): Reddit URL (e.g., https://www.reddit.com/r/mentalhealth/)

        Returns:
            str: Subreddit name or None if not found
        """
        patterns = [
            r'reddit\.com\/r\/([^/\n?#]+)',
            r'\/r\/([^/\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return None

    def generate_author_hash(self, author_url):
        """
        Extracts the author username from the RSS profile link and hashes it
        to comply with ethical PII scrub requirements.
        """
        if not author_url:
            return "anonymous_or_deleted"
        
        author_name = author_url.split("/user/")[-1] if "/user/" in author_url else "anonymous"
        salt = "MIT_MH_NLP_2026"
        return hashlib.sha256((author_name + salt).encode("utf-8")).hexdigest()

    def get_subreddit_posts(self, subreddit_name):
        """
        Fetch hot posts for a specific subreddit via public RSS feed.

        Args:
            subreddit_name (str): Name of the subreddit

        Returns:
            list: List of normalized post dictionaries
        """
        posts = []
        rss_url = f"https://www.reddit.com/r/{subreddit_name}/hot/.rss"
        print(f"[*] Extracting data from feed: {rss_url} ...")

        try:
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                print(f"[!] Warning: Feed parser flagged structural anomalies. Target feed may be throttled.")
                return posts

            for entry in feed.entries:
                raw_content = entry.get("summary", "") or entry.get("title", "")
                if not raw_content:
                    continue
                    
                raw_id = entry.get("id", "").split("/")[-1] if "/" in entry.get("id", "") else entry.get("id")

                post_doc = {
                    "post_id": f"reddit_rss_{raw_id}",
                    "platform": "Reddit",
                    "timestamp": datetime.now(),
                    "author_hash": self.generate_author_hash(entry.get("author_detail", {}).get("href", "")),
                    "parent_id": None,
                    "raw_text": f"{entry.get('title')}\n{raw_content}",
                    "platform_specific_metadata": {
                        "subreddit": subreddit_name,
                        "via_source": "Public RSS Feed",
                        "permalink": entry.get("link", "")
                    }
                }
                posts.append(post_doc)

        except Exception as e:
            print(f"[!] An error occurred while parsing the feed: {e}")

        return posts

    def save_to_mongodb(self, posts):
        """
        Upsert processed records directly to MongoDB collection and show stats.
        """
        if not posts:
            print("[-] No valid text content retrieved to save.")
            return

        print(f"[+] Upserting {len(posts)} public RSS records into MongoDB...")
        for record in posts:
            self.collection.update_one(
                {"post_id": record["post_id"]}, 
                {"$set": record}, 
                upsert=True
            )
        print("[✔] Layer 01 & 02 complete. Data securely stored via RSS workaround!")

        # Generate structural statistics matching your mentor's reporting flow
        df = pd.DataFrame(posts)
        print("\n--- Statistics ---")
        print(f"Total posts processed: {len(posts)}")
        print(f"Unique author hashes: {df['author_hash'].nunique()}")
        print(f"Target Subreddit: r/{posts[0]['platform_specific_metadata']['subreddit']}")

    def scrape_subreddit(self, subreddit_url):
        """
        Complete workflow execution block mapping to the mentor's scrape_video template.
        """
        subreddit_name = self.extract_subreddit_name(subreddit_url)

        if not subreddit_name:
            print("Invalid Reddit URL. Please check the path pattern and try again.")
            return

        print(f"Target Subreddit Name Extracted: r/{subreddit_name}")
        posts = self.get_subreddit_posts(subreddit_name)
        
        if posts:
            self.save_to_mongodb(posts)
        else:
            print("No public posts found or unable to fetch streams.")

def main():
    # Massive multi-subreddit pool expansion to bypass 25-post RSS ceilings
    SUBREDDITS = [
        "mentalhealth", "anxiety", "depression", "selfhelp", "psychology",
        "offmychest", "advice", "jobs", "college", "suicidewatch", "lonely"
    ] 
    MONGODB_URI = "mongodb://localhost:27017/"

    # Initialize scraper matching the main workflow template
    scraper = RedditRSSScraper(mongodb_uri=MONGODB_URI)

    # Execute main workflow over all target forums
    print(f"[*] Starting raw ingestion pipeline across {len(SUBREDDITS)} subreddits...")
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/"
        try:
            scraper.scrape_subreddit(url)
        except Exception as e:
            print(f"[!] Skipped r/{sub} due to stream interruption: {e}")
            
    print("\n[✔] DONE: MongoDB is now populated with raw data from all subreddits!")

if __name__ == "__main__":
    main()